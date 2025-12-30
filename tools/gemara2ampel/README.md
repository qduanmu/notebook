# Gemara to Ampel Converter

This directory contains tools for converting Gemara Layer 3 policy files to other formats.

## gemara_to_ampel.py

Convert Gemara Layer 3 Policy files to Ampel PolicySet format.

### About Ampel

[Ampel](https://github.com/carabiner-dev/ampel) is "The Amazing Multipurpose Policy Engine (and L)" - a lightweight supply chain policy engine designed to verify unforgeable metadata captured in signed attestations throughout the software development lifecycle.

### Usage

```bash
python3 bin/gemara_to_ampel.py <input_yaml> [output_json]
```

**Arguments:**
- `<input_yaml>` - Path to Gemara Layer 3 policy YAML file (required)
- `[output_json]` - Path for output Ampel JSON file (optional, defaults to `<input>.ampel.json`)

### Examples

Convert with automatic output filename:
```bash
python3 bin/gemara_to_ampel.py test-data/good-policy.yaml
# Creates: good-policy.ampel.json
```

Convert with custom output filename:
```bash
python3 bin/gemara_to_ampel.py test-data/good-policy.yaml my-ampel-policy.json
```

### What Gets Converted

The script converts Gemara Layer 3 policies to Ampel PolicySets with the following mappings:

| Gemara Field | Ampel Field | Notes |
|-------------|-------------|-------|
| `metadata.id` | `id` | PolicySet identifier |
| `metadata.version` | `version` | Version string |
| `purpose` / `title` | `meta.description` | Policy description |
| `organization-id` | `meta.organization-id` | Organization identifier |
| `scope` | `common.context` | Converted to context values (boundaries, technologies, providers) |
| `contacts` | `meta.contacts` | Contact information preserved in metadata |
| `guidance-references` | `policies[]` | Each reference with modifications becomes a policy |
| `control-references` | `policies[]` | Each reference with modifications becomes a policy |
| `control-modifications` | `tenets[]` | Each modification becomes a tenet |
| `assessment-requirement-modifications` | `tenets[]` | Each modification becomes a tenet |
| `guideline-modifications` | `tenets[]` | Each modification becomes a tenet |
| `implementation-plan` | `meta.implementation-plan` | Implementation details preserved in metadata |

### Generated Ampel Policy Structure

Each generated Ampel PolicySet contains:

```json
{
  "id": "policy-set-id",
  "version": "1.0.0",
  "meta": {
    "description": "Policy description",
    "source": "Converted from Gemara Layer 3 Policy",
    "organization-id": "org-id",
    "converted-at": "2025-12-30T10:00:00Z",
    "contacts": { ... }
  },
  "common": {
    "context": {
      "boundaries": { ... },
      "technologies": { ... },
      "providers": { ... }
    }
  },
  "policies": [
    {
      "id": "policy-id",
      "version": "v1.0.0",
      "meta": { ... },
      "context": { ... },
      "predicates": {
        "types": ["https://in-toto.io/Statement/v1", ...]
      },
      "tenets": [
        {
          "runtime": "cel@v14.0",
          "code": "true  // TODO: Implement validation logic",
          "outputs": { ... },
          "assessment": { "message": "..." },
          "error": { "message": "...", "guidance": "..." }
        }
      ]
    }
  ]
}
```

### Important: Template Policies

**The conversion creates TEMPLATE policies that require implementation!**

All generated policies contain placeholder CEL code marked with `TODO` comments. You must:

1. **Implement CEL Evaluation Logic** - Replace `TODO` placeholders with actual CEL expressions
2. **Customize Predicate Types** - Update `predicates.types` to match your attestation format
3. **Add Signer Identities** - Add trusted signer identities if attestation verification is needed
4. **Implement Outputs** - Replace placeholder output extraction code with real logic

### Example: Completing a Generated Policy

**Before (Generated Template):**
```json
{
  "code": "true  // TODO: Implement validation logic",
  "outputs": {
    "control_status": {
      "code": "\"PENDING_IMPLEMENTATION\"  // TODO: Extract actual control status"
    }
  }
}
```

**After (Implemented):**
```json
{
  "code": "predicates[0].data.runDetails.builder.id.startsWith('https://github.com/myorg/')",
  "outputs": {
    "builder_id": {
      "code": "predicates[0].data.runDetails.builder.id"
    }
  }
}
```

### Next Steps After Conversion

1. Review the generated Ampel PolicySet
2. Implement CEL code in each tenet's `code` field
3. Customize predicate types based on your attestation format (SLSA, SPDX, CycloneDX, etc.)
4. Add signer identities for attestation verification (optional but recommended)
5. Test your policy:
   ```bash
   ampel verify --policy <output_file> --bundle <attestation_bundle>
   ```

### CEL Runtime Documentation

The generated policies use CEL (Common Expression Language) for evaluation. Key resources:

- [CEL Language Definition](https://cel.dev/)
- [Ampel Policy Guide](https://github.com/carabiner-dev/ampel/blob/main/docs/03-ampel-policy-guide.md)
- [Ampel Examples](https://github.com/carabiner-dev/policies)

### Common Predicate Types

Update the `predicates.types` field based on your attestation format:

- **SLSA Provenance**: `https://slsa.dev/provenance/v1`
- **In-Toto Statement**: `https://in-toto.io/Statement/v1`
- **SPDX SBOM**: `https://spdx.dev/Document`
- **CycloneDX SBOM**: `https://cyclonedx.org/bom`
- **OpenVEX**: `https://openvex.dev/ns/v0.2.0`

### Requirements

- Python 3.7+
- PyYAML (`pip install pyyaml`)

### Troubleshooting

**Error: "Input file not found"**
- Verify the file path is correct
- Use absolute paths or paths relative to the current directory

**Error: "Error parsing YAML file"**
- Ensure your Gemara policy file is valid YAML
- Check for proper indentation and syntax

**Generated policies have no tenets**
- Gemara policies without control/assessment/guideline modifications will generate a basic template
- You'll need to manually add tenets based on your requirements

### See Also

- [Gemara Model Documentation](../../README.md)
- [Layer 3 Schema](../../schemas/layer-3.cue)
- [Ampel Project](https://github.com/carabiner-dev/ampel)
- [Ampel Policies Repository](https://github.com/carabiner-dev/policies)
