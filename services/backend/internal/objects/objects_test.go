package objects_test

import (
	"encoding/json"
	"testing"

	"github.com/edgorman/web-app-demo/services/backend/internal/objects"
)

func TestMessageSerialisesToLowercaseKey(t *testing.T) {
	body, err := json.Marshal(objects.Message{Message: "Hello"})
	if err != nil {
		t.Fatalf("marshal message: %v", err)
	}
	if got, want := string(body), `{"message":"Hello"}`; got != want {
		t.Errorf("marshalled message = %s, want %s", got, want)
	}
}

func TestUserIsAuthenticated(t *testing.T) {
	user := &objects.User{ID: "123", Email: "test@example.com", Name: "Test User"}

	if !user.IsAuthenticated() {
		t.Error("IsAuthenticated() = false, want true")
	}
	if got := user.DisplayName(); got != "Test User" {
		t.Errorf("DisplayName() = %q, want %q", got, "Test User")
	}
}

// The Firestore documents already written by the previous implementation use lowercase
// keys, so both encodings must stay lowercase or the schema forks.
func TestUserFieldNamesAreLowercase(t *testing.T) {
	user := objects.User{ID: "123", Email: "test@example.com", Name: "Test User"}

	body, err := json.Marshal(user)
	if err != nil {
		t.Fatalf("marshal user: %v", err)
	}
	want := `{"id":"123","email":"test@example.com","name":"Test User"}`
	if got := string(body); got != want {
		t.Errorf("marshalled user = %s, want %s", got, want)
	}
}
