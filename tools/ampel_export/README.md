# Ampel Export Tool

A command-line tool to convert Gemara Layer 2 control catalogs into [Ampel](https://github.com/carabiner-dev/ampel) policy format.

## Overview

This tool converts Gemara Layer 2 controls (technology-specific, threat-informed security controls) into Ampel policies (executable evaluation policies). Ampel is The Amazing Multipurpose Policy Engine that can evaluate evidence against policies to determine compliance.

## Installation

Build the tool from the Gemara repository root:

```bash
go build -o bin/ampel_export ./cmd/ampel_export
```

## Usage

```bash
ampel_export -output <output-directory> <catalog-path>
```

### Arguments

- `<catalog-path>`: Path to the Gemara Layer 2 catalog file (YAML or JSON)
- `-output <dir>`: Output directory for generated Ampel policy files (default: `./ampel-policies`)

**Note**: Flags must be specified before positional arguments in Go.

### Example

```bash
# Convert OSPS baseline to Ampel policies
ampel_export -output ./policies test-data/good-osps.yml

# Use default output directory
ampel_export test-data/good-osps.yml
```

## Output Format

The tool generates one JSON file per control in the catalog. Each file contains an Ampel policy with:

- **ID**: Sanitized control ID (lowercase, hyphens instead of dots)
- **Name**: Control title
- **Description**: Control objective
- **Logic**: Policy evaluation logic (default: "AND" - all tenets must pass)
- **Tenets**: Array of evaluation checks, one per assessment requirement
- **Framework**: Links to the source catalog and any guideline mappings

### Example Output

```json
{
  "id": "osps-ac-01",
  "name": "The project's version control system MUST require multi-factor authentication...",
  "description": "Reduce the risk of account compromise or insider threats...",
  "logic": "AND",
  "tenets": [
    {
      "name": "OSPS-AC-01.01",
      "description": "When a user attempts to access a sensitive resource...",
      "evaluation": "// TODO: Implement evaluation logic...",
      "applicability": ["Maturity Level 1", "Maturity Level 2", "Maturity Level 3"]
    }
  ],
  "framework": {
    "catalog": "oscal://osps-b",
    "control": "OSPS-AC-01",
    "mappings": [
      {"framework": "NIST-CSF", "control_id": "PR.A-02", "strength": 7}
    ]
  }
}
```

## Post-Conversion Steps

The generated policies include placeholder evaluation logic that **must be customized** for your use case:

1. **Implement Evaluation Logic**: Replace the TODO comments in the `evaluation` field with actual code that checks evidence data
2. **Define Evidence Schema**: Determine what evidence (SBOM, SLSA provenance, custom JSON) will be evaluated
3. **Test Policies**: Validate that your evaluation logic correctly assesses the evidence
4. **Adjust Logic Type**: Change from "AND" to "OR" if appropriate for specific controls

### Evaluation Logic Examples

The generated placeholder uses this format:
```javascript
// TODO: Implement evaluation logic for: OSPS-AC-01.01
evidence.osps-ac-01-01 !== undefined
```

You should replace this with actual evaluation logic, such as:
```javascript
// Check MFA is enabled in repository settings
evidence.repository.settings.mfa_required === true
```

Or for SLSA provenance:
```javascript
// Check build was on trusted builder
evidence.slsa_provenance.builder.id.startsWith("https://github.com/")
```

## Conversion Mapping

| Gemara Layer 2 | Ampel Policy |
|----------------|--------------|
| Control | Policy |
| Control ID | Policy ID (sanitized) |
| Control Title | Policy Name |
| Control Objective | Policy Description |
| Assessment Requirement | Tenet |
| Assessment Requirement Text | Tenet Description |
| Applicability | Tenet Applicability |
| Guideline Mappings | Framework Mappings |

## Limitations

- **Evaluation Logic**: The tool generates placeholder evaluation code that requires manual implementation
- **Evidence Schema**: You must define what evidence data will be available and how to access it
- **Policy Logic**: All policies default to "AND" logic; you may need to adjust this
- **Threat Mappings**: Threat mappings from Gemara are not currently included in the Ampel output
- **Capabilities**: Capability information is not transferred to Ampel policies

## Resources

- [Ampel GitHub Repository](https://github.com/carabiner-dev/ampel)
- [Gemara Documentation](../../README.md)
- [SLSA + Ampel Integration](https://slsa.dev/blog/2025/10/slsa-e2e-with-ampel)
