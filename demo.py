#!/usr/bin/env python3
"""
Demo script for Text2SOQL MVP
Shows how to use the MCP server tools programmatically
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_server.main import handle_sf_query, handle_health, initialize_salesforce
from utils.logging import setup_logging

logger = setup_logging(__name__)


async def demo_health_check():
    """Demo the health check functionality."""
    print("🔍 Running health check...")
    
    try:
        result = await handle_health()
        print("✅ Health check result:")
        print(json.dumps(result, indent=2))
        return result
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return None


async def demo_salesforce_query(soql: str, limit: int = 5):
    """Demo the Salesforce query functionality."""
    print(f"🔍 Running SOQL query: {soql}")
    
    try:
        result = await handle_sf_query(soql, limit)
        print("✅ Query result:")
        print(json.dumps(result, indent=2))
        return result
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return None


async def run_demo():
    """Run the complete demo."""
    print("🚀 Text2SOQL MVP Demo")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Initialize Salesforce
    print("🔌 Initializing Salesforce connection...")
    try:
        await initialize_salesforce()
        print("✅ Salesforce initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Salesforce: {e}")
        print("💡 Make sure your .env file has the correct Salesforce credentials")
        return
    
    # Run health check
    print("\n" + "=" * 50)
    health_result = await demo_health_check()
    
    if not health_result or health_result.get("status") != "healthy":
        print("❌ Health check failed. Please check your configuration.")
        return
    
    # Run sample queries
    print("\n" + "=" * 50)
    print("📊 Running sample queries...")
    
    sample_queries = [
        "SELECT Id, Name FROM Account LIMIT 3",
        "SELECT Id, Name, StageName FROM Opportunity LIMIT 3",
        "SELECT Id, FirstName, LastName FROM Contact LIMIT 3"
    ]
    
    for i, query in enumerate(sample_queries, 1):
        print(f"\n--- Query {i} ---")
        result = await demo_salesforce_query(query)
        
        if result and result.get("success"):
            records = result.get("records", [])
            print(f"📈 Found {len(records)} records")
            
            # Show first record as example
            if records:
                print("📋 Sample record:")
                print(json.dumps(records[0], indent=2))
        else:
            print("⚠️  Query returned no results or failed")
    
    print("\n" + "=" * 50)
    print("✅ Demo completed!")
    print("\n💡 Next steps:")
    print("1. Add the MCP configuration to Cursor")
    print("2. Try querying from Cursor Chat")
    print("3. Run the seeding script: python scripts/seed_data.py")


if __name__ == "__main__":
    asyncio.run(run_demo())
