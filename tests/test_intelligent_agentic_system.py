#!/usr/bin/env python3
"""
Comprehensive UAT Test Suite for Intelligent Agentic System
Tests functionality, quality, and persona-based scenarios
"""

import unittest
import asyncio
import os
import sys
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from dataclasses import asdict

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.intelligent_agentic_system import (
    EnhancedIntelligentAgenticSystem as IntelligentAgenticSystem, IntentType, PersonaType,
    DataSourceType, IntentAnalysis, AgentResponse, CoffeeBriefing
)
from unittest.mock import mock_open


class TestIntelligentAgenticSystemUAT(unittest.TestCase):
    """Comprehensive UAT tests for Intelligent Agentic System"""

    def setUp(self):
        """Set up test environment"""
        self.env_patcher = patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-openai-key',
            'SALESFORCE_USERNAME': 'test@example.com',
            'SALESFORCE_PASSWORD': 'testpassword',
            'SALESFORCE_SECURITY_TOKEN': 'testtoken',
            'SALESFORCE_DOMAIN': 'login'
        })
        self.mock_os_patcher = patch('app.intelligent_agentic_system.os.listdir', MagicMock(return_value=['vp_sales.txt', 'account_executive.txt', 'cdo.txt', 'data_engineer.txt', 'sales_manager.txt', 'sales_operations.txt', 'customer_success.txt']))

        def open_side_effect(file, mode='r'):
            if 'text_to_soql.json' in file:
                return mock_open(read_data='[{"question": "test", "soql": "SELECT"}]').return_value
            else:
                return mock_open(read_data='mock prompt').return_value

        self.mock_open_patcher = patch('builtins.open', side_effect=open_side_effect)
        self.openai_patcher = patch('app.intelligent_agentic_system.openai.OpenAI')
        self.sf_patcher = patch('app.intelligent_agentic_system.Salesforce')
        self.snow_patcher = patch('app.intelligent_agentic_system.snowflake.connector')


        self.env_patcher.start()
        self.mock_os_patcher.start()
        self.mock_open_patcher.start()
        self.mock_openai = self.openai_patcher.start()
        self.mock_sf = self.sf_patcher.start()
        self.mock_snow = self.snow_patcher.start()

        self.system = IntelligentAgenticSystem()

    def tearDown(self):
        """Clean up after tests"""
        self.env_patcher.stop()
        self.mock_os_patcher.stop()
        self.mock_open_patcher.stop()
        self.openai_patcher.stop()
        self.sf_patcher.stop()
        self.snow_patcher.stop()

    def test_system_initialization(self):
        """Test system initializes correctly"""
        self.assertIsNotNone(self.system)
        self.assertIsNotNone(self.system.openai_client)
        self.assertIsNotNone(self.system.persona_prompts)
        self.assertIsNotNone(self.system.intent_classification_prompt)

    def test_fallback_intent_classification(self):
        """Test fallback intent classification"""
        # Test with simple query
        query = "What's our win rate?"
        result = self.system._fallback_intent_classification(query)

        self.assertEqual(result.primary_intent, IntentType.SALESFORCE_QUERY)
        self.assertEqual(result.confidence, 0.7)

    def test_persona_prompt_loading(self):
        """Test persona prompt loading"""
        prompts = self.system.persona_prompts

        self.assertIn("vp_sales", prompts)
        self.assertIn("account_executive", prompts)
        self.assertIn("cdo", prompts)
        self.assertIn("data_engineer", prompts)

        # Check that the keys exist and the content is a non-empty string
        vp_prompt = prompts["vp_sales"]
        self.assertIsInstance(vp_prompt, str)
        self.assertGreater(len(vp_prompt), 0)

    def test_builder_agent_soql_generation(self):
        """Test that the builder agent correctly generates SOQL."""
        # Arrange
        # Mock the agents in the pipeline
        plan = {
            "primary_intent": IntentType.SALESFORCE_QUERY.value,
            "confidence": 0.95,
            "explanation": "get all accounts"
        }
        self.system._planner_agent = AsyncMock(return_value=plan)
        self.system._builder_agent = AsyncMock(return_value="SELECT Id FROM Account")
        self.system._runner_agent = AsyncMock(return_value={"records": ["foo"]})
        self.system._summarize_data = AsyncMock(return_value="Summary of accounts")

        # This intent object is now only used to get into the right part of orchestrate_response
        intent = IntentAnalysis(
            primary_intent=IntentType.SALESFORCE_QUERY,
            confidence=0.95,
            persona=PersonaType.VP_SALES,
            data_sources=[DataSourceType.SALESFORCE],
            complexity_level="low",
            reasoning_required=False, coffee_briefing=False, dbt_model_required=False, thinking_required=False,
            explanation="get all accounts"
        )

        # Act
        # The orchestrate_response now calls the planner itself, so we don't need to pass the intent
        asyncio.run(self.system.orchestrate_response("get all accounts", intent, "user1"))

        # Assert
        self.system._planner_agent.assert_called_once()
        self.system._builder_agent.assert_called_once()
        # We can even check the plan that was passed to it
        plan_arg = self.system._builder_agent.call_args[0][0]
        self.assertEqual(plan_arg['explanation'], "get all accounts")

    def test_quality_metrics_calculation(self):
        """Test quality metrics calculation"""
        # Add some test conversations
        self.system.conversation_history = [
            {
                "query": "test query",
                "intent": IntentAnalysis(
                    primary_intent=IntentType.SALESFORCE_QUERY,
                    confidence=0.9,
                    persona=PersonaType.VP_SALES,
                    data_sources=[DataSourceType.SALESFORCE],
                    complexity_level="medium",
                    reasoning_required=False,
                    coffee_briefing=False,
                    dbt_model_required=False,
                    thinking_required=False,
                    explanation="test"
                ),
                "response": AgentResponse(
                    response_text="test response",
                    data_sources_used=[DataSourceType.SALESFORCE],
                    reasoning_steps=[],
                    confidence_score=0.9,
                    persona_alignment=0.9,
                    actionability_score=0.8,
                    quality_metrics={}
                ),
                "timestamp": "2025-01-01T00:00:00"
            }
        ]

        metrics = self.system.get_enhanced_quality_metrics()

        self.assertEqual(metrics["total_queries"], 1)
        self.assertEqual(metrics["average_confidence"], 0.9)
        self.assertEqual(metrics["success_rate"], 1.0)
        self.assertIn("salesforce_query", metrics["intent_distribution"])

    def test_orchestration_low_confidence(self):
        """Test the orchestrator's handling of low-confidence intent."""
        low_confidence_intent = IntentAnalysis(
            primary_intent=IntentType.SALESFORCE_QUERY,
            confidence=0.4, # Below the 0.65 threshold
            persona=PersonaType.VP_SALES,
            data_sources=[DataSourceType.SALESFORCE],
            complexity_level="low",
            reasoning_required=False,
            coffee_briefing=False,
            dbt_model_required=False,
            thinking_required=False,
            explanation="Low confidence"
        )

        # Run orchestrator
        response = asyncio.run(self.system.orchestrate_response("some ambiguous query", low_confidence_intent, "user1"))

        # Check that it returns a clarification question
        self.assertIn("I'm not entirely sure", response.response_text)
        self.assertEqual(response.quality_metrics.get("clarification_needed"), 1.0)

    def test_snowflake_initialization(self):
        """Test that the snowflake connection is initialized."""
        # This test runs after setUp, where the system is initialized.
        # We can check if the connect method was called.
        self.mock_snow.connect.assert_called_once()
        # You could also add more specific assertions here about the arguments
        # used in the connect call if you had set more specific env vars.

    def test_orchestration_handles_simple_contact_query(self):
        """Test that a simple query for a contact is routed correctly and returns a summary."""
        # Arrange
        query = "who is my contact on Burlington Textiles Corp of America account"
        plan = {
            "primary_intent": IntentType.SALESFORCE_QUERY.value,
            "confidence": 0.98,
            "explanation": query,
            "data_sources": [DataSourceType.SALESFORCE.value]
        }
        self.system._planner_agent = AsyncMock(return_value=plan)
        self.system._builder_agent = AsyncMock(return_value="SELECT Name, Email FROM Contact WHERE Account.Name LIKE 'Burlington%'")
        self.system._runner_agent = AsyncMock(return_value={"records": [{"Name": "John Doe", "Email": "john.doe@burlington.com"}]})
        self.system._summarize_data = AsyncMock(return_value="The contact is John Doe.")

        intent = IntentAnalysis(primary_intent=IntentType.SALESFORCE_QUERY, confidence=0.98, persona=PersonaType.ACCOUNT_EXECUTIVE, data_sources=[DataSourceType.SALESFORCE], complexity_level="low", reasoning_required=False, coffee_briefing=False, dbt_model_required=False, thinking_required=False, explanation=query)

        # Act
        response = asyncio.run(self.system.orchestrate_response(query, intent, "user1"))

        # Assert
        self.system._builder_agent.assert_called_once()
        self.system._runner_agent.assert_called_once()
        self.system._summarize_data.assert_called_once()
        self.assertEqual(response.response_text, "The contact is John Doe.")

    def test_orchestration_handles_case_query(self):
        """Test that a query for open cases is routed correctly."""
        # Arrange
        query = "what cases are open with Burlington Textiles Corp of America account"
        plan = {
            "primary_intent": IntentType.SALESFORCE_QUERY.value,
            "confidence": 0.97,
            "explanation": query,
            "data_sources": [DataSourceType.SALESFORCE.value]
        }
        # We mock the entire pipeline to test the routing and final output
        self.system._planner_agent = AsyncMock(return_value=plan)
        self.system._builder_agent = AsyncMock(return_value="SELECT CaseNumber, Subject, Status FROM Case WHERE Account.Name LIKE 'Burlington%' AND IsClosed = false")
        self.system._runner_agent = AsyncMock(return_value={"records": [{"CaseNumber": "001", "Subject": "Test Case"}]})
        self.system._summarize_data = AsyncMock(return_value="There is 1 open case.")

        intent = IntentAnalysis(primary_intent=IntentType.SALESFORCE_QUERY, confidence=0.97, persona=PersonaType.ACCOUNT_EXECUTIVE, data_sources=[DataSourceType.SALESFORCE], complexity_level="low", reasoning_required=False, coffee_briefing=False, dbt_model_required=False, thinking_required=False, explanation=query)

        # Act
        response = asyncio.run(self.system.orchestrate_response(query, intent, "user1"))

        # Assert
        # This test currently will pass because we are mocking the whole pipeline.
        # It serves as a good regression test for the orchestration path.
        # In the next step, we will improve the *real* builder and can write a more
        # targeted integration test if needed.
        self.assertEqual(response.response_text, "There is 1 open case.")


class TestQualityEvaluation(unittest.TestCase):
    """Test quality evaluation and assessment"""

    def setUp(self):
        """Set up test environment"""
        self.env_patcher = patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-openai-key',
            'SALESFORCE_USERNAME': 'test@example.com',
            'SALESFORCE_PASSWORD': 'testpassword',
            'SALESFORCE_SECURITY_TOKEN': 'testtoken',
            'SALESFORCE_DOMAIN': 'login'
        })
        self.mock_os_patcher = patch('app.intelligent_agentic_system.os.listdir', MagicMock(return_value=[]))
        def open_side_effect(file, mode='r'):
            if 'text_to_soql.json' in file:
                return mock_open(read_data='[{"question": "test", "soql": "SELECT"}]').return_value
            else:
                return mock_open(read_data='mock prompt').return_value
        self.mock_open_patcher = patch('builtins.open', side_effect=open_side_effect)
        self.openai_patcher = patch('app.intelligent_agentic_system.openai.OpenAI')
        self.sf_patcher = patch('app.intelligent_agentic_system.Salesforce')

        self.env_patcher.start()
        self.mock_os_patcher.start()
        self.mock_open_patcher.start()
        self.openai_patcher.start()
        self.sf_patcher.start()

        self.system = IntelligentAgenticSystem()

    def tearDown(self):
        """Clean up after tests"""
        self.env_patcher.stop()
        self.mock_os_patcher.stop()
        self.mock_open_patcher.stop()
        self.openai_patcher.stop()
        self.sf_patcher.stop()

    def test_response_quality_metrics(self):
        """Test response quality metrics calculation"""
        response = AgentResponse(
            response_text="Test response with insights and recommendations",
            data_sources_used=[DataSourceType.SALESFORCE],
            reasoning_steps=["Step 1", "Step 2"],
            confidence_score=0.9,
            persona_alignment=0.95,
            actionability_score=0.85,
            quality_metrics={"accuracy": 0.9, "relevance": 0.95}
        )

        # Test quality metrics
        self.assertGreater(response.confidence_score, 0.8)
        self.assertGreater(response.persona_alignment, 0.9)
        self.assertGreater(response.actionability_score, 0.8)
        self.assertIn("accuracy", response.quality_metrics)
        self.assertIn("relevance", response.quality_metrics)

    def test_error_response_quality(self):
        """Test error response quality"""
        error_response = self.system._create_error_response("Test error")

        self.assertEqual(error_response.confidence_score, 0.0)
        self.assertEqual(error_response.persona_alignment, 0.0)
        self.assertEqual(error_response.actionability_score, 0.0)
        self.assertIn("Error", error_response.response_text)

    def test_coffee_briefing_quality(self):
        """Test coffee briefing quality assessment"""
        briefing = CoffeeBriefing(
            persona=PersonaType.VP_SALES,
            frequency="daily",
            key_metrics=["Win Rate", "Pipeline Value"],
            insights=["Pipeline health is strong"],
            action_items=["Review top opportunities"],
            risks=["Pipeline concentration"],
            opportunities=["Account expansion"]
        )

        # Test briefing completeness
        self.assertIsNotNone(briefing.key_metrics)
        self.assertIsNotNone(briefing.insights)
        self.assertIsNotNone(briefing.action_items)
        self.assertIsNotNone(briefing.risks)
        self.assertIsNotNone(briefing.opportunities)

        # Test formatting
        formatted = self.system._format_coffee_briefing(briefing)
        self.assertIn("Coffee Briefing", formatted)
        self.assertIn("Key Metrics", formatted)
        self.assertIn("Action Items", formatted)


if __name__ == '__main__':
    unittest.main()
