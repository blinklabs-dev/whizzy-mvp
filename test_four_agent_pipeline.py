#!/usr/bin/env python3
"""Test the four-agent pipeline for coffee briefings"""

import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from intelligent_agentic_system import EnhancedIntelligentAgenticSystem

async def test_four_agent_pipeline():
    print("🧪 Testing Four-Agent Pipeline for Coffee Briefings")
    print("=" * 60)
    
    system = EnhancedIntelligentAgenticSystem()
    
    # Test coffee briefing through four-agent pipeline
    print("\n👤 Testing AE Briefing through Four-Agent Pipeline...")
    try:
        response = await system.process_query("AE briefing", None, None)
        print(f"Response: {response.response_text[:200]}...")
        print(f"Confidence: {response.confidence_score}")
        print(f"Data Sources: {[ds.value for ds in response.data_sources_used]}")
        print(f"Reasoning Steps: {response.reasoning_steps}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n👔 Testing VP Briefing through Four-Agent Pipeline...")
    try:
        response = await system.process_query("VP sales briefing", None, None)
        print(f"Response: {response.response_text[:200]}...")
        print(f"Confidence: {response.confidence_score}")
        print(f"Data Sources: {[ds.value for ds in response.data_sources_used]}")
        print(f"Reasoning Steps: {response.reasoning_steps}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n📊 Testing CDO DBT Model through Four-Agent Pipeline...")
    try:
        response = await system.process_query("As a CDO can you create win rate forecast pipeline", None, None)
        print(f"Response: {response.response_text[:200]}...")
        print(f"Confidence: {response.confidence_score}")
        print(f"Data Sources: {[ds.value for ds in response.data_sources_used]}")
        print(f"Reasoning Steps: {response.reasoning_steps}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Four-Agent Pipeline Tests Complete!")

if __name__ == "__main__":
    asyncio.run(test_four_agent_pipeline())
