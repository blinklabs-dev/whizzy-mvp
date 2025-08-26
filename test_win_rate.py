#!/usr/bin/env python3
"""
Simple test script to verify win rate calculation
"""

import os
import sys
from simple_salesforce import Salesforce
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_win_rate():
    """Test win rate calculation"""
    try:
        # Initialize Salesforce connection
        sf = Salesforce(
            username=os.getenv('SALESFORCE_USERNAME'),
            password=os.getenv('SALESFORCE_PASSWORD'),
            security_token=os.getenv('SALESFORCE_SECURITY_TOKEN'),
            domain=os.getenv('SALESFORCE_DOMAIN', 'login')
        )
        
        print("✅ Salesforce connection successful")
        
        # Test win rate calculation
        print("\n📊 Testing Win Rate Calculation...")
        
        # Get total opportunities
        total_result = sf.query("SELECT COUNT(Id) total FROM Opportunity")
        total = total_result['records'][0]['total']
        print(f"Total opportunities: {total}")
        
        # Get won opportunities
        won_result = sf.query("SELECT COUNT(Id) won FROM Opportunity WHERE StageName = 'Closed Won'")
        won = won_result['records'][0]['won']
        print(f"Won opportunities: {won}")
        
        # Get lost opportunities
        lost_result = sf.query("SELECT COUNT(Id) lost FROM Opportunity WHERE StageName = 'Closed Lost'")
        lost = lost_result['records'][0]['lost']
        print(f"Lost opportunities: {lost}")
        
        # Calculate win rate
        win_rate = (won / total * 100) if total > 0 else 0
        print(f"\n🎯 Win Rate: {win_rate:.1f}%")
        print(f"📈 Success ratio: {won}:{lost} (won:lost)")
        
        # Test pipeline query
        print("\n📊 Testing Pipeline Query...")
        pipeline_result = sf.query(
            "SELECT StageName, COUNT(Id) total_count, SUM(Amount) total_amount "
            "FROM Opportunity WHERE IsClosed = false "
            "GROUP BY StageName ORDER BY SUM(Amount) DESC"
        )
        
        print("Pipeline stages:")
        for record in pipeline_result['records']:
            stage = record['StageName']
            count = record['total_count']
            amount = record['total_amount'] or 0
            print(f"  • {stage}: {count} opportunities, ${amount:,.0f}")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_win_rate()
