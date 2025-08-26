#!/usr/bin/env python3
"""
Comprehensive test runner to validate intelligent improvements
"""

import asyncio
import json
from typing import List, Dict, Tuple

class IntelligenceTestRunner:
    """Test runner for intelligent improvements"""
    
    def __init__(self):
        self.test_results = []
        
    def run_static_command_tests(self) -> List[Dict]:
        """Test static command classification"""
        print("🧪 Testing Static Command Classification...")
        
        test_cases = [
            # Should be static commands
            ("hello", True, "Simple greeting"),
            ("hi", True, "Simple greeting"),
            ("help", True, "Help request"),
            ("status", True, "Status check"),
            ("subscribe", True, "Subscription command"),
            
            # Should NOT be static commands (should use intelligent routing)
            ("what's our win rate?", False, "Data query"),
            ("show pipeline", False, "Data query"),
            ("pipeline $ by stage", False, "Data query with symbols"),
            ("executive briefing", False, "Complex request"),
            ("deals at risk", False, "Analysis request"),
            ("sales forecast", False, "Complex analysis"),
            ("win rate analysis", False, "Analysis request"),
            ("performance metrics", False, "Business intelligence"),
            ("trend analysis", False, "Complex analytics"),
            ("correlation study", False, "Complex analytics"),
            ("root cause analysis", False, "Complex analytics"),
            ("deep dive investigation", False, "Complex analytics"),
            ("sales performance overview", False, "Business intelligence"),
            ("team productivity", False, "Business intelligence"),
            ("strategic pipeline analysis", False, "Business intelligence"),
            ("my deals", False, "Personal data query"),
            ("personal pipeline", False, "Personal data query"),
            ("quota progress", False, "Personal metrics"),
            ("team performance", False, "Team metrics"),
            ("rep coaching opportunities", False, "Management insights"),
            ("pipeline health", False, "Business intelligence"),
            ("resource allocation", False, "Strategic analysis"),
            ("data strategy", False, "Strategic analysis"),
            ("analytics insights", False, "Business intelligence"),
            ("business intelligence", False, "Business intelligence"),
            ("data-driven decisions", False, "Strategic analysis"),
        ]
        
        results = []
        for query, should_be_static, description in test_cases:
            try:
                # Import and test
                from app.whizzy_bot import WhizzyBot
                bot = WhizzyBot()
                
                # Test static command classification
                static_response = bot._handle_static_commands(query)
                is_static = static_response is not None
                
                result = {
                    "query": query,
                    "expected_static": should_be_static,
                    "actual_static": is_static,
                    "passed": is_static == should_be_static,
                    "description": description,
                    "response": static_response[:100] + "..." if static_response and len(static_response) > 100 else static_response
                }
                
                results.append(result)
                
                status = "✅ PASS" if result["passed"] else "❌ FAIL"
                print(f"  {status}: {query} -> {'Static' if is_static else 'Intelligent'} (Expected: {'Static' if should_be_static else 'Intelligent'})")
                
            except Exception as e:
                print(f"  ❌ ERROR: {query} - {e}")
                results.append({
                    "query": query,
                    "expected_static": should_be_static,
                    "actual_static": None,
                    "passed": False,
                    "description": description,
                    "error": str(e)
                })
        
        return results
    
    def run_soql_accuracy_tests(self) -> List[Dict]:
        """Test SOQL query accuracy"""
        print("\n🧪 Testing SOQL Query Accuracy...")
        
        test_cases = [
            ("win rate", ["COUNT", "StageName", "Closed Won", "Closed Lost"]),
            ("pipeline breakdown", ["StageName", "COUNT", "SUM", "Amount"]),
            ("top accounts", ["Name", "AnnualRevenue", "ORDER BY", "DESC"]),
            ("deals at risk", ["Name", "StageName", "Amount", "CloseDate"]),
        ]
        
        results = []
        for query, expected_elements in test_cases:
            try:
                # Test that the query generates appropriate SOQL
                from app.whizzy_bot import WhizzyBot
                bot = WhizzyBot()
                
                response = bot._generate_fallback_response(query)
                
                # Check if response contains expected elements
                response_lower = response.lower()
                found_elements = [elem for elem in expected_elements if elem.lower() in response_lower]
                
                result = {
                    "query": query,
                    "expected_elements": expected_elements,
                    "found_elements": found_elements,
                    "coverage": len(found_elements) / len(expected_elements),
                    "passed": len(found_elements) >= len(expected_elements) * 0.7,  # 70% coverage
                    "response_length": len(response)
                }
                
                results.append(result)
                
                status = "✅ PASS" if result["passed"] else "❌ FAIL"
                coverage = f"{result['coverage']:.1%}"
                print(f"  {status}: {query} -> {coverage} coverage ({len(found_elements)}/{len(expected_elements)} elements)")
                
            except Exception as e:
                print(f"  ❌ ERROR: {query} - {e}")
                results.append({
                    "query": query,
                    "expected_elements": expected_elements,
                    "found_elements": [],
                    "coverage": 0.0,
                    "passed": False,
                    "error": str(e)
                })
        
        return results
    
    def run_response_quality_tests(self) -> List[Dict]:
        """Test response quality"""
        print("\n🧪 Testing Response Quality...")
        
        test_cases = [
            {
                "query": "what's our win rate?",
                "min_length": 100,
                "required_elements": ["win rate", "%", "opportunities", "won", "lost"],
                "expected_format": "🤖 **Whizzy**:"
            },
            {
                "query": "show pipeline breakdown",
                "min_length": 150,
                "required_elements": ["pipeline", "stage", "opportunities", "$"],
                "expected_format": "🤖 **Whizzy**:"
            },
            {
                "query": "executive briefing",
                "min_length": 200,
                "required_elements": ["briefing", "metrics", "insights", "recommendations"],
                "expected_format": "🤖 **Whizzy**:"
            }
        ]
        
        results = []
        for test_case in test_cases:
            try:
                from app.whizzy_bot import WhizzyBot
                bot = WhizzyBot()
                
                response = bot._generate_fallback_response(test_case["query"])
                
                # Check length
                length_ok = len(response) >= test_case["min_length"]
                
                # Check required elements
                response_lower = response.lower()
                found_elements = [elem for elem in test_case["required_elements"] if elem.lower() in response_lower]
                elements_ok = len(found_elements) >= len(test_case["required_elements"]) * 0.8  # 80% coverage
                
                # Check format
                format_ok = test_case["expected_format"] in response
                
                result = {
                    "query": test_case["query"],
                    "length_ok": length_ok,
                    "elements_ok": elements_ok,
                    "format_ok": format_ok,
                    "passed": length_ok and elements_ok and format_ok,
                    "response_length": len(response),
                    "found_elements": found_elements,
                    "coverage": len(found_elements) / len(test_case["required_elements"])
                }
                
                results.append(result)
                
                status = "✅ PASS" if result["passed"] else "❌ FAIL"
                print(f"  {status}: {test_case['query']} -> Length: {len(response)}, Elements: {len(found_elements)}/{len(test_case['required_elements'])}")
                
            except Exception as e:
                print(f"  ❌ ERROR: {test_case['query']} - {e}")
                results.append({
                    "query": test_case["query"],
                    "length_ok": False,
                    "elements_ok": False,
                    "format_ok": False,
                    "passed": False,
                    "error": str(e)
                })
        
        return results
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Running Comprehensive Intelligence Tests...\n")
        
        # Run all test suites
        static_results = self.run_static_command_tests()
        soql_results = self.run_soql_accuracy_tests()
        quality_results = self.run_response_quality_tests()
        
        # Calculate overall statistics
        total_tests = len(static_results) + len(soql_results) + len(quality_results)
        passed_tests = sum(1 for r in static_results if r.get("passed", False)) + \
                      sum(1 for r in soql_results if r.get("passed", False)) + \
                      sum(1 for r in quality_results if r.get("passed", False))
        
        print(f"\n📊 Test Summary:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {total_tests - passed_tests}")
        print(f"  Success Rate: {passed_tests/total_tests:.1%}")
        
        # Detailed results
        print(f"\n📋 Detailed Results:")
        
        print(f"\n  Static Command Classification:")
        static_passed = sum(1 for r in static_results if r.get("passed", False))
        print(f"    {static_passed}/{len(static_results)} passed ({static_passed/len(static_results):.1%})")
        
        print(f"\n  SOQL Query Accuracy:")
        soql_passed = sum(1 for r in soql_results if r.get("passed", False))
        print(f"    {soql_passed}/{len(soql_results)} passed ({soql_passed/len(soql_results):.1%})")
        
        print(f"\n  Response Quality:")
        quality_passed = sum(1 for r in quality_results if r.get("passed", False))
        print(f"    {quality_passed}/{len(quality_results)} passed ({quality_passed/len(quality_results):.1%})")
        
        # Show failed tests
        failed_tests = []
        for r in static_results + soql_results + quality_results:
            if not r.get("passed", False):
                failed_tests.append(r)
        
        if failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"  - {test.get('query', 'Unknown')}: {test.get('description', 'No description')}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": passed_tests/total_tests,
            "static_results": static_results,
            "soql_results": soql_results,
            "quality_results": quality_results,
            "failed_tests": failed_tests
        }

if __name__ == "__main__":
    runner = IntelligenceTestRunner()
    results = runner.run_comprehensive_tests()
    
    # Save results to file
    with open("intelligence_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to intelligence_test_results.json")
    
    if results["success_rate"] >= 0.8:
        print("🎉 Excellent! Intelligence improvements are working well!")
    elif results["success_rate"] >= 0.6:
        print("👍 Good progress! Some areas need improvement.")
    else:
        print("⚠️  Needs work! Significant improvements required.")
