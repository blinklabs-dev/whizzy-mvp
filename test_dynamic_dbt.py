#!/usr/bin/env python3
"""
Test script for dynamic DBT model generation
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

async def test_dynamic_dbt():
    """Test dynamic DBT model generation with complex analytics requests"""
    
    print("🧪 Testing Dynamic DBT Model Generation")
    print("=" * 50)
    
    # Initialize DAG
    dag = MultiAgentDAG()
    
    # Test queries that should trigger dynamic DBT generation
    test_queries = [
        "Show me customer lifetime value analysis with churn prediction and cohort analysis",
        "Create a model for lead scoring based on engagement patterns and conversion history",
        "Build a predictive model for deal success probability using machine learning features",
        "Generate a comprehensive customer segmentation analysis with behavioral patterns",
        "Create a model for sales forecasting using advanced time series analysis"
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
    - OwnerId (reference)
    
    Object: Account
    Fields:
    - Id (id)
    - Name (string)
    - AnnualRevenue (currency)
    - Industry (picklist)
    
    Object: User
    Fields:
    - Id (id)
    - Name (string)
    - Email (string)
    """
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 50)
        
        try:
            response = await dag.execute(query, conversation_history, schema)
            print(f"✅ Response: {response[:300]}...")
            
            # Check if any new DBT models were created
            if "new DBT model" in response or "created and executed" in response:
                print("🎉 Dynamic DBT model generation triggered!")
            else:
                print("ℹ️  Using existing models")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    asyncio.run(test_dynamic_dbt())
