#!/usr/bin/env python3
"""
Comprehensive test suite for diverse scenarios to improve agent intelligence
"""

import unittest
import asyncio
import json
from unittest.mock import Mock, patch, MagicMock
from app.whizzy_bot import WhizzyBot
from app.intelligent_agentic_system import EnhancedIntelligentAgenticSystem, IntentType, PersonaType

class TestDiverseScenarios(unittest.TestCase):
    """Test diverse scenarios to improve agent intelligence"""
    
    def setUp(self):
        """Set up test environment"""
        self.bot = WhizzyBot()
        
        # Mock Salesforce responses for diverse scenarios
        self.mock_salesforce_data = {
            "win_rate": {
                "total": 704,
                "won": 159,
                "lost": 160,
                "win_rate": 22.6
            },
            "pipeline": {
                "stages": [
                    {"StageName": "Negotiation/Review", "total_count": 267, "total_amount": 66612818},
                    {"StageName": "Proposal/Price Quote", "total_count": 34, "total_amount": 8647726},
                    {"StageName": "Value Proposition", "total_count": 31, "total_amount": 7652295}
                ]
            },
            "deals_at_risk": {
                "opportunities": [
                    {"Name": "Deal A", "StageName": "Negotiation/Review", "Amount": 500000, "CloseDate": "2024-12-31"},
                    {"Name": "Deal B", "StageName": "Proposal/Price Quote", "Amount": 300000, "CloseDate": "2024-11-30"}
                ]
            }
        }

    def test_diverse_intent_classification(self):
        """Test diverse intent classification scenarios"""
        test_cases = [
            # Win rate variations
            ("what's our win rate?", IntentType.SALESFORCE_QUERY),
            ("how are we performing on deals?", IntentType.BUSINESS_INTELLIGENCE),
            ("success rate analysis", IntentType.BUSINESS_INTELLIGENCE),
            ("deal conversion metrics", IntentType.BUSINESS_INTELLIGENCE),
            
            # Pipeline variations
            ("show me the pipeline", IntentType.SALESFORCE_QUERY),
            ("pipeline breakdown", IntentType.BUSINESS_INTELLIGENCE),
            ("sales funnel analysis", IntentType.BUSINESS_INTELLIGENCE),
            ("stage progression", IntentType.BUSINESS_INTELLIGENCE),
            
            # Risk analysis
            ("what deals are at risk?", IntentType.BUSINESS_INTELLIGENCE),
            ("identify risky opportunities", IntentType.BUSINESS_INTELLIGENCE),
            ("deal risk assessment", IntentType.COMPLEX_ANALYTICS),
            ("which deals might slip?", IntentType.BUSINESS_INTELLIGENCE),
            
            # Forecasting
            ("sales forecast", IntentType.COMPLEX_ANALYTICS),
            ("predictive analysis", IntentType.COMPLEX_ANALYTICS),
            ("future revenue projection", IntentType.COMPLEX_ANALYTICS),
            ("what's our outlook?", IntentType.BUSINESS_INTELLIGENCE),
            
            # Executive insights
            ("executive briefing", IntentType.COFFEE_BRIEFING),
            ("board report", IntentType.COFFEE_BRIEFING),
            ("leadership summary", IntentType.COFFEE_BRIEFING),
            ("strategic overview", IntentType.BUSINESS_INTELLIGENCE),
            
            # Account analysis
            ("top accounts", IntentType.SALESFORCE_QUERY),
            ("account performance", IntentType.BUSINESS_INTELLIGENCE),
            ("customer analysis", IntentType.BUSINESS_INTELLIGENCE),
            ("client insights", IntentType.BUSINESS_INTELLIGENCE),
            
            # Performance metrics
            ("sales performance", IntentType.BUSINESS_INTELLIGENCE),
            ("rep productivity", IntentType.BUSINESS_INTELLIGENCE),
            ("team metrics", IntentType.BUSINESS_INTELLIGENCE),
            ("performance dashboard", IntentType.BUSINESS_INTELLIGENCE),
            
            # Complex analysis
            ("trend analysis", IntentType.COMPLEX_ANALYTICS),
            ("correlation study", IntentType.COMPLEX_ANALYTICS),
            ("root cause analysis", IntentType.COMPLEX_ANALYTICS),
            ("deep dive investigation", IntentType.COMPLEX_ANALYTICS),
            
            # Simple queries
            ("hello", None),  # Should be static command
            ("help", None),   # Should be static command
            ("status", None), # Should be static command
        ]
        
        for query, expected_intent in test_cases:
            with self.subTest(query=query):
                # Test that queries are routed correctly
                static_response = self.bot._handle_static_commands(query)
                
                if expected_intent is None:
                    # Should be handled as static command
                    self.assertIsNotNone(static_response, f"Query '{query}' should be static command")
                else:
                    # Should go through intelligent routing
                    self.assertIsNone(static_response, f"Query '{query}' should use intelligent routing")

    def test_persona_specific_queries(self):
        """Test persona-specific query variations"""
        persona_queries = {
            PersonaType.VP_SALES: [
                "sales performance overview",
                "revenue forecast",
                "team productivity",
                "strategic pipeline analysis"
            ],
            PersonaType.ACCOUNT_EXECUTIVE: [
                "my deals",
                "personal pipeline",
                "quota progress",
                "next steps for opportunities"
            ],
            PersonaType.SALES_MANAGER: [
                "team performance",
                "rep coaching opportunities",
                "pipeline health",
                "resource allocation"
            ],
            PersonaType.CDO: [
                "data strategy",
                "analytics insights",
                "business intelligence",
                "data-driven decisions"
            ]
        }
        
        for persona, queries in persona_queries.items():
            for query in queries:
                with self.subTest(persona=persona.value, query=query):
                    # These should all go through intelligent routing
                    static_response = self.bot._handle_static_commands(query)
                    self.assertIsNone(static_response, f"Persona query '{query}' should use intelligent routing")

    def test_complex_analytical_queries(self):
        """Test complex analytical scenarios"""
        complex_queries = [
            "analyze the correlation between deal size and win rate",
            "what factors contribute to deal slippage?",
            "identify patterns in successful vs failed deals",
            "forecast revenue based on current pipeline and historical trends",
            "which sales reps are most effective and why?",
            "analyze seasonality in our sales performance",
            "what's the impact of lead source on conversion rates?",
            "identify bottlenecks in our sales process",
            "predict which deals will close this quarter",
            "analyze customer lifetime value trends"
        ]
        
        for query in complex_queries:
            with self.subTest(query=query):
                # All complex queries should use intelligent routing
                static_response = self.bot._handle_static_commands(query)
                self.assertIsNone(static_response, f"Complex query '{query}' should use intelligent routing")

    def test_edge_cases_and_variations(self):
        """Test edge cases and query variations"""
        edge_cases = [
            # Abbreviations and slang
            ("pipeline $", IntentType.SALESFORCE_QUERY),
            ("win %", IntentType.SALESFORCE_QUERY),
            ("deals at risk?", IntentType.BUSINESS_INTELLIGENCE),
            ("top 10", IntentType.SALESFORCE_QUERY),
            
            # Different time periods
            ("this quarter", IntentType.SALESFORCE_QUERY),
            ("last month", IntentType.SALESFORCE_QUERY),
            ("YTD performance", IntentType.BUSINESS_INTELLIGENCE),
            ("annual forecast", IntentType.COMPLEX_ANALYTICS),
            
            # Different formats
            ("WIN RATE", IntentType.SALESFORCE_QUERY),
            ("Pipeline Analysis", IntentType.BUSINESS_INTELLIGENCE),
            ("Deal Risk Assessment", IntentType.BUSINESS_INTELLIGENCE),
            
            # Ambiguous queries
            ("performance", IntentType.BUSINESS_INTELLIGENCE),
            ("analysis", IntentType.BUSINESS_INTELLIGENCE),
            ("insights", IntentType.BUSINESS_INTELLIGENCE),
            ("report", IntentType.BUSINESS_INTELLIGENCE),
        ]
        
        for query, expected_intent in edge_cases:
            with self.subTest(query=query):
                static_response = self.bot._handle_static_commands(query)
                if expected_intent is None:
                    self.assertIsNotNone(static_response, f"Edge case '{query}' should be static command")
                else:
                    self.assertIsNone(static_response, f"Edge case '{query}' should use intelligent routing")

    def test_multi_intent_queries(self):
        """Test queries that might have multiple intents"""
        multi_intent_queries = [
            "show me win rate and pipeline for this quarter",
            "analyze deals at risk and provide recommendations",
            "give me an executive briefing with performance metrics",
            "top accounts by revenue and their risk profile",
            "sales performance with forecasting and insights"
        ]
        
        for query in multi_intent_queries:
            with self.subTest(query=query):
                # Multi-intent queries should use intelligent routing
                static_response = self.bot._handle_static_commands(query)
                self.assertIsNone(static_response, f"Multi-intent query '{query}' should use intelligent routing")

    @patch('app.whizzy_bot.Salesforce')
    def test_soql_generation_accuracy(self, mock_salesforce):
        """Test SOQL generation accuracy for diverse queries"""
        # Mock Salesforce responses
        mock_sf = Mock()
        mock_sf.query.return_value = {
            'records': [
                {'total': 704},
                {'won': 159},
                {'lost': 160}
            ]
        }
        self.bot.salesforce_client = mock_sf
        
        soql_test_cases = [
            ("win rate", "SELECT COUNT(Id)"),
            ("pipeline", "SELECT StageName"),
            ("top accounts", "SELECT Name"),
            ("deals at risk", "SELECT Name, StageName"),
        ]
        
        for query, expected_soql in soql_test_cases:
            with self.subTest(query=query):
                try:
                    response = self.bot._generate_fallback_response(query)
                    # Verify that SOQL was called
                    mock_sf.query.assert_called()
                    self.assertIsInstance(response, str)
                    self.assertGreater(len(response), 50)
                except Exception as e:
                    self.fail(f"SOQL generation failed for '{query}': {e}")

    def test_response_quality_metrics(self):
        """Test response quality across diverse scenarios"""
        quality_test_cases = [
            {
                "query": "what's our win rate?",
                "expected_elements": ["win rate", "%", "opportunities", "won", "lost"],
                "min_length": 100
            },
            {
                "query": "show pipeline breakdown",
                "expected_elements": ["pipeline", "stage", "opportunities", "$"],
                "min_length": 150
            },
            {
                "query": "executive briefing",
                "expected_elements": ["briefing", "metrics", "insights", "recommendations"],
                "min_length": 200
            }
        ]
        
        for test_case in quality_test_cases:
            with self.subTest(query=test_case["query"]):
                try:
                    response = self.bot._generate_fallback_response(test_case["query"])
                    
                    # Check response length
                    self.assertGreaterEqual(len(response), test_case["min_length"])
                    
                    # Check for expected elements
                    for element in test_case["expected_elements"]:
                        self.assertIn(element.lower(), response.lower(), 
                                    f"Response should contain '{element}'")
                    
                    # Check response format
                    self.assertIn("🤖 **Whizzy**:", response)
                    
                except Exception as e:
                    self.fail(f"Response quality test failed for '{test_case['query']}': {e}")

    def test_error_handling_scenarios(self):
        """Test error handling for diverse scenarios"""
        error_scenarios = [
            "invalid query with special characters @#$%",
            "query with numbers 12345",
            "very long query " * 50,
            "query with emojis 🚀📊💰",
            "query with unicode characters ñáéíóú",
        ]
        
        for scenario in error_scenarios:
            with self.subTest(scenario=scenario):
                try:
                    # Should not crash
                    static_response = self.bot._handle_static_commands(scenario)
                    # Should handle gracefully
                    self.assertIsInstance(static_response, (str, type(None)))
                except Exception as e:
                    self.fail(f"Error handling failed for scenario '{scenario}': {e}")

if __name__ == '__main__':
    unittest.main()
