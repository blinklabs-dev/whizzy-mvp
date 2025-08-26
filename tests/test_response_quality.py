#!/usr/bin/env python3
"""
Comprehensive Response Quality Test Suite
Tests the bot's response quality across different query types and scenarios.
"""

import unittest
from unittest.mock import Mock, patch
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.whizzy_bot import WhizzyBot


class TestResponseQuality(unittest.TestCase):
    """Test response quality across different scenarios"""

    def setUp(self):
        """Set up test environment"""
        with patch.dict(os.environ, {
            'SLACK_APP_TOKEN': 'xapp-test-token',
            'SLACK_BOT_TOKEN': 'xoxb-test-token',
            'SALESFORCE_USERNAME': 'test@example.com',
            'SALESFORCE_PASSWORD': 'testpassword',
            'SALESFORCE_SECURITY_TOKEN': 'testtoken',
            'SALESFORCE_DOMAIN': 'login'
        }):
            self.bot = WhizzyBot()
            
        # Mock Salesforce client
        self.bot.salesforce_client = Mock()

    def test_fast_path_quality(self):
        """Test quality of fast path responses"""
        test_cases = [
            ("help", "Whizzy Bot - Salesforce Analytics"),
            ("what can you do", "Whizzy Bot - Salesforce Analytics"),
            ("hello", "Hello! I'm your Salesforce analytics assistant"),
            ("hi", "Hello! I'm your Salesforce analytics assistant"),
            ("status", "I'm up and running! Ready to help"),
            ("are you working", "I'm up and running! Ready to help"),
        ]
        
        for query, expected_content in test_cases:
            with self.subTest(query=query):
                response = self.bot._handle_static_commands(query)
                self.assertIsNotNone(response, f"Response should not be None for query: {query}")
                self.assertIn(expected_content, response, f"Response should contain '{expected_content}' for query: {query}")
                # Check that response is properly formatted (without expecting the prefix since individual methods don't add it)
                self.assertIsInstance(response, str, f"Response should be a string for query: {query}")
                self.assertGreater(len(response), 50, f"Response should be substantial for query: {query}")

    def test_fallback_response_quality(self):
        """Test quality of fallback responses"""
        
        # Test win rate specifically
        self.bot.salesforce_client.query.side_effect = [
            {'records': [{'total': 100}]},
            {'records': [{'won': 25}]},
            {'records': [{'lost': 15}]}
        ]
        
        response = self.bot._generate_fallback_response("win rate")
        self.assertIsNotNone(response, "Response should not be None for win rate query")
        self.assertIn("Win Rate Analysis", response, "Response should contain 'Win Rate Analysis' for win rate query")
        self.assertIsInstance(response, str, "Response should be a string for win rate query")
        self.assertGreater(len(response), 50, "Response should be substantial for win rate query")
        
        # Test pipeline specifically
        self.bot.salesforce_client.query.reset_mock()
        self.bot.salesforce_client.query.side_effect = None  # Clear side_effect
        self.bot.salesforce_client.query.return_value = {
            'records': [
                {'StageName': 'Prospecting', 'total_count': 10, 'total_amount': 100000},
                {'StageName': 'Qualification', 'total_count': 5, 'total_amount': 50000}
            ]
        }
        
        response = self.bot._generate_fallback_response("pipeline")
        self.assertIsNotNone(response, "Response should not be None for pipeline query")
        self.assertIn("Pipeline Overview", response, "Response should contain 'Pipeline Overview' for pipeline query")
        self.assertIsInstance(response, str, "Response should be a string for pipeline query")
        self.assertGreater(len(response), 50, "Response should be substantial for pipeline query")

    def test_response_formatting_quality(self):
        """Test response formatting quality"""
        # Test help response formatting
        response = self.bot._get_help_response()
        
        # Check for proper formatting elements
        self.assertIn("🤖 **Whizzy Bot - Salesforce Analytics**", response)
        self.assertIn("📊 **Data Queries:**", response)
        self.assertIn("📋 **Strategic Insights:**", response)
        self.assertIn("💡 **Examples:**", response)
        self.assertIn("🎯 **I provide:**", response)
        
        # Check for emojis and structure
        self.assertIn("📊", response)
        self.assertIn("📋", response)
        self.assertIn("💡", response)
        self.assertIn("🎯", response)
        self.assertIn("🚀", response)

    def test_win_rate_analysis_quality(self):
        """Test win rate analysis response quality"""
        # Mock Salesforce data
        self.bot.salesforce_client.query.side_effect = [
            {'records': [{'total': 100}]},
            {'records': [{'won': 25}]},
            {'records': [{'lost': 15}]}
        ]
        
        response = self.bot._get_win_rate_analysis()
        
        # Check for required sections
        self.assertIn("🎯 **Win Rate Analysis**", response)
        self.assertIn("📊 **Overall Performance:**", response)
        self.assertIn("💡 **Insights:**", response)
        self.assertIn("🎯 **Recommendations:**", response)
        
        # Check for data
        self.assertIn("Win Rate: 25.0%", response)
        self.assertIn("Total Opportunities: 100", response)
        self.assertIn("Won: 25", response)
        self.assertIn("Lost: 15", response)

    def test_pipeline_overview_quality(self):
        """Test pipeline overview response quality"""
        # Mock Salesforce data
        mock_records = [
            {'StageName': 'Prospecting', 'total_count': 10, 'total_amount': 100000},
            {'StageName': 'Qualification', 'total_count': 5, 'total_amount': 50000}
        ]
        self.bot.salesforce_client.query.return_value = {'records': mock_records}
        
        response = self.bot._get_pipeline_overview()
        
        # Check for required sections
        self.assertIn("📊 **Pipeline Overview**", response)
        self.assertIn("💰 **Total Pipeline Value**:", response)
        self.assertIn("📈 **Total Opportunities**:", response)
        self.assertIn("💡 **Key Insights:**", response)
        self.assertIn("🎯 **Strategic Actions:**", response)
        
        # Check for data
        self.assertIn("$150,000", response)  # Total value
        self.assertIn("15", response)  # Total opportunities
        self.assertIn("Prospecting", response)
        self.assertIn("Qualification", response)

    def test_executive_briefing_quality(self):
        """Test executive briefing response quality"""
        # Mock Salesforce data
        self.bot.salesforce_client.query.side_effect = [
            {'records': [{'total': 50, 'total_value': 500000}]},
            {'records': [{'total': 100, 'won': 25}]}
        ]
        
        response = self.bot._get_executive_briefing()
        
        # Check for required sections
        self.assertIn("📋 **Executive Briefing**", response)
        self.assertIn("📊 **Key Metrics:**", response)
        self.assertIn("🎯 **Strategic Insights:**", response)
        self.assertIn("📈 **Focus Areas:**", response)
        self.assertIn("🚀 **Action Items:**", response)
        self.assertIn("💡 **Risk Assessment:**", response)
        self.assertIn("🎯 **Next Steps:**", response)
        
        # Check for data
        self.assertIn("Open Opportunities**: 50", response)
        self.assertIn("Pipeline Value**: $500,000", response)
        self.assertIn("Overall Win Rate**: 25.0%", response)

    def test_error_handling_quality(self):
        """Test error handling response quality"""
        # Test with no Salesforce client
        self.bot.salesforce_client = None
        response = self.bot._generate_fallback_response("What's our win rate?")
        
        self.assertIn("Salesforce connection not available", response)
        self.assertIn("🤖 **Whizzy**:", response)
        
        # Test with Salesforce query error
        self.bot.salesforce_client = Mock()
        self.bot.salesforce_client.query.side_effect = Exception("Connection error")
        response = self.bot._generate_fallback_response("What's our win rate?")
        
        self.assertIn("Unable to retrieve win rate data", response)
        self.assertIn("🤖 **Whizzy**:", response)

    def test_subscription_commands_quality(self):
        """Test subscription command response quality"""
        # Mock web client
        self.bot.web_client = Mock()
        self.bot.web_client.conversations_open.return_value = {'channel': {'id': 'D123'}}
        
        # Test subscribe command
        response = self.bot._handle_subscribe("U123", "subscribe daily vp")
        self.assertIn("✅ You've been subscribed to **daily VP of Sales** briefings!", response)
        
        # Test unsubscribe command
        response = self.bot._handle_unsubscribe("U123")
        self.assertIn("You have been successfully unsubscribed from all briefings.", response)
        
        # Test list subscriptions
        response = self.bot._handle_list_subscriptions("U123")
        self.assertIn("You are not subscribed to any briefings.", response)

    def test_response_completeness(self):
        """Test that responses are complete and actionable"""
        # Test win rate response completeness
        self.bot.salesforce_client.query.side_effect = [
            {'records': [{'total': 100}]},
            {'records': [{'won': 25}]},
            {'records': [{'lost': 15}]}
        ]
        
        response = self.bot._get_win_rate_analysis()
        
        # Check for completeness indicators
        self.assertGreater(len(response), 200, "Response should be substantial")
        self.assertIn("•", response, "Response should have bullet points")
        self.assertIn(":", response, "Response should have structured sections")
        
        # Check for actionable content
        self.assertIn("Focus on", response, "Response should have actionable recommendations")
        self.assertIn("Review", response, "Response should have actionable recommendations")
        self.assertIn("Monitor", response, "Response should have actionable recommendations")

    def test_response_consistency(self):
        """Test response consistency across similar queries"""
        
        # Test multiple win rate queries
        queries = ["What's our win rate?", "Show me the win rate", "Win rate analysis"]
        responses = []
        
        for query in queries:
            # Mock Salesforce data for each query
            self.bot.salesforce_client.query.side_effect = [
                {'records': [{'total': 100}]},
                {'records': [{'won': 25}]},
                {'records': [{'lost': 15}]}
            ]
            response = self.bot._generate_fallback_response(query)
            responses.append(response)
        
        # All should contain the same key elements
        for response in responses:
            self.assertIn("Win Rate Analysis", response)
            self.assertIn("25.0%", response)
            # Check that response is properly formatted (without expecting the prefix since individual methods don't add it)
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 50)

    def test_performance_under_load(self):
        """Test performance under multiple queries"""
        # Mock Salesforce data
        self.bot.salesforce_client.query.side_effect = [
            {'records': [{'total': 100}]},
            {'records': [{'won': 25}]},
            {'records': [{'lost': 15}]}
        ]
        
        # Test multiple queries in sequence
        queries = [
            "help",
            "What's our win rate?",
            "Show me the pipeline",
            "Executive briefing",
            "Top accounts"
        ]
        
        responses = []
        for query in queries:
            if query == "help":
                response = self.bot._handle_static_commands(query)
            else:
                response = self.bot._generate_fallback_response(query)
            responses.append(response)
        
        # All responses should be valid
        for i, response in enumerate(responses):
            self.assertIsNotNone(response, f"Response {i} should not be None")
            self.assertIsInstance(response, str, f"Response {i} should be a string")
            self.assertGreater(len(response), 50, f"Response {i} should be substantial")


if __name__ == '__main__':
    unittest.main()
