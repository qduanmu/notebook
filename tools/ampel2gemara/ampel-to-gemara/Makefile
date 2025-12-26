# SPDX-FileCopyrightText: Copyright 2025 Carabiner Systems, Inc
# SPDX-License-Identifier: Apache-2.0

.PHONY: build test clean install

BINARY_NAME=ampel-to-gemara
INSTALL_PATH=$(GOPATH)/bin

build:
	go build -o $(BINARY_NAME) .

test:
	go test -v ./...

clean:
	rm -f $(BINARY_NAME)

install: build
	install -m 755 $(BINARY_NAME) $(INSTALL_PATH)/$(BINARY_NAME)

run-example: build
	./$(BINARY_NAME) -i ../test-data/example-result.json
