# Build stage - compile a static binary
ARG GO_VERSION=1.25
FROM golang:${GO_VERSION} AS builder

WORKDIR /app

# Download dependencies first so they stay cached while only sources change.
COPY go.mod go.sum ./
RUN go mod download

COPY main.go ./
COPY internal ./internal

# CGO is disabled so the binary runs on a distroless static base with no libc.
RUN CGO_ENABLED=0 GOOS=linux go build -trimpath -ldflags="-s -w" -o /backend .

# Runtime stage - distroless static, which ships CA certificates and runs as non-root
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=builder /backend /backend
ARG PORT=8080
EXPOSE ${PORT}
ENTRYPOINT ["/backend"]
CMD ["run"]
