#!/usr/bin/env python3
"""Test AE, VP, and CDO briefing fixes"""

import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from intelligent_agentic_system import EnhancedIntelligentAgenticSystem

async def test_briefings():
    print("🧪 Testing Briefing Fixes")
    print("=" * 50)
    
    system = EnhancedIntelligentAgenticSystem()
    
    # Test AE Briefing
    print("\n👤 Testing AE Briefing...")
    response = await system._handle_coffee_briefing("AE briefing", None, None)
    print(f"Response: {response.response_text}")
    print(f"Length: {len(response.response_text)}")
    
    # Check if it's AE-specific content
    has_stuck_deals = any(word in response.response_text.lower() for word in ["stuck", "deals", "days"])
    has_ae_context = any(word in response.response_text.lower() for word in ["account executive", "ae", "individual"])
    print(f"Has Stuck Deals: {has_stuck_deals}")
    print(f"Has AE Context: {has_ae_context}")
    
    # Test VP Briefing
    print("\n👔 Testing VP Briefing...")
    response = await system._handle_coffee_briefing("VP sales briefing", None, None)
    print(f"Response: {response.response_text}")
    print(f"Length: {len(response.response_text)}")
    
    # Check if it's VP-specific content
    has_pipeline = any(word in response.response_text.lower() for word in ["pipeline", "coverage", "quota"])
    has_vp_context = any(word in response.response_text.lower() for word in ["vp", "vice president", "strategic"])
    print(f"Has Pipeline: {has_pipeline}")
    print(f"Has VP Context: {has_vp_context}")
    
    # Test CDO DBT Model Creation
    print("\n📊 Testing CDO DBT Model Creation...")
    response = await system._handle_coffee_briefing("As a CDO can you create win rate forecast pipeline", None, None)
    print(f"Response: {response.response_text}")
    print(f"Length: {len(response.response_text)}")
    
    # Check if it's CDO-specific content
    has_dbt = any(word in response.response_text.lower() for word in ["dbt", "model", "generated"])
    has_cdo_context = any(word in response.response_text.lower() for word in ["cdo", "data quality", "analytics"])
    print(f"Has DBT Model: {has_dbt}")
    print(f"Has CDO Context: {has_cdo_context}")
    
    # Test CDO Forecast Accuracy
    print("\n📈 Testing CDO Forecast Accuracy...")
    response = await system._handle_coffee_briefing("As a CDO show me forecast accuracy", None, None)
    print(f"Response: {response.response_text}")
    print(f"Length: {len(response.response_text)}")
    
    # Check if it's forecast-specific content
    has_forecast = any(word in response.response_text.lower() for word in ["forecast", "accuracy", "prediction"])
    print(f"Has Forecast: {has_forecast}")
    
    print("\n" + "=" * 50)
    print("✅ Briefing Tests Complete!")

if __name__ == "__main__":
    asyncio.run(test_briefings())
