import unittest
from unittest.mock import MagicMock, patch

# Add the root directory to the Python path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.whizzy_bot import WhizzyBot

class TestSubscriptionCommands(unittest.TestCase):

    def setUp(self):
        """Set up a mock WhizzyBot for each test."""
        # We patch the __init__ to avoid it running real setup code
        with patch.object(WhizzyBot, "__init__", lambda x: None):
            self.bot = WhizzyBot()

        # Manually set up the mocks we need
        self.bot.subscriptions = []
        self.bot.web_client = MagicMock()
        self.bot._save_subscriptions = MagicMock()

    def test_handle_subscribe_success(self):
        """Test successful subscription to a briefing."""
        user_id = "U123"
        text = "subscribe daily vp"

        # Mock the Slack API call to open a DM
        self.bot.web_client.conversations_open.return_value = {"channel": {"id": "D123"}}

        response = self.bot._handle_subscribe(user_id, text)

        self.assertIn("You've been subscribed", response)
        self.assertEqual(len(self.bot.subscriptions), 1)
        self.assertEqual(self.bot.subscriptions[0]['user_id'], user_id)
        self.assertEqual(self.bot.subscriptions[0]['frequency'], 'daily')
        self.assertEqual(self.bot.subscriptions[0]['persona'], 'VP of Sales')
        self.bot._save_subscriptions.assert_called_once()

    def test_handle_subscribe_invalid_format(self):
        """Test subscription with invalid command format."""
        response = self.bot._handle_subscribe("U123", "subscribe daily")
        self.assertIn("Sorry, I didn't understand that.", response)
        self.assertEqual(len(self.bot.subscriptions), 0)
        self.bot._save_subscriptions.assert_not_called()

    def test_handle_unsubscribe(self):
        """Test unsubscribing from briefings."""
        user_id = "U123"
        self.bot.subscriptions.append({"user_id": user_id, "frequency": "daily", "persona": "VP"})

        response = self.bot._handle_unsubscribe(user_id)

        self.assertIn("You have been successfully unsubscribed", response)
        self.assertEqual(len(self.bot.subscriptions), 0)
        self.bot._save_subscriptions.assert_called_once()

    def test_handle_unsubscribe_no_subscription(self):
        """Test unsubscribing when there is no active subscription."""
        response = self.bot._handle_unsubscribe("U123")
        self.assertIn("You don't seem to have any active subscriptions", response)
        self.bot._save_subscriptions.assert_not_called()

    def test_handle_list_subscriptions(self):
        """Test listing active subscriptions."""
        user_id = "U123"
        self.bot.subscriptions.append({
            "user_id": user_id,
            "frequency": "weekly",
            "persona": "Account Executive"
        })

        response = self.bot._handle_list_subscriptions(user_id)

        self.assertIn("Here are your current subscriptions", response)
        self.assertIn("Weekly Account Executive Briefing", response)

if __name__ == '__main__':
    unittest.main()
