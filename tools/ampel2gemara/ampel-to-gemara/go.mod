module github.com/carabiner-dev/ampel/tools/ampel-to-gemara

go 1.23

require (
	github.com/carabiner-dev/policy v0.0.0
	github.com/in-toto/attestation/go v1.1.0
	google.golang.org/protobuf v1.36.2
	gopkg.in/yaml.v3 v3.0.1
)

replace github.com/carabiner-dev/policy => ../../vendor/github.com/carabiner-dev/policy
