// Package middleware holds the HTTP middleware wrapping the API handlers.
package middleware

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"strings"

	"google.golang.org/api/idtoken"

	"github.com/edgorman/web-app-demo/services/backend/internal/config"
	"github.com/edgorman/web-app-demo/services/backend/internal/objects"
	"github.com/edgorman/web-app-demo/services/backend/internal/storage"
)

// contextKey is the unexported key type for values this package stores on a context.
type contextKey struct{ name string }

var userContextKey = &contextKey{name: "user"}

// UserFromContext returns the authenticated user attached to ctx. The second result is
// false for anonymous requests, which are allowed rather than rejected.
func UserFromContext(ctx context.Context) (*objects.User, bool) {
	user, ok := ctx.Value(userContextKey).(*objects.User)
	return user, ok
}

// TokenVerifier verifies a provider token against an audience and returns its claims.
// It is a seam so tests can authenticate without reaching the provider.
type TokenVerifier func(ctx context.Context, token, audience string) (map[string]any, error)

// VerifyGoogleIDToken verifies a Google Sign-In ID token's signature, issuer and audience.
func VerifyGoogleIDToken(ctx context.Context, token, audience string) (map[string]any, error) {
	payload, err := idtoken.Validate(ctx, token, audience)
	if err != nil {
		return nil, err
	}
	return payload.Claims, nil
}

// authError is an authentication failure carrying the HTTP status code it should produce.
type authError struct {
	statusCode int
	detail     string
}

func (e *authError) Error() string { return e.detail }

// Authenticate verifies a bearer token from a supported provider, resolves it to a user
// and attaches that user to the request context.
//
// Requests without an Authorization header pass through as anonymous — the handler
// simply finds no user on the context. Malformed or unverifiable credentials are
// rejected with a JSON {"detail": "..."} body.
func Authenticate(googleClientID string, userStorage storage.UserStorage, verify TokenVerifier) func(http.Handler) http.Handler {
	if verify == nil {
		verify = VerifyGoogleIDToken
	}

	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			user, err := authenticate(r, googleClientID, userStorage, verify)
			if err != nil {
				var authErr *authError
				if !errors.As(err, &authErr) {
					authErr = &authError{statusCode: http.StatusInternalServerError, detail: err.Error()}
				}
				writeDetail(w, authErr.statusCode, authErr.detail)
				return
			}
			if user != nil {
				r = r.WithContext(context.WithValue(r.Context(), userContextKey, user))
			}
			next.ServeHTTP(w, r)
		})
	}
}

// authenticate resolves the request's credentials to a user, or to a nil user when the
// request is anonymous.
func authenticate(
	r *http.Request,
	googleClientID string,
	userStorage storage.UserStorage,
	verify TokenVerifier,
) (*objects.User, error) {
	authValues := r.Header.Values(config.AuthorizationHeader)
	if len(authValues) == 0 {
		return nil, nil
	}
	auth := authValues[0]

	if !strings.HasPrefix(auth, config.AuthorizationBearerPrefix) {
		return nil, &authError{
			statusCode: http.StatusBadRequest,
			detail: fmt.Sprintf("`%s` header malformed, must start with `%s`.",
				config.AuthorizationHeader, config.AuthorizationBearerPrefix),
		}
	}
	token := auth[len(config.AuthorizationBearerPrefix):]

	providerValues := r.Header.Values(config.AuthorizationProviderHeader)
	if len(providerValues) == 0 {
		return nil, &authError{
			statusCode: http.StatusBadRequest,
			detail:     fmt.Sprintf("`%s` is missing.", config.AuthorizationProviderHeader),
		}
	}
	rawProvider := providerValues[0]

	provider, ok := config.ParseAuthProvider(rawProvider)
	if !ok {
		return nil, &authError{
			statusCode: http.StatusBadRequest,
			detail: fmt.Sprintf("`%s` is not a valid value for `%s`.",
				rawProvider, config.AuthorizationProviderHeader),
		}
	}

	var claims map[string]any
	var err error
	switch provider {
	case config.AuthProviderGoogle:
		claims, err = authGoogle(r.Context(), token, googleClientID, verify)
	default:
		err = &authError{
			statusCode: http.StatusNotImplemented,
			detail:     fmt.Sprintf("Provider `%s` has not been implemented.", provider),
		}
	}
	if err != nil {
		return nil, err
	}

	user, err := userFromClaims(claims)
	if err != nil {
		return nil, err
	}
	return storeUser(r.Context(), userStorage, user)
}

// authGoogle verifies a Google Sign-In ID token and returns its claims.
func authGoogle(ctx context.Context, token, clientID string, verify TokenVerifier) (map[string]any, error) {
	if clientID == "" {
		return nil, &authError{
			statusCode: http.StatusInternalServerError,
			detail:     "Google authentication is not configured",
		}
	}

	claims, err := verify(ctx, token, clientID)
	if err != nil {
		return nil, &authError{
			statusCode: http.StatusUnauthorized,
			detail: fmt.Sprintf("Could not authenticate with provider `%s`: `%s`.",
				config.AuthProviderGoogle, err),
		}
	}
	return claims, nil
}

// userFromClaims maps verified provider claims onto a user, falling back to the email
// address when the provider supplied no name.
func userFromClaims(claims map[string]any) (*objects.User, error) {
	id, err := claimString(claims, "sub")
	if err != nil {
		return nil, err
	}
	email, err := claimString(claims, "email")
	if err != nil {
		return nil, err
	}

	name, ok := claims["name"].(string)
	if !ok {
		name = email
	}
	return &objects.User{ID: id, Email: email, Name: name}, nil
}

// claimString reads a required string claim.
func claimString(claims map[string]any, key string) (string, error) {
	value, ok := claims[key].(string)
	if !ok {
		return "", &authError{
			statusCode: http.StatusUnauthorized,
			detail:     fmt.Sprintf("Token is missing the `%s` claim.", key),
		}
	}
	return value, nil
}

// storeUser creates or refreshes the user's persisted profile on each successful login.
func storeUser(ctx context.Context, userStorage storage.UserStorage, user *objects.User) (*objects.User, error) {
	existing, err := userStorage.Get(ctx, user.ID)
	if err != nil {
		return nil, &authError{
			statusCode: http.StatusInternalServerError,
			detail:     fmt.Sprintf("Could not read the stored user: `%s`.", err),
		}
	}

	var stored *objects.User
	if existing == nil {
		stored, err = userStorage.Create(ctx, user)
	} else {
		stored, err = userStorage.Update(ctx, user)
	}
	if err != nil {
		return nil, &authError{
			statusCode: http.StatusInternalServerError,
			detail:     fmt.Sprintf("Could not persist the user: `%s`.", err),
		}
	}
	return stored, nil
}

// writeDetail writes the {"detail": "..."} error body used for authentication failures.
func writeDetail(w http.ResponseWriter, status int, detail string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(map[string]string{"detail": detail})
}
