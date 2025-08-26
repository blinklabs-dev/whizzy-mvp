import json
from .agent import SalesforceAgent

# --- Mocking Dependencies for Standalone Execution ---
# This allows us to test the briefing generation without a live bot.
class MockSalesforceAgent(SalesforceAgent):
    def __init__(self):
        self.client = None # No OpenAI client needed for mocking
        self.sf = None # No Salesforce client needed

    def generate_soql_query(self, user_query: str, chat_history=None) -> str:
        # In a real scenario, this would generate SOQL. Here we return a mock.
        return f"SELECT Id FROM Opportunity WHERE OwnerId = 'mock_user_id' AND Question = '{user_query}'"

    def summarize_data_with_llm(self, user_query: str, data: str) -> str:
        # Return a mock summary based on the question
        return f"- **Mock Summary for '{user_query}'**: The data shows important trends and metrics that are very insightful."

def generate_vp_briefing(agent: SalesforceAgent) -> str:
    """
    Generates a briefing for a VP of Sales.

    Args:
        agent: An instance of the SalesforceAgent.

    Returns:
        A formatted string containing the briefing.
    """
    print("Generating VP of Sales briefing...")

    briefing_sections = []

    # Header
    briefing_sections.append("## 📈 **VP of Sales - Weekly Briefing**")
    briefing_sections.append("Here is your summary of the team's performance over the last week.")

    vp_questions = [
        "What was the team's overall win rate last week?",
        "How did the total open pipeline value change in the last 7 days?",
        "Who were the top 3 sales reps by closed-won deals last week?",
        "Which high-value deals are at risk (close date in the past but still open)?"
    ]

    for question in vp_questions:
        print(f"  - Answering question: {question}")
        # In a real run, this would query SF and summarize real data.
        # Here, we use the mock agent to get a placeholder summary.
        mock_data = json.dumps([{"mock": "data"}])
        summary = agent.summarize_data_with_llm(question, mock_data)
        briefing_sections.append(f"\n### {question}\n{summary}")

    return "\n".join(briefing_sections)


def generate_ae_briefing(agent: SalesforceAgent, user_id: str) -> str:
    """
    Generates a personalized briefing for an Account Executive.

    Args:
        agent: An instance of the SalesforceAgent.
        user_id: The Slack user ID of the AE.

    Returns:
        A formatted string containing the briefing.
    """
    print(f"Generating Account Executive briefing for user {user_id}...")

    briefing_sections = []

    # Header
    briefing_sections.append("## 🎯 **Your Personalized Daily Briefing**")
    briefing_sections.append("Here are your key updates to get your day started.")

    # The questions are phrased from the user's perspective
    ae_questions = [
        f"Which of my open opportunities are scheduled to close this week?",
        f"What are my top 3 largest open opportunities by amount?",
        f"Show me my recently logged activities from yesterday.",
    ]

    for question in ae_questions:
        print(f"  - Answering question: {question}")
        # We pass the user_id in the query for personalization
        # The agent would need to be trained to handle "my" in the context of the user.
        personalized_question = f"{question} (for user: {user_id})"
        mock_data = json.dumps([{"mock": "data"}])
        summary = agent.summarize_data_with_llm(personalized_question, mock_data)
        briefing_sections.append(f"\n### {question.replace(' my', ' your')}\n{summary}")

    return "\n".join(briefing_sections)


# --- Example of how to run this file standalone for testing ---
if __name__ == '__main__':
    print("--- Running Briefing Generation Test ---")
    mock_agent = MockSalesforceAgent()

    print("\n--- VP Briefing ---")
    vp_briefing = generate_vp_briefing(mock_agent)
    print(vp_briefing)

    print("\n--- AE Briefing ---")
    ae_briefing = generate_ae_briefing(mock_agent, user_id="U12345ABC")
    print(ae_briefing)
