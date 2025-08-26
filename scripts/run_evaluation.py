import yaml
import os
import sys
import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime

# Add the root directory to the Python path to allow importing 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.intelligent_agentic_system import EnhancedIntelligentAgenticSystem

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

    report_lines.append(f"# Whizzy Bot Evaluation Report")
    report_lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**Total Cases:** {len(results)}")

    # --- Overall Scores ---
    # This part needs to be adapted once grading is in place
    report_lines.append("\n## 📊 Overall Performance (Grading TBD)")

    # --- Detailed Results ---
    report_lines.append("\n## 📋 Detailed Test Case Results")
    for result in results:
        case = result['case']
        response = result['response']

        report_lines.append(f"\n### Case ID: {case['id']} ({case['persona']})")
        report_lines.append(f"**Question:** _{case['question']}_")
        report_lines.append(f"\n**Generated Response:**\n> {response.response_text.replace(chr(10), ' ')}")
        report_lines.append(f"\n**Thinking Process:**\n```json\n{response.thinking_process}\n```")
        report_lines.append("\n---")

    with open(output_path, 'w') as f:
        f.write("\n".join(report_lines))
    print(f"\n✅ Evaluation report generated at {output_path}")


async def run_evaluation():
    """
    Runs the evaluation suite against the SalesforceAgent.
    """
    print("--- Starting Evaluation Run ---")

    cases_filepath = os.path.join(os.path.dirname(__file__), '..', 'tests', 'evaluation_cases.yml')
    evaluation_cases = load_evaluation_cases(cases_filepath)
    print(f"Loaded {len(evaluation_cases)} evaluation cases.")

    try:
        agent = EnhancedIntelligentAgenticSystem()
    except Exception as e:
        print(f"Failed to initialize agent: {e}. Ensure OPENAI_API_KEY is set.")
        sys.exit(1)

    results = []

    for i, case in enumerate(evaluation_cases):
        print(f"\n--- Running Case {i+1}/{len(evaluation_cases)}: {case['id']} ---")
        print(f"Question: {case['question']}")

        # Process the query through the agent
        response = await agent.process_query(case['question'], user_id=f"eval_{case['id']}")

        results.append({
            'case': case,
            'response': response,
        })

    print("\n--- Evaluation Run Complete ---")

    report_path = os.path.join(os.path.dirname(__file__), '..', 'evaluation_report.md')
    generate_markdown_report(results, report_path)


if __name__ == "__main__":
    asyncio.run(run_evaluation())
