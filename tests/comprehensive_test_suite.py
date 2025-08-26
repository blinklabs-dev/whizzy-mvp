#!/usr/bin/env python3
"""
Comprehensive Test Suite - 10+ test cases per spectrum
"""

import unittest
import asyncio
import json
from unittest.mock import Mock, patch, MagicMock
from app.whizzy_bot import WhizzyBot
from app.intelligent_agentic_system import EnhancedIntelligentAgenticSystem, IntentType, PersonaType

class ComprehensiveTestSuite(unittest.TestCase):
    """Comprehensive test suite with 10+ test cases per spectrum"""
    
    def setUp(self):
        """Set up test environment"""
        self.bot = WhizzyBot()

    def test_spectrum_1_static_commands(self):
        """Test Spectrum 1: Static Commands (10+ test cases)"""
        print("\n🧪 Testing Spectrum 1: Static Commands")
        
        static_test_cases = [
            # Basic greetings
            ("hello", True, "Basic greeting"),
            ("hi", True, "Basic greeting"),
            ("hey", True, "Basic greeting"),
            ("good morning", True, "Time-based greeting"),
            ("good afternoon", True, "Time-based greeting"),
            ("good evening", True, "Time-based greeting"),
            
            # Help requests
            ("help", True, "Help request"),
            ("what can you do", True, "Capability inquiry"),
            ("what all can you do", True, "Capability inquiry"),
            ("capabilities", True, "Capability inquiry"),
            ("features", True, "Feature inquiry"),
            ("commands", True, "Command list request"),
            ("how to use", True, "Usage inquiry"),
            ("what do you do", True, "Function inquiry"),
            
            # Status checks
            ("status", True, "Status check"),
            ("are you working", True, "Status check"),
            ("bot status", True, "Status check"),
            ("are you online", True, "Status check"),
            ("are you alive", True, "Status check"),
            
            # Subscription commands
            ("subscribe", True, "Subscription command"),
            ("unsubscribe", True, "Unsubscription command"),
            ("list subscriptions", True, "Subscription list"),
        ]
        
        passed = 0
        total = len(static_test_cases)
        
        for query, should_be_static, description in static_test_cases:
            with self.subTest(query=query):
                try:
                    static_response = self.bot._handle_static_commands(query)
                    is_static = static_response is not None
                    
                    if is_static == should_be_static:
                        passed += 1
                        print(f"  ✅ PASS: {query} -> {'Static' if is_static else 'Intelligent'}")
                    else:
                        print(f"  ❌ FAIL: {query} -> {'Static' if is_static else 'Intelligent'} (Expected: {'Static' if should_be_static else 'Intelligent'})")
                        
                except Exception as e:
                    print(f"  ❌ ERROR: {query} - {e}")
        
        print(f"  📊 Static Commands: {passed}/{total} passed ({passed/total:.1%})")
        self.assertGreaterEqual(passed/total, 0.9, f"Static command accuracy should be >= 90%, got {passed/total:.1%}")

    def test_spectrum_2_salesforce_queries(self):
        """Test Spectrum 2: Salesforce Queries (10+ test cases)"""
        print("\n🧪 Testing Spectrum 2: Salesforce Queries")
        
        sf_test_cases = [
            # Win rate variations
            ("what's our win rate?", False, "Win rate query"),
            ("show me the win rate", False, "Win rate query"),
            ("win rate analysis", False, "Win rate analysis"),
            ("how are we performing on deals", False, "Performance query"),
            ("success rate", False, "Success rate query"),
            ("deal conversion rate", False, "Conversion rate query"),
            ("win percentage", False, "Win percentage query"),
            ("deal success metrics", False, "Success metrics query"),
            ("conversion analysis", False, "Conversion analysis"),
            ("win rate this quarter", False, "Time-based win rate"),
            ("win rate last month", False, "Time-based win rate"),
            ("win rate YTD", False, "Time-based win rate"),
            
            # Pipeline variations
            ("show me the pipeline", False, "Pipeline query"),
            ("pipeline breakdown", False, "Pipeline breakdown"),
            ("pipeline overview", False, "Pipeline overview"),
            ("sales funnel", False, "Sales funnel query"),
            ("pipeline stages", False, "Pipeline stages"),
            ("pipeline $ by stage", False, "Pipeline with symbols"),
            ("pipeline value", False, "Pipeline value"),
            ("pipeline status", False, "Pipeline status"),
            ("pipeline health", False, "Pipeline health"),
            ("pipeline analysis", False, "Pipeline analysis"),
            ("pipeline this quarter", False, "Time-based pipeline"),
            
            # Account variations
            ("top accounts", False, "Top accounts query"),
            ("accounts by revenue", False, "Accounts by revenue"),
            ("top 10 accounts", False, "Top 10 accounts"),
            ("customer accounts", False, "Customer accounts"),
            ("account performance", False, "Account performance"),
            ("account list", False, "Account list"),
            ("account overview", False, "Account overview"),
            ("account analysis", False, "Account analysis"),
            ("account revenue", False, "Account revenue"),
            ("account ranking", False, "Account ranking"),
        ]
        
        passed = 0
        total = len(sf_test_cases)
        
        for query, should_be_static, description in sf_test_cases:
            with self.subTest(query=query):
                try:
                    static_response = self.bot._handle_static_commands(query)
                    is_static = static_response is not None
                    
                    if is_static == should_be_static:
                        passed += 1
                        print(f"  ✅ PASS: {query} -> {'Static' if is_static else 'Intelligent'}")
                    else:
                        print(f"  ❌ FAIL: {query} -> {'Static' if is_static else 'Intelligent'} (Expected: {'Static' if should_be_static else 'Intelligent'})")
                        
                except Exception as e:
                    print(f"  ❌ ERROR: {query} - {e}")
        
        print(f"  📊 Salesforce Queries: {passed}/{total} passed ({passed/total:.1%})")
        self.assertGreaterEqual(passed/total, 0.9, f"Salesforce query accuracy should be >= 90%, got {passed/total:.1%}")

    def test_spectrum_3_business_intelligence(self):
        """Test Spectrum 3: Business Intelligence (10+ test cases)"""
        print("\n🧪 Testing Spectrum 3: Business Intelligence")
        
        bi_test_cases = [
            # Performance analysis
            ("performance metrics", False, "Performance metrics"),
            ("sales performance", False, "Sales performance"),
            ("performance analysis", False, "Performance analysis"),
            ("performance dashboard", False, "Performance dashboard"),
            ("performance insights", False, "Performance insights"),
            ("performance trends", False, "Performance trends"),
            ("performance report", False, "Performance report"),
            ("performance overview", False, "Performance overview"),
            ("performance summary", False, "Performance summary"),
            ("performance data", False, "Performance data"),
            
            # Risk analysis
            ("deals at risk", False, "Deals at risk"),
            ("risk analysis", False, "Risk analysis"),
            ("risk assessment", False, "Risk assessment"),
            ("risk factors", False, "Risk factors"),
            ("risk evaluation", False, "Risk evaluation"),
            ("risk identification", False, "Risk identification"),
            ("risk management", False, "Risk management"),
            ("risk profile", False, "Risk profile"),
            ("risk scoring", False, "Risk scoring"),
            ("risk trends", False, "Risk trends"),
            
            # Team analysis
            ("team performance", False, "Team performance"),
            ("team productivity", False, "Team productivity"),
            ("team metrics", False, "Team metrics"),
            ("team analysis", False, "Team analysis"),
            ("team insights", False, "Team insights"),
            ("team effectiveness", False, "Team effectiveness"),
            ("team efficiency", False, "Team efficiency"),
            ("team comparison", False, "Team comparison"),
            ("team ranking", False, "Team ranking"),
            ("team trends", False, "Team trends"),
        ]
        
        passed = 0
        total = len(bi_test_cases)
        
        for query, should_be_static, description in bi_test_cases:
            with self.subTest(query=query):
                try:
                    static_response = self.bot._handle_static_commands(query)
                    is_static = static_response is not None
                    
                    if is_static == should_be_static:
                        passed += 1
                        print(f"  ✅ PASS: {query} -> {'Static' if is_static else 'Intelligent'}")
                    else:
                        print(f"  ❌ FAIL: {query} -> {'Static' if is_static else 'Intelligent'} (Expected: {'Static' if should_be_static else 'Intelligent'})")
                        
                except Exception as e:
                    print(f"  ❌ ERROR: {query} - {e}")
        
        print(f"  📊 Business Intelligence: {passed}/{total} passed ({passed/total:.1%})")
        self.assertGreaterEqual(passed/total, 0.9, f"Business intelligence accuracy should be >= 90%, got {passed/total:.1%}")

    def test_spectrum_4_complex_analytics(self):
        """Test Spectrum 4: Complex Analytics (10+ test cases)"""
        print("\n🧪 Testing Spectrum 4: Complex Analytics")
        
        complex_test_cases = [
            # Forecasting
            ("sales forecast", False, "Sales forecast"),
            ("revenue forecast", False, "Revenue forecast"),
            ("forecast analysis", False, "Forecast analysis"),
            ("predictive analysis", False, "Predictive analysis"),
            ("future projections", False, "Future projections"),
            ("forecast trends", False, "Forecast trends"),
            ("forecast model", False, "Forecast model"),
            ("forecast accuracy", False, "Forecast accuracy"),
            ("forecast comparison", False, "Forecast comparison"),
            ("forecast insights", False, "Forecast insights"),
            
            # Correlation analysis
            ("correlation analysis", False, "Correlation analysis"),
            ("correlation study", False, "Correlation study"),
            ("correlation trends", False, "Correlation trends"),
            ("correlation factors", False, "Correlation factors"),
            ("correlation insights", False, "Correlation insights"),
            ("correlation patterns", False, "Correlation patterns"),
            ("correlation model", False, "Correlation model"),
            ("correlation data", False, "Correlation data"),
            ("correlation report", False, "Correlation report"),
            ("correlation summary", False, "Correlation summary"),
            
            # Deep analysis
            ("deep dive analysis", False, "Deep dive analysis"),
            ("root cause analysis", False, "Root cause analysis"),
            ("comprehensive analysis", False, "Comprehensive analysis"),
            ("detailed investigation", False, "Detailed investigation"),
            ("thorough analysis", False, "Thorough analysis"),
            ("in-depth analysis", False, "In-depth analysis"),
            ("comprehensive study", False, "Comprehensive study"),
            ("detailed examination", False, "Detailed examination"),
            ("thorough investigation", False, "Thorough investigation"),
            ("deep investigation", False, "Deep investigation"),
        ]
        
        passed = 0
        total = len(complex_test_cases)
        
        for query, should_be_static, description in complex_test_cases:
            with self.subTest(query=query):
                try:
                    static_response = self.bot._handle_static_commands(query)
                    is_static = static_response is not None
                    
                    if is_static == should_be_static:
                        passed += 1
                        print(f"  ✅ PASS: {query} -> {'Static' if is_static else 'Intelligent'}")
                    else:
                        print(f"  ❌ FAIL: {query} -> {'Static' if is_static else 'Intelligent'} (Expected: {'Static' if should_be_static else 'Intelligent'})")
                        
                except Exception as e:
                    print(f"  ❌ ERROR: {query} - {e}")
        
        print(f"  📊 Complex Analytics: {passed}/{total} passed ({passed/total:.1%})")
        self.assertGreaterEqual(passed/total, 0.9, f"Complex analytics accuracy should be >= 90%, got {passed/total:.1%}")

    def test_spectrum_5_executive_briefings(self):
        """Test Spectrum 5: Executive Briefings (10+ test cases)"""
        print("\n🧪 Testing Spectrum 5: Executive Briefings")
        
        executive_test_cases = [
            # Executive summaries
            ("executive briefing", False, "Executive briefing"),
            ("board report", False, "Board report"),
            ("leadership summary", False, "Leadership summary"),
            ("executive summary", False, "Executive summary"),
            ("management report", False, "Management report"),
            ("executive overview", False, "Executive overview"),
            ("leadership briefing", False, "Leadership briefing"),
            ("executive dashboard", False, "Executive dashboard"),
            ("board summary", False, "Board summary"),
            ("executive insights", False, "Executive insights"),
            
            # Strategic analysis
            ("strategic overview", False, "Strategic overview"),
            ("strategic analysis", False, "Strategic analysis"),
            ("strategic insights", False, "Strategic insights"),
            ("strategic summary", False, "Strategic summary"),
            ("strategic report", False, "Strategic report"),
            ("strategic briefing", False, "Strategic briefing"),
            ("strategic dashboard", False, "Strategic dashboard"),
            ("strategic overview", False, "Strategic overview"),
            ("strategic assessment", False, "Strategic assessment"),
            ("strategic evaluation", False, "Strategic evaluation"),
            
            # High-level summaries
            ("high-level summary", False, "High-level summary"),
            ("high-level overview", False, "High-level overview"),
            ("high-level analysis", False, "High-level analysis"),
            ("high-level insights", False, "High-level insights"),
            ("high-level report", False, "High-level report"),
            ("high-level briefing", False, "High-level briefing"),
            ("high-level dashboard", False, "High-level dashboard"),
            ("high-level assessment", False, "High-level assessment"),
            ("high-level evaluation", False, "High-level evaluation"),
            ("high-level trends", False, "High-level trends"),
        ]
        
        passed = 0
        total = len(executive_test_cases)
        
        for query, should_be_static, description in executive_test_cases:
            with self.subTest(query=query):
                try:
                    static_response = self.bot._handle_static_commands(query)
                    is_static = static_response is not None
                    
                    if is_static == should_be_static:
                        passed += 1
                        print(f"  ✅ PASS: {query} -> {'Static' if is_static else 'Intelligent'}")
                    else:
                        print(f"  ❌ FAIL: {query} -> {'Static' if is_static else 'Intelligent'} (Expected: {'Static' if should_be_static else 'Intelligent'})")
                        
                except Exception as e:
                    print(f"  ❌ ERROR: {query} - {e}")
        
        print(f"  📊 Executive Briefings: {passed}/{total} passed ({passed/total:.1%})")
        self.assertGreaterEqual(passed/total, 0.9, f"Executive briefing accuracy should be >= 90%, got {passed/total:.1%}")

    def test_response_quality_appropriateness(self):
        """Test response quality appropriateness - not overdoing or underdoing"""
        print("\n🧪 Testing Response Quality Appropriateness")
        
        quality_test_cases = [
            {
                "query": "what's our win rate?",
                "expected_length_range": (100, 500),
                "expected_elements": ["win rate", "%", "opportunities"],
                "description": "Simple win rate query should be concise"
            },
            {
                "query": "show pipeline breakdown",
                "expected_length_range": (150, 600),
                "expected_elements": ["pipeline", "stage", "opportunities", "$"],
                "description": "Pipeline query should be detailed but not overwhelming"
            },
            {
                "query": "executive briefing",
                "expected_length_range": (200, 800),
                "expected_elements": ["briefing", "metrics", "insights", "recommendations"],
                "description": "Executive briefing should be comprehensive"
            },
            {
                "query": "hello",
                "expected_length_range": (50, 150),
                "expected_elements": ["hello", "assistant"],
                "description": "Greeting should be brief and friendly"
            },
            {
                "query": "help",
                "expected_length_range": (200, 600),
                "expected_elements": ["help", "analytics", "examples"],
                "description": "Help should be informative but not overwhelming"
            }
        ]
        
        passed = 0
        total = len(quality_test_cases)
        
        for test_case in quality_test_cases:
            with self.subTest(query=test_case["query"]):
                try:
                    response = self.bot._generate_fallback_response(test_case["query"])
                    
                    # Check length appropriateness
                    length_ok = test_case["expected_length_range"][0] <= len(response) <= test_case["expected_length_range"][1]
                    
                    # Check content appropriateness
                    response_lower = response.lower()
                    found_elements = [elem for elem in test_case["expected_elements"] if elem.lower() in response_lower]
                    content_ok = len(found_elements) >= len(test_case["expected_elements"]) * 0.7
                    
                    # Check format
                    format_ok = "🤖 **Whizzy**: " in response
                    
                    if length_ok and content_ok and format_ok:
                        passed += 1
                        print(f"  ✅ PASS: {test_case['query']} -> Length: {len(response)}, Elements: {len(found_elements)}/{len(test_case['expected_elements'])}")
                    else:
                        print(f"  ❌ FAIL: {test_case['query']} -> Length: {len(response)} (expected {test_case['expected_length_range']}), Elements: {len(found_elements)}/{len(test_case['expected_elements'])}")
                        
                except Exception as e:
                    print(f"  ❌ ERROR: {test_case['query']} - {e}")
        
        print(f"  📊 Response Quality: {passed}/{total} passed ({passed/total:.1%})")
        self.assertGreaterEqual(passed/total, 0.8, f"Response quality should be >= 80%, got {passed/total:.1%}")

    def test_context_awareness(self):
        """Test context awareness and appropriate response depth"""
        print("\n🧪 Testing Context Awareness")
        
        context_test_cases = [
            {
                "query": "win rate",
                "context": "quick check",
                "expected_depth": "concise"
            },
            {
                "query": "win rate analysis",
                "context": "detailed analysis",
                "expected_depth": "detailed"
            },
            {
                "query": "executive briefing",
                "context": "leadership meeting",
                "expected_depth": "comprehensive"
            },
            {
                "query": "pipeline overview",
                "context": "team meeting",
                "expected_depth": "moderate"
            },
            {
                "query": "sales forecast",
                "context": "strategic planning",
                "expected_depth": "detailed"
            }
        ]
        
        passed = 0
        total = len(context_test_cases)
        
        for test_case in context_test_cases:
            with self.subTest(query=test_case["query"]):
                try:
                    response = self.bot._generate_fallback_response(test_case["query"])
                    
                    # Check if response depth matches context
                    if test_case["expected_depth"] == "concise":
                        depth_ok = len(response) < 300
                    elif test_case["expected_depth"] == "moderate":
                        depth_ok = 200 <= len(response) <= 600
                    elif test_case["expected_depth"] == "detailed":
                        depth_ok = 400 <= len(response) <= 800
                    elif test_case["expected_depth"] == "comprehensive":
                        depth_ok = len(response) > 500
                    else:
                        depth_ok = True
                    
                    if depth_ok:
                        passed += 1
                        print(f"  ✅ PASS: {test_case['query']} ({test_case['context']}) -> Length: {len(response)}")
                    else:
                        print(f"  ❌ FAIL: {test_case['query']} ({test_case['context']}) -> Length: {len(response)} (expected {test_case['expected_depth']})")
                        
                except Exception as e:
                    print(f"  ❌ ERROR: {test_case['query']} - {e}")
        
        print(f"  📊 Context Awareness: {passed}/{total} passed ({passed/total:.1%})")
        self.assertGreaterEqual(passed/total, 0.7, f"Context awareness should be >= 70%, got {passed/total:.1%}")

if __name__ == '__main__':
    unittest.main()
