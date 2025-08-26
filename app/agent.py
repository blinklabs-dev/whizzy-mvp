import os
import openai
from simple_salesforce import Salesforce
import structlog

# Initialize logging
logger = structlog.get_logger()

class SalesforceAgent:
    """An intelligent agent that can interact with Salesforce via natural language."""

    def __init__(self, salesforce_client: Salesforce):
        """
        Initializes the SalesforceAgent.

        Args:
            salesforce_client: An authenticated simple-salesforce client instance.
        """
        self.sf = salesforce_client
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        openai.api_key = self.openai_api_key
        self.client = openai.OpenAI()
        self._schema_cache = None
        logger.info("SalesforceAgent initialized.")

    def _get_salesforce_schema(self, object_names: list[str] = None) -> str:
        """
        Fetches a simplified schema for key Salesforce objects.

        Args:
            object_names: A list of Salesforce object names to describe.
                          Defaults to ['Opportunity', 'Account', 'User'].

        Returns:
            A string describing the schema of the requested objects.
        """
        if self._schema_cache:
            return self._schema_cache

        if object_names is None:
            object_names = ['Opportunity', 'Account', 'User']

        schema_description = "Salesforce Schema:\n"
        for obj_name in object_names:
            try:
                obj_desc = getattr(self.sf, obj_name).describe()
                schema_description += f"Object: {obj_desc['name']}\n"
                schema_description += "Fields:\n"
                for field in obj_desc['fields']:
                    schema_description += f"- {field['name']} ({field['type']})\n"
                schema_description += "\n"
            except Exception as e:
                logger.error("Failed to describe object", object_name=obj_name, error=e)

        self._schema_cache = schema_description
        logger.info("Salesforce schema loaded and cached.")
        return schema_description

    def generate_soql_query(self, user_query: str, chat_history: list[dict] = None) -> str:
        """
        Generates a SOQL query from a natural language user query.

        Args:
            user_query: The user's natural language question.
            chat_history: A list of previous user/assistant messages.

        Returns:
            A SOQL query string.
        """
        schema = self._get_salesforce_schema()

        system_prompt = f"""
You are a world-class Salesforce expert and data analyst. Your task is to convert a user's natural language question into a precise and valid Salesforce Object Query Language (SOQL) query.

You will be given the schema of the available Salesforce objects and their fields.
You must only respond with the SOQL query. Do not include any other text, explanations, or markdown formatting.

The Salesforce schema you have access to is:
{schema}
"""

        messages = [{"role": "system", "content": system_prompt}]

        if chat_history:
            for message in chat_history:
                messages.append(message)

        messages.append({"role": "user", "content": user_query})

        logger.info("Generating SOQL query for user request", user_query=user_query)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0,
                max_tokens=500,
                stop=None,
            )
            soql_query = response.choices[0].message.content.strip()

            # Basic validation to ensure it's a SELECT statement
            if soql_query.upper().startswith("SELECT"):
                logger.info("Successfully generated SOQL query", soql_query=soql_query)
                return soql_query
            else:
                logger.warning("Generated response is not a valid SOQL query", response=soql_query)
                return "Error: Could not generate a valid SOQL query."

        except Exception as e:
            logger.error("OpenAI API call failed", error=e)
            return f"Error: Failed to communicate with OpenAI API: {e}"

    def summarize_data_with_llm(self, user_query: str, data: str) -> str:
        """
        Summarizes raw data using an LLM into a user-friendly format.

        Args:
            user_query: The original user query for context.
            data: The raw JSON data from the Salesforce query.

        Returns:
            A formatted string with a summary of the data.
        """
        if not data:
            return "There was no data to summarize."

        system_prompt = """
You are a senior business analyst. Your task is to interpret a raw JSON dataset from Salesforce and present it as a clear, insightful, and professionally formatted summary for a business executive.

**Instructions:**
1.  **Analyze the Data:** Understand the data provided in the JSON.
2.  **Summarize Key Insights:** Extract the most important insights. Don't just list the data; explain what it means.
3.  **Use Professional Formatting:** Use Markdown for clear presentation. This includes:
    - A clear, concise title (e.g., "**🏆 Top 10 Accounts by Revenue**").
    - Bullet points (•) for key metrics and insights.
    - Bold text (`**`) to highlight important terms and numbers.
    - Emojis to add visual cues (e.g., 📊, 💰, 🎯).
4.  **Maintain a Professional Tone:** The language should be appropriate for an executive audience.
5.  **Do Not Include the Raw JSON:** Your output should only be the formatted summary.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here is the user's original request: '{user_query}'\n\nAnd here is the data I retrieved from Salesforce in JSON format:\n\n{data}"}
        ]

        logger.info("Summarizing data with LLM", original_query=user_query)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.5,
                max_tokens=1000
            )
            summary = response.choices[0].message.content.strip()
            logger.info("Successfully generated summary.")
            return summary
        except Exception as e:
            logger.error("Summarization API call failed", error=e)
            return "Error: Failed to generate a summary for the data."
