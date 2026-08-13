package config_test

import (
	"os"
	"path/filepath"
	"reflect"
	"testing"

	"github.com/edgorman/web-app-demo/services/backend/internal/config"
)

func TestDefaultServiceConfig(t *testing.T) {
	cfg := config.DefaultServiceConfig()

	if cfg.HTTP.Host != "0.0.0.0" {
		t.Errorf("HTTP.Host = %q, want %q", cfg.HTTP.Host, "0.0.0.0")
	}
	if cfg.HTTP.Port != 8080 {
		t.Errorf("HTTP.Port = %d, want %d", cfg.HTTP.Port, 8080)
	}
	if cfg.HTTP.Reload {
		t.Error("HTTP.Reload = true, want false")
	}
	if cfg.HTTP.AppName != "Web-App-Demo Backend" {
		t.Errorf("HTTP.AppName = %q, want %q", cfg.HTTP.AppName, "Web-App-Demo Backend")
	}
	if cfg.HTTP.AppVersion != "0.1.0" {
		t.Errorf("HTTP.AppVersion = %q, want %q", cfg.HTTP.AppVersion, "0.1.0")
	}
	if len(cfg.HTTP.CORS.AllowOrigins) != 0 {
		t.Errorf("CORS.AllowOrigins = %v, want empty", cfg.HTTP.CORS.AllowOrigins)
	}
	if cfg.HTTP.CORS.AllowCredentials {
		t.Error("CORS.AllowCredentials = true, want false")
	}
	if !reflect.DeepEqual(cfg.HTTP.CORS.AllowMethods, []string{"*"}) {
		t.Errorf("CORS.AllowMethods = %v, want [*]", cfg.HTTP.CORS.AllowMethods)
	}
	if !reflect.DeepEqual(cfg.HTTP.CORS.AllowHeaders, []string{"*"}) {
		t.Errorf("CORS.AllowHeaders = %v, want [*]", cfg.HTTP.CORS.AllowHeaders)
	}
	if cfg.Auth.Google.ClientID != "" {
		t.Errorf("Auth.Google.ClientID = %q, want empty", cfg.Auth.Google.ClientID)
	}
	if cfg.Storage.Firestore.ProjectID != "" || cfg.Storage.Firestore.Database != "" {
		t.Errorf("Storage.Firestore = %+v, want empty fields", cfg.Storage.Firestore)
	}
}

func TestLoadServiceConfigFromEnvironment(t *testing.T) {
	t.Setenv("SERVICE__HTTP__HOST", "127.0.0.1")
	t.Setenv("SERVICE__HTTP__PORT", "9000")
	t.Setenv("SERVICE__HTTP__RELOAD", "true")
	t.Setenv("SERVICE__HTTP__APP_NAME", "Renamed Backend")
	t.Setenv("SERVICE__HTTP__APP_VERSION", "9.9.9")
	t.Setenv("SERVICE__HTTP__CORS__ALLOW_ORIGINS", `["https://a.example","https://b.example"]`)
	t.Setenv("SERVICE__HTTP__CORS__ALLOW_CREDENTIALS", "true")
	t.Setenv("SERVICE__HTTP__CORS__ALLOW_METHODS", `["GET","POST"]`)
	t.Setenv("SERVICE__HTTP__CORS__ALLOW_HEADERS", `["Authorization"]`)
	t.Setenv("SERVICE__AUTH__GOOGLE__CLIENT_ID", "client-id.apps.googleusercontent.com")
	t.Setenv("SERVICE__STORAGE__FIRESTORE__PROJECT_ID", "web-app-demo-dev")
	t.Setenv("SERVICE__STORAGE__FIRESTORE__DATABASE", "web-app-demo-dev-database")

	cfg := config.LoadServiceConfig()

	if cfg.HTTP.Host != "127.0.0.1" || cfg.HTTP.Port != 9000 || !cfg.HTTP.Reload {
		t.Errorf("HTTP = %+v, want host 127.0.0.1, port 9000, reload true", cfg.HTTP)
	}
	if cfg.HTTP.AppName != "Renamed Backend" || cfg.HTTP.AppVersion != "9.9.9" {
		t.Errorf("app identity = %q %q, want %q %q",
			cfg.HTTP.AppName, cfg.HTTP.AppVersion, "Renamed Backend", "9.9.9")
	}
	wantOrigins := []string{"https://a.example", "https://b.example"}
	if !reflect.DeepEqual(cfg.HTTP.CORS.AllowOrigins, wantOrigins) {
		t.Errorf("CORS.AllowOrigins = %v, want %v", cfg.HTTP.CORS.AllowOrigins, wantOrigins)
	}
	if !cfg.HTTP.CORS.AllowCredentials {
		t.Error("CORS.AllowCredentials = false, want true")
	}
	if !reflect.DeepEqual(cfg.HTTP.CORS.AllowMethods, []string{"GET", "POST"}) {
		t.Errorf("CORS.AllowMethods = %v, want [GET POST]", cfg.HTTP.CORS.AllowMethods)
	}
	if !reflect.DeepEqual(cfg.HTTP.CORS.AllowHeaders, []string{"Authorization"}) {
		t.Errorf("CORS.AllowHeaders = %v, want [Authorization]", cfg.HTTP.CORS.AllowHeaders)
	}
	if cfg.Auth.Google.ClientID != "client-id.apps.googleusercontent.com" {
		t.Errorf("Auth.Google.ClientID = %q, want the configured id", cfg.Auth.Google.ClientID)
	}
	if cfg.Storage.Firestore.ProjectID != "web-app-demo-dev" {
		t.Errorf("Firestore.ProjectID = %q, want %q", cfg.Storage.Firestore.ProjectID, "web-app-demo-dev")
	}
	if cfg.Storage.Firestore.Database != "web-app-demo-dev-database" {
		t.Errorf("Firestore.Database = %q, want %q",
			cfg.Storage.Firestore.Database, "web-app-demo-dev-database")
	}
}

// Terraform sets the origins with jsonencode(), so a JSON array is the wire format.
func TestAllowOriginsAcceptsTerraformJSONEncoding(t *testing.T) {
	t.Setenv("SERVICE__HTTP__CORS__ALLOW_ORIGINS",
		`["https://frontend-abc.a.run.app","https://frontend.web-app-demo-dev.run.app"]`)

	got := config.LoadServiceConfig().HTTP.CORS.AllowOrigins
	want := []string{"https://frontend-abc.a.run.app", "https://frontend.web-app-demo-dev.run.app"}
	if !reflect.DeepEqual(got, want) {
		t.Errorf("CORS.AllowOrigins = %v, want %v", got, want)
	}
}

func TestUnparseableValuesFallBackToDefaults(t *testing.T) {
	t.Setenv("SERVICE__HTTP__PORT", "not-a-number")
	t.Setenv("SERVICE__HTTP__RELOAD", "not-a-bool")
	t.Setenv("SERVICE__HTTP__CORS__ALLOW_ORIGINS", "not-json")

	cfg := config.LoadServiceConfig()

	if cfg.HTTP.Port != 8080 {
		t.Errorf("HTTP.Port = %d, want the default 8080", cfg.HTTP.Port)
	}
	if cfg.HTTP.Reload {
		t.Error("HTTP.Reload = true, want the default false")
	}
	if len(cfg.HTTP.CORS.AllowOrigins) != 0 {
		t.Errorf("CORS.AllowOrigins = %v, want the empty default", cfg.HTTP.CORS.AllowOrigins)
	}
}

func TestLoadEnvFile(t *testing.T) {
	path := filepath.Join(t.TempDir(), ".env")
	contents := "# a comment\n" +
		"\n" +
		"SERVICE__HTTP__HOST=127.0.0.1\n" +
		"SERVICE__HTTP__APP_NAME=\"Quoted Name\"\n" +
		"export SERVICE__HTTP__PORT=9001\n" +
		"SERVICE__AUTH__GOOGLE__CLIENT_ID=\n"
	if err := os.WriteFile(path, []byte(contents), 0o600); err != nil {
		t.Fatalf("write env file: %v", err)
	}

	// Clear the keys the file sets so the fixture starts from a known state, and let
	// t.Setenv restore them afterwards.
	for _, key := range []string{
		"SERVICE__HTTP__HOST", "SERVICE__HTTP__APP_NAME",
		"SERVICE__HTTP__PORT", "SERVICE__AUTH__GOOGLE__CLIENT_ID",
	} {
		t.Setenv(key, "")
		if err := os.Unsetenv(key); err != nil {
			t.Fatalf("unset %s: %v", key, err)
		}
	}

	if err := config.LoadEnvFile(path); err != nil {
		t.Fatalf("LoadEnvFile: %v", err)
	}

	cfg := config.LoadServiceConfig()
	if cfg.HTTP.Host != "127.0.0.1" {
		t.Errorf("HTTP.Host = %q, want %q", cfg.HTTP.Host, "127.0.0.1")
	}
	if cfg.HTTP.AppName != "Quoted Name" {
		t.Errorf("HTTP.AppName = %q, want the surrounding quotes stripped", cfg.HTTP.AppName)
	}
	if cfg.HTTP.Port != 9001 {
		t.Errorf("HTTP.Port = %d, want %d", cfg.HTTP.Port, 9001)
	}
	if cfg.Auth.Google.ClientID != "" {
		t.Errorf("Auth.Google.ClientID = %q, want empty", cfg.Auth.Google.ClientID)
	}
}

// Real environment variables win over the .env file, matching the previous behaviour.
func TestLoadEnvFileDoesNotOverrideProcessEnvironment(t *testing.T) {
	path := filepath.Join(t.TempDir(), ".env")
	if err := os.WriteFile(path, []byte("SERVICE__HTTP__HOST=from-file\n"), 0o600); err != nil {
		t.Fatalf("write env file: %v", err)
	}
	t.Setenv("SERVICE__HTTP__HOST", "from-environment")

	if err := config.LoadEnvFile(path); err != nil {
		t.Fatalf("LoadEnvFile: %v", err)
	}

	if got := os.Getenv("SERVICE__HTTP__HOST"); got != "from-environment" {
		t.Errorf("SERVICE__HTTP__HOST = %q, want %q", got, "from-environment")
	}
}

func TestLoadEnvFileIgnoresMissingFile(t *testing.T) {
	if err := config.LoadEnvFile(filepath.Join(t.TempDir(), "absent")); err != nil {
		t.Errorf("LoadEnvFile on a missing file = %v, want nil", err)
	}
}

func TestLoadEnvFileRejectsMalformedLine(t *testing.T) {
	path := filepath.Join(t.TempDir(), ".env")
	if err := os.WriteFile(path, []byte("not a pair\n"), 0o600); err != nil {
		t.Fatalf("write env file: %v", err)
	}

	if err := config.LoadEnvFile(path); err == nil {
		t.Error("LoadEnvFile on a malformed line = nil, want an error")
	}
}

func TestParseAuthProvider(t *testing.T) {
	provider, ok := config.ParseAuthProvider("google")
	if !ok || provider != config.AuthProviderGoogle {
		t.Errorf("ParseAuthProvider(google) = %q, %t; want google, true", provider, ok)
	}

	if _, ok := config.ParseAuthProvider("facebook"); ok {
		t.Error("ParseAuthProvider(facebook) reported the provider as supported")
	}
}
