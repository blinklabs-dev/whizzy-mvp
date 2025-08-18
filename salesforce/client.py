"""
Salesforce client for executing SOQL queries
"""

import asyncio
import logging
import os
from typing import Any, Dict, Optional

from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceError

from utils.logging import setup_logging

logger = setup_logging(__name__)


class SalesforceClient:
    """Client for interacting with Salesforce via SOQL queries."""
    
    def __init__(self):
        """Initialize Salesforce client with environment variables."""
        self.username = os.getenv("SALESFORCE_USERNAME")
        self.password = os.getenv("SALESFORCE_PASSWORD")
        self.security_token = os.getenv("SALESFORCE_SECURITY_TOKEN")
        self.domain = os.getenv("SALESFORCE_DOMAIN", "login")
        
        if not all([self.username, self.password, self.security_token]):
            raise ValueError(
                "Missing required Salesforce environment variables: "
                "SALESFORCE_USERNAME, SALESFORCE_PASSWORD, SALESFORCE_SECURITY_TOKEN"
            )
        
        self.sf: Optional[Salesforce] = None
        self._connected = False
    
    async def connect(self) -> None:
        """Establish connection to Salesforce."""
        try:
            logger.info("Connecting to Salesforce...")
            
            # Run connection in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self.sf = await loop.run_in_executor(
                None,
                self._create_connection
            )
            
            self._connected = True
            logger.info("Successfully connected to Salesforce")
            
        except Exception as e:
            logger.error(f"Failed to connect to Salesforce: {e}")
            self._connected = False
            raise
    
    def _create_connection(self) -> Salesforce:
        """Create Salesforce connection (synchronous)."""
        return Salesforce(
            username=self.username,
            password=self.password,
            security_token=self.security_token,
            domain=self.domain
        )
    
    def is_connected(self) -> bool:
        """Check if client is connected to Salesforce."""
        return self._connected and self.sf is not None
    
    async def query(self, soql: str) -> Dict[str, Any]:
        """Execute a SOQL query against Salesforce."""
        if not self.is_connected():
            raise Exception("Not connected to Salesforce")
        
        try:
            logger.info(f"Executing SOQL query: {soql}")
            
            # Run query in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.sf.query,
                soql
            )
            
            # Convert result to dict for JSON serialization
            result_dict = {
                "totalSize": result.get("totalSize", 0),
                "done": result.get("done", True),
                "records": []
            }
            
            # Process records
            for record in result.get("records", []):
                # Remove Salesforce metadata
                record_dict = {k: v for k, v in record.items() if not k.startswith("attributes")}
                result_dict["records"].append(record_dict)
            
            logger.info(f"Query completed. Found {result_dict['totalSize']} records.")
            return result_dict
            
        except SalesforceError as e:
            logger.error(f"Salesforce error: {e}")
            raise Exception(f"Salesforce query failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during query: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from Salesforce."""
        if self.sf:
            try:
                # Simple Salesforce doesn't have an explicit disconnect method
                # Just clear the reference
                self.sf = None
                self._connected = False
                logger.info("Disconnected from Salesforce")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
    
    async def test_connection(self) -> bool:
        """Test the Salesforce connection with a simple query."""
        try:
            await self.query("SELECT Id FROM User LIMIT 1")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information (without sensitive data)."""
        return {
            "connected": self.is_connected(),
            "username": self.username,
            "domain": self.domain,
            "has_password": bool(self.password),
            "has_security_token": bool(self.security_token)
        }
