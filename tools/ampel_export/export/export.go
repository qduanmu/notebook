package export

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/ossf/gemara"
)

// AmpelPolicy represents an Ampel policy structure
type AmpelPolicy struct {
	ID          string          `json:"id"`
	Name        string          `json:"name"`
	Description string          `json:"description"`
	Logic       string          `json:"logic"` // "AND" or "OR"
	Tenets      []AmpelTenet    `json:"tenets"`
	Framework   *AmpelFramework `json:"framework,omitempty"`
}

// AmpelTenet represents a single evaluation check in an Ampel policy
type AmpelTenet struct {
	Name          string   `json:"name"`
	Description   string   `json:"description,omitempty"`
	Evaluation    string   `json:"evaluation"`
	Applicability []string `json:"applicability,omitempty"`
}

// AmpelFramework links the policy to a compliance framework
type AmpelFramework struct {
	Catalog     string            `json:"catalog"`
	Control     string            `json:"control"`
	Requirement string            `json:"requirement,omitempty"`
	Mappings    []FrameworkMapping `json:"mappings,omitempty"`
}

// FrameworkMapping represents mappings to external frameworks
type FrameworkMapping struct {
	Framework string `json:"framework"`
	ControlID string `json:"control_id"`
	Strength  int64  `json:"strength,omitempty"`
}

// CatalogToAmpel converts a Gemara Layer 2 catalog to Ampel policies
func CatalogToAmpel(catalogPath, outputDir string) error {
	// Parse the catalog using the LoadFile method
	catalog := &gemara.Catalog{}
	pathWithScheme := fmt.Sprintf("file://%s", catalogPath)
	if err := catalog.LoadFile(pathWithScheme); err != nil {
		return fmt.Errorf("failed to load catalog: %w", err)
	}

	// Create output directory
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		return fmt.Errorf("failed to create output directory: %w", err)
	}

	// Convert each control to an Ampel policy
	policyCount := 0
	for _, family := range catalog.ControlFamilies {
		for _, control := range family.Controls {
			policy := convertControlToPolicy(control, catalog.Metadata, catalog.Title)

			// Write policy to file
			policyFile := filepath.Join(outputDir, fmt.Sprintf("%s.json", sanitizeFilename(control.Id)))
			if err := writePolicy(policy, policyFile); err != nil {
				return fmt.Errorf("failed to write policy %s: %w", control.Id, err)
			}
			policyCount++
		}
	}

	fmt.Printf("Converted %d controls to Ampel policies\n", policyCount)
	return nil
}

// convertControlToPolicy converts a Gemara Control to an Ampel Policy
func convertControlToPolicy(control gemara.Control, metadata gemara.Metadata, catalogTitle string) AmpelPolicy {
	policy := AmpelPolicy{
		ID:          sanitizePolicyID(control.Id),
		Name:        cleanText(control.Title),
		Description: cleanText(control.Objective),
		Logic:       "AND", // Default to AND - all requirements must pass
		Tenets:      []AmpelTenet{},
	}

	// Convert assessment requirements to tenets
	for _, req := range control.AssessmentRequirements {
		tenet := AmpelTenet{
			Name:          req.Id,
			Description:   cleanText(req.Text),
			Evaluation:    generateEvaluationTemplate(req),
			Applicability: req.Applicability,
		}
		policy.Tenets = append(policy.Tenets, tenet)
	}

	// Add framework information
	if len(control.GuidelineMappings) > 0 {
		policy.Framework = &AmpelFramework{
			Catalog:  fmt.Sprintf("oscal://%s", sanitizeFilename(metadata.Id)),
			Control:  control.Id,
			Mappings: []FrameworkMapping{},
		}

		// Add guideline mappings as framework mappings
		for _, mapping := range control.GuidelineMappings {
			for _, entry := range mapping.Entries {
				policy.Framework.Mappings = append(policy.Framework.Mappings, FrameworkMapping{
					Framework: mapping.ReferenceId,
					ControlID: entry.ReferenceId,
					Strength:  entry.Strength,
				})
			}
		}
	}

	return policy
}

// generateEvaluationTemplate creates a placeholder evaluation expression
// In a real implementation, this would need to be customized based on the requirement
func generateEvaluationTemplate(req gemara.AssessmentRequirement) string {
	// Create a template that needs to be filled in with actual evaluation logic
	// This is a placeholder that indicates what evidence should be checked
	template := fmt.Sprintf(`// TODO: Implement evaluation logic for: %s
// Requirement: %s
//
// This evaluation should return true if the requirement is met.
// You can access evidence data through the 'evidence' object.
// Example: evidence.repository.mfa_enabled === true
//
// Placeholder evaluation (replace with actual logic):
evidence.%s !== undefined`,
		req.Id,
		strings.ReplaceAll(req.Text, "\n", "\n// "),
		sanitizePolicyID(req.Id),
	)

	return template
}

// writePolicy writes an Ampel policy to a JSON file
func writePolicy(policy AmpelPolicy, filename string) error {
	data, err := json.MarshalIndent(policy, "", "  ")
	if err != nil {
		return err
	}

	return os.WriteFile(filename, data, 0644)
}

// sanitizePolicyID converts a control ID to a valid policy ID
func sanitizePolicyID(id string) string {
	// Convert to lowercase and replace dots/spaces with hyphens
	id = strings.ToLower(id)
	id = strings.ReplaceAll(id, ".", "-")
	id = strings.ReplaceAll(id, " ", "-")
	return id
}

// sanitizeFilename creates a safe filename from a string
func sanitizeFilename(name string) string {
	// Replace unsafe characters with hyphens
	name = strings.ToLower(name)
	name = strings.ReplaceAll(name, " ", "-")
	name = strings.ReplaceAll(name, "/", "-")
	name = strings.ReplaceAll(name, "\\", "-")
	name = strings.ReplaceAll(name, ":", "-")
	return name
}

// cleanText removes leading/trailing whitespace and normalizes internal whitespace
func cleanText(text string) string {
	// Trim leading and trailing whitespace
	text = strings.TrimSpace(text)
	// Replace multiple spaces with single space
	text = strings.Join(strings.Fields(text), " ")
	return text
}
