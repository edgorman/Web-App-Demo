package firestore_test

import (
	"reflect"
	"testing"

	"github.com/edgorman/web-app-demo/services/backend/internal/objects"
	firestorestorage "github.com/edgorman/web-app-demo/services/backend/internal/storage/firestore"
)

func TestUsersCollection(t *testing.T) {
	if firestorestorage.UsersCollection != "users" {
		t.Errorf("UsersCollection = %q, want %q", firestorestorage.UsersCollection, "users")
	}
}

// Firestore defaults a document's field names to the Go field names unless they are
// tagged. The documents already stored by the previous implementation use lowercase
// keys, so losing these tags would silently fork the schema.
func TestUserFirestoreTagsMatchStoredSchema(t *testing.T) {
	want := map[string]string{"ID": "id", "Email": "email", "Name": "name"}

	userType := reflect.TypeOf(objects.User{})
	if userType.NumField() != len(want) {
		t.Fatalf("User has %d fields, want %d — update the stored schema expectations",
			userType.NumField(), len(want))
	}

	for i := range userType.NumField() {
		field := userType.Field(i)
		if got := field.Tag.Get("firestore"); got != want[field.Name] {
			t.Errorf("User.%s firestore tag = %q, want %q", field.Name, got, want[field.Name])
		}
	}
}
