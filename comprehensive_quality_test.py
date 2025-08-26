#!/usr/bin/env python3
"""
Comprehensive Quality Test Suite for Whizzy Bot
Tests all major use cases, response quality, and persona-specific briefings
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from intelligent_agentic_system import EnhancedIntelligentAgenticSystem, PersonaType
from briefing_system import BriefingType

class ComprehensiveQualityTest:
    def __init__(self):
        self.system = None
        self.test_results = []
        
    async def setup(self):
        """Initialize the intelligent system"""
        print("🔧 Setting up test environment...")
        self.system = EnhancedIntelligentAgenticSystem()
        print("✅ Test environment ready")
        
    def log_test(self, test_name: str, success: bool, details: str = "", response: str = ""):
        """Log test results"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "response_length": len(response) if response else 0,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if response and len(response) > 100:
            print(f"   Response: {response[:100]}...")
        elif response:
            print(f"   Response: {response}")
        print()
        
    async def test_win_rate_query(self):
        """Test win rate calculation"""
        print("🎯 Testing Win Rate Query...")
        try:
            response = await self.system._handle_win_rate_query("whats our win rate", None)
            
            # Check if response contains percentage
            has_percentage = "%" in response.response_text
            has_win_rate = "win rate" in response.response_text.lower()
            is_concise = len(response.response_text) < 500
            
            success = has_percentage and has_win_rate and is_concise
            details = f"Percentage: {has_percentage}, Win Rate: {has_win_rate}, Concise: {is_concise}"
            
            self.log_test("Win Rate Query", success, details, response.response_text)
            
        except Exception as e:
            self.log_test("Win Rate Query", False, f"Error: {e}")
            
    async def test_ae_briefing(self):
        """Test AE briefing - should show stuck deals"""
        print("👤 Testing AE Briefing...")
        try:
            response = await self.system._handle_coffee_briefing("AE briefing", None, None)
            
            # Check if it's AE-focused content
            has_stuck_deals = any(word in response.response_text.lower() for word in ["stuck", "deals", "days"])
            has_ae_context = any(word in response.response_text.lower() for word in ["account executive", "ae", "individual"])
            is_concise = len(response.response_text) < 800
            
            success = has_stuck_deals and has_ae_context and is_concise
            details = f"Stuck Deals: {has_stuck_deals}, AE Context: {has_ae_context}, Concise: {is_concise}"
            
            self.log_test("AE Briefing", success, details, response.response_text)
            
        except Exception as e:
            self.log_test("AE Briefing", False, f"Error: {e}")
            
    async def test_vp_briefing(self):
        """Test VP briefing - should show pipeline coverage"""
        print("👔 Testing VP Briefing...")
        try:
            response = await self.system._handle_coffee_briefing("VP sales briefing", None, None)
            
            # Check if it's VP-focused content
            has_pipeline = any(word in response.response_text.lower() for word in ["pipeline", "coverage", "quota"])
            has_vp_context = any(word in response.response_text.lower() for word in ["vp", "vice president", "strategic"])
            is_concise = len(response.response_text) < 800
            
            success = has_pipeline and has_vp_context and is_concise
            details = f"Pipeline: {has_pipeline}, VP Context: {has_vp_context}, Concise: {is_concise}"
            
            self.log_test("VP Briefing", success, details, response.response_text)
            
        except Exception as e:
            self.log_test("VP Briefing", False, f"Error: {e}")
            
    async def test_cdo_briefing(self):
        """Test CDO briefing - should show forecast accuracy"""
        print("📊 Testing CDO Briefing...")
        try:
            response = await self.system._handle_cdo_forecast_query("As a CDO can you create win rate forecast pipeline", None)
            
            # Check if it's CDO-focused content
            has_forecast = any(word in response.response_text.lower() for word in ["forecast", "accuracy", "prediction"])
            has_cdo_context = any(word in response.response_text.lower() for word in ["cdo", "data quality", "analytics"])
            is_concise = len(response.response_text) < 800
            
            success = has_forecast and has_cdo_context and is_concise
            details = f"Forecast: {has_forecast}, CDO Context: {has_cdo_context}, Concise: {is_concise}"
            
            self.log_test("CDO Briefing", success, details, response.response_text)
            
        except Exception as e:
            self.log_test("CDO Briefing", False, f"Error: {e}")
            
    async def test_persona_detection(self):
        """Test persona detection logic"""
        print("🎭 Testing Persona Detection...")
        try:
            # Test AE detection
            ae_persona = self.system._detect_persona_from_query("AE briefing", None)
            ae_correct = ae_persona == PersonaType.ACCOUNT_EXECUTIVE
            
            # Test VP detection
            vp_persona = self.system._detect_persona_from_query("VP sales briefing", None)
            vp_correct = vp_persona == PersonaType.VP_SALES
            
            # Test CDO detection
            cdo_persona = self.system._detect_persona_from_query("As a CDO can you create win rate forecast pipeline", None)
            cdo_correct = cdo_persona == PersonaType.CDO
            
            success = ae_correct and vp_correct and cdo_correct
            details = f"AE: {ae_correct}, VP: {vp_correct}, CDO: {cdo_correct}"
            
            self.log_test("Persona Detection", success, details)
            
        except Exception as e:
            self.log_test("Persona Detection", False, f"Error: {e}")
            
    async def test_basic_queries(self):
        """Test basic Salesforce queries"""
        print("🔍 Testing Basic Queries...")
        test_queries = [
            "what all can you do",
            "show pipeline breakdown by stage",
            "top 10 opportunities",
            "what are my tasks this week"
        ]
        
        for query in test_queries:
            try:
                response = await self.system.process_query(query, None)
                
                # Check response quality
                has_response = len(response.response_text) > 10
                is_concise = len(response.response_text) < 1000
                has_confidence = response.confidence_score > 0.5
                
                success = has_response and is_concise and has_confidence
                details = f"Length: {len(response.response_text)}, Confidence: {response.confidence_score}"
                
                self.log_test(f"Basic Query: {query[:30]}...", success, details, response.response_text)
                
            except Exception as e:
                self.log_test(f"Basic Query: {query[:30]}...", False, f"Error: {e}")
                
    async def test_complex_queries(self):
        """Test complex analytics queries"""
        print("🧠 Testing Complex Queries...")
        complex_queries = [
            "analyze our biggest deals",
            "what's our win rate trend over time",
            "show me forecast accuracy for last quarter",
            "which deals are at risk this month"
        ]
        
        for query in complex_queries:
            try:
                response = await self.system.process_query(query, None)
                
                # Check response quality
                has_response = len(response.response_text) > 20
                is_concise = len(response.response_text) < 1200
                has_insights = any(word in response.response_text.lower() for word in ["insight", "analysis", "trend", "recommend"])
                
                success = has_response and is_concise and has_insights
                details = f"Length: {len(response.response_text)}, Has Insights: {has_insights}"
                
                self.log_test(f"Complex Query: {query[:30]}...", success, details, response.response_text)
                
            except Exception as e:
                self.log_test(f"Complex Query: {query[:30]}...", False, f"Error: {e}")
                
    async def test_error_handling(self):
        """Test error handling and fallbacks"""
        print("🛡️ Testing Error Handling...")
        
        # Test invalid query
        try:
            response = await self.system.process_query("invalid query that should fail", None)
            
            # Should still return a response (even if it's an error message)
            has_response = len(response.response_text) > 0
            is_graceful = "error" not in response.response_text.lower() or "try" in response.response_text.lower()
            
            success = has_response and is_graceful
            details = f"Has Response: {has_response}, Graceful: {is_graceful}"
            
            self.log_test("Error Handling", success, details, response.response_text)
            
        except Exception as e:
            self.log_test("Error Handling", False, f"Error: {e}")
            
    async def test_response_quality(self):
        """Test overall response quality metrics"""
        print("📈 Testing Response Quality...")
        
        quality_tests = [
            ("Win Rate Query", "whats our win rate"),
            ("Pipeline Query", "show pipeline breakdown"),
            ("AE Briefing", "AE briefing"),
            ("VP Briefing", "VP sales briefing")
        ]
        
        total_length = 0
        total_confidence = 0
        test_count = 0
        
        for test_name, query in quality_tests:
            try:
                response = await self.system.process_query(query, None)
                
                total_length += len(response.response_text)
                total_confidence += response.confidence_score
                test_count += 1
                
                # Check individual quality metrics
                is_concise = len(response.response_text) < 1000
                has_confidence = response.confidence_score > 0.7
                is_relevant = len(response.response_text) > 20
                
                success = is_concise and has_confidence and is_relevant
                details = f"Length: {len(response.response_text)}, Confidence: {response.confidence_score:.2f}"
                
                self.log_test(f"Quality: {test_name}", success, details)
                
            except Exception as e:
                self.log_test(f"Quality: {test_name}", False, f"Error: {e}")
                
        # Calculate averages
        if test_count > 0:
            avg_length = total_length / test_count
            avg_confidence = total_confidence / test_count
            
            length_ok = avg_length < 800
            confidence_ok = avg_confidence > 0.8
            
            success = length_ok and confidence_ok
            details = f"Avg Length: {avg_length:.0f}, Avg Confidence: {avg_confidence:.2f}"
            
            self.log_test("Overall Quality Metrics", success, details)
            
    async def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive Quality Test Suite")
        print("=" * 60)
        
        await self.setup()
        
        # Run all test categories
        await self.test_persona_detection()
        await self.test_win_rate_query()
        await self.test_ae_briefing()
        await self.test_vp_briefing()
        await self.test_cdo_briefing()
        await self.test_basic_queries()
        await self.test_complex_queries()
        await self.test_error_handling()
        await self.test_response_quality()
        
        # Generate summary
        self.generate_summary()
        
    def generate_summary(self):
        """Generate test summary"""
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Show failed tests
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['details']}")
                    
        # Save results
        with open("comprehensive_test_results.json", "w") as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": (passed_tests/total_tests)*100
                },
                "results": self.test_results
            }, f, indent=2)
            
        print(f"\n📄 Results saved to: comprehensive_test_results.json")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! The bot is ready for production.")
        else:
            print(f"\n⚠️ {failed_tests} tests failed. Review the issues above.")

async def main():
    """Main test runner"""
    tester = ComprehensiveQualityTest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
