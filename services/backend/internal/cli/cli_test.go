package cli_test

import (
	"context"
	"io"
	"strings"
	"testing"

	"github.com/edgorman/web-app-demo/services/backend/internal/cli"
)

func TestExecuteWithoutCommandPrintsUsage(t *testing.T) {
	var stderr strings.Builder

	if code := cli.Execute(context.Background(), nil, &stderr); code != 2 {
		t.Errorf("exit code = %d, want 2", code)
	}
	if !strings.Contains(stderr.String(), "run") {
		t.Errorf("usage = %q, want it to mention the run command", stderr.String())
	}
}

func TestExecuteWithUnknownCommand(t *testing.T) {
	var stderr strings.Builder

	if code := cli.Execute(context.Background(), []string{"serve"}, &stderr); code != 2 {
		t.Errorf("exit code = %d, want 2", code)
	}
	if !strings.Contains(stderr.String(), `unknown command "serve"`) {
		t.Errorf("stderr = %q, want it to name the unknown command", stderr.String())
	}
}

func TestExecuteHelp(t *testing.T) {
	if code := cli.Execute(context.Background(), []string{"--help"}, io.Discard); code != 0 {
		t.Errorf("exit code = %d, want 0", code)
	}
}
