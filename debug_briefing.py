#!/usr/bin/env python3
"""Debug briefing system"""

import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from briefing_system import BriefingSystem, PersonaType, BriefingType

async def debug_briefing():
    print("🔍 Debugging Briefing System")
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
    
    # Test AE briefing
    print("\n👤 Testing AE Briefing Classification...")
    ae_type = briefing_system._classify_briefing_type("AE briefing", PersonaType.ACCOUNT_EXECUTIVE)
    print(f"AE Briefing Type: {ae_type}")
    print(f"Expected: {BriefingType.STUCK_DEALS}")
    print(f"Match: {ae_type == BriefingType.STUCK_DEALS}")
    
    # Test VP briefing
    print("\n👔 Testing VP Briefing Classification...")
    vp_type = briefing_system._classify_briefing_type("VP sales briefing", PersonaType.VP_SALES)
    print(f"VP Briefing Type: {vp_type}")
    print(f"Expected: {BriefingType.PIPELINE_COVERAGE}")
    print(f"Match: {vp_type == BriefingType.PIPELINE_COVERAGE}")
    
    # Test CDO briefing
    print("\n📊 Testing CDO Briefing Classification...")
    cdo_type = briefing_system._classify_briefing_type("As a CDO can you create win rate forecast pipeline", PersonaType.CDO)
    print(f"CDO Briefing Type: {cdo_type}")
    print(f"Expected: {BriefingType.DBT_MODEL}")
    print(f"Match: {cdo_type == BriefingType.DBT_MODEL}")
    
    print("\n" + "=" * 50)
    print("✅ Debug Complete!")

if __name__ == "__main__":
    asyncio.run(debug_briefing())
