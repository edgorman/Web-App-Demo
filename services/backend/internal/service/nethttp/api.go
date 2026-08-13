// Package nethttp is the net/http implementation of the API interface.
package nethttp

import (
	"fmt"
	"log/slog"
	"net"
	"net/http"
	"strconv"

	"github.com/edgorman/web-app-demo/services/backend/internal/config"
	"github.com/edgorman/web-app-demo/services/backend/internal/service"
	"github.com/edgorman/web-app-demo/services/backend/internal/service/nethttp/middleware"
	v1 "github.com/edgorman/web-app-demo/services/backend/internal/service/nethttp/resources/v1"
	"github.com/edgorman/web-app-demo/services/backend/internal/storage"
)

// APIPrefixV1 is the path every version 1 resource is mounted under.
const APIPrefixV1 = "/api/v1"

// Service is the net/http implementation of the API interface.
type Service struct {
	config  config.HTTPServiceConfig
	handler http.Handler
}

// compile-time check that the net/http implementation satisfies the API interface.
var _ service.API = (*Service)(nil)

// Option customises a Service at construction.
type Option func(*options)

type options struct {
	verifyToken middleware.TokenVerifier
}

// WithTokenVerifier overrides how provider tokens are verified. Tests use it to
// authenticate without reaching the provider.
func WithTokenVerifier(verify middleware.TokenVerifier) Option {
	return func(o *options) { o.verifyToken = verify }
}

// New builds the API service: the versioned routers, wrapped by authentication, wrapped
// by CORS.
func New(cfg config.ServiceConfig, userStorage storage.UserStorage, opts ...Option) *Service {
	var o options
	for _, opt := range opts {
		opt(&o)
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/", notFound)

	// Include routers with the /api/v1 prefix.
	v1Router := http.NewServeMux()
	v1Router.HandleFunc("/", notFound)
	v1Router.HandleFunc(v1.HelloRoute, v1.Hello)
	mux.Handle(APIPrefixV1+"/", http.StripPrefix(APIPrefixV1, v1Router))

	// Add authentication middleware (Google Sign-In, for now).
	handler := middleware.Authenticate(cfg.Auth.Google.ClientID, userStorage, o.verifyToken)(mux)

	// Add CORS middleware. It is applied last so that it runs outermost and annotates
	// authentication failures too.
	handler = middleware.CORS(cfg.HTTP.CORS)(handler)

	return &Service{config: cfg.HTTP, handler: handler}
}

// Config returns the HTTP configuration the service was built with.
func (s *Service) Config() config.HTTPServiceConfig {
	return s.config
}

// Handler returns the fully wrapped HTTP handler.
func (s *Service) Handler() http.Handler {
	return s.handler
}

// Run starts the HTTP server and blocks until it stops.
func (s *Service) Run() error {
	if s.config.Reload {
		slog.Warn("reload is not supported by the net/http service and has no effect")
	}

	address := net.JoinHostPort(s.config.Host, strconv.Itoa(s.config.Port))
	slog.Info("starting service",
		"name", s.config.AppName,
		"version", s.config.AppVersion,
		"address", address,
	)

	server := &http.Server{Addr: address, Handler: s.handler}
	if err := server.ListenAndServe(); err != nil {
		return fmt.Errorf("serve on %s: %w", address, err)
	}
	return nil
}

// notFound answers unrouted paths with the same JSON error shape the rest of the API uses.
func notFound(w http.ResponseWriter, r *http.Request) {
	v1.WriteJSON(w, http.StatusNotFound, map[string]string{"detail": "Not Found"})
}
