#!/usr/bin/env python3
"""
Convert Gemara Layer 3 Policy Files to Ampel Policy Format

This script reads a Gemara Layer 3 policy YAML file and converts it to an
Ampel PolicySet in JSON format. The conversion creates policy templates that
need to be completed with actual CEL evaluation code.

Usage:
    python gemara_to_ampel.py <input_yaml> [output_json]

Examples:
    python gemara_to_ampel.py policy.yaml
    python gemara_to_ampel.py policy.yaml ampel-policy.json
"""

import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone


class GemaraToAmpelConverter:
    """Converts Gemara Layer 3 policies to Ampel policy format."""

    def __init__(self):
        self.runtime_version = "cel@v14.0"

    def load_gemara_policy(self, filepath: str) -> Dict[str, Any]:
        """Load a Gemara Layer 3 policy from YAML file."""
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)

    def convert(self, gemara_policy: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Gemara Layer 3 policy to Ampel PolicySet format."""

        metadata = gemara_policy.get('metadata', {})
        org_id = gemara_policy.get('organization-id', '')
        title = gemara_policy.get('title', '')
        purpose = gemara_policy.get('purpose', '')
        scope = gemara_policy.get('scope', {})
        contacts = gemara_policy.get('contacts', {})
        guidance_refs = gemara_policy.get('guidance-references', [])
        control_refs = gemara_policy.get('control-references', [])
        impl_plan = gemara_policy.get('implementation-plan', {})

        # Create the PolicySet
        policy_set = {
            "id": metadata.get('id', 'gemara-policy'),
            "version": metadata.get('version', '1.0.0'),
            "meta": {
                "description": purpose or title,
                "source": "Converted from Gemara Layer 3 Policy",
                "organization-id": org_id,
                "converted-at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        }

        # Add common context from scope
        if scope:
            policy_set["common"] = {
                "context": self._create_context_from_scope(scope)
            }

        # Convert policies from guidance and control references
        policies = []

        # Process guidance references
        for ref in guidance_refs:
            policies.extend(self._convert_policy_mapping(
                ref,
                "guidance",
                metadata,
                scope
            ))

        # Process control references
        for ref in control_refs:
            policies.extend(self._convert_policy_mapping(
                ref,
                "control",
                metadata,
                scope
            ))

        # If no references with modifications, create a basic policy template
        if not policies:
            policies.append(self._create_basic_policy(
                metadata,
                title,
                purpose,
                scope
            ))

        policy_set["policies"] = policies

        # Add implementation details as metadata
        if impl_plan:
            policy_set["meta"]["implementation-plan"] = self._extract_implementation_metadata(impl_plan)

        # Add contact information as metadata
        if contacts:
            policy_set["meta"]["contacts"] = contacts

        return policy_set

    def _create_context_from_scope(self, scope: Dict[str, Any]) -> Dict[str, Any]:
        """Create Ampel context values from Gemara scope."""
        context = {}

        if scope.get('boundaries'):
            context['boundaries'] = {
                "type": "list",
                "default": scope['boundaries'],
                "required": False
            }

        if scope.get('technologies'):
            context['technologies'] = {
                "type": "list",
                "default": scope['technologies'],
                "required": False
            }

        if scope.get('providers'):
            context['providers'] = {
                "type": "list",
                "default": scope['providers'],
                "required": False
            }

        return context

    def _convert_policy_mapping(
        self,
        mapping: Dict[str, Any],
        mapping_type: str,
        metadata: Dict[str, Any],
        scope: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Convert a Gemara PolicyMapping to Ampel policies."""

        policies = []
        reference_id = mapping.get('reference-id', 'unknown')
        in_scope = mapping.get('in-scope', {})
        out_of_scope = mapping.get('out-of-scope', {})

        # Process control modifications
        control_mods = mapping.get('control-modifications', [])
        for mod in control_mods:
            policy = self._create_policy_from_modification(
                mod,
                reference_id,
                mapping_type,
                "control",
                in_scope,
                out_of_scope,
                metadata
            )
            policies.append(policy)

        # Process assessment requirement modifications
        assessment_mods = mapping.get('assessment-requirement-modifications', [])
        for mod in assessment_mods:
            policy = self._create_policy_from_modification(
                mod,
                reference_id,
                mapping_type,
                "assessment",
                in_scope,
                out_of_scope,
                metadata
            )
            policies.append(policy)

        # Process guideline modifications
        guideline_mods = mapping.get('guideline-modifications', [])
        for mod in guideline_mods:
            policy = self._create_policy_from_modification(
                mod,
                reference_id,
                mapping_type,
                "guideline",
                in_scope,
                out_of_scope,
                metadata
            )
            policies.append(policy)

        return policies

    def _create_policy_from_modification(
        self,
        modification: Dict[str, Any],
        reference_id: str,
        mapping_type: str,
        mod_category: str,
        in_scope: Dict[str, Any],
        out_of_scope: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create an Ampel policy from a Gemara modification."""

        target_id = modification.get('target-id', 'unknown')
        mod_type = modification.get('modification-type', 'clarify')
        rationale = modification.get('modification-rationale', '')

        policy_id = f"{reference_id}-{target_id}".replace('.', '-')

        # Build policy description
        title = modification.get('title', '')
        objective = modification.get('objective', '')
        description = title or objective or rationale

        policy = {
            "id": policy_id,
            "version": "v1.0.0",
            "meta": {
                "description": description,
                "reference-id": reference_id,
                "target-id": target_id,
                "modification-type": mod_type,
                "modification-rationale": rationale,
                "mapping-type": mapping_type,
                "category": mod_category
            }
        }

        # Add context for scope
        context = {}
        if in_scope:
            context.update(self._create_context_from_scope(in_scope))

        if context:
            policy["context"] = context

        # Create tenets
        tenets = []

        if mod_category == "control":
            tenet = self._create_control_tenet(modification, mod_type)
        elif mod_category == "assessment":
            tenet = self._create_assessment_tenet(modification, mod_type)
        elif mod_category == "guideline":
            tenet = self._create_guideline_tenet(modification, mod_type)
        else:
            tenet = self._create_generic_tenet(modification, mod_type)

        tenets.append(tenet)
        policy["tenets"] = tenets

        # Add predicates spec (placeholder - needs to be customized)
        policy["predicates"] = {
            "types": [
                "https://in-toto.io/Statement/v1",
                "https://slsa.dev/provenance/v1"
            ]
        }

        return policy

    def _create_control_tenet(self, modification: Dict[str, Any], mod_type: str) -> Dict[str, Any]:
        """Create a tenet for a control modification."""

        title = modification.get('title', 'Control Check')
        objective = modification.get('objective', '')

        # Create placeholder CEL code based on modification type
        if mod_type == "increase-strictness":
            code_template = 'true  // TODO: Implement stricter validation logic'
        elif mod_type == "reduce-strictness":
            code_template = 'true  // TODO: Implement relaxed validation logic'
        elif mod_type == "exclude":
            code_template = 'true  // TODO: Implement exclusion logic'
        else:  # clarify
            code_template = 'true  // TODO: Implement clarified validation logic'

        tenet = {
            "runtime": self.runtime_version,
            "code": code_template,
            "outputs": {
                "control_status": {
                    "code": "\"PENDING_IMPLEMENTATION\"  // TODO: Extract actual control status"
                }
            },
            "assessment": {
                "message": f"{title}: {objective}".strip(': ')
            },
            "error": {
                "message": f"Control validation failed: {title}",
                "guidance": f"Review the control requirements and ensure compliance. Modification type: {mod_type}"
            }
        }

        return tenet

    def _create_assessment_tenet(self, modification: Dict[str, Any], mod_type: str) -> Dict[str, Any]:
        """Create a tenet for an assessment requirement modification."""

        text = modification.get('text', '')
        applicability = modification.get('applicability', [])
        recommendation = modification.get('recommendation', '')

        tenet = {
            "runtime": self.runtime_version,
            "code": 'true  // TODO: Implement assessment validation logic',
            "outputs": {
                "assessment_result": {
                    "code": "\"PENDING_IMPLEMENTATION\"  // TODO: Extract assessment result"
                },
                "applicability": {
                    "code": json.dumps(applicability)
                }
            },
            "assessment": {
                "message": text or "Assessment requirement validated"
            },
            "error": {
                "message": f"Assessment validation failed",
                "guidance": recommendation or "Review the assessment requirements"
            }
        }

        return tenet

    def _create_guideline_tenet(self, modification: Dict[str, Any], mod_type: str) -> Dict[str, Any]:
        """Create a tenet for a guideline modification."""

        title = modification.get('title', 'Guideline Check')
        recommendations = modification.get('recommendations', [])

        tenet = {
            "runtime": self.runtime_version,
            "code": 'true  // TODO: Implement guideline validation logic',
            "outputs": {
                "guideline_compliance": {
                    "code": "\"PENDING_IMPLEMENTATION\"  // TODO: Extract compliance status"
                }
            },
            "assessment": {
                "message": f"Guideline validated: {title}"
            },
            "error": {
                "message": f"Guideline validation failed: {title}",
                "guidance": " | ".join(recommendations) if recommendations else "Review guideline requirements"
            }
        }

        return tenet

    def _create_generic_tenet(self, modification: Dict[str, Any], mod_type: str) -> Dict[str, Any]:
        """Create a generic tenet."""

        tenet = {
            "runtime": self.runtime_version,
            "code": 'true  // TODO: Implement validation logic',
            "outputs": {
                "status": {
                    "code": "\"PENDING_IMPLEMENTATION\""
                }
            },
            "assessment": {
                "message": "Policy requirement validated"
            },
            "error": {
                "message": "Policy validation failed",
                "guidance": modification.get('modification-rationale', 'Review policy requirements')
            }
        }

        return tenet

    def _create_basic_policy(
        self,
        metadata: Dict[str, Any],
        title: str,
        purpose: str,
        scope: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a basic policy template when no modifications are present."""

        policy = {
            "id": metadata.get('id', 'basic-policy'),
            "version": metadata.get('version', 'v1.0.0'),
            "meta": {
                "description": purpose or title or "Basic policy template",
                "note": "This is a template policy. Please customize with specific tenets."
            },
            "predicates": {
                "types": [
                    "https://in-toto.io/Statement/v1"
                ]
            },
            "tenets": [
                {
                    "runtime": self.runtime_version,
                    "code": 'true  // TODO: Implement policy validation logic',
                    "outputs": {
                        "policy_status": {
                            "code": "\"PENDING_IMPLEMENTATION\""
                        }
                    },
                    "assessment": {
                        "message": "Policy validated successfully"
                    },
                    "error": {
                        "message": "Policy validation failed",
                        "guidance": "Implement specific validation logic for this policy"
                    }
                }
            ]
        }

        # Add context if scope is available
        if scope:
            policy["context"] = self._create_context_from_scope(scope)

        return policy

    def _extract_implementation_metadata(self, impl_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant implementation plan metadata."""

        metadata = {}

        if 'notification-process' in impl_plan:
            metadata['notification-process'] = impl_plan['notification-process']

        if 'notified-parties' in impl_plan:
            metadata['notified-parties'] = impl_plan['notified-parties']

        if 'evaluation' in impl_plan:
            metadata['evaluation'] = impl_plan['evaluation']

        if 'evaluation-points' in impl_plan:
            metadata['evaluation-points'] = impl_plan['evaluation-points']

        if 'enforcement' in impl_plan:
            metadata['enforcement'] = impl_plan['enforcement']

        if 'enforcement-methods' in impl_plan:
            metadata['enforcement-methods'] = impl_plan['enforcement-methods']

        if 'noncompliance-plan' in impl_plan:
            metadata['noncompliance-plan'] = impl_plan['noncompliance-plan']

        return metadata

    def save_ampel_policy(self, policy_set: Dict[str, Any], filepath: str):
        """Save Ampel PolicySet to JSON file."""

        with open(filepath, 'w') as f:
            json.dump(policy_set, f, indent=2)

        print(f"✓ Ampel PolicySet saved to: {filepath}")


def main():
    """Main entry point for the converter."""

    if len(sys.argv) < 2:
        print("Error: Input file required")
        print(f"\nUsage: {sys.argv[0]} <input_yaml> [output_json]")
        print("\nExamples:")
        print(f"  {sys.argv[0]} policy.yaml")
        print(f"  {sys.argv[0]} policy.yaml ampel-policy.json")
        sys.exit(1)

    input_file = sys.argv[1]

    # Determine output file
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        # Default output: replace extension with .ampel.json
        input_path = Path(input_file)
        output_file = input_path.stem + '.ampel.json'

    # Validate input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    print(f"Converting Gemara Layer 3 policy to Ampel format...")
    print(f"  Input:  {input_file}")
    print(f"  Output: {output_file}")
    print()

    try:
        # Convert
        converter = GemaraToAmpelConverter()
        gemara_policy = converter.load_gemara_policy(input_file)
        ampel_policy = converter.convert(gemara_policy)
        converter.save_ampel_policy(ampel_policy, output_file)

        # Print summary
        print()
        print("Conversion Summary:")
        print(f"  PolicySet ID: {ampel_policy['id']}")
        print(f"  Policies:     {len(ampel_policy.get('policies', []))}")
        print()
        print("⚠️  Important Notes:")
        print("  - This conversion creates TEMPLATE policies that require implementation")
        print("  - All 'code' fields contain placeholders marked with 'TODO'")
        print("  - You must implement actual CEL evaluation logic for each tenet")
        print("  - Review and customize the 'predicates.types' for each policy")
        print("  - Add signer 'identities' if attestation verification is needed")
        print()
        print("📚 Next Steps:")
        print("  1. Review the generated Ampel PolicySet")
        print("  2. Implement CEL code in each tenet's 'code' field")
        print("  3. Customize predicate types based on your attestation format")
        print("  4. Add signer identities for attestation verification")
        print("  5. Test with: ampel verify --policy <output_file> <attestation>")

    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
