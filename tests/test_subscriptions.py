import unittest
from unittest.mock import MagicMock, patch

# Add app directory to path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.enhanced_whizzy_bot import EnhancedWhizzyBot

class TestSubscriptionCommands(unittest.TestCase):

    def setUp(self):
        """Set up a mock EnhancedWhizzyBot for each test."""
        # We patch the __init__ to avoid it running real setup code that needs credentials
        with patch.object(EnhancedWhizzyBot, "__init__", lambda x: None):
            self.bot = EnhancedWhizzyBot()

        # Manually set up the mocks and state we need for these tests
        self.bot.subscriptions = []
        self.bot.web_client = MagicMock()
        self.bot._save_subscriptions = MagicMock() # Mock the file writing

    def test_handle_subscribe_success(self):
        """Test successful subscription to a briefing."""
        user_id = "U123"
        text = "subscribe daily vp"

        # Mock the Slack API call to open a DM channel
        self.bot.web_client.conversations_open.return_value = {"channel": {"id": "D123"}}

        response = self.bot._handle_subscribe(user_id, text)

        self.assertIn("You've been subscribed", response)
        self.assertEqual(len(self.bot.subscriptions), 1)
        self.assertEqual(self.bot.subscriptions[0]['user_id'], user_id)
        self.assertEqual(self.bot.subscriptions[0]['frequency'], 'daily')
        self.assertEqual(self.bot.subscriptions[0]['persona'], 'VP_SALES')
        self.bot._save_subscriptions.assert_called_once()

    def test_handle_subscribe_invalid_persona(self):
        """Test subscription with an invalid persona."""
        user_id = "U123"
        text = "subscribe daily manager" # 'manager' is not a valid short code
        response = self.bot._handle_subscribe(user_id, text)
        self.assertIn("Invalid persona", response)
        self.assertEqual(len(self.bot.subscriptions), 0)

    def test_handle_unsubscribe(self):
        """Test unsubscribing from briefings."""
        user_id = "U123"
        self.bot.subscriptions.append({"user_id": user_id})

        response = self.bot._handle_unsubscribe(user_id)

        self.assertIn("You have been successfully unsubscribed", response)
        self.assertEqual(len(self.bot.subscriptions), 0)
        self.bot._save_subscriptions.assert_called_once()

    def test_handle_list_subscriptions(self):
        """Test listing a user's active subscriptions."""
        user_id = "U123"
        self.bot.subscriptions.append({
            "user_id": user_id,
            "frequency": "weekly",
            "persona": "ACCOUNT_EXECUTIVE"
        })

        response = self.bot._handle_list_subscriptions(user_id)

        self.assertIn("Here are your current subscriptions", response)
        self.assertIn("Weekly Account Executive Briefing", response)

if __name__ == '__main__':
    unittest.main()
