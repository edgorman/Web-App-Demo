package v1

import (
	"fmt"
	"net/http"

	"github.com/edgorman/web-app-demo/services/backend/internal/objects"
	"github.com/edgorman/web-app-demo/services/backend/internal/service/nethttp/middleware"
)

// HelloRoute is the pattern the hello handler is registered under, relative to the
// router's /api/v1 prefix.
const HelloRoute = "GET /hello"

// Hello greets the caller, by name when the request carried a verified identity.
func Hello(w http.ResponseWriter, r *http.Request) {
	message := "Hello from the Web-App-Demo backend!"
	if user, ok := middleware.UserFromContext(r.Context()); ok && user.IsAuthenticated() {
		message = fmt.Sprintf("Hello %s from the Web-App-Demo backend!", user.DisplayName())
	}

	WriteJSON(w, http.StatusOK, NewResponse(objects.Message{Message: message}))
}
