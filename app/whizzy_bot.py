#!/usr/bin/env python3
"""
Whizzy Bot - Consolidated Salesforce Analytics Bot
A production-ready Slack bot that provides real-time Salesforce analytics through natural language queries.

Features:
- Real-time Salesforce integration
- Persona-specific responses
- Professional formatting
- Error handling and logging
- Background processing
"""

import os
import logging
import signal
import sys
import json
import time
import asyncio
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.web import WebClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from dotenv import load_dotenv
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.spectrum_aware_router import SpectrumAwareRouter
from app.intelligent_agentic_system import EnhancedIntelligentAgenticSystem

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SUBSCRIPTIONS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'subscriptions.json')


class WhizzyBot:
    """Whizzy Bot - Salesforce Analytics Bot"""
    
    def __init__(self):
        self.subscriptions = self._load_subscriptions()
        # Load tokens from environment
        self.app_token = os.getenv('SLACK_APP_TOKEN')
        self.bot_token = os.getenv('SLACK_BOT_TOKEN')
        
        if not self.app_token or not self.bot_token:
            logger.error("❌ Missing Slack tokens! Please check your .env file")
            logger.error("Required: SLACK_APP_TOKEN and SLACK_BOT_TOKEN")
            sys.exit(1)
        
        self.web_client = WebClient(token=self.bot_token)
        self.client = None
        self.request_count = 0
        self.conversation_history: Dict[str, list] = {}
        
        # Initialize Salesforce connection
        self.salesforce_client = None
        self._initialize_salesforce()
        
        # Initialize intelligent routing system
        self.router = None
        self.intelligent_system = None
        if self.salesforce_client:
            schema = self._get_salesforce_schema()
            self.router = SpectrumAwareRouter()
            self.intelligent_system = EnhancedIntelligentAgenticSystem()
            logger.info("✅ Intelligent routing system initialized")
        else:
            logger.warning("Salesforce client not available, intelligent system not initialized.")
        
        logger.info("🚀 Whizzy Bot initialized successfully")
        logger.info(f"🔍 App Token: {self.app_token[:30]}...")
        logger.info(f"🔍 Bot Token: {self.bot_token[:30]}...")
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _initialize_salesforce(self):
        """Initialize Salesforce connection"""
        try:
            from simple_salesforce import Salesforce
            
            self.salesforce_client = Salesforce(
                username=os.getenv('SALESFORCE_USERNAME'),
                password=os.getenv('SALESFORCE_PASSWORD'),
                security_token=os.getenv('SALESFORCE_SECURITY_TOKEN'),
                domain=os.getenv('SALESFORCE_DOMAIN', 'login')
            )
            logger.info("✅ Salesforce connection initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Salesforce: {e}")
            self.salesforce_client = None
    
    def _get_salesforce_schema(self) -> str:
        """Get Salesforce schema for intelligent agents"""
        try:
            schema_description = "Salesforce Schema:\n"
            object_names = ['Opportunity', 'Account', 'User']
            
            for obj_name in object_names:
                try:
                    obj_desc = getattr(self.salesforce_client, obj_name).describe()
                    schema_description += f"Object: {obj_desc['name']}\n"
                    schema_description += "Fields:\n"
                    for field in obj_desc['fields']:
                        schema_description += f"- {field['name']} ({field['type']})\n"
                    schema_description += "\n"
                except Exception as e:
                    logger.error(f"Failed to describe object {obj_name}: {e}")
            
            return schema_description
        except Exception as e:
            logger.error(f"Failed to get schema: {e}")
            return "Basic Salesforce schema (Opportunity, Account, User objects available)"
    
    def _signal_handler(self, signum, frame):
        """Graceful shutdown handler"""
        logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
        if self.client:
            self.client.close()
        sys.exit(0)
    
    def handle_socket_mode_request(self, client: SocketModeClient, req: SocketModeRequest):
        """Handle Socket Mode requests"""
        self.request_count += 1
        try:
            logger.info(f"🎯 REQUEST #{self.request_count} RECEIVED!")
            logger.info(f"🔍 Request type: {req.type}")
            
            # Acknowledge immediately
            response = SocketModeResponse(envelope_id=req.envelope_id)
            client.send_socket_mode_response(response)
            logger.info("✅ Acknowledged request")
            
            if req.type == "events_api":
                event = req.payload.get("event", {})
                event_type = event.get("type")
                
                if event_type in ["app_mention", "message"]:
                    channel = event.get("channel")
                    text = event.get("text", "")
                    user = event.get("user", "")
                    ts = event.get("ts", "")
                    thread_ts = event.get("thread_ts", ts)
                    conversation_id = f"{channel}-{thread_ts}"

                    if "bot_id" in event: # Ignore messages from bots, including self
                        return

                    if event_type == "app_mention":
                        # Extract bot mention from text and remove it
                        import re
                        bot_mention_pattern = r'<@[A-Z0-9]+>'
                        text = re.sub(bot_mention_pattern, '', text).strip()
                    
                    logger.info(f"📨 Received message: Channel={channel}, User={user}, Text='{text}', ConversationID={conversation_id}")
                    
                    # Send immediate response in a thread
                    immediate_response = "🤖 **Whizzy**: Processing your request..."
                    try:
                        self.web_client.chat_postMessage(channel=channel, text=immediate_response, thread_ts=ts)
                        logger.info("✅ Sent immediate response to thread")
                    except Exception as e:
                        logger.error(f"❌ Error sending immediate response: {e}")
                    
                    # Process in background with async support
                    import asyncio
                    asyncio.create_task(self._process_query_async(text, channel, user, conversation_id, ts))
            else:
                logger.info(f"⏭️ Non-events_api request: {req.type}")
                
        except Exception as e:
            logger.error(f"❌ Error handling request: {e}")
    
    async def _process_query_async(self, text: str, channel: str, user: str, conversation_id: str, thread_ts: str):
        """Process user query and generate response asynchronously"""
        try:
            if not text.strip():
                return
            
            logger.info(f"🤖 Processing query: '{text}' for conversation {conversation_id}")

            # For now, we are just storing history. In the next step, we'll pass it to the agent.
            history = self.conversation_history.get(conversation_id, [])
            
            # Get response based on query type
            response = await self._generate_response(text, user, history)
            
            # Update history
            history.append({"role": "user", "content": text})
            history.append({"role": "assistant", "content": response})
            self.conversation_history[conversation_id] = history[-10:]  # Keep last 5 pairs
            logger.info(f"📓 Updated conversation history for {conversation_id}")

            # Send response
            try:
                self.web_client.chat_postMessage(channel=channel, text=response, thread_ts=thread_ts)
                logger.info("✅ Sent response to thread")
            except Exception as e:
                logger.error(f"❌ Error sending response: {e}")
                
        except Exception as e:
            logger.error(f"❌ Error in query processing: {e}")
            error_response = "🤖 **Whizzy**: I encountered an error processing your request. Please try again."
            try:
                self.web_client.chat_postMessage(channel=channel, text=error_response, thread_ts=thread_ts)
            except Exception as send_error:
                logger.error(f"❌ Error sending error response: {send_error}")
    
    def _process_query(self, text: str, channel: str, user: str, conversation_id: str, thread_ts: str):
        """Process user query and generate response (sync wrapper for async)"""
        import asyncio
        asyncio.run(self._process_query_async(text, channel, user, conversation_id, thread_ts))
    
    async def _generate_response(self, text: str, user: str, history: list[dict]) -> str:
                """Generate response using intelligent spectrum-aware routing."""
        
        if not self.router or not self.intelligent_system:
            return "🤖 **Whizzy**: The intelligent routing system is not available. Please check the configuration."
        
        # Convert history format
        conversation_history = []
        for msg in history:
            conversation_history.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        # Get Salesforce schema
        schema = self._get_salesforce_schema()

        # Use spectrum-aware intelligent routing
        logger.info(f"Processing query with spectrum-aware router: {text}")
        routing_decision = self.router.route_query(text)
        
        if routing_decision.layer.value == "fast_path":
            response = self.router._get_fast_path_response(routing_decision.specific_intent)
        elif routing_decision.layer.value == "smart_data_path":
            response = await self.intelligent_system.process_query(text, {})
        else:  # deep_thinking_path
            response = await self.intelligent_system.process_complex_query(text, {})
        
        return response
    
    def _load_subscriptions(self) -> List[Dict[str, Any]]:
        """Loads subscriptions from the JSON file."""
        try:
            if os.path.exists(SUBSCRIPTIONS_FILE):
                with open(SUBSCRIPTIONS_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading subscriptions: {e}")
        return []

    def _save_subscriptions(self):
        """Saves the current subscriptions to the JSON file."""
        try:
            with open(SUBSCRIPTIONS_FILE, 'w') as f:
                json.dump(self.subscriptions, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving subscriptions: {e}")

    def _handle_subscribe(self, user_id: str, text: str) -> str:
        """Handles a user's request to subscribe to a briefing."""
        parts = text.lower().split()
        if len(parts) != 3:
            return "Sorry, I didn't understand that. Please use the format: `subscribe <frequency> <persona>` (e.g., `subscribe daily vp`)."

        _, frequency, persona_short = parts

        valid_freqs = ['daily', 'weekly']
        if frequency not in valid_freqs:
            return f"Invalid frequency. Please choose from: {', '.join(valid_freqs)}."

        valid_personas = {'vp': 'VP of Sales', 'ae': 'Account Executive'}
        if persona_short not in valid_personas:
            return f"Invalid persona. Please choose from: {', '.join(valid_personas.keys())}."

        persona = valid_personas[persona_short]

        # Get user's DM channel
        try:
            im_response = self.web_client.conversations_open(users=user_id)
            channel_id = im_response['channel']['id']
        except Exception as e:
            logger.error(f"Failed to open DM with user {user_id}: {e}")
            return "I couldn't open a direct message channel with you to send briefings."

        # Remove existing subscription for the user, if any
        self.subscriptions = [s for s in self.subscriptions if s['user_id'] != user_id]

        new_subscription = {
            "user_id": user_id,
            "channel_id": channel_id,
            "persona": persona,
            "frequency": frequency,
            "subscribed_at": datetime.now().isoformat()
        }
        self.subscriptions.append(new_subscription)
        self._save_subscriptions()

        logger.info(f"User {user_id} subscribed to {frequency} {persona} briefings.")
        return f"✅ You've been subscribed to **{frequency} {persona}** briefings! I'll send them to you via DM."

    def _handle_unsubscribe(self, user_id: str) -> str:
        """Handles a user's request to unsubscribe."""
        original_count = len(self.subscriptions)
        self.subscriptions = [s for s in self.subscriptions if s['user_id'] != user_id]

        if len(self.subscriptions) < original_count:
            self._save_subscriptions()
            logger.info(f"User {user_id} unsubscribed.")
            return "You have been successfully unsubscribed from all briefings."
        else:
            return "You don't seem to have any active subscriptions."

    def _handle_list_subscriptions(self, user_id: str) -> str:
        """Lists the current user's subscriptions."""
        user_subs = [s for s in self.subscriptions if s['user_id'] == user_id]
        if not user_subs:
            return "You are not subscribed to any briefings."

        response = "Here are your current subscriptions:\n"
        for sub in user_subs:
            response += f"- **{sub['frequency'].capitalize()} {sub['persona']} Briefing**\n"
        return response

    def _get_help_response(self) -> str:
        """Get help response with available commands"""
        return """🤖 **Whizzy Bot - Salesforce Analytics**

I can help you with real-time Salesforce analytics! Here are some things you can ask me:

📊 **Data Queries:**
• "What's our win rate?"
• "Show me the pipeline"
• "Top 10 accounts by revenue"
• "Analyze our biggest deals"
• "Sales performance metrics"

📋 **Strategic Insights:**
• "Give me an executive briefing"
• "What deals are at risk?"
• "Where should we focus resources?"

💡 **Examples:**
• "What's our win rate this quarter?"
• "Show pipeline breakdown by stage"
• "Top accounts by revenue"
• "Executive briefing for Q4"

🎯 **I provide:**
• Real-time Salesforce data
• Persona-specific insights
• Actionable recommendations
• Professional formatting

Just ask me anything about your Salesforce data! 🚀"""
    
    def start(self):
        """Start the Whizzy bot"""
        try:
            logger.info("🚀 Starting Whizzy Bot...")
            
            self.client = SocketModeClient(
                app_token=self.app_token,
                web_client=self.web_client
            )
            
            self.client.socket_mode_request_listeners.append(self.handle_socket_mode_request)
            
            logger.info("✅ Whizzy Bot is now listening for requests!")
            logger.info("📱 Try mentioning @whizzy or sending a DM")
            logger.info("🛑 Press Ctrl+C to stop")
            
            self.client.connect()
            
            # Keep the bot alive
            while True:
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"❌ Error starting bot: {e}")
            sys.exit(1)

if __name__ == "__main__":
    bot = WhizzyBot()
    bot.start()
