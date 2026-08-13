package middleware

import (
	"net/http"
	"strconv"
	"strings"

	"github.com/edgorman/web-app-demo/services/backend/internal/config"
)

// corsMaxAge is how long a browser may cache a preflight result, in seconds. It matches
// the default the previous Starlette CORS middleware used.
const corsMaxAge = 600

// wildcard matches every origin, method or header when it is the sole configured value.
const wildcard = "*"

// CORS answers preflight requests and annotates cross-origin responses according to the
// configured allow-lists.
//
// It must wrap the authentication middleware rather than the other way round: preflight
// requests carry no credentials, and authentication failures still need CORS headers or
// the browser reports them as opaque CORS errors instead of the actual status.
func CORS(cfg config.CORSConfig) func(http.Handler) http.Handler {
	allowMethods := strings.Join(cfg.AllowMethods, ", ")
	allowHeaders := strings.Join(cfg.AllowHeaders, ", ")

	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			origin := r.Header.Get("Origin")
			if origin == "" {
				next.ServeHTTP(w, r)
				return
			}

			allowedOrigin, allowed := resolveOrigin(cfg, origin)
			isPreflight := r.Method == http.MethodOptions && r.Header.Get("Access-Control-Request-Method") != ""

			if allowed {
				w.Header().Set("Access-Control-Allow-Origin", allowedOrigin)
				if cfg.AllowCredentials {
					w.Header().Set("Access-Control-Allow-Credentials", "true")
				}
				if allowedOrigin != wildcard {
					w.Header().Add("Vary", "Origin")
				}
			}

			if !isPreflight {
				next.ServeHTTP(w, r)
				return
			}

			// A preflight is answered here and never reaches the handlers, so an
			// unauthenticated OPTIONS is not an authentication failure.
			if allowed {
				w.Header().Set("Access-Control-Allow-Methods", allowMethods)
				w.Header().Set("Access-Control-Allow-Headers", resolvePreflightHeaders(allowHeaders, r))
				w.Header().Set("Access-Control-Max-Age", strconv.Itoa(corsMaxAge))
			}
			w.WriteHeader(http.StatusOK)
		})
	}
}

// resolveOrigin reports whether origin is allowed and what to echo back for it.
func resolveOrigin(cfg config.CORSConfig, origin string) (string, bool) {
	for _, allowed := range cfg.AllowOrigins {
		if allowed == wildcard {
			// A wildcard cannot be echoed alongside credentials, so the concrete
			// origin is returned instead when credentials are enabled.
			if cfg.AllowCredentials {
				return origin, true
			}
			return wildcard, true
		}
		if allowed == origin {
			return origin, true
		}
	}
	return "", false
}

// resolvePreflightHeaders echoes the requested headers back when every header is
// allowed, so that a wildcard still works for credentialed requests.
func resolvePreflightHeaders(allowHeaders string, r *http.Request) string {
	if allowHeaders != wildcard {
		return allowHeaders
	}
	if requested := r.Header.Get("Access-Control-Request-Headers"); requested != "" {
		return requested
	}
	return wildcard
}
