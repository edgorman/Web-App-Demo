package v1_test

import (
	"encoding/json"
	"testing"
	"time"

	"github.com/edgorman/web-app-demo/services/backend/internal/objects"
	v1 "github.com/edgorman/web-app-demo/services/backend/internal/service/nethttp/resources/v1"
)

func TestNewResponseDefaults(t *testing.T) {
	before := time.Now().UTC()
	response := v1.NewResponse(objects.Message{Message: "Hello"})
	after := time.Now().UTC()

	if !response.Success {
		t.Error("Success = false, want true")
	}
	if response.Message != nil {
		t.Errorf("Message = %v, want nil", *response.Message)
	}
	if response.Timestamp.Before(before) || response.Timestamp.After(after) {
		t.Errorf("Timestamp = %v, want it between %v and %v", response.Timestamp, before, after)
	}
	if response.Data.Message != "Hello" {
		t.Errorf("Data.Message = %q, want %q", response.Data.Message, "Hello")
	}
}

func TestResponseEnvelopeShape(t *testing.T) {
	response := v1.Response[objects.Message]{
		Data:      objects.Message{Message: "Hello"},
		Timestamp: time.Date(2026, 8, 13, 12, 0, 0, 0, time.UTC),
		Success:   true,
	}

	body, err := json.Marshal(response)
	if err != nil {
		t.Fatalf("marshal response: %v", err)
	}

	want := `{"data":{"message":"Hello"},"timestamp":"2026-08-13T12:00:00Z","success":true,"message":null}`
	if got := string(body); got != want {
		t.Errorf("marshalled response = %s, want %s", got, want)
	}
}

func TestResponseCarriesFailureMessage(t *testing.T) {
	detail := "Error occurred"
	response := v1.Response[objects.Message]{
		Data:    objects.Message{Message: "Hello"},
		Success: false,
		Message: &detail,
	}

	body, err := json.Marshal(response)
	if err != nil {
		t.Fatalf("marshal response: %v", err)
	}

	var decoded v1.Response[objects.Message]
	if err := json.Unmarshal(body, &decoded); err != nil {
		t.Fatalf("unmarshal response: %v", err)
	}
	if decoded.Success {
		t.Error("Success = true, want false")
	}
	if decoded.Message == nil || *decoded.Message != detail {
		t.Errorf("Message = %v, want %q", decoded.Message, detail)
	}
}

func TestRequestWrapsData(t *testing.T) {
	var request v1.Request[objects.Message]
	if err := json.Unmarshal([]byte(`{"data":{"message":"Hello"}}`), &request); err != nil {
		t.Fatalf("unmarshal request: %v", err)
	}
	if request.Data.Message != "Hello" {
		t.Errorf("Data.Message = %q, want %q", request.Data.Message, "Hello")
	}
}
