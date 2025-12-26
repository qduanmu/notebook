# Ampel Tools

This directory contains utility tools for working with Ampel verification results.

## ampel-to-gemara

Converts Ampel verify results to [Gemara](https://github.com/ossf/gemara/) Layer 4 evaluation format.

### Python Version

**Requirements:**
```bash
pip install pyyaml
```

**Usage:**
```bash
# Output to stdout
python ampel-to-gemara.py results.json

# Output to file
python ampel-to-gemara.py results.json output.yaml
```

**Example:**
```bash
# Run ampel verify with JSON attestation output
ampel verify \
  --subject-file myapp \
  --policy policy.hjson \
  --attestation sbom.json \
  --attest-results \
  --results-path results.json

# Convert to Gemara Layer 4
python ampel-to-gemara.py results.json gemara-l4.yaml
```

### Go Version

**Build:**
```bash
cd ampel-to-gemara
go build -o ampel-to-gemara
```

**Usage:**
```bash
# Output to stdout
./ampel-to-gemara -i results.json

# Output to file
./ampel-to-gemara -i results.json -o output.yaml
```

**Installation:**
```bash
# Install to $GOPATH/bin
go install github.com/carabiner-dev/ampel/tools/ampel-to-gemara@latest
```

## Output Format

The tools convert Ampel results to Gemara Layer 4 evaluation format with the following mappings:

| Ampel Field | Gemara Layer 4 Field |
|-------------|---------------------|
| `Result` | `evaluation` metadata |
| `subject` | `subject` with identifiers |
| `status` | `assessment.status` |
| `policy` | `policy` reference |
| `controls` | `controls[]` array |
| `eval_results[]` | `findings[]` array |
| `assessment.message` | `finding.description` |
| `error` | `finding.error` with remediation |
| `output` | `finding.outputs` |
| `statements` | `finding.evidence[]` |

### Example Output

```yaml
gemara_version: '1.0'
layer: 4
type: evaluation
evaluations:
- evaluation:
    id: ampel-eval-20251226-103045
    timestamp: '2025-12-26T10:30:45Z'
    duration_ms: 234
    evaluator: ampel
    evaluator_version: '1.0'
  subject:
    name: myapp-binary
    type: artifact
    identifiers:
    - type: sha256
      value: 08bdfa07a9a1404eb8929f45896c715a...
  assessment:
    status: PASS
    summary: All policy tenets validated successfully
  policy:
    id: AC-07
    version: v0.0.1
    description: MFA authentication required
  controls:
  - id: AC-07
    framework: NIST-800-53
    status: PASS
  findings:
  - id: check-0
    description: Predicates loaded successfully
    status: PASS
    timestamp: '2025-12-26T10:30:45.200Z'
    outputs:
      predicate_count: 1
```

## Integration with Gemara

The generated YAML can be used with Gemara tools for:
- Compliance reporting across Layer 1 (Guidance) and Layer 2 (Controls)
- Aggregating evaluation results from multiple tools
- Mapping security assessments to regulatory frameworks
- Building audit trails for governance activities

For more information about Gemara:
- [Gemara Documentation](https://gemara.openssf.org/)
- [Gemara GitHub](https://github.com/ossf/gemara/)
