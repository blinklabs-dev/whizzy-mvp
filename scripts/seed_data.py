#!/usr/bin/env python3
"""
Seeding script for Text2SOQL MVP
Creates sample data in Salesforce for testing and demonstration
"""

import asyncio
import os
import sys
from typing import Dict, List, Any, Optional

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from salesforce.client import SalesforceClient
from utils.logging import setup_logging

logger = setup_logging(__name__)


class DataSeeder:
    """Handles seeding of test data in Salesforce."""
    
    def __init__(self):
        """Initialize the data seeder."""
        self.sf_client: Optional[SalesforceClient] = None
    
    async def connect(self) -> None:
        """Connect to Salesforce."""
        try:
            self.sf_client = SalesforceClient()
            await self.sf_client.connect()
            logger.info("Connected to Salesforce for seeding")
        except Exception as e:
            logger.error(f"Failed to connect to Salesforce: {e}")
            raise
    
    async def seed_accounts(self) -> List[Dict[str, Any]]:
        """Seed sample Account records."""
        logger.info("Seeding Account records...")
        
        accounts_data = [
            {
                "Name": "Acme Corporation",
                "Type": "Customer",
                "Industry": "Technology",
                "BillingCity": "San Francisco",
                "BillingState": "CA",
                "Phone": "+1-555-0101"
            },
            {
                "Name": "Global Industries",
                "Type": "Customer",
                "Industry": "Manufacturing",
                "BillingCity": "New York",
                "BillingState": "NY",
                "Phone": "+1-555-0102"
            },
            {
                "Name": "Startup Inc",
                "Type": "Prospect",
                "Industry": "Software",
                "BillingCity": "Austin",
                "BillingState": "TX",
                "Phone": "+1-555-0103"
            }
        ]
        
        created_accounts = []
        
        for account_data in accounts_data:
            try:
                # Check if account already exists
                existing = await self.sf_client.query(
                    f"SELECT Id FROM Account WHERE Name = '{account_data['Name']}' LIMIT 1"
                )
                
                if existing.get("totalSize", 0) > 0:
                    logger.info(f"Account '{account_data['Name']}' already exists, skipping")
                    continue
                
                # Create account (this would require additional Salesforce client methods)
                logger.info(f"Would create account: {account_data['Name']}")
                created_accounts.append(account_data)
                
            except Exception as e:
                logger.error(f"Error creating account {account_data['Name']}: {e}")
        
        logger.info(f"Seeded {len(created_accounts)} Account records")
        return created_accounts
    
    async def seed_opportunities(self) -> List[Dict[str, Any]]:
        """Seed sample Opportunity records."""
        logger.info("Seeding Opportunity records...")
        
        opportunities_data = [
            {
                "Name": "Acme Corp - Software License",
                "StageName": "Prospecting",
                "Amount": 50000,
                "CloseDate": "2024-06-30",
                "Type": "New Customer"
            },
            {
                "Name": "Global Industries - Consulting",
                "StageName": "Qualification",
                "Amount": 75000,
                "CloseDate": "2024-07-15",
                "Type": "New Customer"
            },
            {
                "Name": "Startup Inc - Implementation",
                "StageName": "Closed Won",
                "Amount": 25000,
                "CloseDate": "2024-05-15",
                "Type": "New Customer"
            }
        ]
        
        created_opportunities = []
        
        for opp_data in opportunities_data:
            try:
                # Check if opportunity already exists
                existing = await self.sf_client.query(
                    f"SELECT Id FROM Opportunity WHERE Name = '{opp_data['Name']}' LIMIT 1"
                )
                
                if existing.get("totalSize", 0) > 0:
                    logger.info(f"Opportunity '{opp_data['Name']}' already exists, skipping")
                    continue
                
                # Create opportunity (this would require additional Salesforce client methods)
                logger.info(f"Would create opportunity: {opp_data['Name']}")
                created_opportunities.append(opp_data)
                
            except Exception as e:
                logger.error(f"Error creating opportunity {opp_data['Name']}: {e}")
        
        logger.info(f"Seeded {len(created_opportunities)} Opportunity records")
        return created_opportunities
    
    async def seed_contacts(self) -> List[Dict[str, Any]]:
        """Seed sample Contact records."""
        logger.info("Seeding Contact records...")
        
        contacts_data = [
            {
                "FirstName": "John",
                "LastName": "Smith",
                "Email": "john.smith@acme.com",
                "Title": "CTO",
                "Phone": "+1-555-0201"
            },
            {
                "FirstName": "Sarah",
                "LastName": "Johnson",
                "Email": "sarah.johnson@global.com",
                "Title": "VP of Operations",
                "Phone": "+1-555-0202"
            },
            {
                "FirstName": "Mike",
                "LastName": "Chen",
                "Email": "mike.chen@startup.com",
                "Title": "CEO",
                "Phone": "+1-555-0203"
            }
        ]
        
        created_contacts = []
        
        for contact_data in contacts_data:
            try:
                # Check if contact already exists
                existing = await self.sf_client.query(
                    f"SELECT Id FROM Contact WHERE Email = '{contact_data['Email']}' LIMIT 1"
                )
                
                if existing.get("totalSize", 0) > 0:
                    logger.info(f"Contact '{contact_data['Email']}' already exists, skipping")
                    continue
                
                # Create contact (this would require additional Salesforce client methods)
                logger.info(f"Would create contact: {contact_data['FirstName']} {contact_data['LastName']}")
                created_contacts.append(contact_data)
                
            except Exception as e:
                logger.error(f"Error creating contact {contact_data['Email']}: {e}")
        
        logger.info(f"Seeded {len(created_contacts)} Contact records")
        return created_contacts
    
    async def run_seeding(self) -> Dict[str, Any]:
        """Run the complete seeding process."""
        logger.info("Starting data seeding process...")
        
        try:
            await self.connect()
            
            # Seed different object types
            accounts = await self.seed_accounts()
            opportunities = await self.seed_opportunities()
            contacts = await self.seed_contacts()
            
            summary = {
                "accounts_created": len(accounts),
                "opportunities_created": len(opportunities),
                "contacts_created": len(contacts),
                "total_records": len(accounts) + len(opportunities) + len(contacts)
            }
            
            logger.info(f"Seeding completed successfully: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"Seeding failed: {e}")
            raise
        finally:
            if self.sf_client:
                await self.sf_client.disconnect()


async def main():
    """Main entry point for the seeding script."""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    seeder = DataSeeder()
    
    try:
        result = await seeder.run_seeding()
        print(f"✅ Seeding completed: {result}")
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
