#!/usr/bin/env python3
"""
Enhanced Whizzy Bot - Spot Check Response Review
Purpose: Manual review of specific responses for quality validation
before deployment for live testing.
"""

import asyncio
import json
from typing import Dict, Any
from dotenv import load_dotenv

# Import enhanced system
from app.intelligent_agentic_system import EnhancedIntelligentAgenticSystem

# Load environment variables
load_dotenv()

class SpotChecker:
    """Manual spot check for response quality validation"""
    
    def __init__(self):
        self.enhanced_system = EnhancedIntelligentAgenticSystem()
    
    async def spot_check_responses(self):
        """Run spot checks on critical response scenarios"""
        print("🔍 Enhanced Whizzy Bot - Spot Check Response Review")
        print("=" * 60)
        
        # Critical scenarios for spot checking
        critical_scenarios = [
            {
                'name': 'CRITICAL: VP Sales Strategic Query',
                'query': 'What are our biggest risks to hitting Q4 targets and what should I focus on this week?',
                'persona': 'VP_SALES',
                'user_id': 'vp_sales_critical'
            },
            {
                'name': 'CRITICAL: AE Deal Preparation',
                'query': 'I have a meeting with a $500k opportunity tomorrow. What should I know and prepare for?',
                'persona': 'ACCOUNT_EXECUTIVE',
                'user_id': 'ae_critical'
            },
            {
                'name': 'CRITICAL: Complex Analytics',
                'query': 'Why are our sales cycles getting longer and what systemic issues should we address?',
                'persona': 'VP_SALES',
                'user_id': 'analytics_critical'
            },
            {
                'name': 'CRITICAL: Coffee Briefing',
                'query': 'Give me my morning briefing with key metrics and action items',
                'persona': 'VP_SALES',
                'user_id': 'briefing_critical'
            }
        ]
        
        for scenario in critical_scenarios:
            print(f"\n🎯 {scenario['name']}")
            print(f"📝 Query: {scenario['query']}")
            print("-" * 50)
            
            try:
                # Get response
                response = await self.enhanced_system.process_query(
                    scenario['query'],
                    {}
                )
                
                # Display full response for manual review
                print(f"💬 FULL RESPONSE:")
                print(response.response_text)
                print()
                
                # Display technical details
                print(f"🔧 TECHNICAL DETAILS:")
                print(f"   • Intent Type: Unknown (not stored in AgentResponse)")
                print(f"   • Confidence: {response.confidence_score:.1%}")
                print(f"   • Data Sources: {[ds.value for ds in response.data_sources_used] if response.data_sources_used else 'None'}")
                
                if response.chain_of_thought:
                    print(f"   • Chain of Thought: {len(response.chain_of_thought.thinking_steps)} steps")
                    print(f"   • Final Confidence: {response.chain_of_thought.final_confidence:.1%}")
                
                # Manual quality assessment
                self._manual_quality_assessment(response, scenario)
                
                # Wait for user input to continue
                input("\n⏸️  Press Enter to continue to next scenario...")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                input("\n⏸️  Press Enter to continue...")
    
    def _manual_quality_assessment(self, response: Any, scenario: Dict):
        """Guide manual quality assessment"""
        print(f"\n📊 MANUAL QUALITY ASSESSMENT:")
        print(f"Scenario: {scenario['name']}")
        print()
        
        # Quality criteria
        criteria = [
            "✅ Response is relevant to the query",
            "✅ Response provides actionable insights",
            "✅ Response is appropriate for the persona",
            "✅ Response uses appropriate data sources",
            "✅ Response demonstrates thinking/reasoning",
            "✅ Response is clear and well-structured",
            "✅ Response includes specific recommendations",
            "✅ Response shows context awareness"
        ]
        
        print("Rate each criterion (1-5, where 5 is excellent):")
        scores = {}
        
        for i, criterion in enumerate(criteria, 1):
            while True:
                try:
                    score = input(f"{i}. {criterion}: ")
                    score = int(score)
                    if 1 <= score <= 5:
                        scores[criterion] = score
                        break
                    else:
                        print("Please enter a score between 1 and 5")
                except ValueError:
                    print("Please enter a valid number")
        
        # Calculate average score
        avg_score = sum(scores.values()) / len(scores)
        print(f"\n📈 Average Quality Score: {avg_score:.1f}/5.0")
        
        if avg_score >= 4.0:
            print("✅ EXCELLENT - Ready for deployment")
        elif avg_score >= 3.0:
            print("⚠️  GOOD - Minor improvements needed")
        else:
            print("❌ NEEDS IMPROVEMENT - Review required")
        
        # Store assessment
        assessment = {
            'scenario': scenario['name'],
            'query': scenario['query'],
            'persona': scenario['persona'],
            'scores': scores,
            'average_score': avg_score,
            'response_preview': response.response_text[:200] + "..." if len(response.response_text) > 200 else response.response_text
        }
        
        # Save to file
        self._save_assessment(assessment)
    
    def _save_assessment(self, assessment: Dict):
        """Save manual assessment to file"""
        try:
            with open('spot_check_assessments.json', 'a') as f:
                f.write(json.dumps(assessment) + '\n')
        except Exception as e:
            print(f"Warning: Could not save assessment: {e}")

async def main():
    """Main spot check function"""
    checker = SpotChecker()
    await checker.spot_check_responses()

if __name__ == "__main__":
    asyncio.run(main())
