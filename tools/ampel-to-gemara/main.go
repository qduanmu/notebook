// SPDX-FileCopyrightText: Copyright 2025 Carabiner Systems, Inc
// SPDX-License-Identifier: Apache-2.0

package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"time"

	papi "github.com/carabiner-dev/policy/api/v1"
	intoto "github.com/in-toto/attestation/go/v1"
	"google.golang.org/protobuf/encoding/protojson"
	"google.golang.org/protobuf/types/known/structpb"
	"google.golang.org/protobuf/types/known/timestamppb"
	"gopkg.in/yaml.v3"
)

// Gemara Layer 4 structures
type GemaraEvaluation struct {
	GemaraVersion string               `yaml:"gemara_version"`
	Layer         int                  `yaml:"layer"`
	Type          string               `yaml:"type"`
	Evaluations   []EvaluationResult   `yaml:"evaluations"`
}

type EvaluationResult struct {
	Evaluation EvaluationMetadata `yaml:"evaluation"`
	Subject    Subject            `yaml:"subject"`
	Assessment Assessment         `yaml:"assessment"`
	Policy     PolicyRef          `yaml:"policy"`
	Controls   []Control          `yaml:"controls,omitempty"`
	Findings   []Finding          `yaml:"findings,omitempty"`
	Context    *Context           `yaml:"context,omitempty"`
}

type EvaluationMetadata struct {
	ID               string `yaml:"id"`
	Timestamp        string `yaml:"timestamp"`
	DurationMs       int64  `yaml:"duration_ms"`
	Evaluator        string `yaml:"evaluator"`
	EvaluatorVersion string `yaml:"evaluator_version"`
}

type Subject struct {
	Name        string       `yaml:"name"`
	Type        string       `yaml:"type"`
	Identifiers []Identifier `yaml:"identifiers"`
}

type Identifier struct {
	Type  string `yaml:"type"`
	Value string `yaml:"value"`
}

type Assessment struct {
	Status  string `yaml:"status"`
	Summary string `yaml:"summary"`
}

type PolicyRef struct {
	ID          string `yaml:"id"`
	Version     string `yaml:"version"`
	Description string `yaml:"description,omitempty"`
}

type Control struct {
	ID        string `yaml:"id"`
	Framework string `yaml:"framework"`
	Status    string `yaml:"status"`
}

type Finding struct {
	ID          string                 `yaml:"id"`
	Description string                 `yaml:"description,omitempty"`
	Status      string                 `yaml:"status"`
	Timestamp   string                 `yaml:"timestamp,omitempty"`
	Error       *FindingError          `yaml:"error,omitempty"`
	Outputs     map[string]interface{} `yaml:"outputs,omitempty"`
	Evidence    []Evidence             `yaml:"evidence,omitempty"`
}

type FindingError struct {
	Message     string `yaml:"message"`
	Remediation string `yaml:"remediation,omitempty"`
}

type Evidence struct {
	Type   string `yaml:"type"`
	Digest string `yaml:"digest,omitempty"`
}

type Context struct {
	Runtime    string                 `yaml:"runtime,omitempty"`
	AssertMode string                 `yaml:"assert_mode,omitempty"`
	Values     map[string]interface{} `yaml:"values,omitempty"`
}

func mapSubject(subject *intoto.ResourceDescriptor) Subject {
	identifiers := []Identifier{}
	for algo, value := range subject.GetDigest() {
		identifiers = append(identifiers, Identifier{
			Type:  algo,
			Value: value,
		})
	}

	return Subject{
		Name:        subject.GetName(),
		Type:        "artifact",
		Identifiers: identifiers,
	}
}

func calculateDurationMs(start, end *timestamppb.Timestamp) int64 {
	if start == nil || end == nil {
		return 0
	}
	return end.AsTime().Sub(start.AsTime()).Milliseconds()
}

func structToMap(s *structpb.Struct) map[string]interface{} {
	if s == nil {
		return nil
	}
	return s.AsMap()
}

func mapFinding(evalResult *papi.EvalResult, index int) Finding {
	finding := Finding{
		ID:        evalResult.GetId(),
		Status:    evalResult.GetStatus(),
		Timestamp: evalResult.GetDate().AsTime().Format(time.RFC3339),
	}

	if finding.ID == "" {
		finding.ID = fmt.Sprintf("check-%d", index)
	}

	// Add description and error based on status
	if evalResult.GetStatus() == papi.StatusPASS {
		if evalResult.GetAssessment() != nil {
			finding.Description = evalResult.GetAssessment().GetMessage()
		}
	} else {
		if evalResult.GetError() != nil {
			finding.Description = evalResult.GetError().GetMessage()
			finding.Error = &FindingError{
				Message:     evalResult.GetError().GetMessage(),
				Remediation: evalResult.GetError().GetGuidance(),
			}
		}
	}

	// Add outputs
	if evalResult.GetOutput() != nil {
		finding.Outputs = structToMap(evalResult.GetOutput())
	}

	// Add evidence
	for _, stmt := range evalResult.GetStatements() {
		finding.Evidence = append(finding.Evidence, Evidence{
			Type:   stmt.GetType(),
			Digest: stmt.GetDigest(),
		})
	}

	return finding
}

func mapControls(meta *papi.Meta, status string) []Control {
	controls := []Control{}
	for _, ctrl := range meta.GetControls() {
		framework := ctrl.GetClass()
		if framework == "" {
			framework = "custom"
		}
		controls = append(controls, Control{
			ID:        ctrl.GetId(),
			Framework: framework,
			Status:    status,
		})
	}
	return controls
}

func mapResult(result *papi.Result) EvaluationResult {
	policy := result.GetPolicy()
	meta := result.GetMeta()

	// Calculate duration
	durationMs := calculateDurationMs(result.GetDateStart(), result.GetDateEnd())

	// Determine summary
	status := result.GetStatus()
	summary := meta.GetDescription()
	if status == papi.StatusPASS && summary == "" {
		summary = "All policy tenets validated successfully"
	} else if status != papi.StatusPASS {
		// Try to get failure summary from first failed check
		for _, evalResult := range result.GetEvalResults() {
			if evalResult.GetStatus() != papi.StatusPASS {
				if evalResult.GetError() != nil {
					summary = evalResult.GetError().GetMessage()
					break
				}
			}
		}
	}

	// Build evaluation ID
	evalID := fmt.Sprintf("ampel-eval-%s", result.GetDateEnd().AsTime().Format("20060102-150405"))

	evaluation := EvaluationResult{
		Evaluation: EvaluationMetadata{
			ID:               evalID,
			Timestamp:        result.GetDateEnd().AsTime().Format(time.RFC3339),
			DurationMs:       durationMs,
			Evaluator:        "ampel",
			EvaluatorVersion: "1.0",
		},
		Subject: mapSubject(result.GetSubject()),
		Assessment: Assessment{
			Status:  status,
			Summary: summary,
		},
		Policy: PolicyRef{
			ID:          policy.GetId(),
			Version:     policy.GetVersion(),
			Description: meta.GetDescription(),
		},
	}

	// Add controls
	controls := mapControls(meta, status)
	if len(controls) > 0 {
		evaluation.Controls = controls
	}

	// Map findings
	findings := []Finding{}
	for idx, evalResult := range result.GetEvalResults() {
		findings = append(findings, mapFinding(evalResult, idx))
	}
	if len(findings) > 0 {
		evaluation.Findings = findings
	}

	// Add context
	if result.GetContext() != nil {
		evaluation.Context = &Context{
			Runtime:    meta.GetRuntime(),
			AssertMode: meta.GetAssertMode(),
			Values:     structToMap(result.GetContext()),
		}
	}

	return evaluation
}

func convertAmpelToGemara(data []byte) (*GemaraEvaluation, error) {
	evaluations := []EvaluationResult{}

	// Try to parse as in-toto statement first
	var statement map[string]interface{}
	if err := json.Unmarshal(data, &statement); err != nil {
		return nil, fmt.Errorf("parsing JSON: %w", err)
	}

	// Check if it's an in-toto statement
	if statement["_type"] == "https://in-toto.io/Statement/v1" {
		// Extract predicate
		predicateData, err := json.Marshal(statement["predicate"])
		if err != nil {
			return nil, fmt.Errorf("extracting predicate: %w", err)
		}

		// Try to parse as ResultSet
		var resultSet papi.ResultSet
		if err := protojson.Unmarshal(predicateData, &resultSet); err == nil {
			for _, result := range resultSet.GetResults() {
				evaluations = append(evaluations, mapResult(result))
			}
		} else {
			// Try as single Result
			var result papi.Result
			if err := protojson.Unmarshal(predicateData, &result); err == nil {
				evaluations = append(evaluations, mapResult(&result))
			} else {
				return nil, fmt.Errorf("parsing predicate as Result or ResultSet: %w", err)
			}
		}
	} else {
		// Try direct Result or ResultSet
		var resultSet papi.ResultSet
		if err := protojson.Unmarshal(data, &resultSet); err == nil && len(resultSet.GetResults()) > 0 {
			for _, result := range resultSet.GetResults() {
				evaluations = append(evaluations, mapResult(result))
			}
		} else {
			var result papi.Result
			if err := protojson.Unmarshal(data, &result); err == nil {
				evaluations = append(evaluations, mapResult(&result))
			} else {
				return nil, fmt.Errorf("parsing as Result or ResultSet: %w", err)
			}
		}
	}

	return &GemaraEvaluation{
		GemaraVersion: "1.0",
		Layer:         4,
		Type:          "evaluation",
		Evaluations:   evaluations,
	}, nil
}

func main() {
	var inputFile, outputFile string

	flag.StringVar(&inputFile, "input", "", "Input ampel result JSON file")
	flag.StringVar(&inputFile, "i", "", "Input ampel result JSON file (shorthand)")
	flag.StringVar(&outputFile, "output", "", "Output Gemara YAML file (optional, defaults to stdout)")
	flag.StringVar(&outputFile, "o", "", "Output Gemara YAML file (shorthand)")
	flag.Parse()

	if inputFile == "" {
		fmt.Fprintln(os.Stderr, "Usage: ampel-to-gemara -i <input.json> [-o <output.yaml>]")
		flag.PrintDefaults()
		os.Exit(1)
	}

	// Read input file
	data, err := os.ReadFile(inputFile)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error reading input file: %v\n", err)
		os.Exit(1)
	}

	// Convert to Gemara format
	gemara, err := convertAmpelToGemara(data)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error converting to Gemara format: %v\n", err)
		os.Exit(1)
	}

	// Output YAML
	yamlData, err := yaml.Marshal(gemara)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error generating YAML: %v\n", err)
		os.Exit(1)
	}

	if outputFile != "" {
		if err := os.WriteFile(outputFile, yamlData, 0644); err != nil {
			fmt.Fprintf(os.Stderr, "Error writing output file: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("Gemara Layer 4 evaluation written to: %s\n", outputFile)
	} else {
		fmt.Print(string(yamlData))
	}
}
