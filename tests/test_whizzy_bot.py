#!/usr/bin/env python3
"""
Test suite for Whizzy Bot
Basic functionality tests for the Salesforce analytics bot
"""

import unittest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.whizzy_bot import WhizzyBot


class TestWhizzyBot(unittest.TestCase):
    """Test cases for WhizzyBot class"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'SLACK_APP_TOKEN': 'xapp-test-token',
            'SLACK_BOT_TOKEN': 'xoxb-test-token',
            'SALESFORCE_USERNAME': 'test@example.com',
            'SALESFORCE_PASSWORD': 'testpassword',
            'SALESFORCE_SECURITY_TOKEN': 'testtoken',
            'SALESFORCE_DOMAIN': 'login'
        })
        self.env_patcher.start()
        
        # Mock Salesforce client
        self.sf_patcher = patch('simple_salesforce.Salesforce')
        self.mock_sf = self.sf_patcher.start()
        
        # Create bot instance
        self.bot = WhizzyBot()
    
    def tearDown(self):
        """Clean up after tests"""
        self.env_patcher.stop()
        self.sf_patcher.stop()
    
    def test_bot_initialization(self):
        """Test bot initializes correctly"""
        self.assertIsNotNone(self.bot)
        self.assertEqual(self.bot.app_token, 'xapp-test-token')
        self.assertEqual(self.bot.bot_token, 'xoxb-test-token')
        self.assertIsNotNone(self.bot.web_client)
    
    def test_salesforce_initialization(self):
        """Test Salesforce client initialization"""
        self.mock_sf.assert_called_once_with(
            username='test@example.com',
            password='testpassword',
            security_token='testtoken',
            domain='login'
        )
    
    def test_win_rate_analysis(self):
        """Test win rate analysis response"""
        # Mock Salesforce query responses
        self.bot.salesforce_client.query.side_effect = [
            {'records': [{'total': 100}]},
            {'records': [{'won': 25}]},
            {'records': [{'lost': 15}]}
        ]
        
        response = self.bot._get_win_rate_analysis()
        
        # Verify response contains expected content
        self.assertIn('Win Rate: 25.0%', response)
        self.assertIn('Total Opportunities: 100', response)
        self.assertIn('Won: 25', response)
        self.assertIn('Lost: 15', response)
    
    def test_pipeline_overview(self):
        """Test pipeline overview response"""
        # Mock Salesforce query response
        mock_records = [
            {'StageName': 'Prospecting', 'total_count': 10, 'total_amount': 100000},
            {'StageName': 'Qualification', 'total_count': 5, 'total_amount': 50000}
        ]
        self.bot.salesforce_client.query.return_value = {'records': mock_records}
        
        response = self.bot._get_pipeline_overview()
        
        # Verify response contains expected content
        self.assertIn('Total Pipeline Value**: $150,000', response)
        self.assertIn('**Prospecting**: 10 opportunities, $100,000', response)
        self.assertIn('**Qualification**: 5 opportunities, $50,000', response)
    
    def test_top_accounts(self):
        """Test top accounts response"""
        # Mock Salesforce query response
        mock_records = [
            {
                'Name': 'Test Company 1',
                'AnnualRevenue': 1000000,
                'Industry': 'Technology',
                'BillingCity': 'San Francisco',
                'BillingState': 'CA'
            }
        ]
        self.bot.salesforce_client.query.return_value = {'records': mock_records}
        
        response = self.bot._get_top_accounts()
        
        # Verify response contains expected content
        self.assertIn('Test Company 1', response)
        self.assertIn('Revenue: $1,000,000', response)
        self.assertIn('Industry: Technology', response)
    
    def test_executive_briefing(self):
        """Test executive briefing response"""
        # Mock Salesforce query responses
        self.bot.salesforce_client.query.side_effect = [
            {'records': [{'total': 50, 'total_value': 500000}]},
            {'records': [{'total': 100, 'won': 25}]}
        ]
        
        response = self.bot._get_executive_briefing()
        
        # Verify response contains expected content
        self.assertIn('Open Opportunities**: 50', response)
        self.assertIn('Pipeline Value**: $500,000', response)
        self.assertIn('Overall Win Rate**: 25.0%', response)
    
    def test_help_response(self):
        """Test help response"""
        response = self.bot._get_help_response()
        
        # Verify response contains expected content
        self.assertIn('Whizzy Bot - Salesforce Analytics', response)
        self.assertIn('What\'s our win rate?', response)
        self.assertIn('Show me the pipeline', response)
    
    def test_query_routing(self):
        """Test query routing logic"""
        # Test win rate query - need to mock the Salesforce client first
        self.bot.salesforce_client.query.side_effect = [
            {'records': [{'total': 100}]},
            {'records': [{'won': 25}]},
            {'records': [{'lost': 15}]}
        ]
        response = self.bot._generate_response("What's our win rate?", "test_user")
        self.assertIn('Win Rate Analysis', response)
        
        # Test pipeline query - need to mock the Salesforce client
        self.bot.salesforce_client.query.side_effect = None  # Reset side_effect
        mock_records = [
            {'StageName': 'Prospecting', 'total_count': 10, 'total_amount': 100000},
            {'StageName': 'Qualification', 'total_count': 5, 'total_amount': 50000}
        ]
        self.bot.salesforce_client.query.return_value = {'records': mock_records}
        response = self.bot._generate_response("Show me the pipeline", "test_user")
        self.assertIn('Pipeline Overview', response)
        
        # Test help query
        response = self.bot._generate_response("help", "test_user")
        self.assertIn('Whizzy Bot - Salesforce Analytics', response)
    
    def test_error_handling(self):
        """Test error handling"""
        # Test with no Salesforce client
        self.bot.salesforce_client = None
        response = self.bot._generate_response("What's our win rate?", "test_user")
        self.assertIn('Salesforce connection not available', response)
        
        # Test with Salesforce query error
        self.bot.salesforce_client = Mock()
        self.bot.salesforce_client.query.side_effect = Exception("Connection error")
        response = self.bot._generate_response("What's our win rate?", "test_user")
        self.assertIn('Unable to retrieve win rate data', response)


class TestWhizzyBotIntegration(unittest.TestCase):
    """Integration tests for WhizzyBot"""
    
    @patch('simple_salesforce.Salesforce')
    def test_full_query_flow(self, mock_sf):
        """Test complete query flow"""
        # Mock environment
        with patch.dict(os.environ, {
            'SLACK_APP_TOKEN': 'xapp-test-token',
            'SLACK_BOT_TOKEN': 'xoxb-test-token',
            'SALESFORCE_USERNAME': 'test@example.com',
            'SALESFORCE_PASSWORD': 'testpassword',
            'SALESFORCE_SECURITY_TOKEN': 'testtoken',
            'SALESFORCE_DOMAIN': 'login'
        }):
            bot = WhizzyBot()
            
            # Mock Salesforce responses
            bot.salesforce_client.query.side_effect = [
                {'records': [{'total': 100}]},
                {'records': [{'won': 25}]},
                {'records': [{'lost': 15}]}
            ]
            
            # Test complete flow
            response = bot._generate_response("What's our win rate?", "test_user")
            self.assertIsInstance(response, str)
            self.assertIn('Win Rate', response)


if __name__ == '__main__':
    unittest.main()
