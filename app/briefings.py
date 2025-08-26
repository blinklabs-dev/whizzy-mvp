import asyncio
from typing import List

# Add app directory to path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.intelligent_agentic_system import EnhancedIntelligentAgenticSystem, PersonaType

async def generate_vp_briefing(agent: EnhancedIntelligentAgenticSystem) -> str:
    """
    Generates a briefing for a VP of Sales by asking a series of questions.
    """
    print("Generating VP of Sales briefing...")

    briefing_sections = [
        "## 📈 **VP of Sales - Weekly Performance Briefing**",
        "Here is your summary of the team's performance and pipeline health."
    ]

    vp_questions = [
        "What was the team's overall win rate last week?",
        "How did the total open pipeline value change in the last 7 days vs the prior 7 days?",
        "Who were the top 3 sales reps by closed-won deals last week?",
        "Analyze our deal slippage from last quarter. Which deals that were supposed to close, didn't?"
    ]

    for question in vp_questions:
        print(f"  - Generating section for: {question}")
        try:
            # We process each question through the agent to get a summarized response
            response = await agent.process_query(question, user_id="vp_briefing_user")
            briefing_sections.append(f"\n---\n\n{response.response_text}")
        except Exception as e:
            briefing_sections.append(f"\n---\n\nCould not generate section for '{question}': {e}")

    return "\n".join(briefing_sections)


async def generate_ae_briefing(agent: EnhancedIntelligentAgenticSystem, user_id: str) -> str:
    """
    Generates a personalized briefing for an Account Executive.
    """
    print(f"Generating Account Executive briefing for user {user_id}...")

    briefing_sections = [
        "## 🎯 **Your Personalized Daily Briefing**",
        "Here are your key updates and action items to get your day started."
    ]

    # These questions are phrased to be generic; the agent's context for the user_id
    # should allow it to generate personalized responses.
    ae_questions = [
        "Which of my open opportunities are scheduled to close this week?",
        "What are my top 3 largest open opportunities by amount?",
        "Show me my recently logged activities from yesterday.",
        "Are there any of my high-priority accounts I haven't contacted in the last 2 weeks?"
    ]

    for question in ae_questions:
        print(f"  - Generating section for: {question}")
        try:
            response = await agent.process_query(question, user_id=user_id)
            briefing_sections.append(f"\n---\n\n{response.response_text}")
        except Exception as e:
            briefing_sections.append(f"\n---\n\nCould not generate section for '{question}': {e}")

    return "\n".join(briefing_sections)


# --- Example of how to run this file standalone for testing ---
async def main():
    print("--- Running Briefing Generation Test ---")

    # We need to mock the agent for standalone testing since it requires API keys
    class MockAgent(EnhancedIntelligentAgenticSystem):
        async def process_query(self, query: str, user_context: dict = None, user_id: str = None) -> 'AgentResponse':
            # Dynamically create AgentResponse for mocking
            from app.intelligent_agentic_system import AgentResponse, DataSourceType
            return AgentResponse(
                response_text=f"This is a mock summary for the question: '{query}'",
                data_sources_used=[DataSourceType.SALESFORCE],
                reasoning_steps=["mocked"],
                confidence_score=0.99,
                persona_alignment=0.99,
                actionability_score=0.99,
                quality_metrics={}
            )

    mock_agent = MockAgent()

    print("\n--- VP Briefing ---")
    vp_briefing = await generate_vp_briefing(mock_agent)
    print(vp_briefing)

    print("\n--- AE Briefing ---")
    ae_briefing = await generate_ae_briefing(mock_agent, user_id="U12345ABC")
    print(ae_briefing)

if __name__ == '__main__':
    asyncio.run(main())
