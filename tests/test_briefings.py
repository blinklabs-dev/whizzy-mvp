import unittest
from unittest.mock import MagicMock

# Add the root directory to the Python path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.briefings import generate_vp_briefing, generate_ae_briefing

class TestBriefings(unittest.TestCase):

    def setUp(self):
        """Set up a mock agent for each test."""
        self.mock_agent = MagicMock()
        # Configure the mock to return a predictable summary
        def mock_summarize(question, data):
            return f"Summary for '{question}'"
        self.mock_agent.summarize_data_with_llm.side_effect = mock_summarize

    def test_generate_vp_briefing(self):
        """Test the content generation for a VP of Sales briefing."""
        briefing = generate_vp_briefing(self.mock_agent)

        self.assertIn("VP of Sales - Weekly Briefing", briefing)
        # Check that it asked the expected questions
        self.assertIn("What was the team's overall win rate last week?", briefing)
        self.assertIn("How did the total open pipeline value change in the last 7 days?", briefing)
        self.assertIn("Who were the top 3 sales reps by closed-won deals last week?", briefing)

        # Check that the mock summaries were included
        self.assertIn("Summary for 'What was the team's overall win rate last week?'", briefing)

        # Ensure the agent was called for each question
        self.assertEqual(self.mock_agent.summarize_data_with_llm.call_count, 4)

    def test_generate_ae_briefing(self):
        """Test the content generation for an Account Executive briefing."""
        user_id = "U123XYZ"
        briefing = generate_ae_briefing(self.mock_agent, user_id)

        self.assertIn("Your Personalized Daily Briefing", briefing)
        # Check that it asked the expected questions
        self.assertIn("Which of your open opportunities are scheduled to close this week?", briefing)
        self.assertIn("What are your top 3 largest open opportunities by amount?", briefing)

        # Check that the mock summaries were included
        self.assertIn("Summary for 'Which of my open opportunities are scheduled to close this week? (for user: U123XYZ)'", briefing)

        # Ensure the agent was called for each question
        self.assertEqual(self.mock_agent.summarize_data_with_llm.call_count, 3)

if __name__ == '__main__':
    unittest.main()
