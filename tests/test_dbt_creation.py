import unittest
import asyncio
import os
import sys
from unittest.mock import patch, MagicMock, AsyncMock
from concurrent.futures import ThreadPoolExecutor

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.intelligent_agentic_system import (
    EnhancedIntelligentAgenticSystem, IntentAnalysis, IntentType, PersonaType, DataSourceType
)

class TestDbtCreation(unittest.TestCase):

    def setUp(self):
        """Set up a mock EnhancedIntelligentAgenticSystem for each test."""
        # We patch the __init__ to avoid real API calls and file loading during tests
        # We patch __init__ but then create a real executor
        with patch.object(EnhancedIntelligentAgenticSystem, "__init__", lambda x: None):
            self.system = EnhancedIntelligentAgenticSystem()
            # Manually set the attributes that would be set in __init__
            self.system.executor = ThreadPoolExecutor(max_workers=1)
            self.system.openai_client = MagicMock()
            self.system.extract_dbt_requirements_prompt = "extract: {query}"
            self.system.generate_dbt_model_prompt = "generate: {requirements}"

    @patch('app.intelligent_agentic_system.json.loads')
    def test_extract_dbt_requirements_success(self, mock_json_loads):
        """Test that dbt requirement extraction calls the LLM correctly."""
        # Arrange
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = '{"model_name": "test_model"}'
        self.system.openai_client.chat.completions.create.return_value = mock_completion
        mock_json_loads.return_value = {"model_name": "test_model"}

        # Act
        query = "create a model for users"
        requirements = asyncio.run(self.system._extract_dbt_requirements(query))

        # Assert
        self.system.openai_client.chat.completions.create.assert_called_once()
        self.assertEqual(requirements, {"model_name": "test_model"})

    @patch('app.intelligent_agentic_system.json.loads')
    def test_generate_dbt_model_success(self, mock_json_loads):
        """Test that dbt model generation calls the LLM correctly."""
        # Arrange
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = '{"sql": "SELECT 1", "yaml": "version: 2"}'
        self.system.openai_client.chat.completions.create.return_value = mock_completion
        mock_json_loads.return_value = {"sql": "SELECT 1", "yaml": "version: 2"}

        # Act
        requirements = {"model_name": "test_model", "description": "a model"}
        model = asyncio.run(self.system._generate_dbt_model(requirements))

        # Assert
        self.system.openai_client.chat.completions.create.assert_called_once()
        self.assertEqual(model['sql'], "SELECT 1")
        self.assertEqual(model['yaml'], "version: 2")
        self.assertEqual(model['name'], "test_model")

    def test_handle_dbt_model_request(self):
        """Test the main handler for dbt model requests."""
        # Arrange
        self.system._extract_dbt_requirements = AsyncMock(return_value={"model_name": "my_new_model"})
        self.system._generate_dbt_model = AsyncMock(return_value={
            "name": "my_new_model",
            "sql": "SELECT * FROM source",
            "yaml": "version: 2"
        })
        self.system._create_error_response = MagicMock()

        intent = IntentAnalysis(
            primary_intent=IntentType.DBT_MODEL,
            confidence=0.95,
            persona=PersonaType.CDO,
            data_sources=[],
            complexity_level="high",
            reasoning_required=True,
            coffee_briefing=False,
            dbt_model_required=True,
            thinking_required=False,
            explanation="test"
        )

        # Act
        response = asyncio.run(self.system._handle_dbt_model_request("test query", intent, {}))

        # Assert
        self.system._extract_dbt_requirements.assert_called_once_with("test query")
        self.system._generate_dbt_model.assert_called_once_with({"model_name": "my_new_model"})
        self.assertIn("I have created the following files", response.response_text)
        self.assertIn("analytics/models/marts/my_new_model.sql", response.response_text)
        self.assertIn("analytics/models/marts/my_new_model.yml", response.response_text)
        self.assertIn("SELECT * FROM source", response.response_text)

if __name__ == '__main__':
    unittest.main()
