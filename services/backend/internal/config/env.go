package config

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"strconv"
	"strings"
)

// EnvFile is the file environment variables are read from when it exists.
const EnvFile = ".env"

// LoadEnvFile reads KEY=VALUE pairs from path into the process environment.
//
// Variables already present in the process environment are never overwritten, so
// real environment variables take precedence over the file. A missing file is not
// an error — it is the normal case in deployed environments, where Cloud Run
// supplies everything directly.
func LoadEnvFile(path string) error {
	file, err := os.Open(path)
	if err != nil {
		if os.IsNotExist(err) {
			return nil
		}
		return fmt.Errorf("open %s: %w", path, err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for lineNo := 1; scanner.Scan(); lineNo++ {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		line = strings.TrimPrefix(line, "export ")

		key, value, found := strings.Cut(line, "=")
		if !found {
			return fmt.Errorf("%s:%d: expected KEY=VALUE, got %q", path, lineNo, line)
		}

		key = strings.TrimSpace(key)
		if key == "" {
			return fmt.Errorf("%s:%d: empty key", path, lineNo)
		}
		if _, set := os.LookupEnv(key); set {
			continue
		}
		if err := os.Setenv(key, unquote(strings.TrimSpace(value))); err != nil {
			return fmt.Errorf("%s:%d: %w", path, lineNo, err)
		}
	}
	if err := scanner.Err(); err != nil {
		return fmt.Errorf("read %s: %w", path, err)
	}
	return nil
}

// unquote strips one layer of matching surrounding quotes.
func unquote(value string) string {
	if len(value) < 2 {
		return value
	}
	first, last := value[0], value[len(value)-1]
	if first == last && (first == '"' || first == '\'') {
		return value[1 : len(value)-1]
	}
	return value
}

// envString returns the value of key, or fallback when it is unset.
//
// An explicitly empty value is honoured rather than falling back, so a deployment can
// blank out a setting that has a non-empty default.
func envString(key, fallback string) string {
	if value, set := os.LookupEnv(key); set {
		return value
	}
	return fallback
}

// envInt returns the value of key parsed as an integer, or fallback when it is
// unset, empty, or unparseable.
func envInt(key string, fallback int) int {
	raw, set := os.LookupEnv(key)
	if !set || raw == "" {
		return fallback
	}
	value, err := strconv.Atoi(raw)
	if err != nil {
		return fallback
	}
	return value
}

// envBool returns the value of key parsed as a boolean, or fallback when it is
// unset, empty, or unparseable.
func envBool(key string, fallback bool) bool {
	raw, set := os.LookupEnv(key)
	if !set || raw == "" {
		return fallback
	}
	value, err := strconv.ParseBool(raw)
	if err != nil {
		return fallback
	}
	return value
}

// envStringSlice returns the value of key parsed as a JSON array of strings, or
// fallback when it is unset, empty, or unparseable.
//
// JSON is the wire format because that is what Terraform's jsonencode() produces for
// SERVICE__HTTP__CORS__ALLOW_ORIGINS (see infrastructure/env/gcp_cloud_run.tf).
func envStringSlice(key string, fallback []string) []string {
	raw, set := os.LookupEnv(key)
	if !set || raw == "" {
		return fallback
	}
	var value []string
	if err := json.Unmarshal([]byte(raw), &value); err != nil {
		return fallback
	}
	return value
}
