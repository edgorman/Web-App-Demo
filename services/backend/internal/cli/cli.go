// Package cli is the command line entry point for the backend service.
package cli

import (
	"context"
	"flag"
	"fmt"
	"io"
	"os"

	"cloud.google.com/go/firestore"

	"github.com/edgorman/web-app-demo/services/backend/internal/config"
	"github.com/edgorman/web-app-demo/services/backend/internal/service"
	"github.com/edgorman/web-app-demo/services/backend/internal/service/nethttp"
	firestorestorage "github.com/edgorman/web-app-demo/services/backend/internal/storage/firestore"
)

// Execute runs the CLI with the given arguments (excluding the program name) and
// returns the process exit code.
func Execute(ctx context.Context, args []string, stderr io.Writer) int {
	if len(args) == 0 {
		usage(stderr)
		return 2
	}

	switch args[0] {
	case "run":
		if err := run(ctx, args[1:]); err != nil {
			fmt.Fprintf(stderr, "error: %v\n", err)
			return 1
		}
		return 0
	case "-h", "--help", "help":
		usage(stderr)
		return 0
	default:
		fmt.Fprintf(stderr, "error: unknown command %q\n\n", args[0])
		usage(stderr)
		return 2
	}
}

// usage prints the available commands.
func usage(w io.Writer) {
	fmt.Fprint(w, "Backend service CLI.\n\nUsage:\n  backend <command>\n\nCommands:\n  run\trun the backend service\n")
}

// run wires up storage and the API service, then serves until the process stops.
func run(ctx context.Context, args []string) error {
	flags := flag.NewFlagSet("run", flag.ContinueOnError)
	flags.Usage = func() { fmt.Fprint(flags.Output(), "Usage:\n  backend run\n") }
	if err := flags.Parse(args); err != nil {
		return err
	}

	cfg, err := config.NewServiceConfig()
	if err != nil {
		return err
	}

	firestoreClient, err := newFirestoreClient(ctx, cfg.Storage.Firestore)
	if err != nil {
		return err
	}
	defer firestoreClient.Close()

	userStorage := firestorestorage.NewUserStorage(firestoreClient)

	var api service.API = nethttp.New(cfg, userStorage)
	return api.Run()
}

// newFirestoreClient builds the Firestore client, letting the client resolve the project
// from Application Default Credentials and the database from its own default when either
// is left unset.
func newFirestoreClient(ctx context.Context, cfg config.FirestoreStorageConfig) (*firestore.Client, error) {
	projectID := cfg.ProjectID
	if projectID == "" {
		projectID = firestore.DetectProjectID
	}

	var client *firestore.Client
	var err error
	if cfg.Database == "" {
		client, err = firestore.NewClient(ctx, projectID)
	} else {
		client, err = firestore.NewClientWithDatabase(ctx, projectID, cfg.Database)
	}
	if err != nil {
		return nil, fmt.Errorf("create firestore client: %w", err)
	}
	return client, nil
}

// Main is the process entry point.
func Main() {
	os.Exit(Execute(context.Background(), os.Args[1:], os.Stderr))
}
