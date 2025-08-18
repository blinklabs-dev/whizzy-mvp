#!/usr/bin/env python3
"""
Salesforce Permissions Checker and Documentation
Helps identify and document required permissions for comprehensive data seeding
"""

import asyncio
import sys
import os
from typing import Dict, List, Any

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from salesforce.client import SalesforceClient
from dotenv import load_dotenv

# Required Salesforce objects for comprehensive MVP
REQUIRED_OBJECTS = [
    "Account",
    "Contact", 
    "Opportunity",
    "Campaign",
    "CampaignMember",
    "Lead",
    "Task",
    "Event",
    "User",
    "Profile"
]

# Required permissions for each object
REQUIRED_PERMISSIONS = {
    "Account": ["Create", "Read", "Edit", "Delete"],
    "Contact": ["Create", "Read", "Edit", "Delete"],
    "Opportunity": ["Create", "Read", "Edit", "Delete"],
    "Campaign": ["Create", "Read", "Edit", "Delete"],
    "CampaignMember": ["Create", "Read", "Edit", "Delete"],
    "Lead": ["Create", "Read", "Edit", "Delete"],
    "Task": ["Create", "Read", "Edit", "Delete"],
    "Event": ["Create", "Read", "Edit", "Delete"]
}

async def check_object_permissions(sf_client: SalesforceClient) -> Dict[str, Any]:
    """Check permissions for required Salesforce objects."""
    results = {}
    
    print("🔍 CHECKING SALESFORCE OBJECT PERMISSIONS")
    print("=" * 60)
    
    for object_name in REQUIRED_OBJECTS:
        try:
            # Try to describe the object to check access
            describe_result = sf_client.sf.__getattr__(object_name).describe()
            
            # Check if we can create records
            can_create = describe_result.get('createable', False)
            can_read = describe_result.get('queryable', False)
            can_edit = describe_result.get('updateable', False)
            can_delete = describe_result.get('deletable', False)
            
            results[object_name] = {
                'accessible': True,
                'createable': can_create,
                'readable': can_read,
                'editable': can_edit,
                'deletable': can_delete,
                'fields': len(describe_result.get('fields', [])),
                'error': None
            }
            
            status = "✅" if can_create else "❌"
            print(f"{status} {object_name}: Create={can_create}, Read={can_read}, Edit={can_edit}, Delete={can_delete}")
            
        except Exception as e:
            results[object_name] = {
                'accessible': False,
                'createable': False,
                'readable': False,
                'editable': False,
                'deletable': False,
                'fields': 0,
                'error': str(e)
            }
            print(f"❌ {object_name}: Not accessible - {e}")
    
    return results

async def check_user_profile(sf_client: SalesforceClient) -> Dict[str, Any]:
    """Check current user's profile and permissions."""
    try:
        # Get current user info
        user_info = sf_client.sf.User.describe()
        current_user = sf_client.sf.User.get(sf_client.sf.session_id.split('!')[0])
        
        print(f"\n👤 CURRENT USER PROFILE")
        print("=" * 60)
        print(f"User: {current_user.get('Name', 'Unknown')}")
        print(f"Email: {current_user.get('Email', 'Unknown')}")
        print(f"Profile: {current_user.get('Profile', {}).get('Name', 'Unknown')}")
        print(f"Role: {current_user.get('UserRole', {}).get('Name', 'None')}")
        
        return {
            'user_name': current_user.get('Name'),
            'user_email': current_user.get('Email'),
            'profile_name': current_user.get('Profile', {}).get('Name'),
            'role_name': current_user.get('UserRole', {}).get('Name')
        }
        
    except Exception as e:
        print(f"❌ Error getting user info: {e}")
        return {}

async def generate_permission_guide(results: Dict[str, Any], user_info: Dict[str, Any]):
    """Generate a comprehensive permission guide."""
    
    print(f"\n📋 SALESFORCE PERMISSIONS GUIDE")
    print("=" * 60)
    
    # Identify missing permissions
    missing_permissions = []
    for obj_name, obj_result in results.items():
        if not obj_result['createable']:
            missing_permissions.append(f"Create access for {obj_name}")
        if not obj_result['readable']:
            missing_permissions.append(f"Read access for {obj_name}")
    
    if missing_permissions:
        print("❌ MISSING PERMISSIONS:")
        for permission in missing_permissions:
            print(f"  - {permission}")
        
        print(f"\n🔧 TO FIX PERMISSIONS:")
        print("1. Go to Setup > Users > Profiles")
        print("2. Find your profile or create a new one")
        print("3. Go to Object Permissions")
        print("4. Enable the following permissions:")
        
        for obj_name in REQUIRED_OBJECTS:
            if obj_name in results and not results[obj_name]['createable']:
                print(f"   - {obj_name}: Create, Read, Edit, Delete")
        
        print(f"\n📝 ALTERNATIVE: Use System Administrator profile")
        print("   - This profile has all permissions by default")
        print("   - Recommended for development/testing")
        
    else:
        print("✅ ALL REQUIRED PERMISSIONS ARE AVAILABLE!")
    
    # Generate comprehensive seeding recommendations
    print(f"\n🎯 COMPREHENSIVE MVP DATA SEEDING STRATEGY")
    print("=" * 60)
    
    working_objects = [obj for obj, result in results.items() if result['createable']]
    blocked_objects = [obj for obj, result in results.items() if not result['createable']]
    
    print(f"✅ WORKING OBJECTS ({len(working_objects)}):")
    for obj in working_objects:
        print(f"  - {obj}")
    
    if blocked_objects:
        print(f"\n❌ BLOCKED OBJECTS ({len(blocked_objects)}):")
        for obj in blocked_objects:
            print(f"  - {obj}")
    
    print(f"\n📊 RECOMMENDED SEEDING VOLUMES:")
    print("  - Accounts: 200-500 (companies)")
    print("  - Contacts: 800-2000 (people)")
    print("  - Opportunities: 1000-3000 (deals)")
    print("  - Campaigns: 50-100 (marketing campaigns)")
    print("  - CampaignMembers: 2000-5000 (campaign participants)")
    print("  - Leads: 500-1000 (prospects)")
    print("  - Tasks: 1000-3000 (activities)")
    print("  - Events: 200-500 (meetings)")

async def main():
    """Main function to check permissions and generate guide."""
    load_dotenv()
    
    try:
        # Connect to Salesforce
        sf_client = SalesforceClient()
        await sf_client.connect()
        
        # Check permissions
        permission_results = await check_object_permissions(sf_client)
        user_info = await check_user_profile(sf_client)
        
        # Generate comprehensive guide
        await generate_permission_guide(permission_results, user_info)
        
        await sf_client.disconnect()
        
    except Exception as e:
        print(f"❌ Failed to check permissions: {e}")

if __name__ == "__main__":
    asyncio.run(main())
