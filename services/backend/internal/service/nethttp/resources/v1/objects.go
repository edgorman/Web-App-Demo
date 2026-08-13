// Package v1 holds the versioned API resources, mounted under /api/v1.
package v1

import (
	"encoding/json"
	"net/http"
	"time"
)

// Request is the generic API request wrapper.
type Request[T any] struct {
	// Data is the request data.
	Data T `json:"data"`
}

// Response is the generic API response wrapper. Every resource wraps its payload in
// this envelope, which adds a timestamp, a success flag and an optional message.
type Response[T any] struct {
	// Data is the response data.
	Data T `json:"data"`
	// Timestamp is when the response was produced.
	Timestamp time.Time `json:"timestamp"`
	// Success reports whether the request was successful.
	Success bool `json:"success"`
	// Message is an optional message about the response. It is serialised as null when
	// unset, matching the frontend's `message?: string | null`.
	Message *string `json:"message"`
}

// NewResponse wraps data in a successful response stamped with the current UTC time.
func NewResponse[T any](data T) Response[T] {
	return Response[T]{
		Data:      data,
		Timestamp: time.Now().UTC(),
		Success:   true,
		Message:   nil,
	}
}

// WriteJSON writes value as a JSON body with the given status code.
func WriteJSON(w http.ResponseWriter, status int, value any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	// The header and status are already committed, so a marshalling failure here can
	// only be reported by truncating the body; there is nothing else to fall back to.
	_ = json.NewEncoder(w).Encode(value)
}
