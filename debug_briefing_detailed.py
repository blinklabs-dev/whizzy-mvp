#!/usr/bin/env python3
"""Detailed debug briefing system"""

import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from briefing_system import BriefingSystem, PersonaType, BriefingType

async def debug_briefing_detailed():
    print("🔍 Detailed Debugging Briefing System")
    print("=" * 50)
    
    # Mock Salesforce client
    class MockSalesforceClient:
        def query(self, query):
            return {
                'records': [
                    {'total_opps': 385, 'total_pipeline': 97063009.0},
                    {'total': 704},
                    {'won': 159},
                    {'lost': 545},
                    {'stuck_count': 0}
                ]
            }
    
    # Mock OpenAI client
    class MockOpenAIClient:
        pass
    
    sf_client = MockSalesforceClient()
    openai_client = MockOpenAIClient()
    
    briefing_system = BriefingSystem(sf_client, openai_client)
    
    # Test AE briefing step by step
    print("\n👤 Testing AE Briefing Step by Step...")
    ae_query = "AE briefing"
    ae_persona = PersonaType.ACCOUNT_EXECUTIVE
    
    print(f"Query: {ae_query}")
    print(f"Persona: {ae_persona}")
    
    ae_type = briefing_system._classify_briefing_type(ae_query, ae_persona)
    print(f"Classified Type: {ae_type}")
    
    try:
        ae_metrics = await briefing_system._extract_metrics(ae_query, ae_type)
        print(f"Metrics extracted: {len(ae_metrics)} items")
        
        ae_insights, ae_actions = await briefing_system._generate_insights_actions(ae_query, ae_persona, ae_metrics, ae_type)
        print(f"Insights: {len(ae_insights)}")
        print(f"Actions: {len(ae_actions)}")
        
        ae_headline = briefing_system._generate_headline(ae_type, ae_metrics, ae_persona)
        print(f"Headline: {ae_headline}")
        
        # Create contract
        from datetime import datetime
        ae_contract = briefing_system.BriefingContract(
            headline=ae_headline,
            pipeline=ae_metrics,
            insights=ae_insights,
            actions=ae_actions,
            persona=ae_persona,
            briefing_type=ae_type,
            timestamp=datetime.now().isoformat()
        )
        
        print(f"Contract Type: {ae_contract.briefing_type}")
        ae_markdown = ae_contract.to_slack_markdown()
        print(f"Markdown starts with: {ae_markdown[:100]}...")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Test CDO DBT model step by step
    print("\n📊 Testing CDO DBT Model Step by Step...")
    cdo_query = "As a CDO can you create win rate forecast pipeline"
    cdo_persona = PersonaType.CDO
    
    print(f"Query: {cdo_query}")
    print(f"Persona: {cdo_persona}")
    
    cdo_type = briefing_system._classify_briefing_type(cdo_query, cdo_persona)
    print(f"Classified Type: {cdo_type}")
    
    try:
        cdo_metrics = await briefing_system._extract_metrics(cdo_query, cdo_type)
        print(f"Metrics extracted: {len(cdo_metrics)} items")
        print(f"Metrics keys: {list(cdo_metrics.keys())}")
        
        cdo_insights, cdo_actions = await briefing_system._generate_insights_actions(cdo_query, cdo_persona, cdo_metrics, cdo_type)
        print(f"Insights: {len(cdo_insights)}")
        print(f"Actions: {len(cdo_actions)}")
        
        cdo_headline = briefing_system._generate_headline(cdo_type, cdo_metrics, cdo_persona)
        print(f"Headline: {cdo_headline}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Detailed Debug Complete!")

if __name__ == "__main__":
    asyncio.run(debug_briefing_detailed())
