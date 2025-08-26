import os
import json
import asyncio
from typing import Any, Dict, List

import openai
from simple_salesforce import Salesforce

from .base_tool import BaseTool

class SalesforceTool(BaseTool):
    """A tool for interacting with Salesforce."""
    name = "salesforce_tool"
    description = "Used for querying Salesforce data. Input should be a natural language question about Salesforce opportunities, accounts, or users."

    def __init__(self, sf_client: Salesforce, openai_client: openai.OpenAI, executor):
        self.sf = sf_client
        self.openai = openai_client
        self.executor = executor
        self.text_to_soql_prompt = self._load_prompt_from_file(os.path.join(os.path.dirname(__file__), '..', '..', 'prompts', 'system', 'text_to_soql.txt'))
        self.few_shot_examples = self._load_few_shot_examples(os.path.join(os.path.dirname(__file__), '..', '..', 'prompts', 'examples', 'text_to_soql.json'))

    def _load_prompt_from_file(self, file_path: str) -> str:
        with open(file_path, 'r') as f:
            return f.read()

    def _load_few_shot_examples(self, file_path: str) -> List[Dict[str, str]]:
        with open(file_path, 'r') as f:
            return json.load(f)

    def _get_salesforce_schema(self) -> str:
        """Fetches a simplified schema for key Salesforce objects."""
        object_names = ['Opportunity', 'Account', 'User']
        schema_description = "Salesforce Schema:\n"
        for obj_name in object_names:
            try:
                obj_desc = getattr(self.sf, obj_name).describe()
                schema_description += f"Object: {obj_desc['name']}\nFields:\n"
                for field in obj_desc['fields']:
                    if field['createable'] or not field['nillable']:
                        schema_description += f"- {field['name']} ({field['type']})\n"
                schema_description += "\n"
            except Exception:
                pass # Ignore errors for objects that might not exist
        return schema_description

    async def run(self, query: str) -> Dict[str, Any]:
        """
        Runs a natural language query against Salesforce.
        1. Gets the Salesforce schema.
        2. Converts the natural language query to SOQL using an LLM with few-shot examples.
        3. Executes the SOQL query.
        4. Returns the result.
        """
        if not self.sf:
            return {"error": "Salesforce client not initialized."}

        try:
            schema = self._get_salesforce_schema()
            few_shot_text = "\n".join([f"Question: {ex['question']}\nSOQL: {ex['soql']}" for ex in self.few_shot_examples])
            system_prompt = self.text_to_soql_prompt.format(
                few_shot_examples=few_shot_text,
                query=query,
                schema=schema
            )

            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.openai.chat.completions.create(
                    model="gpt-4o-mini", messages=[{"role": "system", "content": system_prompt}], temperature=0.0
                )
            )
            soql_query = response.choices[0].message.content.strip()

            result = self.sf.query_all(soql_query)
            return {"records": result['records']}
        except Exception as e:
            return {"error": str(e)}
