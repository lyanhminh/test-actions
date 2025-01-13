# Build the application from source
FROM golang:1.23 AS builder

WORKDIR /app

COPY *.go ./

RUN CGO_ENABLED=0 GOOS=linux go build -o /hello

# Run the tests in the container
FROM builder AS test
RUN go test -v ./...

# Deploy the application binary into a lean image
FROM gcr.io/distroless/base-debian11 AS release

WORKDIR /

COPY --from=builder /hello /hello


USER nonroot:nonroot

ENTRYPOINT ["/hello"]
