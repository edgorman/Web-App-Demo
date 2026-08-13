package config

const (
	// AuthorizationHeader carries the provider's bearer token.
	AuthorizationHeader = "Authorization"
	// AuthorizationBearerPrefix is the required prefix of the Authorization header value.
	AuthorizationBearerPrefix = "Bearer "
	// AuthorizationProviderHeader names the provider that issued the token.
	AuthorizationProviderHeader = "Authorization-Provider"
)

// AuthProvider is a supported authentication provider.
type AuthProvider string

// Supported authentication providers.
const (
	AuthProviderGoogle AuthProvider = "google"
)

// ParseAuthProvider resolves a header value to a supported provider.
func ParseAuthProvider(value string) (AuthProvider, bool) {
	switch AuthProvider(value) {
	case AuthProviderGoogle:
		return AuthProviderGoogle, true
	default:
		return "", false
	}
}

// GoogleAuthConfig is the Google Sign-In configuration.
type GoogleAuthConfig struct {
	ClientID string
}

// AuthConfig is the authentication configuration.
type AuthConfig struct {
	Google GoogleAuthConfig
}

func defaultAuthConfig() AuthConfig {
	return AuthConfig{
		Google: GoogleAuthConfig{
			ClientID: "",
		},
	}
}

func (c *AuthConfig) load() {
	c.Google.ClientID = envString("SERVICE__AUTH__GOOGLE__CLIENT_ID", c.Google.ClientID)
}
