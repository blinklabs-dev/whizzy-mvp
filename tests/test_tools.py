import unittest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

# Add app directory to path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.tools.salesforce_tool import SalesforceTool
from app.tools.snowflake_tool import SnowflakeTool

class TestSalesforceTool(unittest.TestCase):

    def test_run_salesforce_tool_as_runner(self):
        """Test the refactored SalesforceTool's run method, which now only executes SOQL."""
        # Arrange
        mock_sf_client = MagicMock()
        mock_sf_client.query_all.return_value = {"records": ["sf_record"]}

        # The tool no longer needs openai_client or executor
        tool = SalesforceTool(sf_client=mock_sf_client)

        # Act
        soql_query = "SELECT Id FROM Account"
        result = tool.run(soql_query) # The method is now synchronous

        # Assert
        # Check that the SOQL was executed directly
        mock_sf_client.query_all.assert_called_once_with(soql_query)
        # Check that the LLM was NOT called
        # (The mock_openai_client doesn't exist, so this is implicitly tested)
        # Check the result
        self.assertEqual(result, {"records": ["sf_record"]})


class TestSnowflakeTool(unittest.TestCase):

    def test_run_snowflake_tool(self):
        """Test the SnowflakeTool's run method."""
        mock_snow_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = ["snow_record"]
        mock_snow_conn.cursor.return_value = mock_cursor

        mock_openai_client = MagicMock()
        mock_llm_response = MagicMock()
        mock_llm_response.choices[0].message.content = "SELECT * FROM SNOW_TABLE"
        mock_openai_client.chat.completions.create.return_value = mock_llm_response

        # We need a real executor for the test to run the sync function in a thread
        from concurrent.futures import ThreadPoolExecutor
        executor = ThreadPoolExecutor(max_workers=1)

        tool = SnowflakeTool(snow_conn=mock_snow_conn, openai_client=mock_openai_client, executor=executor)

        result = asyncio.run(tool.run("get all snow data"))

        # Check that the LLM was called to generate SQL
        mock_openai_client.chat.completions.create.assert_called_once()
        # Check that the SQL was executed
        mock_cursor.execute.assert_called_once_with("SELECT * FROM SNOW_TABLE")
        # Check the result
        self.assertEqual(result, {"records": ["snow_record"]})


if __name__ == '__main__':
    unittest.main()
