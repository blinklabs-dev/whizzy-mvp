#!/usr/bin/env python3
"""
Quick test to validate basic functionality and see actual responses
"""

import asyncio
from dotenv import load_dotenv
from app.intelligent_agentic_system import EnhancedIntelligentAgenticSystem

load_dotenv()

async def quick_test():
    """Quick test of the enhanced system"""
    print("🧠 Quick Test - Enhanced Intelligent Agentic System")
    print("=" * 50)

    system = EnhancedIntelligentAgenticSystem()

    # Test a simple query
    query = "What's our current pipeline health?"

    print(f"📝 Query: {query}")
    print("-" * 30)

    try:
        response = await system.process_query(query, {})

        print(f"✅ Response generated!")
        print(f"📊 Confidence: {response.confidence_score:.1%}")
        print(f"🔍 Data Sources: {[ds.value for ds in response.data_sources_used]}")
        print(f"🧠 Chain of Thought: {'Yes' if response.chain_of_thought else 'No'}")

        print(f"\n💬 Response Text:")
        print(response.response_text)

        if response.chain_of_thought:
            print(f"\n🔗 Chain of Thought Details:")
            print(f"   • Steps: {len(response.chain_of_thought.thinking_steps)}")
            print(f"   • Final Confidence: {response.chain_of_thought.final_confidence:.1%}")
            print(f"   • Reasoning Path: {response.chain_of_thought.reasoning_path[:200]}...")

        print(f"\n📈 Quality Metrics:")
        for key, value in response.quality_metrics.items():
            print(f"   • {key}: {value:.1%}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(quick_test())
