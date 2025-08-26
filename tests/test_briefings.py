import unittest
import asyncio
from unittest.mock import MagicMock, AsyncMock

# Add app directory to path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.briefings import generate_vp_briefing, generate_ae_briefing
from app.intelligent_agentic_system import EnhancedIntelligentAgenticSystem, AgentResponse, DataSourceType

class TestBriefingGeneration(unittest.TestCase):

    def setUp(self):
        """Set up a mock agent for each test."""
        self.mock_agent = MagicMock(spec=EnhancedIntelligentAgenticSystem)

        # Configure the mock's process_query to be an async method
        async def mock_process_query(query, user_id=None, user_context=None):
            return AgentResponse(
                response_text=f"Mock summary for '{query}'",
                data_sources_used=[DataSourceType.SALESFORCE],
                reasoning_steps=["mocked_step"],
                confidence_score=0.99,
                persona_alignment=0.99,
                actionability_score=0.99,
                quality_metrics={}
            )
        self.mock_agent.process_query = mock_process_query

    def test_generate_vp_briefing(self):
        """Test the content generation for a VP of Sales briefing."""
        # Since the function is async, we run it in an event loop
        briefing = asyncio.run(generate_vp_briefing(self.mock_agent))

        self.assertIn("VP of Sales - Weekly Performance Briefing", briefing)
        # Check that it asked one of the expected questions
        self.assertIn("What was the team's overall win rate last week?", briefing)
        # Check that a mock summary was included
        self.assertIn("Mock summary for", briefing)

    def test_generate_ae_briefing(self):
        """Test the content generation for an Account Executive briefing."""
        user_id = "U123XYZ"
        briefing = asyncio.run(generate_ae_briefing(self.mock_agent, user_id))

        self.assertIn("Your Personalized Daily Briefing", briefing)
        # Check that it asked one of the expected questions
        self.assertIn("Which of my open opportunities are scheduled to close this week?", briefing)
        # Check that a mock summary was included
        self.assertIn("Mock summary for", briefing)

if __name__ == '__main__':
    unittest.main()
