import os
import sys
import json
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List

from slack_sdk import WebClient
from dotenv import load_dotenv

# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.intelligent_agentic_system import EnhancedIntelligentAgenticSystem, PersonaType
from app.briefings import generate_vp_briefing, generate_ae_briefing

# --- Configuration ---
load_dotenv()
SUBSCRIPTIONS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'subscriptions.json')
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
TARGET_HOUR_UTC = 13  # 8am CST is 13:00 UTC. A reasonable default for a daily briefing.
LOOP_SLEEP_SECONDS = 3600  # Check every hour

def load_subscriptions() -> List[Dict[str, Any]]:
    """Loads subscriptions from the JSON file."""
    if not os.path.exists(SUBSCRIPTIONS_FILE):
        return []
    try:
        with open(SUBSCRIPTIONS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Scheduler: Could not load subscriptions: {e}")
        return []

def save_subscriptions(subscriptions: List[Dict[str, Any]]):
    """Saves subscriptions to the JSON file."""
    try:
        with open(SUBSCRIPTIONS_FILE, 'w') as f:
            json.dump(subscriptions, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Scheduler: Could not save subscriptions: {e}")

async def run_scheduler():
    """
    The main scheduler loop that checks for and sends briefings.
    """
    if not SLACK_BOT_TOKEN:
        print("[ERROR] Scheduler: SLACK_BOT_TOKEN not found. Cannot send messages.")
        return

    print("--- ☕ Starting Proactive Briefing Scheduler ---")
    slack_client = WebClient(token=SLACK_BOT_TOKEN)

    # Initialize the agent once for the entire scheduler lifecycle
    try:
        agent = EnhancedIntelligentAgenticSystem()
    except Exception as e:
        print(f"[ERROR] Scheduler: Failed to initialize agent. Exiting. Error: {e}")
        return

    while True:
        print(f"\n--- Scheduler checking at {datetime.utcnow()} UTC ---")
        subscriptions = load_subscriptions()
        now = datetime.utcnow()

        for sub in subscriptions:
            is_due = False
            last_sent_str = sub.get('last_sent')
            last_sent = datetime.fromisoformat(last_sent_str) if last_sent_str else datetime(1970, 1, 1)

            if (now - last_sent) < timedelta(hours=23):
                continue

            if sub['frequency'] == 'daily' and now.hour == TARGET_HOUR_UTC:
                is_due = True
            elif sub['frequency'] == 'weekly' and now.weekday() == 0 and now.hour == TARGET_HOUR_UTC: # 0 is Monday
                is_due = True

            if is_due:
                print(f"  - Briefing due for user {sub['user_id']} ({sub['persona']})")

                briefing_content = ""
                try:
                    if sub['persona'] == PersonaType.VP_SALES.value:
                        briefing_content = await generate_vp_briefing(agent)
                    elif sub['persona'] == PersonaType.ACCOUNT_EXECUTIVE.value:
                        briefing_content = await generate_ae_briefing(agent, sub['user_id'])

                    if briefing_content:
                        slack_client.chat_postMessage(channel=sub['channel_id'], text=briefing_content, mrkdwn=True)
                        print(f"    - ✅ Successfully sent briefing to user {sub['user_id']}.")
                        sub['last_sent'] = now.isoformat()
                    else:
                        print(f"    - [WARN] No content generated for {sub['persona']}.")
                except Exception as e:
                    print(f"    - [ERROR] Failed to generate or send briefing for user {sub['user_id']}: {e}")

        save_subscriptions(subscriptions)

        print(f"--- Scheduler sleeping for {LOOP_SLEEP_SECONDS / 60:.0f} minutes ---")
        time.sleep(LOOP_SLEEP_SECONDS)

if __name__ == "__main__":
    asyncio.run(run_scheduler())
