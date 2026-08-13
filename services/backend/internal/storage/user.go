// Package storage defines the persistence interfaces; concrete backends live in
// subpackages (e.g. storage/firestore), mirroring the service/nethttp split.
package storage

import (
	"context"

	"github.com/edgorman/web-app-demo/services/backend/internal/objects"
)

// UserStorage persists user profiles.
type UserStorage interface {
	// Get fetches a user by id, returning a nil user when none is stored.
	Get(ctx context.Context, userID string) (*objects.User, error)
	// Create persists a new user and returns it.
	Create(ctx context.Context, user *objects.User) (*objects.User, error)
	// Update persists changes to an existing user and returns it.
	Update(ctx context.Context, user *objects.User) (*objects.User, error)
	// Delete removes a user by id.
	Delete(ctx context.Context, userID string) error
}
