// Package config holds the service's configuration, one file per concern.
//
// Values come from the process environment, optionally seeded from a .env file, under
// the SERVICE__ prefix with __ separating nesting levels — for example
// SERVICE__HTTP__CORS__ALLOW_ORIGINS. Binding is explicit per field rather than
// reflective, so the mapping from environment variable to struct field is readable.
package config

// CORSConfig is the CORS configuration.
type CORSConfig struct {
	AllowOrigins     []string
	AllowCredentials bool
	AllowMethods     []string
	AllowHeaders     []string
}

// HTTPServiceConfig is the HTTP-server-specific configuration.
type HTTPServiceConfig struct {
	Host string
	Port int
	// Reload has no effect: the server has no hot-reload support. It is kept so the
	// configuration tree still mirrors the documented one, and the service logs a
	// warning when it is enabled.
	Reload     bool
	AppName    string
	AppVersion string
	CORS       CORSConfig
}

// ServiceConfig is the service configuration.
type ServiceConfig struct {
	HTTP    HTTPServiceConfig
	Auth    AuthConfig
	Storage StorageConfig
}

// DefaultServiceConfig returns the configuration with no environment applied.
func DefaultServiceConfig() ServiceConfig {
	return ServiceConfig{
		HTTP: HTTPServiceConfig{
			Host:       "0.0.0.0",
			Port:       8080,
			Reload:     false,
			AppName:    "Web-App-Demo Backend",
			AppVersion: "0.1.0",
			CORS: CORSConfig{
				AllowOrigins:     []string{},
				AllowCredentials: false,
				AllowMethods:     []string{"*"},
				AllowHeaders:     []string{"*"},
			},
		},
		Auth:    defaultAuthConfig(),
		Storage: defaultStorageConfig(),
	}
}

// NewServiceConfig builds the configuration from defaults overlaid with the
// environment, seeding the environment from EnvFile when that file exists.
func NewServiceConfig() (ServiceConfig, error) {
	if err := LoadEnvFile(EnvFile); err != nil {
		return ServiceConfig{}, err
	}
	return LoadServiceConfig(), nil
}

// LoadServiceConfig builds the configuration from defaults overlaid with the current
// process environment, without touching the .env file.
func LoadServiceConfig() ServiceConfig {
	c := DefaultServiceConfig()
	c.HTTP.load()
	c.Auth.load()
	c.Storage.load()
	return c
}

func (c *HTTPServiceConfig) load() {
	c.Host = envString("SERVICE__HTTP__HOST", c.Host)
	c.Port = envInt("SERVICE__HTTP__PORT", c.Port)
	c.Reload = envBool("SERVICE__HTTP__RELOAD", c.Reload)
	c.AppName = envString("SERVICE__HTTP__APP_NAME", c.AppName)
	c.AppVersion = envString("SERVICE__HTTP__APP_VERSION", c.AppVersion)
	c.CORS.AllowOrigins = envStringSlice("SERVICE__HTTP__CORS__ALLOW_ORIGINS", c.CORS.AllowOrigins)
	c.CORS.AllowCredentials = envBool("SERVICE__HTTP__CORS__ALLOW_CREDENTIALS", c.CORS.AllowCredentials)
	c.CORS.AllowMethods = envStringSlice("SERVICE__HTTP__CORS__ALLOW_METHODS", c.CORS.AllowMethods)
	c.CORS.AllowHeaders = envStringSlice("SERVICE__HTTP__CORS__ALLOW_HEADERS", c.CORS.AllowHeaders)
}
