package objects

// User is an authenticated user profile, sourced from a verified auth provider token.
//
// The firestore tags are load-bearing: without them the Firestore client would write
// the Go field names (ID, Email, Name) and fork the document schema already in use.
type User struct {
	ID    string `json:"id" firestore:"id"`
	Email string `json:"email" firestore:"email"`
	Name  string `json:"name" firestore:"name"`
}

// IsAuthenticated reports whether the user came from a verified provider token.
func (u *User) IsAuthenticated() bool {
	return true
}

// DisplayName is the name to greet the user by.
func (u *User) DisplayName() string {
	return u.Name
}
