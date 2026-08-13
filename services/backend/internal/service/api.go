// Package service defines the API interface; concrete implementations live in
// subpackages (e.g. service/nethttp). Call sites depend on this interface, not on a
// particular HTTP implementation.
package service

// API is implemented by every API server implementation. Host, port and the rest of the
// server's settings come from the configuration injected at construction.
type API interface {
	// Run starts the API server and blocks until it stops.
	Run() error
}
