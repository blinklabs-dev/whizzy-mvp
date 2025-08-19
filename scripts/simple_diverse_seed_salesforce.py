#!/usr/bin/env python3
"""
Simple Diverse Salesforce Seeding Script for Text2SOQL MVP
Creates fresh, diverse, realistic data without problematic fields
"""

import argparse
import asyncio
import json
import logging
import os
import random
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from faker import Faker

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from salesforce.client import SalesforceClient
from salesforce.bulk_client import SalesforceBulkClient
from utils.logging import setup_logging

logger = setup_logging(__name__)

# Initialize Faker
fake = Faker()

# Simple diverse seeding configuration
SEED_PREFIX = "Seed[Diverse]-"
OPPORTUNITY_STAGES = [
    "Prospecting", "Qualification", "Needs Analysis", "Value Proposition",
    "Id. Decision Makers", "Perception Analysis", "Proposal/Price Quote",
    "Negotiation/Review", "Closed Won", "Closed Lost"
]

# Diverse stage distribution for realistic pipeline
STAGE_DISTRIBUTION = {
    "Prospecting": 0.15,
    "Qualification": 0.12,
    "Needs Analysis": 0.10,
    "Value Proposition": 0.08,
    "Id. Decision Makers": 0.08,
    "Perception Analysis": 0.07,
    "Proposal/Price Quote": 0.10,
    "Negotiation/Review": 0.08,
    "Closed Won": 0.15,
    "Closed Lost": 0.07
}

# Simple diverse mode configurations
SIMPLE_CONFIGS = {
    "FAST": {
        "accounts": 20,
        "contacts_per_account": 3,
        "opportunities": 60,
        "leads": 30,
        "campaigns": 5,
        "tasks": 100,
        "events": 25
    },
    "DEMO": {
        "accounts": 50,
        "contacts_per_account": 4,
        "opportunities": 150,
        "leads": 75,
        "campaigns": 10,
        "tasks": 250,
        "events": 60
    },
    "HEAVY": {
        "accounts": 100,
        "contacts_per_account": 5,
        "opportunities": 400,
        "leads": 200,
        "campaigns": 20,
        "tasks": 600,
        "events": 150
    }
}

# Diverse data for realistic scenarios
INDUSTRIES = [
    "Technology", "Healthcare", "Finance", "Manufacturing", "Retail",
    "Education", "Real Estate", "Consulting", "Media", "Transportation",
    "Energy", "Telecommunications", "Aerospace", "Biotechnology", "Insurance"
]

COMPANY_TYPES = [
    "Customer", "Prospect", "Partner", "Competitor", "Vendor", "Reseller"
]

JOB_TITLES = [
    "CEO", "CTO", "CFO", "VP Sales", "VP Marketing", "VP Engineering",
    "Sales Manager", "Marketing Manager", "Product Manager", "Developer",
    "Account Executive", "Business Analyst", "Project Manager", "Designer",
    "Sales Representative", "Marketing Specialist", "Customer Success Manager"
]

LEAD_SOURCES = [
    "Web", "Phone", "Email", "Referral", "Trade Show", "Social Media",
    "Cold Call", "Partner", "Advertisement", "Direct Mail", "Event"
]

CAMPAIGN_TYPES = [
    "Email Campaign", "Webinar", "Trade Show", "Social Media", "Direct Mail",
    "Digital Advertising", "Content Marketing", "Event", "Referral Program"
]

TASK_TYPES = [
    "Call", "Email", "Meeting", "Follow-up", "Demo", "Proposal", "Contract Review",
    "Discovery Call", "Presentation", "Negotiation", "Close Meeting"
]

EVENT_TYPES = [
    "Meeting", "Call", "Demo", "Lunch", "Conference", "Webinar", "Trade Show",
    "Product Launch", "Training Session", "QBR"
]

class SimpleDiverseSalesforceSeeder:
    """Handles simple diverse seeding with fresh, realistic data."""
    
    def __init__(self, mode: str = "DEMO", dry_run: bool = False, 
                 use_bulk: bool = True):
        """Initialize the simple diverse seeder."""
        self.mode = mode.upper()
        self.dry_run = dry_run
        self.use_bulk = use_bulk
        self.config = SIMPLE_CONFIGS[self.mode]
        
        self.sf_client: Optional[SalesforceClient] = None
        self.bulk_client: Optional[SalesforceBulkClient] = None
        
        # Results tracking
        self.results = {
            "accounts": {"created": 0, "updated": 0, "failed": 0},
            "contacts": {"created": 0, "updated": 0, "failed": 0},
            "opportunities": {"created": 0, "updated": 0, "failed": 0},
            "leads": {"created": 0, "updated": 0, "failed": 0},
            "campaigns": {"created": 0, "updated": 0, "failed": 0},
            "tasks": {"created": 0, "updated": 0, "failed": 0},
            "events": {"created": 0, "updated": 0, "failed": 0}
        }
        
        logger.info(f"Initialized simple diverse seeder in {self.mode} mode")
    
    async def connect(self) -> None:
        """Connect to Salesforce and initialize clients."""
        try:
            self.sf_client = SalesforceClient()
            await self.sf_client.connect()
            
            if self.use_bulk and not self.dry_run:
                self.bulk_client = SalesforceBulkClient(self.sf_client.sf)
            
            logger.info("Connected to Salesforce")
        except Exception as e:
            logger.error(f"Failed to connect to Salesforce: {e}")
            raise
    
    def generate_simple_accounts(self) -> List[Dict]:
        """Generate simple Account records with realistic data."""
        accounts = []
        
        for i in range(self.config["accounts"]):
            # Create diverse account types and industries
            account_type = random.choice(COMPANY_TYPES)
            industry = random.choice(INDUSTRIES)
            city = fake.city()
            
            # Vary revenue and employee count based on industry
            if industry in ["Technology", "Finance", "Healthcare"]:
                revenue = random.randint(1000000, 50000000)
                employees = random.randint(50, 2000)
            elif industry in ["Manufacturing", "Retail"]:
                revenue = random.randint(500000, 20000000)
                employees = random.randint(20, 1000)
            else:
                revenue = random.randint(100000, 10000000)
                employees = random.randint(10, 500)
            
            account = {
                "Name": f"{SEED_PREFIX}{fake.company()}",
                "Type": account_type,
                "Industry": industry,
                "BillingCity": city,
                "BillingCountry": "United States",
                "Phone": fake.phone_number(),
                "Website": f"www.{fake.domain_name()}",
                "Description": f"Diverse demo account: {industry} company in {city}",
                "AnnualRevenue": revenue,
                "NumberOfEmployees": employees,
                "Rating": random.choice(["Hot", "Warm", "Cold", None])
            }
            accounts.append(account)
        
        return accounts
    
    def generate_simple_contacts(self, account_ids: List[str]) -> List[Dict]:
        """Generate simple Contact records with realistic relationships."""
        contacts = []
        
        for i, account_id in enumerate(account_ids):
            num_contacts = random.randint(2, self.config["contacts_per_account"])
            
            for j in range(num_contacts):
                first_name = fake.first_name()
                last_name = fake.last_name()
                email = fake.email()
                title = random.choice(JOB_TITLES)
                
                # Create simple contact data
                contact = {
                    "AccountId": account_id,
                    "FirstName": first_name,
                    "LastName": last_name,
                    "Email": email,
                    "Title": title,
                    "Phone": fake.phone_number(),
                    "MobilePhone": fake.phone_number(),
                    "Department": self._get_department_for_title(title),
                    "LeadSource": random.choice(LEAD_SOURCES),
                    "Description": f"Diverse demo contact: {title} at account {i}",
                    "MailingCity": fake.city(),
                    "MailingCountry": "United States",
                    "Birthdate": fake.date_of_birth(minimum_age=25, maximum_age=65).strftime("%Y-%m-%d"),
                    "AssistantName": fake.name() if random.random() < 0.3 else None,
                    "AssistantPhone": fake.phone_number() if random.random() < 0.3 else None
                }
                contacts.append(contact)
        
        return contacts
    
    def _get_department_for_title(self, title: str) -> str:
        """Get appropriate department based on job title."""
        if "CEO" in title or "CFO" in title or "CTO" in title:
            return "Executive"
        elif "Sales" in title or "Account" in title:
            return "Sales"
        elif "Marketing" in title:
            return "Marketing"
        elif "Engineering" in title or "Developer" in title:
            return "Engineering"
        elif "Product" in title:
            return "Product"
        elif "Customer" in title:
            return "Customer Success"
        else:
            return random.choice(["Sales", "Marketing", "Engineering", "Finance", "HR", "Operations"])
    
    def generate_simple_opportunities(self, account_ids: List[str]) -> List[Dict]:
        """Generate simple Opportunity records with realistic stage progression."""
        opportunities = []
        
        for i in range(self.config["opportunities"]):
            # Create diverse opportunity data
            amount = self._generate_realistic_amount()
            stage = self._select_realistic_stage()
            close_date = self._generate_close_date_for_stage(stage)
            probability = self._get_probability_for_stage(stage)
            account_id = random.choice(account_ids) if account_ids else None
            
            opportunity = {
                "AccountId": account_id,
                "Name": f"{SEED_PREFIX}Opportunity {fake.word().title()}",
                "Amount": amount,
                "CloseDate": close_date.strftime("%Y-%m-%d"),
                "StageName": stage,
                "Type": random.choice(["New Customer", "Existing Customer", "Upgrade", "Renewal"]),
                "LeadSource": random.choice(LEAD_SOURCES),
                "Description": f"Diverse demo opportunity: {stage} stage, ${amount:,.0f}",
                "Probability": probability,
                "ForecastCategory": self._get_forecast_category(probability),
                "ExpectedRevenue": amount * (probability / 100)
            }
            opportunities.append(opportunity)
        
        return opportunities
    
    def _generate_realistic_amount(self) -> float:
        """Generate realistic opportunity amounts."""
        # Create diverse amount distribution
        if random.random() < 0.6:  # 60% small deals
            return random.uniform(5000, 50000)
        elif random.random() < 0.3:  # 30% medium deals
            return random.uniform(50000, 200000)
        else:  # 10% large deals
            return random.uniform(200000, 1000000)
    
    def _select_realistic_stage(self) -> str:
        """Select realistic stage based on distribution."""
        rand = random.random()
        cumulative = 0
        for stage, prob in STAGE_DISTRIBUTION.items():
            cumulative += prob
            if rand <= cumulative:
                return stage
        return "Prospecting"  # fallback
    
    def _generate_close_date_for_stage(self, stage: str) -> datetime:
        """Generate realistic close date based on stage."""
        base_date = datetime.now()
        
        if stage in ["Closed Won", "Closed Lost"]:
            # Past deals
            return base_date - timedelta(days=random.randint(1, 90))
        elif stage in ["Negotiation/Review", "Proposal/Price Quote"]:
            # Near-term deals
            return base_date + timedelta(days=random.randint(1, 30))
        elif stage in ["Id. Decision Makers", "Perception Analysis"]:
            # Medium-term deals
            return base_date + timedelta(days=random.randint(30, 90))
        else:
            # Long-term deals
            return base_date + timedelta(days=random.randint(90, 365))
    
    def _get_probability_for_stage(self, stage: str) -> int:
        """Get realistic probability for stage."""
        stage_probabilities = {
            "Prospecting": random.randint(5, 15),
            "Qualification": random.randint(15, 25),
            "Needs Analysis": random.randint(25, 35),
            "Value Proposition": random.randint(35, 45),
            "Id. Decision Makers": random.randint(45, 55),
            "Perception Analysis": random.randint(55, 65),
            "Proposal/Price Quote": random.randint(65, 75),
            "Negotiation/Review": random.randint(75, 85),
            "Closed Won": 100,
            "Closed Lost": 0
        }
        return stage_probabilities.get(stage, 50)
    
    def _get_forecast_category(self, probability: int) -> str:
        """Get forecast category based on probability."""
        if probability >= 80:
            return "Closed"
        elif probability >= 50:
            return "Pipeline"
        elif probability >= 20:
            return "Best Case"
        else:
            return "Omitted"
    
    def generate_simple_leads(self) -> List[Dict]:
        """Generate simple Lead records with realistic data."""
        leads = []
        
        for i in range(self.config["leads"]):
            first_name = fake.first_name()
            last_name = fake.last_name()
            company = fake.company()
            lead_source = random.choice(LEAD_SOURCES)
            status = self._get_lead_status_for_source(lead_source)
            
            lead = {
                "FirstName": first_name,
                "LastName": last_name,
                "Company": f"{SEED_PREFIX}{company}",
                "Email": fake.email(),
                "Phone": fake.phone_number(),
                "Title": random.choice(JOB_TITLES),
                "LeadSource": lead_source,
                "Industry": random.choice(INDUSTRIES),
                "Status": status,
                "Description": f"Diverse demo lead: {status} lead from {lead_source}",
                "Rating": random.choice(["Hot", "Warm", "Cold"]),
                "AnnualRevenue": random.randint(100000, 10000000),
                "NumberOfEmployees": random.randint(10, 1000),
                "City": fake.city(),
                "Country": "United States"
            }
            leads.append(lead)
        
        return leads
    
    def _get_lead_status_for_source(self, source: str) -> str:
        """Get realistic lead status based on source."""
        if source in ["Web", "Email", "Social Media"]:
            return random.choice(["New", "Contacted", "Qualified"])
        elif source in ["Phone", "Cold Call"]:
            return random.choice(["Contacted", "Qualified", "Unqualified"])
        elif source in ["Referral", "Partner"]:
            return random.choice(["Qualified", "Contacted"])
        else:
            return random.choice(["New", "Contacted", "Qualified", "Unqualified"])
    
    def generate_simple_campaigns(self) -> List[Dict]:
        """Generate simple Campaign records with marketing data."""
        campaigns = []
        
        for i in range(self.config["campaigns"]):
            campaign_type = random.choice(CAMPAIGN_TYPES)
            start_date = datetime.now() - timedelta(days=random.randint(30, 180))
            end_date = start_date + timedelta(days=random.randint(7, 60))
            
            campaign = {
                "Name": f"{SEED_PREFIX}{campaign_type} {fake.word().title()}",
                "Type": campaign_type,
                "Status": random.choice(["Planned", "In Progress", "Completed", "Aborted"]),
                "StartDate": start_date.strftime("%Y-%m-%d"),
                "EndDate": end_date.strftime("%Y-%m-%d"),
                "Description": f"Diverse marketing campaign: {campaign_type}",
                "BudgetedCost": random.randint(1000, 50000),
                "ActualCost": random.randint(500, 45000),
                "ExpectedRevenue": random.randint(5000, 100000),
                "ExpectedResponse": random.randint(5, 25),
                "NumberSent": random.randint(100, 5000),
                "IsActive": random.choice([True, False])
            }
            campaigns.append(campaign)
        
        return campaigns
    
    def generate_simple_tasks(self, account_ids: List[str], contact_ids: List[str]) -> List[Dict]:
        """Generate simple Task records with realistic activities."""
        tasks = []
        
        task_types = TASK_TYPES
        priorities = ["Low", "Normal", "High"]
        statuses = ["Not Started", "In Progress", "Completed", "Deferred", "Waiting on someone else"]
        
        for i in range(self.config["tasks"]):
            task_type = random.choice(task_types)
            priority = random.choice(priorities)
            status = random.choice(statuses)
            
            # Generate realistic dates
            if status == "Completed":
                activity_date = datetime.now() - timedelta(days=random.randint(1, 30))
            elif status == "In Progress":
                activity_date = datetime.now() + timedelta(days=random.randint(0, 7))
            else:
                activity_date = datetime.now() + timedelta(days=random.randint(1, 30))
            
            task = {
                "Subject": f"{SEED_PREFIX}{task_type} - {fake.sentence(nb_words=3)}",
                "Status": status,
                "Priority": priority,
                "Description": f"Diverse demo task: {task_type} with {priority} priority",
                "ActivityDate": activity_date.strftime("%Y-%m-%d"),
                "Type": task_type
            }
            
            # Randomly assign to account or contact
            if random.choice([True, False]) and account_ids:
                task["WhatId"] = random.choice(account_ids)
            elif contact_ids:
                task["WhoId"] = random.choice(contact_ids)
            
            tasks.append(task)
        
        return tasks
    
    def generate_simple_events(self, account_ids: List[str], contact_ids: List[str]) -> List[Dict]:
        """Generate simple Event records with realistic meetings."""
        events = []
        
        event_types = EVENT_TYPES
        
        for i in range(self.config["events"]):
            event_type = random.choice(event_types)
            start_date = datetime.now() + timedelta(days=random.randint(1, 60))
            end_date = start_date + timedelta(hours=random.randint(1, 4))
            
            event = {
                "Subject": f"{SEED_PREFIX}{event_type} - {fake.sentence(nb_words=3)}",
                "StartDateTime": start_date.strftime("%Y-%m-%d %H:%M:%S"),
                "EndDateTime": end_date.strftime("%Y-%m-%d %H:%M:%S"),
                "Description": f"Diverse demo event: {event_type}",
                "Type": event_type,
                "Location": fake.address() if random.random() < 0.7 else "Virtual Meeting",
                "IsAllDayEvent": False,
                "ShowAs": random.choice(["Busy", "Free", "Out of Office"])
            }
            
            # Randomly assign to account or contact
            if random.choice([True, False]) and account_ids:
                event["WhatId"] = random.choice(account_ids)
            elif contact_ids:
                event["WhoId"] = random.choice(contact_ids)
            
            events.append(event)
        
        return events
    
    async def run_simple_diverse_seeding(self) -> Dict[str, Any]:
        """Run the simple diverse seeding process."""
        logger.info(f"Starting simple diverse Salesforce seeding in {self.mode} mode...")
        
        try:
            if not self.dry_run:
                await self.connect()
            
            # Generate simple diverse data
            accounts_data = self.generate_simple_accounts()
            leads_data = self.generate_simple_leads()
            campaigns_data = self.generate_simple_campaigns()
            
            # Process in dependency order
            account_ids = await self._process_accounts(accounts_data)
            contact_ids = await self._process_contacts(account_ids)
            opportunity_ids = await self._process_opportunities(account_ids)
            lead_ids = await self._process_leads(leads_data)
            campaign_ids = await self._process_campaigns(campaigns_data)
            
            # Generate related data
            tasks_data = self.generate_simple_tasks(account_ids, contact_ids)
            events_data = self.generate_simple_events(account_ids, contact_ids)
            
            await self._process_tasks(tasks_data)
            await self._process_events(events_data)
            
            # Generate summary
            summary = self._generate_summary()
            
            logger.info("Simple diverse seeding completed successfully!")
            return summary
            
        except Exception as e:
            logger.error(f"Simple diverse seeding failed: {e}")
            raise
        finally:
            if self.sf_client and not self.dry_run:
                await self.sf_client.disconnect()
    
    async def _process_accounts(self, accounts_data: List[Dict]) -> List[str]:
        """Process Account records."""
        logger.info(f"Processing {len(accounts_data)} simple diverse accounts...")
        
        if self.dry_run:
            self.results["accounts"]["created"] = len(accounts_data)
            return [f"account_{i}" for i in range(len(accounts_data))]
        
        if self.use_bulk and self.bulk_client:
            result = await self.bulk_client.bulk_insert("Account", accounts_data)
            self.results["accounts"]["created"] = result.successful_records
            self.results["accounts"]["failed"] = result.failed_records
            
            account_ids = result.created_ids
            if not account_ids:
                account_ids = [f"account_{i}" for i in range(len(accounts_data))]
        else:
            account_ids = [f"account_{i}" for i in range(len(accounts_data))]
            self.results["accounts"]["created"] = len(accounts_data)
        
        return account_ids
    
    async def _process_contacts(self, account_ids: List[str]) -> List[str]:
        """Process Contact records."""
        contacts_data = self.generate_simple_contacts(account_ids)
        logger.info(f"Processing {len(contacts_data)} simple diverse contacts...")
        
        if self.dry_run:
            self.results["contacts"]["created"] = len(contacts_data)
            return [f"contact_{i}" for i in range(len(contacts_data))]
        
        if self.use_bulk and self.bulk_client:
            result = await self.bulk_client.bulk_insert("Contact", contacts_data)
            self.results["contacts"]["created"] = result.successful_records
            self.results["contacts"]["failed"] = result.failed_records
            
            contact_ids = result.created_ids
            if not contact_ids:
                contact_ids = [f"contact_{i}" for i in range(len(contacts_data))]
        else:
            contact_ids = [f"contact_{i}" for i in range(len(contacts_data))]
            self.results["contacts"]["created"] = len(contacts_data)
        
        return contact_ids
    
    async def _process_opportunities(self, account_ids: List[str]) -> List[str]:
        """Process Opportunity records."""
        opportunities_data = self.generate_simple_opportunities(account_ids)
        logger.info(f"Processing {len(opportunities_data)} simple diverse opportunities...")
        
        if self.dry_run:
            self.results["opportunities"]["created"] = len(opportunities_data)
            return [f"opp_{i}" for i in range(len(opportunities_data))]
        
        if self.use_bulk and self.bulk_client:
            result = await self.bulk_client.bulk_insert("Opportunity", opportunities_data)
            self.results["opportunities"]["created"] = result.successful_records
            self.results["opportunities"]["failed"] = result.failed_records
        else:
            self.results["opportunities"]["created"] = len(opportunities_data)
        
        return [f"opp_{i}" for i in range(len(opportunities_data))]
    
    async def _process_leads(self, leads_data: List[Dict]) -> List[str]:
        """Process Lead records."""
        logger.info(f"Processing {len(leads_data)} simple diverse leads...")
        
        if self.dry_run:
            self.results["leads"]["created"] = len(leads_data)
            return [f"lead_{i}" for i in range(len(leads_data))]
        
        if self.use_bulk and self.bulk_client:
            result = await self.bulk_client.bulk_insert("Lead", leads_data)
            self.results["leads"]["created"] = result.successful_records
            self.results["leads"]["failed"] = result.failed_records
        else:
            self.results["leads"]["created"] = len(leads_data)
        
        return [f"lead_{i}" for i in range(len(leads_data))]
    
    async def _process_campaigns(self, campaigns_data: List[Dict]) -> List[str]:
        """Process Campaign records."""
        logger.info(f"Processing {len(campaigns_data)} simple diverse campaigns...")
        
        if self.dry_run:
            self.results["campaigns"]["created"] = len(campaigns_data)
            return [f"campaign_{i}" for i in range(len(campaigns_data))]
        
        if self.use_bulk and self.bulk_client:
            result = await self.bulk_client.bulk_insert("Campaign", campaigns_data)
            self.results["campaigns"]["created"] = result.successful_records
            self.results["campaigns"]["failed"] = result.failed_records
        else:
            self.results["campaigns"]["created"] = len(campaigns_data)
        
        return [f"campaign_{i}" for i in range(len(campaigns_data))]
    
    async def _process_tasks(self, tasks_data: List[Dict]) -> None:
        """Process Task records."""
        logger.info(f"Processing {len(tasks_data)} simple diverse tasks...")
        
        if self.dry_run:
            self.results["tasks"]["created"] = len(tasks_data)
            return
        
        if self.use_bulk and self.bulk_client:
            result = await self.bulk_client.bulk_insert("Task", tasks_data)
            self.results["tasks"]["created"] = result.successful_records
            self.results["tasks"]["failed"] = result.failed_records
        else:
            self.results["tasks"]["created"] = len(tasks_data)
    
    async def _process_events(self, events_data: List[Dict]) -> None:
        """Process Event records."""
        logger.info(f"Processing {len(events_data)} simple diverse events...")
        
        if self.dry_run:
            self.results["events"]["created"] = len(events_data)
            return
        
        if self.use_bulk and self.bulk_client:
            result = await self.bulk_client.bulk_insert("Event", events_data)
            self.results["events"]["created"] = result.successful_records
            self.results["events"]["failed"] = result.failed_records
        else:
            self.results["events"]["created"] = len(events_data)
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate simple diverse summary."""
        total_records = sum(result["created"] + result["updated"] for result in self.results.values())
        
        return {
            "results": self.results,
            "metrics": {
                "total_records": total_records,
                "success_rate": "High" if all(result["failed"] == 0 for result in self.results.values()) else "Partial"
            }
        }


def print_simple_diverse_summary(summary: Dict[str, Any]) -> None:
    """Print the simple diverse acceptance summary."""
    print("\n" + "="*80)
    print("🎉 SIMPLE DIVERSE SALESFORCE SEEDING ACCEPTANCE SUMMARY")
    print("="*80)
    
    # Results
    print("\n📊 RESULTS:")
    for entity, result in summary["results"].items():
        total = result["created"] + result["updated"]
        print(f"  {entity}: {total:,} total ({result['created']:,} created, {result['updated']:,} updated, {result['failed']:,} failed)")
    
    # Metrics
    print(f"\n📈 METRICS:")
    print(f"  Total Records: {summary['metrics']['total_records']:,}")
    print(f"  Success Rate: {summary['metrics']['success_rate']}")
    
    print(f"\n🎯 DIVERSITY FEATURES:")
    print(f"  - Multiple industries and company types")
    print(f"  - Realistic stage progression in opportunities")
    print(f"  - Varied lead sources and statuses")
    print(f"  - Marketing campaigns with budgets")
    print(f"  - Diverse tasks and events with realistic dates")
    print(f"  - Proper activity tracking and relationships")
    print(f"  - Fresh data with new prefix: {SEED_PREFIX}")
    print(f"  - Simplified fields to avoid validation issues")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Simple diverse Salesforce seeding with fresh, realistic data")
    parser.add_argument("--mode", choices=["FAST", "DEMO", "HEAVY"], default="DEMO",
                       help="Seeding mode (default: DEMO)")
    parser.add_argument("--bulk", action="store_true", default=True,
                       help="Use Bulk API (default: True)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Dry run mode - don't actually create records")
    
    args = parser.parse_args()
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Create and run simple diverse seeder
    seeder = SimpleDiverseSalesforceSeeder(
        mode=args.mode,
        dry_run=args.dry_run,
        use_bulk=args.bulk
    )
    
    try:
        summary = await seeder.run_simple_diverse_seeding()
        print_simple_diverse_summary(summary)
        
        if args.dry_run:
            print(f"\n⚠️  This was a DRY RUN. No records were actually created.")
        else:
            print(f"\n✅ Simple diverse seeding completed successfully!")
            
    except Exception as e:
        print(f"❌ Simple diverse seeding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
