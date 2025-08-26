#!/usr/bin/env python3
"""
Enhanced Whizzy Bot - Response Testing & Review Framework
Purpose: Test actual responses from the enhanced intelligent agentic system
before deployment for live testing.
"""

import asyncio
import json
import time
from typing import Dict, List, Any
from datetime import datetime
import os
from dotenv import load_dotenv

# Import enhanced system
from app.intelligent_agentic_system import (
    EnhancedIntelligentAgenticSystem, IntentType, PersonaType, 
    DataSourceType, IntentAnalysis, AgentResponse, CoffeeBriefing,
    ChainOfThought, ContextState
)

# Load environment variables
load_dotenv()

class ResponseTester:
    """Comprehensive response testing and review framework"""
    
    def __init__(self):
        self.enhanced_system = EnhancedIntelligentAgenticSystem()
        self.test_results = []
        self.performance_metrics = {}
        
    async def run_comprehensive_tests(self):
        """Run comprehensive response tests with actual queries"""
        print("🧠 Enhanced Whizzy Bot - Response Testing & Review")
        print("=" * 60)
        
        # Test scenarios by persona and complexity
        test_scenarios = self._get_test_scenarios()
        
        for scenario in test_scenarios:
            print(f"\n🎯 Testing Scenario: {scenario['name']}")
            print(f"📝 Query: {scenario['query']}")
            print(f"👤 Persona: {scenario['persona']}")
            print("-" * 40)
            
            try:
                # Test the response
                start_time = time.time()
                response = await self.enhanced_system.process_query(
                    scenario['query'], 
                    scenario.get('context', {})
                )
                end_time = time.time()
                
                # Analyze response
                analysis = self._analyze_response(response, scenario, end_time - start_time)
                
                # Display results
                self._display_response_analysis(analysis)
                
                # Store results
                self.test_results.append(analysis)
                
            except Exception as e:
                print(f"❌ Error in scenario '{scenario['name']}': {e}")
                self.test_results.append({
                    'scenario': scenario['name'],
                    'error': str(e),
                    'status': 'failed'
                })
        
        # Generate comprehensive report
        self._generate_test_report()
    
    def _get_test_scenarios(self) -> List[Dict[str, Any]]:
        """Define comprehensive test scenarios"""
        return [
            # VP Sales Scenarios
            {
                'name': 'VP Sales - Strategic Pipeline Analysis',
                'query': 'What\'s our current pipeline health and what are the biggest risks to our Q4 targets?',
                'persona': 'VP_SALES',
                'context': {'role': 'executive', 'focus': 'strategic'},
                'user_id': 'vp_sales_user'
            },
            {
                'name': 'VP Sales - Team Performance Review',
                'query': 'Show me our top and bottom performing sales reps and what coaching opportunities exist',
                'persona': 'VP_SALES',
                'context': {'role': 'executive', 'focus': 'team_management'},
                'user_id': 'vp_sales_user'
            },
            
            # Account Executive Scenarios
            {
                'name': 'AE - Deal Preparation',
                'query': 'I have a meeting with Acme Corp tomorrow. What should I know about their account and recent activity?',
                'persona': 'ACCOUNT_EXECUTIVE',
                'context': {'role': 'sales_rep', 'focus': 'deal_prep'},
                'user_id': 'ae_user'
            },
            {
                'name': 'AE - Performance Analysis',
                'query': 'How am I performing compared to my quota and what areas should I focus on improving?',
                'persona': 'ACCOUNT_EXECUTIVE',
                'context': {'role': 'sales_rep', 'focus': 'self_assessment'},
                'user_id': 'ae_user'
            },
            
            # CDO Scenarios
            {
                'name': 'CDO - Data Pipeline Health',
                'query': 'What\'s the current health of our data pipelines and are there any quality issues I should be concerned about?',
                'persona': 'CDO',
                'context': {'role': 'data_leader', 'focus': 'infrastructure'},
                'user_id': 'cdo_user'
            },
            {
                'name': 'CDO - Analytics Adoption',
                'query': 'How are our analytics tools being adopted across the organization and what can we do to improve usage?',
                'persona': 'CDO',
                'context': {'role': 'data_leader', 'focus': 'adoption'},
                'user_id': 'cdo_user'
            },
            
            # Complex Analytics Scenarios
            {
                'name': 'Complex - Multi-source Analysis',
                'query': 'Analyze our customer churn patterns by combining Salesforce data with our usage analytics and recommend retention strategies',
                'persona': 'CDO',
                'context': {'role': 'analyst', 'focus': 'complex_analysis'},
                'user_id': 'analyst_user'
            },
            {
                'name': 'Complex - Predictive Insights',
                'query': 'Based on our historical data, what\'s our predicted win rate for Q4 and what factors are most influencing our success?',
                'persona': 'VP_SALES',
                'context': {'role': 'executive', 'focus': 'predictive'},
                'user_id': 'vp_sales_user'
            },
            
            # Coffee Briefing Scenarios
            {
                'name': 'Coffee Briefing - VP Sales Daily',
                'query': 'Generate my morning coffee briefing with key metrics and strategic insights',
                'persona': 'VP_SALES',
                'context': {'role': 'executive', 'focus': 'daily_briefing'},
                'user_id': 'vp_sales_user'
            },
            {
                'name': 'Coffee Briefing - AE Weekly',
                'query': 'Give me my weekly performance summary and action items',
                'persona': 'ACCOUNT_EXECUTIVE',
                'context': {'role': 'sales_rep', 'focus': 'weekly_review'},
                'user_id': 'ae_user'
            },
            
            # Thinking & Reasoning Scenarios
            {
                'name': 'Thinking - Root Cause Analysis',
                'query': 'Why are our sales cycles getting longer and what systemic issues might be causing this trend?',
                'persona': 'VP_SALES',
                'context': {'role': 'executive', 'focus': 'root_cause'},
                'user_id': 'vp_sales_user'
            },
            {
                'name': 'Thinking - Strategic Planning',
                'query': 'What should our go-to-market strategy be for the next quarter given our current pipeline and market conditions?',
                'persona': 'VP_SALES',
                'context': {'role': 'executive', 'focus': 'strategy'},
                'user_id': 'vp_sales_user'
            }
        ]
    
    def _analyze_response(self, response: AgentResponse, scenario: Dict, response_time: float) -> Dict[str, Any]:
        """Analyze response quality and characteristics"""
        return {
            'scenario': scenario['name'],
            'query': scenario['query'],
            'persona': scenario['persona'],
            'response_time': response_time,
            'response_text': response.response_text,
            'confidence_score': response.confidence_score,
            'intent_type': 'unknown',  # AgentResponse doesn't have intent_type field
            'data_sources_used': [ds.value for ds in response.data_sources_used] if response.data_sources_used else [],
            'reasoning_steps': response.reasoning_steps,
            'chain_of_thought': self._analyze_chain_of_thought(response.chain_of_thought),
            'quality_metrics': response.quality_metrics,
            'thinking_required': getattr(response, 'thinking_required', False),
            'context_awareness': self._assess_context_awareness(response),
            'actionability': self._assess_actionability(response),
            'persona_alignment': self._assess_persona_alignment(response, scenario['persona']),
            'overall_quality': self._calculate_overall_quality(response, scenario)
        }
    
    def _analyze_chain_of_thought(self, chain_of_thought: ChainOfThought) -> Dict[str, Any]:
        """Analyze chain of thought characteristics"""
        if not chain_of_thought:
            return None
        
        return {
            'steps_count': len(chain_of_thought.thinking_steps),
            'final_confidence': chain_of_thought.final_confidence,
            'reasoning_path_length': len(chain_of_thought.reasoning_path),
            'average_step_confidence': sum(step.confidence for step in chain_of_thought.thinking_steps) / len(chain_of_thought.thinking_steps) if chain_of_thought.thinking_steps else 0,
            'thinking_techniques': [step.technique for step in chain_of_thought.thinking_steps if step.technique]
        }
    
    def _assess_context_awareness(self, response: AgentResponse) -> float:
        """Assess how well the response uses context"""
        # Simple heuristic - check for references to previous interactions
        context_indicators = ['previous', 'earlier', 'last time', 'as mentioned', 'based on our conversation']
        text_lower = response.response_text.lower()
        
        context_score = 0.0
        for indicator in context_indicators:
            if indicator in text_lower:
                context_score += 0.2
        
        return min(context_score, 1.0)
    
    def _assess_actionability(self, response: AgentResponse) -> float:
        """Assess how actionable the response is"""
        action_indicators = ['should', 'recommend', 'action', 'next steps', 'focus on', 'improve', 'optimize']
        text_lower = response.response_text.lower()
        
        action_score = 0.0
        for indicator in action_indicators:
            if indicator in text_lower:
                action_score += 0.15
        
        return min(action_score, 1.0)
    
    def _assess_persona_alignment(self, response: AgentResponse, expected_persona: str) -> float:
        """Assess how well the response aligns with the expected persona"""
        persona_keywords = {
            'VP_SALES': ['strategic', 'executive', 'team', 'pipeline', 'quarterly', 'targets'],
            'ACCOUNT_EXECUTIVE': ['deal', 'customer', 'opportunity', 'meeting', 'preparation', 'performance'],
            'CDO': ['data', 'analytics', 'pipeline', 'quality', 'infrastructure', 'adoption']
        }
        
        expected_keywords = persona_keywords.get(expected_persona, [])
        text_lower = response.response_text.lower()
        
        alignment_score = 0.0
        for keyword in expected_keywords:
            if keyword in text_lower:
                alignment_score += 0.2
        
        return min(alignment_score, 1.0)
    
    def _calculate_overall_quality(self, response: AgentResponse, scenario: Dict) -> float:
        """Calculate overall response quality score"""
        scores = [
            response.confidence_score * 0.3,
            self._assess_actionability(response) * 0.25,
            self._assess_persona_alignment(response, scenario['persona']) * 0.25,
            self._assess_context_awareness(response) * 0.2
        ]
        
        return sum(scores)
    
    def _display_response_analysis(self, analysis: Dict[str, Any]):
        """Display detailed response analysis"""
        print(f"⏱️  Response Time: {analysis['response_time']:.2f}s")
        print(f"🎯 Intent Type: {analysis['intent_type']}")
        print(f"📊 Confidence: {analysis['confidence_score']:.1%}")
        print(f"🧠 Thinking Required: {analysis['thinking_required']}")
        
        if analysis['chain_of_thought']:
            cot = analysis['chain_of_thought']
            print(f"🔗 Chain of Thought: {cot['steps_count']} steps, {cot['final_confidence']:.1%} confidence")
        
        print(f"📈 Quality Scores:")
        print(f"   • Overall Quality: {analysis['overall_quality']:.1%}")
        print(f"   • Actionability: {analysis['actionability']:.1%}")
        print(f"   • Persona Alignment: {analysis['persona_alignment']:.1%}")
        print(f"   • Context Awareness: {analysis['context_awareness']:.1%}")
        
        print(f"🔍 Data Sources: {', '.join(analysis['data_sources_used']) if analysis['data_sources_used'] else 'None'}")
        
        # Show response preview
        response_preview = analysis['response_text'][:200] + "..." if len(analysis['response_text']) > 200 else analysis['response_text']
        print(f"💬 Response Preview: {response_preview}")
        
        # Quality assessment
        if analysis['overall_quality'] >= 0.8:
            print("✅ EXCELLENT - Ready for deployment")
        elif analysis['overall_quality'] >= 0.6:
            print("⚠️  GOOD - Minor improvements needed")
        else:
            print("❌ NEEDS IMPROVEMENT - Review required")
    
    def _generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        # Overall statistics
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r.get('status') != 'failed'])
        failed_tests = total_tests - successful_tests
        
        print(f"📈 Test Summary:")
        print(f"   • Total Tests: {total_tests}")
        print(f"   • Successful: {successful_tests}")
        print(f"   • Failed: {failed_tests}")
        print(f"   • Success Rate: {successful_tests/total_tests:.1%}")
        
        # Performance metrics
        response_times = [r['response_time'] for r in self.test_results if 'response_time' in r]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            print(f"⏱️  Performance Metrics:")
            print(f"   • Average Response Time: {avg_time:.2f}s")
            print(f"   • Fastest Response: {min_time:.2f}s")
            print(f"   • Slowest Response: {max_time:.2f}s")
        
        # Quality metrics
        quality_scores = [r['overall_quality'] for r in self.test_results if 'overall_quality' in r]
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            excellent_count = len([q for q in quality_scores if q >= 0.8])
            good_count = len([q for q in quality_scores if 0.6 <= q < 0.8])
            needs_improvement_count = len([q for q in quality_scores if q < 0.6])
            
            print(f"🎯 Quality Metrics:")
            print(f"   • Average Quality Score: {avg_quality:.1%}")
            print(f"   • Excellent Responses: {excellent_count}")
            print(f"   • Good Responses: {good_count}")
            print(f"   • Needs Improvement: {needs_improvement_count}")
        
        # Thinking analysis
        thinking_responses = [r for r in self.test_results if r.get('thinking_required')]
        if thinking_responses:
            print(f"🧠 Thinking Analysis:")
            print(f"   • Thinking Responses: {len(thinking_responses)}")
            print(f"   • Thinking Rate: {len(thinking_responses)/total_tests:.1%}")
            
            cot_scores = [r['chain_of_thought']['final_confidence'] for r in thinking_responses if r.get('chain_of_thought')]
            if cot_scores:
                avg_cot_confidence = sum(cot_scores) / len(cot_scores)
                print(f"   • Average CoT Confidence: {avg_cot_confidence:.1%}")
        
        # Deployment recommendation
        print(f"\n🚀 DEPLOYMENT RECOMMENDATION:")
        if successful_tests/total_tests >= 0.9 and avg_quality >= 0.7:
            print("✅ READY FOR DEPLOYMENT - High success rate and quality scores")
        elif successful_tests/total_tests >= 0.8 and avg_quality >= 0.6:
            print("⚠️  CONDITIONAL DEPLOYMENT - Monitor closely and be ready to rollback")
        else:
            print("❌ NOT READY FOR DEPLOYMENT - Address issues before deployment")
        
        # Save detailed results
        self._save_detailed_results()
    
    def _save_detailed_results(self):
        """Save detailed test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{timestamp}.json"
        
        # Prepare results for JSON serialization
        serializable_results = []
        for result in self.test_results:
            serializable_result = {}
            for key, value in result.items():
                if hasattr(value, 'value'):  # Handle enums
                    serializable_result[key] = value.value
                elif hasattr(value, '__dict__'):  # Handle objects
                    serializable_result[key] = str(value)
                else:
                    serializable_result[key] = value
            serializable_results.append(serializable_result)
        
        with open(filename, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"📄 Detailed results saved to: {filename}")

async def main():
    """Main testing function"""
    tester = ResponseTester()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())
