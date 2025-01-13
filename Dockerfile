FROM golang:1.23 AS builder

WORKDIR /app

COPY main.go go.mod hello_test.go  ./

RUN CGO_ENABLED=0 GOOS=linux go build -o /hello
RUN apt update && apt install vim -y
RUN apt install net-tools tree  -y

# Run the tests in the container
FROM builder AS test
RUN go test -v ./...

# Deploy the application binary into a lean image
FROM gcr.io/distroless/base-debian11 AS release

WORKDIR /

COPY --from=builder /hello /hello


USER nonroot:nonroot

ENTRYPOINT ["/hello"]
