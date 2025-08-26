import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

from slack_sdk import WebClient
from dotenv import load_dotenv

# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agent import SalesforceAgent
from app.briefings import generate_vp_briefing, generate_ae_briefing
from unittest.mock import MagicMock # Using mock for SF client

# --- Configuration ---
load_dotenv()
SUBSCRIPTIONS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'subscriptions.json')
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
TARGET_HOUR_UTC = 13 # 8am CST is 13:00 UTC, 9am EST is 14:00 UTC. A reasonable default.
LOOP_SLEEP_SECONDS = 3600 # Check every hour

def load_subscriptions() -> List[Dict[str, Any]]:
    """Loads subscriptions from the JSON file."""
    if not os.path.exists(SUBSCRIPTIONS_FILE):
        return []
    try:
        with open(SUBSCRIPTIONS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Could not load subscriptions: {e}")
        return []

def save_subscriptions(subscriptions: List[Dict[str, Any]]):
    """Saves subscriptions to the JSON file."""
    try:
        with open(SUBSCRIPTIONS_FILE, 'w') as f:
            json.dump(subscriptions, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Could not save subscriptions: {e}")

def create_mock_salesforce_client():
    """Creates a mock simple-salesforce client."""
    mock_sf = MagicMock()
    return mock_sf

def run_scheduler():
    """
    The main scheduler loop that checks for and sends briefings.
    """
    if not SLACK_BOT_TOKEN:
        print("[ERROR] SLACK_BOT_TOKEN not found. Cannot send messages.")
        return

    print("--- Starting Scheduler ---")
    slack_client = WebClient(token=SLACK_BOT_TOKEN)

    # In a real application, you'd initialize a real Salesforce connection.
    # For this example, we use a mock one.
    mock_sf_client = create_mock_salesforce_client()
    agent = SalesforceAgent(salesforce_client=mock_sf_client)

    while True:
        print(f"\n--- Scheduler checking at {datetime.utcnow()} UTC ---")
        subscriptions = load_subscriptions()
        now = datetime.utcnow()

        for sub in subscriptions:
            # Check if a briefing is due
            is_due = False
            last_sent = datetime.fromisoformat(sub.get('last_sent', '1970-01-01T00:00:00'))

            # Check if it has been at least 23 hours since last send to avoid duplicates
            if (now - last_sent) < timedelta(hours=23):
                continue

            if sub['frequency'] == 'daily' and now.hour == TARGET_HOUR_UTC:
                is_due = True
            elif sub['frequency'] == 'weekly' and now.weekday() == 0 and now.hour == TARGET_HOUR_UTC: # Monday
                is_due = True

            if is_due:
                print(f"  - Briefing due for user {sub['user_id']} ({sub['persona']})")

                # Generate briefing content
                briefing_content = ""
                if sub['persona'] == 'VP of Sales':
                    briefing_content = generate_vp_briefing(agent)
                elif sub['persona'] == 'Account Executive':
                    briefing_content = generate_ae_briefing(agent, sub['user_id'])

                if not briefing_content:
                    print(f"    - [WARN] No content generated for {sub['persona']}.")
                    continue

                # Send briefing via DM
                try:
                    slack_client.chat_postMessage(
                        channel=sub['channel_id'],
                        text=briefing_content,
                        mrkdwn=True
                    )
                    print(f"    - ✅ Successfully sent briefing to user {sub['user_id']}.")
                    sub['last_sent'] = now.isoformat()
                except Exception as e:
                    print(f"    - [ERROR] Failed to send message to user {sub['user_id']}: {e}")

        # Save the updated last_sent timestamps
        save_subscriptions(subscriptions)

        print(f"--- Scheduler sleeping for {LOOP_SLEEP_SECONDS / 60} minutes ---")
        time.sleep(LOOP_SLEEP_SECONDS)


if __name__ == "__main__":
    run_scheduler()
