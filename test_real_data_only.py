#!/usr/bin/env python3
"""
Test Real Data Connections Only (No OpenAI)
Tests Salesforce and Snowflake connections without using LLM
"""

import os
import asyncio
import json
from dotenv import load_dotenv
from simple_salesforce import Salesforce
import snowflake.connector

# Load environment variables
load_dotenv()

async def test_salesforce_connection():
    """Test real Salesforce connection"""
    print("🔍 Testing Salesforce Connection...")
    
    try:
        sf = Salesforce(
            username=os.getenv('SALESFORCE_USERNAME'),
            password=os.getenv('SALESFORCE_PASSWORD'),
            security_token=os.getenv('SALESFORCE_SECURITY_TOKEN')
        )
        
        # Test basic query
        result = sf.query('SELECT Id, Name, Amount, StageName FROM Opportunity LIMIT 5')
        
        print(f"✅ Salesforce Connected!")
        print(f"📊 Found {result['totalSize']} opportunities")
        
        for record in result['records']:
            print(f"  - {record['Name']}: ${record.get('Amount', 0)} ({record['StageName']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Salesforce Error: {e}")
        return False

async def test_snowflake_connection():
    """Test real Snowflake connection"""
    print("\n🔍 Testing Snowflake Connection...")
    
    try:
        conn = snowflake.connector.connect(
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            role=os.getenv('SNOWFLAKE_ROLE'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA')
        )
        
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT COUNT(*) as total_opportunities FROM stg_sf__opportunity")
        result = cursor.fetchone()
        
        print(f"✅ Snowflake Connected!")
        print(f"📊 Found {result[0]} opportunities in staging")
        
        # Test executive briefing query
        cursor.execute("""
        SELECT 
            COUNT(*) as total_opportunities,
            SUM(OPPORTUNITY_AMOUNT) as total_pipeline_value,
            AVG(OPPORTUNITY_AMOUNT) as avg_deal_size,
            COUNT(CASE WHEN STAGE_NAME = 'Closed Won' THEN 1 END) as won_opportunities,
            COUNT(CASE WHEN STAGE_NAME = 'Closed Won' THEN 1 END) / NULLIF(COUNT(*), 0) as win_rate
        FROM stg_sf__opportunity 
        WHERE OPPORTUNITY_AMOUNT > 0
        """)
        
        exec_data = cursor.fetchone()
        print(f"📈 Executive Summary:")
        print(f"  - Total Opportunities: {exec_data[0]}")
        print(f"  - Pipeline Value: ${exec_data[1]:,.2f}")
        print(f"  - Avg Deal Size: ${exec_data[2]:,.2f}")
        print(f"  - Won Opportunities: {exec_data[3]}")
        print(f"  - Win Rate: {exec_data[4]:.1%}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Snowflake Error: {e}")
        return False

async def test_real_data_flow():
    """Test the complete real data flow"""
    print("\n🔍 Testing Complete Real Data Flow...")
    
    # Test Salesforce
    sf_success = await test_salesforce_connection()
    
    # Test Snowflake
    snowflake_success = await test_snowflake_connection()
    
    if sf_success and snowflake_success:
        print("\n🎉 SUCCESS: All real data connections working!")
        print("✅ Salesforce: Real data accessible")
        print("✅ Snowflake: Real analytics working")
        print("✅ Ready for production use!")
    else:
        print("\n❌ Some connections failed")
        print(f"Salesforce: {'✅' if sf_success else '❌'}")
        print(f"Snowflake: {'✅' if snowflake_success else '❌'}")

if __name__ == "__main__":
    print("🧪 Testing Real Data Connections (No OpenAI)")
    print("=" * 50)
    asyncio.run(test_real_data_flow())
