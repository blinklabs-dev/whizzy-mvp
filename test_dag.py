#!/usr/bin/env python3
"""
Test script for the Multi-Agent DAG architecture
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
load_dotenv()

from multi_agent_dag import MultiAgentDAG

async def test_dag():
    """Test the DAG with different query types"""
    
    print("🧪 Testing Multi-Agent DAG Architecture")
    print("=" * 50)
    
    # Initialize DAG
    dag = MultiAgentDAG()
    
    # Test queries
    test_queries = [
        "What's our win rate?",
        "vp sales briefing", 
        "Show slippage this quarter",
        "What can you do?",
        "Top 10 accounts by revenue"
    ]
    
    # Mock conversation history and schema
    conversation_history = []
    schema = """
    Salesforce Schema:
    Object: Opportunity
    Fields:
    - Id (id)
    - Name (string)
    - Amount (currency)
    - StageName (picklist)
    - CloseDate (date)
    - IsWon (boolean)
    - IsClosed (boolean)
    
    Object: Account
    Fields:
    - Id (id)
    - Name (string)
    - AnnualRevenue (currency)
    - Industry (picklist)
    """
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 30)
        
        try:
            response = await dag.execute(query, conversation_history, schema)
            print(f"✅ Response: {response[:200]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_dag())
