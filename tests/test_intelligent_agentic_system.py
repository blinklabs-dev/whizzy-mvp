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

    def test_data_source_gathering(self):
        """Test data source gathering"""
        data_sources = [DataSourceType.SALESFORCE, DataSourceType.SNOWFLAKE]

        result = asyncio.run(self.system._gather_data_sources(data_sources, "test query"))

        self.assertIn("salesforce", result)
        self.assertIn("snowflake", result)

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


    def test_dag_executor(self):
        """Test the DAG executor logic."""
        # Mock tools
        mock_sf_tool = AsyncMock()
        mock_sf_tool.run.return_value = {"data": "salesforce_data"}
        mock_snow_tool = AsyncMock()
        mock_snow_tool.run.return_value = {"data": "snowflake_data"}
        self.system.tools = {
            "salesforce": mock_sf_tool,
            "snowflake": mock_snow_tool
        }

        dag = {
            "steps": [
                {"id": 1, "tool": "salesforce", "query": "q1", "dependencies": []},
                {"id": 2, "tool": "snowflake", "query": "q2", "dependencies": [1]}
            ]
        }

        results = asyncio.run(self.system._execute_dag(dag))

        # Assert that both tools were called
        mock_sf_tool.run.assert_called_once_with("q1")
        mock_snow_tool.run.assert_called_once_with("q2")

        # Assert results are stored correctly
        self.assertEqual(results[1], {"data": "salesforce_data"})
        self.assertEqual(results[2], {"data": "snowflake_data"})


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
