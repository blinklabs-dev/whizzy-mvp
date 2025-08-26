import os
import json
import asyncio
from typing import Any, Dict

import openai
import snowflake.connector

from .base_tool import BaseTool

class SnowflakeTool(BaseTool):
    """A tool for interacting with a Snowflake data warehouse."""
    name = "snowflake_tool"
    description = "Used for querying data from the Snowflake data warehouse. Input should be a natural language question about business data."

    def __init__(self, snow_conn: snowflake.connector.SnowflakeConnection, openai_client: openai.OpenAI, executor):
        self.connection = snow_conn
        self.openai = openai_client
        self.executor = executor

    async def run(self, query: str) -> Dict[str, Any]:
        """
        Runs a natural language query against Snowflake.
        1. Converts the natural language query to a Snowflake SQL query using an LLM.
        2. Executes the SQL query.
        3. Returns the result.
        """
        if not self.connection:
            return {"error": "Snowflake connection not initialized."}

        try:
            system_prompt = "You are a Snowflake SQL expert. Convert the user's question into a single, valid Snowflake SQL query. Only return the SQL query."

            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.0
                )
            )
            sql_query = response.choices[0].message.content.strip()

            def execute_sync_query():
                cursor = self.connection.cursor(snowflake.connector.DictCursor)
                cursor.execute(sql_query)
                return cursor.fetchall()

            results = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                execute_sync_query
            )

            return {"records": results}
        except Exception as e:
            return {"error": str(e)}
