import yaml
import os
import sys
import json
from typing import Dict, Any, List
from datetime import datetime

# Add the root directory to the Python path to allow importing 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agent import SalesforceAgent
from unittest.mock import MagicMock

def create_mock_salesforce_client():
    """Creates a mock simple-salesforce client."""
    mock_sf = MagicMock()
    mock_sf.query_all.return_value = {
        'totalSize': 1,
        'records': [{'Id': '001xx000003DGb2AAG', 'Name': 'Sample Account'}]
    }
    return mock_sf

def load_evaluation_cases(filepath: str) -> List[Dict[str, Any]]:
    """Loads evaluation cases from a YAML file."""
    try:
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Evaluation cases file not found at {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading YAML file: {e}")
        sys.exit(1)

def generate_markdown_report(results: List[Dict[str, Any]], output_path: str):
    """Generates a Markdown report from the evaluation results."""
    report_lines = []

    # --- Header ---
    report_lines.append(f"# Whizzy Bot Evaluation Report")
    report_lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**Total Cases:** {len(results)}")

    # --- Overall Scores ---
    total_accuracy = sum(r['grades']['accuracy']['score'] for r in results)
    total_relevance = sum(r['grades']['relevance']['score'] for r in results)
    total_succinctness = sum(r['grades']['succinctness']['score'] for r in results)
    num_results = len(results)

    avg_accuracy = total_accuracy / num_results if num_results else 0
    avg_relevance = total_relevance / num_results if num_results else 0
    avg_succinctness = total_succinctness / num_results if num_results else 0

    report_lines.append("\n## 📊 Overall Performance")
    report_lines.append(f"- **Average Accuracy:** {avg_accuracy:.2f} / 5.0")
    report_lines.append(f"- **Average Relevance:** {avg_relevance:.2f} / 5.0")
    report_lines.append(f"- **Average Succinctness:** {avg_succinctness:.2f} / 5.0")

    # --- Detailed Results ---
    report_lines.append("\n## 📋 Detailed Test Case Results")
    for result in results:
        case = result['case']
        soql = result['generated_soql']
        summary = result['generated_summary']
        grades = result['grades']

        report_lines.append(f"\n### Case ID: {case['id']} ({case['persona']})")
        report_lines.append(f"**Question:** _{case['question']}_")
        report_lines.append(f"\n**Generated SOQL:**\n```sql\n{soql}\n```")
        report_lines.append(f"\n**Generated Summary:**\n> {summary.replace(chr(10), ' ')}")

        report_lines.append("\n**Grading:**")
        report_lines.append("| Criterion    | Score | Justification |")
        report_lines.append("|--------------|-------|---------------|")
        report_lines.append(f"| Accuracy     | {grades['accuracy']['score']}/5 | {grades['accuracy']['justification']} |")
        report_lines.append(f"| Relevance    | {grades['relevance']['score']}/5 | {grades['relevance']['justification']} |")
        report_lines.append(f"| Succinctness | {grades['succinctness']['score']}/5 | {grades['succinctness']['justification']} |")
        report_lines.append("\n---")

    # Write to file
    with open(output_path, 'w') as f:
        f.write("\n".join(report_lines))
    print(f"\n✅ Evaluation report generated at {output_path}")


def run_evaluation():
    """
    Runs the evaluation suite against the SalesforceAgent.
    """
    print("--- Starting Evaluation Run ---")

    cases_filepath = os.path.join(os.path.dirname(__file__), '..', 'tests', 'evaluation_cases.yml')
    evaluation_cases = load_evaluation_cases(cases_filepath)
    print(f"Loaded {len(evaluation_cases)} evaluation cases.")

    mock_sf_client = create_mock_salesforce_client()
    try:
        agent = SalesforceAgent(salesforce_client=mock_sf_client)
    except ValueError as e:
        print(f"Failed to initialize SalesforceAgent: {e}")
        print("Please ensure your OPENAI_API_KEY is set in your environment.")
        sys.exit(1)

    results = []

    for i, case in enumerate(evaluation_cases):
        print(f"\n--- Running Case {i+1}/{len(evaluation_cases)}: {case['id']} ---")
        print(f"Persona: {case['persona']}")
        print(f"Question: {case['question']}")

        generated_soql = agent.generate_soql_query(case['question'])
        print(f"Generated SOQL: {generated_soql}")

        mock_data = json.dumps(mock_sf_client.query_all.return_value['records'])
        generated_summary = agent.summarize_data_with_llm(case['question'], mock_data)
        print("Generated Summary: (omitted for brevity)")

        grades = agent.grade_response_with_llm(case['question'], generated_soql, generated_summary)
        print(f"Grades: {grades}")

        results.append({
            'case': case,
            'generated_soql': generated_soql,
            'generated_summary': generated_summary,
            'grades': grades
        })

    print("\n--- Evaluation Run Complete ---")

    report_path = os.path.join(os.path.dirname(__file__), '..', 'evaluation_report.md')
    generate_markdown_report(results, report_path)

if __name__ == "__main__":
    run_evaluation()
