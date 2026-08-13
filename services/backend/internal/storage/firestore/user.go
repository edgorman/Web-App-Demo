// Package firestore is the Firestore-backed implementation of the storage interfaces.
package firestore

import (
	"context"
	"fmt"

	"cloud.google.com/go/firestore"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	"github.com/edgorman/web-app-demo/services/backend/internal/objects"
	"github.com/edgorman/web-app-demo/services/backend/internal/storage"
)

// UsersCollection is the Firestore collection users are stored in.
const UsersCollection = "users"

// UserStorage stores users as documents in a Firestore `users` collection, keyed by user id.
type UserStorage struct {
	client *firestore.Client
}

// compile-time check that the Firestore backend satisfies the storage interface.
var _ storage.UserStorage = (*UserStorage)(nil)

// NewUserStorage returns a Firestore-backed user store.
func NewUserStorage(client *firestore.Client) *UserStorage {
	return &UserStorage{client: client}
}

// Get fetches a user by id, returning a nil user when no document exists.
func (s *UserStorage) Get(ctx context.Context, userID string) (*objects.User, error) {
	snapshot, err := s.client.Collection(UsersCollection).Doc(userID).Get(ctx)
	if err != nil {
		if status.Code(err) == codes.NotFound {
			return nil, nil
		}
		return nil, fmt.Errorf("get user %q: %w", userID, err)
	}

	var user objects.User
	if err := snapshot.DataTo(&user); err != nil {
		return nil, fmt.Errorf("decode user %q: %w", userID, err)
	}
	return &user, nil
}

// Create persists a new user, overwriting any existing document.
func (s *UserStorage) Create(ctx context.Context, user *objects.User) (*objects.User, error) {
	if _, err := s.client.Collection(UsersCollection).Doc(user.ID).Set(ctx, user); err != nil {
		return nil, fmt.Errorf("create user %q: %w", user.ID, err)
	}
	return user, nil
}

// Update merges changes into an existing user's document.
func (s *UserStorage) Update(ctx context.Context, user *objects.User) (*objects.User, error) {
	if _, err := s.client.Collection(UsersCollection).Doc(user.ID).Set(ctx, user, firestore.MergeAll); err != nil {
		return nil, fmt.Errorf("update user %q: %w", user.ID, err)
	}
	return user, nil
}

// Delete removes a user's document.
func (s *UserStorage) Delete(ctx context.Context, userID string) error {
	if _, err := s.client.Collection(UsersCollection).Doc(userID).Delete(ctx); err != nil {
		return fmt.Errorf("delete user %q: %w", userID, err)
	}
	return nil
}
