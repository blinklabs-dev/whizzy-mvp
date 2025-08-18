"""
Tests for Salesforce client
"""

import pytest
from unittest.mock import Mock, patch

from salesforce.client import SalesforceClient


class TestSalesforceClient:
    """Test cases for SalesforceClient."""
    
    def test_init_with_missing_env_vars(self):
        """Test initialization fails with missing environment variables."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Missing required Salesforce environment variables"):
                SalesforceClient()
    
    def test_init_with_valid_env_vars(self):
        """Test initialization succeeds with valid environment variables."""
        env_vars = {
            "SALESFORCE_USERNAME": "test@example.com",
            "SALESFORCE_PASSWORD": "password123",
            "SALESFORCE_SECURITY_TOKEN": "token123",
            "SALESFORCE_DOMAIN": "login"
        }
        
        with patch.dict('os.environ', env_vars):
            client = SalesforceClient()
            assert client.username == "test@example.com"
            assert client.password == "password123"
            assert client.security_token == "token123"
            assert client.domain == "login"
            assert not client.is_connected()
    
    def test_is_connected_when_not_connected(self):
        """Test is_connected returns False when not connected."""
        env_vars = {
            "SALESFORCE_USERNAME": "test@example.com",
            "SALESFORCE_PASSWORD": "password123",
            "SALESFORCE_SECURITY_TOKEN": "token123"
        }
        
        with patch.dict('os.environ', env_vars):
            client = SalesforceClient()
            assert not client.is_connected()
    
    def test_get_connection_info(self):
        """Test get_connection_info returns correct information."""
        env_vars = {
            "SALESFORCE_USERNAME": "test@example.com",
            "SALESFORCE_PASSWORD": "password123",
            "SALESFORCE_SECURITY_TOKEN": "token123",
            "SALESFORCE_DOMAIN": "test"
        }
        
        with patch.dict('os.environ', env_vars):
            client = SalesforceClient()
            info = client.get_connection_info()
            
            assert info["connected"] is False
            assert info["username"] == "test@example.com"
            assert info["domain"] == "test"
            assert info["has_password"] is True
            assert info["has_security_token"] is True
