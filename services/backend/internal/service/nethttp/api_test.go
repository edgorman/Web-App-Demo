package nethttp_test

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/edgorman/web-app-demo/services/backend/internal/config"
	"github.com/edgorman/web-app-demo/services/backend/internal/objects"
	"github.com/edgorman/web-app-demo/services/backend/internal/service/nethttp"
	"github.com/edgorman/web-app-demo/services/backend/internal/service/nethttp/middleware"
	v1 "github.com/edgorman/web-app-demo/services/backend/internal/service/nethttp/resources/v1"
)

const (
	testClientID   = "test-client-id.apps.googleusercontent.com"
	testOrigin     = "https://example.com"
	helloPath      = "/api/v1/hello"
	anonymousHello = "Hello from the Web-App-Demo backend!"
)

// testConfig is the service configuration shared by the tests in this package.
func testConfig() config.ServiceConfig {
	cfg := config.DefaultServiceConfig()
	cfg.HTTP.CORS.AllowOrigins = []string{testOrigin}
	cfg.Auth.Google.ClientID = testClientID
	return cfg
}

// fakeUserStorage is an in-memory UserStorage that records the calls made against it.
type fakeUserStorage struct {
	existing *objects.User

	getCalls    []string
	createCalls []objects.User
	updateCalls []objects.User
	deleteCalls []string
}

func (s *fakeUserStorage) Get(_ context.Context, userID string) (*objects.User, error) {
	s.getCalls = append(s.getCalls, userID)
	return s.existing, nil
}

func (s *fakeUserStorage) Create(_ context.Context, user *objects.User) (*objects.User, error) {
	s.createCalls = append(s.createCalls, *user)
	return user, nil
}

func (s *fakeUserStorage) Update(_ context.Context, user *objects.User) (*objects.User, error) {
	s.updateCalls = append(s.updateCalls, *user)
	return user, nil
}

func (s *fakeUserStorage) Delete(_ context.Context, userID string) error {
	s.deleteCalls = append(s.deleteCalls, userID)
	return nil
}

// claimsVerifier returns a TokenVerifier that always succeeds with the given claims.
func claimsVerifier(claims map[string]any) middleware.TokenVerifier {
	return func(context.Context, string, string) (map[string]any, error) {
		return claims, nil
	}
}

// failingVerifier returns a TokenVerifier that always rejects the token.
func failingVerifier() middleware.TokenVerifier {
	return func(context.Context, string, string) (map[string]any, error) {
		return nil, errors.New("token is invalid")
	}
}

// serve runs a request against a service built from cfg and returns the recorded response.
func serve(
	t *testing.T,
	cfg config.ServiceConfig,
	store *fakeUserStorage,
	verify middleware.TokenVerifier,
	request *http.Request,
) *httptest.ResponseRecorder {
	t.Helper()

	var opts []nethttp.Option
	if verify != nil {
		opts = append(opts, nethttp.WithTokenVerifier(verify))
	}
	recorder := httptest.NewRecorder()
	nethttp.New(cfg, store, opts...).Handler().ServeHTTP(recorder, request)
	return recorder
}

// decodeHello decodes a hello response body, failing the test if it is not valid.
func decodeHello(t *testing.T, body string) v1.Response[objects.Message] {
	t.Helper()

	var response v1.Response[objects.Message]
	if err := json.Unmarshal([]byte(body), &response); err != nil {
		t.Fatalf("decode response: %v (body %q)", err, body)
	}
	return response
}

// decodeDetail decodes an error body, failing the test if it is not valid.
func decodeDetail(t *testing.T, body string) string {
	t.Helper()

	var response struct {
		Detail string `json:"detail"`
	}
	if err := json.Unmarshal([]byte(body), &response); err != nil {
		t.Fatalf("decode error response: %v (body %q)", err, body)
	}
	return response.Detail
}

func TestNewKeepsHTTPConfig(t *testing.T) {
	cfg := testConfig()
	service := nethttp.New(cfg, &fakeUserStorage{})

	if got := service.Config(); got.AppName != cfg.HTTP.AppName || got.Port != cfg.HTTP.Port {
		t.Errorf("Config() = %+v, want %+v", got, cfg.HTTP)
	}
	if service.Config().AppName != "Web-App-Demo Backend" {
		t.Errorf("app name = %q, want %q", service.Config().AppName, "Web-App-Demo Backend")
	}
	if service.Config().AppVersion != "0.1.0" {
		t.Errorf("app version = %q, want %q", service.Config().AppVersion, "0.1.0")
	}
}

func TestHelloAnonymous(t *testing.T) {
	recorder := serve(t, testConfig(), &fakeUserStorage{}, nil, httptest.NewRequest(http.MethodGet, helloPath, nil))

	if recorder.Code != http.StatusOK {
		t.Fatalf("status = %d, want %d (body %q)", recorder.Code, http.StatusOK, recorder.Body.String())
	}

	response := decodeHello(t, recorder.Body.String())
	if response.Data.Message != anonymousHello {
		t.Errorf("message = %q, want %q", response.Data.Message, anonymousHello)
	}
	if !response.Success {
		t.Error("success = false, want true")
	}
	if response.Timestamp.IsZero() {
		t.Error("timestamp is zero, want it populated")
	}
	if !strings.Contains(recorder.Body.String(), `"message":null`) {
		t.Errorf("envelope message = %q, want it serialised as null", recorder.Body.String())
	}
}

func TestHelloAuthenticated(t *testing.T) {
	verify := claimsVerifier(map[string]any{
		"sub":   "1234567890",
		"email": "test@example.com",
		"name":  "Test User",
	})

	request := httptest.NewRequest(http.MethodGet, helloPath, nil)
	request.Header.Set(config.AuthorizationHeader, config.AuthorizationBearerPrefix+"valid-credential")
	request.Header.Set(config.AuthorizationProviderHeader, string(config.AuthProviderGoogle))

	recorder := serve(t, testConfig(), &fakeUserStorage{}, verify, request)
	if recorder.Code != http.StatusOK {
		t.Fatalf("status = %d, want %d (body %q)", recorder.Code, http.StatusOK, recorder.Body.String())
	}

	want := "Hello Test User from the Web-App-Demo backend!"
	if got := decodeHello(t, recorder.Body.String()).Data.Message; got != want {
		t.Errorf("message = %q, want %q", got, want)
	}
}

func TestHelloAuthenticatedFallsBackToEmailWhenNameClaimMissing(t *testing.T) {
	verify := claimsVerifier(map[string]any{
		"sub":   "1234567890",
		"email": "test@example.com",
	})

	request := httptest.NewRequest(http.MethodGet, helloPath, nil)
	request.Header.Set(config.AuthorizationHeader, config.AuthorizationBearerPrefix+"valid-credential")
	request.Header.Set(config.AuthorizationProviderHeader, string(config.AuthProviderGoogle))

	recorder := serve(t, testConfig(), &fakeUserStorage{}, verify, request)

	want := "Hello test@example.com from the Web-App-Demo backend!"
	if got := decodeHello(t, recorder.Body.String()).Data.Message; got != want {
		t.Errorf("message = %q, want %q", got, want)
	}
}

func TestFirstLoginCreatesUser(t *testing.T) {
	store := &fakeUserStorage{existing: nil}
	verify := claimsVerifier(map[string]any{
		"sub":   "1234567890",
		"email": "test@example.com",
		"name":  "Test User",
	})

	request := httptest.NewRequest(http.MethodGet, helloPath, nil)
	request.Header.Set(config.AuthorizationHeader, config.AuthorizationBearerPrefix+"valid-credential")
	request.Header.Set(config.AuthorizationProviderHeader, string(config.AuthProviderGoogle))

	if recorder := serve(t, testConfig(), store, verify, request); recorder.Code != http.StatusOK {
		t.Fatalf("status = %d, want %d", recorder.Code, http.StatusOK)
	}

	if len(store.getCalls) != 1 || store.getCalls[0] != "1234567890" {
		t.Errorf("get calls = %v, want one call for 1234567890", store.getCalls)
	}
	want := objects.User{ID: "1234567890", Email: "test@example.com", Name: "Test User"}
	if len(store.createCalls) != 1 || store.createCalls[0] != want {
		t.Errorf("create calls = %v, want one call with %+v", store.createCalls, want)
	}
	if len(store.updateCalls) != 0 {
		t.Errorf("update calls = %v, want none", store.updateCalls)
	}
}

func TestRepeatLoginUpdatesUser(t *testing.T) {
	store := &fakeUserStorage{
		existing: &objects.User{ID: "1234567890", Email: "test@example.com", Name: "Old Name"},
	}
	verify := claimsVerifier(map[string]any{
		"sub":   "1234567890",
		"email": "test@example.com",
		"name":  "New Name",
	})

	request := httptest.NewRequest(http.MethodGet, helloPath, nil)
	request.Header.Set(config.AuthorizationHeader, config.AuthorizationBearerPrefix+"valid-credential")
	request.Header.Set(config.AuthorizationProviderHeader, string(config.AuthProviderGoogle))

	recorder := serve(t, testConfig(), store, verify, request)

	want := objects.User{ID: "1234567890", Email: "test@example.com", Name: "New Name"}
	if len(store.updateCalls) != 1 || store.updateCalls[0] != want {
		t.Errorf("update calls = %v, want one call with %+v", store.updateCalls, want)
	}
	if len(store.createCalls) != 0 {
		t.Errorf("create calls = %v, want none", store.createCalls)
	}

	wantMessage := "Hello New Name from the Web-App-Demo backend!"
	if got := decodeHello(t, recorder.Body.String()).Data.Message; got != wantMessage {
		t.Errorf("message = %q, want %q", got, wantMessage)
	}
}

func TestAuthenticationFailures(t *testing.T) {
	tests := []struct {
		name           string
		authorization  string
		provider       string
		clientID       string
		verify         middleware.TokenVerifier
		wantStatus     int
		wantDetailPart string
	}{
		{
			name:           "malformed authorization header",
			authorization:  "fake-credential",
			provider:       string(config.AuthProviderGoogle),
			clientID:       testClientID,
			wantStatus:     http.StatusBadRequest,
			wantDetailPart: "must start with `Bearer `",
		},
		{
			name:           "missing provider header",
			authorization:  config.AuthorizationBearerPrefix + "valid-credential",
			clientID:       testClientID,
			wantStatus:     http.StatusBadRequest,
			wantDetailPart: "`Authorization-Provider` is missing.",
		},
		{
			name:           "unsupported provider",
			authorization:  config.AuthorizationBearerPrefix + "valid-credential",
			provider:       "facebook",
			clientID:       testClientID,
			wantStatus:     http.StatusBadRequest,
			wantDetailPart: "is not a valid value for `Authorization-Provider`",
		},
		{
			name:           "google client id not configured",
			authorization:  config.AuthorizationBearerPrefix + "valid-credential",
			provider:       string(config.AuthProviderGoogle),
			clientID:       "",
			wantStatus:     http.StatusInternalServerError,
			wantDetailPart: "Google authentication is not configured",
		},
		{
			name:           "invalid token",
			authorization:  config.AuthorizationBearerPrefix + "invalid-credential",
			provider:       string(config.AuthProviderGoogle),
			clientID:       testClientID,
			verify:         failingVerifier(),
			wantStatus:     http.StatusUnauthorized,
			wantDetailPart: "Could not authenticate with provider `google`",
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			cfg := testConfig()
			cfg.Auth.Google.ClientID = test.clientID

			request := httptest.NewRequest(http.MethodGet, helloPath, nil)
			request.Header.Set(config.AuthorizationHeader, test.authorization)
			if test.provider != "" {
				request.Header.Set(config.AuthorizationProviderHeader, test.provider)
			}

			recorder := serve(t, cfg, &fakeUserStorage{}, test.verify, request)
			if recorder.Code != test.wantStatus {
				t.Fatalf("status = %d, want %d (body %q)", recorder.Code, test.wantStatus, recorder.Body.String())
			}
			if detail := decodeDetail(t, recorder.Body.String()); !strings.Contains(detail, test.wantDetailPart) {
				t.Errorf("detail = %q, want it to contain %q", detail, test.wantDetailPart)
			}
		})
	}
}

func TestCORSAllowsConfiguredOrigin(t *testing.T) {
	request := httptest.NewRequest(http.MethodGet, helloPath, nil)
	request.Header.Set("Origin", testOrigin)

	recorder := serve(t, testConfig(), &fakeUserStorage{}, nil, request)

	if got := recorder.Header().Get("Access-Control-Allow-Origin"); got != testOrigin {
		t.Errorf("Access-Control-Allow-Origin = %q, want %q", got, testOrigin)
	}
	if recorder.Code != http.StatusOK {
		t.Errorf("status = %d, want %d", recorder.Code, http.StatusOK)
	}
}

func TestCORSRejectsUnknownOrigin(t *testing.T) {
	request := httptest.NewRequest(http.MethodGet, helloPath, nil)
	request.Header.Set("Origin", "https://evil.example")

	recorder := serve(t, testConfig(), &fakeUserStorage{}, nil, request)

	if got := recorder.Header().Get("Access-Control-Allow-Origin"); got != "" {
		t.Errorf("Access-Control-Allow-Origin = %q, want it absent", got)
	}
}

func TestCORSPreflightIsAnsweredBeforeAuthentication(t *testing.T) {
	request := httptest.NewRequest(http.MethodOptions, helloPath, nil)
	request.Header.Set("Origin", testOrigin)
	request.Header.Set("Access-Control-Request-Method", http.MethodGet)
	request.Header.Set("Access-Control-Request-Headers", "authorization,authorization-provider")

	recorder := serve(t, testConfig(), &fakeUserStorage{}, nil, request)

	if recorder.Code != http.StatusOK {
		t.Fatalf("status = %d, want %d", recorder.Code, http.StatusOK)
	}
	if got := recorder.Header().Get("Access-Control-Allow-Origin"); got != testOrigin {
		t.Errorf("Access-Control-Allow-Origin = %q, want %q", got, testOrigin)
	}
	if got := recorder.Header().Get("Access-Control-Allow-Methods"); got != "*" {
		t.Errorf("Access-Control-Allow-Methods = %q, want %q", got, "*")
	}
	if got := recorder.Header().Get("Access-Control-Allow-Headers"); got != "authorization,authorization-provider" {
		t.Errorf("Access-Control-Allow-Headers = %q, want the requested headers echoed", got)
	}
	if got := recorder.Header().Get("Access-Control-Max-Age"); got == "" {
		t.Error("Access-Control-Max-Age is absent, want it set")
	}
}

// A browser only surfaces the real status of a failed request when the error response
// itself carries CORS headers, so CORS must wrap authentication rather than the reverse.
func TestAuthenticationErrorsCarryCORSHeaders(t *testing.T) {
	request := httptest.NewRequest(http.MethodGet, helloPath, nil)
	request.Header.Set("Origin", testOrigin)
	request.Header.Set(config.AuthorizationHeader, "fake-credential")

	recorder := serve(t, testConfig(), &fakeUserStorage{}, nil, request)

	if recorder.Code != http.StatusBadRequest {
		t.Fatalf("status = %d, want %d", recorder.Code, http.StatusBadRequest)
	}
	if got := recorder.Header().Get("Access-Control-Allow-Origin"); got != testOrigin {
		t.Errorf("Access-Control-Allow-Origin = %q, want %q", got, testOrigin)
	}
}

func TestUnknownPathReturnsJSONNotFound(t *testing.T) {
	recorder := serve(t, testConfig(), &fakeUserStorage{}, nil,
		httptest.NewRequest(http.MethodGet, "/api/v1/nope", nil))

	if recorder.Code != http.StatusNotFound {
		t.Fatalf("status = %d, want %d", recorder.Code, http.StatusNotFound)
	}
	if got := decodeDetail(t, recorder.Body.String()); got != "Not Found" {
		t.Errorf("detail = %q, want %q", got, "Not Found")
	}
}
