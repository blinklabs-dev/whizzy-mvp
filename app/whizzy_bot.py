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
from typing import Dict, Any, Optional
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.web import WebClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from dotenv import load_dotenv
from app.agent import SalesforceAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WhizzyBot:
    """Whizzy Bot - Salesforce Analytics Bot"""
    
    def __init__(self):
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
        self.salesforce_agent = None
        if self.salesforce_client:
            self.salesforce_agent = SalesforceAgent(self.salesforce_client)
        else:
            logger.warning("Salesforce client not available, agent not initialized.")
        
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
                        bot_id = f"<@{client.current_bot_id}>"
                        text = text.replace(bot_id, "").strip()
                    
                    logger.info(f"📨 Received message: Channel={channel}, User={user}, Text='{text}', ConversationID={conversation_id}")
                    
                    # Send immediate response in a thread
                    immediate_response = "🤖 **Whizzy**: Processing your request..."
                    try:
                        self.web_client.chat_postMessage(channel=channel, text=immediate_response, thread_ts=ts)
                        logger.info("✅ Sent immediate response to thread")
                    except Exception as e:
                        logger.error(f"❌ Error sending immediate response: {e}")
                    
                    # Process in background
                    threading.Thread(target=self._process_query, args=(text, channel, user, conversation_id, ts)).start()
            else:
                logger.info(f"⏭️ Non-events_api request: {req.type}")
                
        except Exception as e:
            logger.error(f"❌ Error handling request: {e}")
    
    def _process_query(self, text: str, channel: str, user: str, conversation_id: str, thread_ts: str):
        """Process user query and generate response"""
        try:
            if not text.strip():
                return
            
            logger.info(f"🤖 Processing query: '{text}' for conversation {conversation_id}")

            # For now, we are just storing history. In the next step, we'll pass it to the agent.
            history = self.conversation_history.get(conversation_id, [])
            
            # Get response based on query type
            response = self._generate_response(text, user, history)
            
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
    
    def _generate_response(self, text: str, user: str, history: list[dict]) -> str:
        """Generate response using the Salesforce Agent."""
        text_lower = text.lower()

        # Add a backdoor for help
        if "help" in text_lower:
            return self._get_help_response()

        if not self.salesforce_agent:
            return "🤖 **Whizzy**: The Salesforce Agent is not available. Please check the configuration."

        logger.info("Handing query to Salesforce Agent", user_query=text)
        soql_query = self.salesforce_agent.generate_soql_query(text, history)

        if soql_query.startswith("Error:"):
            logger.warning("Agent failed to generate SOQL", error=soql_query)
            return f"🤖 **Whizzy**: I had trouble generating a Salesforce query for that. {soql_query}"

        # If the agent returns a non-query response, it might be a clarifying question or a direct answer.
        if not soql_query.upper().startswith("SELECT"):
            logger.info("Agent returned a conversational response", response=soql_query)
            return soql_query

        try:
            logger.info("Executing generated SOQL", soql_query=soql_query)
            result = self.salesforce_client.query_all(soql_query)
            
            if result['totalSize'] == 0:
                return "I found no results for that query."
            
            # Convert the raw data to a string for the summarizer
            raw_data_str = json.dumps(result['records'], indent=2, default=str)

            # Summarize the data using the agent
            summary = self.salesforce_agent.summarize_data_with_llm(text, raw_data_str)
            return summary

        except Exception as e:
            logger.error("Error executing SOQL query", soql_query=soql_query, error=e)
            return f"🤖 **Whizzy**: I tried to run a query, but it failed: `{soql_query}`. \nError: `{e}`"
    
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
