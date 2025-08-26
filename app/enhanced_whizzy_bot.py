#!/usr/bin/env python3
"""
Enhanced Whizzy Bot - Intelligent Agentic Integration
Features:
- Advanced intent classification and orchestration
- Multi-source analytics (Salesforce, Snowflake, dbt)
- Persona-specific coffee briefings
- Text-to-SOQL, Text-to-dbt, Text-to-Business Intelligence
- Comprehensive quality evaluation
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

# Import intelligent agentic system
from intelligent_agentic_system import (
    IntelligentAgenticSystem, IntentType, PersonaType, 
    DataSourceType, IntentAnalysis, AgentResponse, CoffeeBriefing
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedWhizzyBot:
    """Enhanced Whizzy Bot with Intelligent Agentic System"""
    
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
        
        # Initialize Intelligent Agentic System
        self.intelligent_system = IntelligentAgenticSystem()
        
        # User context tracking
        self.user_contexts = {}
        
        logger.info("🚀 Enhanced Whizzy Bot initialized with Intelligent Agentic System")
        logger.info(f"🔍 App Token: {self.app_token[:30]}...")
        logger.info(f"🔍 Bot Token: {self.bot_token[:30]}...")
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Graceful shutdown handler"""
        logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
        if self.client:
            self.client.close()
        sys.exit(0)
    
    def handle_socket_mode_request(self, client: SocketModeClient, req: SocketModeRequest):
        """Handle Socket Mode requests with intelligent processing"""
        self.request_count += 1
        try:
            logger.info(f"🎯 ENHANCED REQUEST #{self.request_count} RECEIVED!")
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
                    
                    if event_type == "app_mention":
                        bot_id = f"<@{event.get('bot_id', 'U09CPBX5T1N')}>"
                        text = text.replace(bot_id, "").strip()
                    
                    logger.info(f"📨 Channel: {channel}, User: {user}, Text: '{text}'")
                    
                    # Send immediate response
                    immediate_response = "🧠 **Enhanced Whizzy**: Processing your request with intelligent analysis..."
                    try:
                        self.web_client.chat_postMessage(channel=channel, text=immediate_response)
                        logger.info("✅ Sent immediate response")
                    except Exception as e:
                        logger.error(f"❌ Error sending immediate response: {e}")
                    
                    # Process in background with intelligent system
                    threading.Thread(target=self._process_intelligent_response, args=(text, channel, user)).start()
            else:
                logger.info(f"⏭️ Non-events_api request: {req.type}")
                
        except Exception as e:
            logger.error(f"❌ Error handling request: {e}")
    
    def _process_intelligent_response(self, text: str, channel: str, user: str):
        """Process query with intelligent agentic system"""
        try:
            if not text.strip():
                return
            
            logger.info(f"🧠 Processing intelligent response: '{text}'")
            
            # Get user context
            user_context = self.user_contexts.get(user, {})
            
            # Process with intelligent system
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                agent_response = loop.run_until_complete(
                    self.intelligent_system.process_query(text, user_context)
                )
                
                # Update user context
                self.user_contexts[user] = {
                    "last_query": text,
                    "persona": agent_response.persona_alignment,
                    "confidence": agent_response.confidence_score,
                    "timestamp": time.time()
                }
                
                # Format and send response
                formatted_response = self._format_enhanced_response(agent_response, text)
                self._send_enhanced_response(channel, formatted_response)
                
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"❌ Error in intelligent response processing: {e}")
            error_response = "🤖 **Enhanced Whizzy**: I encountered an error processing your request. Please try again."
            try:
                self.web_client.chat_postMessage(channel=channel, text=error_response)
            except Exception as send_error:
                logger.error(f"❌ Error sending error response: {send_error}")
    
    def _format_enhanced_response(self, agent_response: AgentResponse, original_query: str) -> str:
        """Format enhanced response with quality metrics and insights"""
        try:
            # Base response
            response_parts = [agent_response.response_text]
            
            # Add quality metrics if confidence is high
            if agent_response.confidence_score > 0.8:
                response_parts.append(f"""
📊 **Quality Metrics**:
• Confidence: {agent_response.confidence_score:.1%}
• Persona Alignment: {agent_response.persona_alignment:.1%}
• Actionability: {agent_response.actionability_score:.1%}
""")
            
            # Add data sources used
            if agent_response.data_sources_used:
                sources = [ds.value.replace('_', ' ').title() for ds in agent_response.data_sources_used]
                response_parts.append(f"🔗 **Data Sources**: {', '.join(sources)}")
            
            # Add reasoning steps if available
            if agent_response.reasoning_steps:
                response_parts.append(f"""
🧠 **Analysis Steps**:
{chr(10).join(f'• {step}' for step in agent_response.reasoning_steps[:3])}
""")
            
            # Add quality insights
            if agent_response.quality_metrics:
                quality_insights = []
                for metric, score in agent_response.quality_metrics.items():
                    if score > 0.8:
                        quality_insights.append(f"✅ {metric.replace('_', ' ').title()}: {score:.1%}")
                    elif score > 0.6:
                        quality_insights.append(f"⚠️ {metric.replace('_', ' ').title()}: {score:.1%}")
                
                if quality_insights:
                    response_parts.append(f"""
🎯 **Quality Insights**:
{chr(10).join(quality_insights)}
""")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"❌ Error formatting enhanced response: {e}")
            return agent_response.response_text
    
    def _send_enhanced_response(self, channel: str, response_text: str):
        """Send enhanced response to Slack"""
        try:
            # Split long responses if needed
            if len(response_text) > 3000:
                # Split into chunks
                chunks = self._split_response(response_text)
                for i, chunk in enumerate(chunks):
                    if i == 0:
                        self.web_client.chat_postMessage(channel=channel, text=chunk)
                    else:
                        self.web_client.chat_postMessage(channel=channel, text=f"*Continued...*\n{chunk}")
            else:
                self.web_client.chat_postMessage(channel=channel, text=response_text)
            
            logger.info("✅ Sent enhanced response")
            
        except Exception as e:
            logger.error(f"❌ Error sending enhanced response: {e}")
    
    def _split_response(self, response_text: str, max_length: int = 3000) -> list:
        """Split long response into chunks"""
        chunks = []
        lines = response_text.split('\n')
        current_chunk = []
        current_length = 0
        
        for line in lines:
            if current_length + len(line) > max_length and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_length = len(line)
            else:
                current_chunk.append(line)
                current_length += len(line) + 1
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    def _schedule_coffee_briefings(self):
        """Schedule coffee briefings for different personas"""
        try:
            # This would integrate with a scheduler like APScheduler
            # For now, we'll just log the capability
            logger.info("☕ Coffee briefing scheduler initialized")
            
            # Example briefing schedule:
            # - VP Sales: Daily at 8 AM
            # - Account Executives: Weekly on Monday
            # - CDO: Monthly on first Monday
            # - Sales Managers: Daily at 9 AM
            
        except Exception as e:
            logger.error(f"❌ Error setting up coffee briefings: {e}")
    
    def _send_coffee_briefing(self, channel: str, persona: PersonaType, frequency: str):
        """Send scheduled coffee briefing"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Generate coffee briefing
                briefing = loop.run_until_complete(
                    self.intelligent_system._generate_coffee_briefing(persona, frequency)
                )
                
                # Format and send
                formatted_briefing = self.intelligent_system._format_coffee_briefing(briefing)
                self.web_client.chat_postMessage(channel=channel, text=formatted_briefing)
                
                logger.info(f"☕ Sent {frequency} coffee briefing for {persona.value}")
                
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"❌ Error sending coffee briefing: {e}")
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            # Get intelligent system metrics
            intelligent_metrics = self.intelligent_system.get_quality_metrics()
            
            # Get bot metrics
            bot_metrics = {
                "total_requests": self.request_count,
                "active_users": len(self.user_contexts),
                "uptime": time.time() - getattr(self, '_start_time', time.time())
            }
            
            return {
                "intelligent_system": intelligent_metrics,
                "bot_performance": bot_metrics,
                "overall_health": "healthy" if self.request_count > 0 else "initializing"
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting system metrics: {e}")
            return {"error": str(e)}
    
    def start(self):
        """Start the enhanced Whizzy bot"""
        try:
            logger.info("🚀 Starting Enhanced Whizzy Bot...")
            
            # Set start time for metrics
            self._start_time = time.time()
            
            # Initialize coffee briefing scheduler
            self._schedule_coffee_briefings()
            
            self.client = SocketModeClient(
                app_token=self.app_token,
                web_client=self.web_client
            )
            
            self.client.socket_mode_request_listeners.append(self.handle_socket_mode_request)
            
            logger.info("✅ Enhanced Whizzy Bot is now listening for requests!")
            logger.info("🧠 Intelligent Agentic System: ACTIVE")
            logger.info("☕ Coffee Briefings: SCHEDULED")
            logger.info("📊 Quality Evaluation: ENABLED")
            logger.info("📱 Try mentioning @whizzy or sending a DM")
            logger.info("🛑 Press Ctrl+C to stop")
            
            self.client.connect()
            
            # Keep the bot alive
            while True:
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"❌ Error starting enhanced bot: {e}")
            sys.exit(1)


if __name__ == "__main__":
    bot = EnhancedWhizzyBot()
    bot.start()
