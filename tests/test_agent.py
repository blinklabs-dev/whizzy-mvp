import unittest
from unittest.mock import MagicMock, patch
import os

# Set dummy environment variables for testing
os.environ['OPENAI_API_KEY'] = 'test_key'

from app.agent import SalesforceAgent

class TestSalesforceAgent(unittest.TestCase):

    def setUp(self):
        """Set up a mock Salesforce client and the agent for each test."""
        self.mock_sf_client = MagicMock()
        self.agent = SalesforceAgent(salesforce_client=self.mock_sf_client)

    def test_initialization(self):
        """Test that the agent initializes correctly."""
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.sf, self.mock_sf_client)
        self.assertIsNotNone(self.agent.client)

    def test_get_salesforce_schema(self):
        """Test the Salesforce schema fetching and caching."""
        mock_opportunity_desc = {
            'name': 'Opportunity',
            'fields': [
                {'name': 'Id', 'type': 'id'},
                {'name': 'Name', 'type': 'string'},
                {'name': 'Amount', 'type': 'currency'}
            ]
        }
        mock_account_desc = {
            'name': 'Account',
            'fields': [
                {'name': 'Id', 'type': 'id'},
                {'name': 'Name', 'type': 'string'},
                {'name': 'AnnualRevenue', 'type': 'currency'}
            ]
        }

        # Configure the mock to return different descriptions for different objects
        self.mock_sf_client.Opportunity.describe.return_value = mock_opportunity_desc
        self.mock_sf_client.Account.describe.return_value = mock_account_desc
        # Mock the User object as well as it's in the default list
        self.mock_sf_client.User.describe.return_value = {'name': 'User', 'fields': []}


        # First call - should fetch schema
        schema = self.agent._get_salesforce_schema(object_names=['Opportunity', 'Account'])

        self.assertIn("Object: Opportunity", schema)
        self.assertIn("- Name (string)", schema)
        self.assertIn("Object: Account", schema)
        self.assertIn("- AnnualRevenue (currency)", schema)

        # Check that the describe methods were called
        self.mock_sf_client.Opportunity.describe.assert_called_once()
        self.mock_sf_client.Account.describe.assert_called_once()

        # Second call - should use cache
        schema2 = self.agent._get_salesforce_schema()
        self.assertEqual(schema, schema2)

        # Ensure describe was not called again
        self.mock_sf_client.Opportunity.describe.assert_called_once()
        self.mock_sf_client.Account.describe.assert_called_once()


    @patch('openai.resources.chat.completions.Completions.create')
    def test_generate_soql_query_success(self, mock_openai_create):
        """Test successful generation of a SOQL query."""
        # Mock the schema to avoid SF call
        self.agent._schema_cache = "Mock Schema"

        # Mock the OpenAI API response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "SELECT Id, Name FROM Opportunity"
        mock_openai_create.return_value = mock_response

        user_query = "show me opportunities"
        soql = self.agent.generate_soql_query(user_query)

        # Check that the OpenAI client was called with a constructed prompt
        mock_openai_create.assert_called_once()
        call_args = mock_openai_create.call_args
        messages = call_args.kwargs['messages']

        # Verify the structure and content of the prompt
        self.assertEqual(messages[0]['role'], 'system')
        self.assertIn("You are a world-class Salesforce expert", messages[0]['content'])
        self.assertIn("Mock Schema", messages[0]['content'])
        self.assertEqual(messages[1]['role'], 'user')
        self.assertEqual(messages[1]['content'], user_query)

        # Verify the result
        self.assertEqual(soql, "SELECT Id, Name FROM Opportunity")

    @patch('openai.resources.chat.completions.Completions.create')
    def test_generate_soql_query_with_history(self, mock_openai_create):
        """Test that chat history is correctly included in the prompt."""
        self.agent._schema_cache = "Mock Schema"
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "SELECT Id FROM Account"
        mock_openai_create.return_value = mock_response

        user_query = "now for accounts"
        chat_history = [
            {"role": "user", "content": "show me top 5 opportunities"},
            {"role": "assistant", "content": "SELECT Id, Name, Amount FROM Opportunity ORDER BY Amount DESC LIMIT 5"}
        ]

        self.agent.generate_soql_query(user_query, chat_history)

        # Check that the history was included in the messages
        messages = mock_openai_create.call_args.kwargs['messages']
        self.assertEqual(len(messages), 4) # system, user_hist, assistant_hist, user_new
        self.assertEqual(messages[1], chat_history[0])
        self.assertEqual(messages[2], chat_history[1])
        self.assertEqual(messages[3]['content'], user_query)


    @patch('openai.resources.chat.completions.Completions.create')
    def test_generate_soql_query_invalid_response(self, mock_openai_create):
        """Test handling of a non-SOQL response from the API."""
        self.agent._schema_cache = "Mock Schema"
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "I'm sorry, I cannot do that."
        mock_openai_create.return_value = mock_response

        soql = self.agent.generate_soql_query("tell me a joke")
        self.assertIn("Error: Could not generate a valid SOQL query", soql)


if __name__ == '__main__':
    unittest.main()
