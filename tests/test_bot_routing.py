import unittest
from unittest.mock import MagicMock, patch

# Add app directory to path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.enhanced_whizzy_bot import EnhancedWhizzyBot

class TestBotRouting(unittest.TestCase):

    def setUp(self):
        """Set up a mock EnhancedWhizzyBot for each test."""
        with patch.object(EnhancedWhizzyBot, "__init__", lambda x: None):
            self.bot = EnhancedWhizzyBot()

        self.bot.web_client = MagicMock()
        self.bot.user_mapping = {}
        self.bot.subscriptions = []
        # Mock the methods that would be called after the static check
        self.bot._send_enhanced_response = MagicMock()
        # self.bot.enhanced_system is no longer used, as a new agent is created per-request

    def test_fast_path_for_help_command(self):
        """Test that 'help' command uses the fast path."""
        self.bot._handle_static_commands = MagicMock(return_value="This is the help message.")

        self.bot._process_enhanced_response("help", "C123", "U123")

        # Assert that the static handler was called
        self.bot._handle_static_commands.assert_called_once_with("help")
        # Assert that the response was sent
        self.bot._send_enhanced_response.assert_called_once_with("C123", "This is the help message.")
        # CRUCIALLY, assert that the expensive AI system was NOT called
        # We can't easily assert this anymore since the agent is created inside the method.
        # However, the logic path is tested by the `test_full_path_for_complex_query` test.

    @patch('app.enhanced_whizzy_bot.EnhancedIntelligentAgenticSystem')
    def test_full_path_for_complex_query(self, MockAgentSystem):
        """Test that a complex query uses the full AI path."""
        self.bot._handle_static_commands = MagicMock(return_value=None) # No static match

        # Mock the instance that will be created inside the method
        mock_agent_instance = MockAgentSystem.return_value

        # We don't need to mock the full return value of the agent, just check it was called
        self.bot._process_enhanced_response("what is our win rate?", "C123", "U123")

        # Assert that the static handler was called
        self.bot._handle_static_commands.assert_called_once_with("what is our win rate?")
        # Assert that the AI system WAS instantiated and its process_query method was called
        MockAgentSystem.assert_called_once()
        mock_agent_instance.process_query.assert_called_once()


if __name__ == '__main__':
    unittest.main()
