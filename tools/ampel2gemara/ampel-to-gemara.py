#!/usr/bin/env python3
"""
Convert ampel verify results to Gemara Layer 4 evaluation format.

Usage:
    python ampel-to-gemara.py <ampel-result.json> [output.yaml]
"""

import json
import sys
import yaml
from datetime import datetime
from typing import Dict, List, Any, Optional


def parse_timestamp(ts_str: str) -> str:
    """Parse timestamp string to ISO format."""
    return ts_str


def calculate_duration_ms(start: str, end: str) -> int:
    """Calculate duration in milliseconds between two timestamps."""
    try:
        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
        return int((end_dt - start_dt).total_seconds() * 1000)
    except Exception:
        return 0


def map_subject(ampel_subject: Dict[str, Any]) -> Dict[str, Any]:
    """Map ampel subject to Gemara subject format."""
    if not ampel_subject:
        return {
            'name': 'unknown',
            'type': 'artifact',
            'identifiers': []
        }

    identifiers = []
    for algo, value in ampel_subject.get('digest', {}).items():
        identifiers.append({
            'type': algo,
            'value': value
        })

    return {
        'name': ampel_subject.get('name', 'unknown'),
        'type': 'artifact',
        'identifiers': identifiers
    }


def map_finding(eval_result: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Map ampel eval_result to Gemara finding."""
    finding = {
        'id': eval_result.get('id', f'check-{index}'),
        'status': eval_result.get('status', 'UNKNOWN'),
        'timestamp': eval_result.get('date', '')
    }

    # Add description from assessment or error
    if eval_result.get('status') == 'PASS':
        assessment = eval_result.get('assessment', {})
        finding['description'] = assessment.get('message', '')
    else:
        error = eval_result.get('error', {})
        finding['description'] = error.get('message', '')
        if error.get('guidance'):
            finding['error'] = {
                'message': error.get('message', ''),
                'remediation': error.get('guidance', '')
            }

    # Add outputs if present
    if eval_result.get('output'):
        finding['outputs'] = eval_result.get('output')

    # Add evidence from statements
    statements = eval_result.get('statements', [])
    if statements:
        finding['evidence'] = []
        for stmt in statements:
            finding['evidence'].append({
                'type': stmt.get('type', 'attestation'),
                'digest': stmt.get('digest', '')
            })

    return finding


def map_controls(meta: Dict[str, Any], status: str) -> List[Dict[str, Any]]:
    """Map ampel controls to Gemara controls."""
    controls = []
    for control in meta.get('controls', []):
        controls.append({
            'id': control.get('id', ''),
            'framework': control.get('class', 'custom'),
            'status': status
        })
    return controls


def map_result_to_evaluation(result: Dict[str, Any]) -> Dict[str, Any]:
    """Map a single ampel Result to Gemara Layer 4 evaluation."""
    policy = result.get('policy', {})
    meta = result.get('meta', {})

    # Calculate duration
    duration_ms = calculate_duration_ms(
        result.get('date_start', ''),
        result.get('date_end', '')
    )

    # Determine overall assessment
    status = result.get('status', 'UNKNOWN')
    summary = meta.get('description', '')
    if status == 'PASS':
        summary = summary or 'All policy tenets validated successfully'
    elif status == 'FAIL':
        # Try to get failure summary from first failed check
        for eval_result in result.get('eval_results', []):
            if eval_result.get('status') != 'PASS':
                error = eval_result.get('error', {})
                summary = error.get('message', summary)
                break

    evaluation = {
        'evaluation': {
            'id': f"ampel-eval-{result.get('date_end', '').replace(':', '').replace('.', '').replace('Z', '')}",
            'timestamp': result.get('date_end', ''),
            'duration_ms': duration_ms,
            'evaluator': 'ampel',
            'evaluator_version': '1.0'
        },
        'subject': map_subject(result.get('subject', {})),
        'assessment': {
            'status': status,
            'summary': summary
        },
        'policy': {
            'id': policy.get('id', ''),
            'version': policy.get('version', ''),
            'description': meta.get('description', '')
        }
    }

    # Add controls if present
    controls = map_controls(meta, status)
    if controls:
        evaluation['controls'] = controls

    # Map findings
    findings = []
    for idx, eval_result in enumerate(result.get('eval_results', [])):
        findings.append(map_finding(eval_result, idx))

    if findings:
        evaluation['findings'] = findings

    # Add context if present
    if result.get('context'):
        evaluation['context'] = {
            'runtime': meta.get('runtime', ''),
            'assert_mode': meta.get('assert_mode', ''),
            'values': result.get('context')
        }

    return evaluation


def convert_ampel_to_gemara(ampel_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert ampel attestation format to Gemara Layer 4 format."""
    evaluations = []

    # Check if this is an in-toto statement
    if ampel_data.get('_type') == 'https://in-toto.io/Statement/v1':
        predicate = ampel_data.get('predicate', {})

        # Handle ResultSet
        if 'results' in predicate:
            for result in predicate.get('results', []):
                evaluations.append(map_result_to_evaluation(result))

        # Handle single Result wrapped in ResultSet
        elif 'policy' in predicate:
            evaluations.append(map_result_to_evaluation(predicate))

    # Direct Result or ResultSet (not in attestation wrapper)
    elif 'status' in ampel_data and 'policy' in ampel_data:
        evaluations.append(map_result_to_evaluation(ampel_data))
    elif 'results' in ampel_data:
        for result in ampel_data.get('results', []):
            evaluations.append(map_result_to_evaluation(result))

    # Handle raw predicate format (predicateType at top level)
    elif 'predicateType' in ampel_data and 'predicate' in ampel_data:
        predicate = ampel_data.get('predicate', {})
        if 'results' in predicate:
            for result in predicate.get('results', []):
                evaluations.append(map_result_to_evaluation(result))
        elif 'policy' in predicate:
            evaluations.append(map_result_to_evaluation(predicate))

    return evaluations


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    # Read ampel result
    try:
        with open(input_file, 'r') as f:
            ampel_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {input_file}: {e}")
        sys.exit(1)

    # Convert to Gemara format
    evaluations = convert_ampel_to_gemara(ampel_data)

    if not evaluations:
        print("Warning: No evaluations found in input")
        sys.exit(1)

    # Output YAML
    output = {
        'gemara_version': '1.0',
        'layer': 4,
        'type': 'evaluation',
        'evaluations': evaluations
    }

    yaml_output = yaml.dump(output, default_flow_style=False, sort_keys=False, allow_unicode=True)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(yaml_output)
        print(f"Gemara Layer 4 evaluation written to: {output_file}")
    else:
        print(yaml_output)


if __name__ == '__main__':
    main()
