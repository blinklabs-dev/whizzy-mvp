#!/usr/bin/env python3
"""
Enhanced Whizzy Bot - Intelligent Agentic Integration with Advanced Thinking
Features:
- Advanced intent classification and orchestration with thinking capabilities
- Multi-source analytics (Salesforce, Snowflake, dbt)
- Persona-specific coffee briefings with context awareness
- Text-to-SOQL, Text-to-dbt, Text-to-Business Intelligence
- Comprehensive quality evaluation with thinking metrics
- Chain of thought reasoning and context management
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

# Import enhanced intelligent agentic system
from intelligent_agentic_system import (
    EnhancedIntelligentAgenticSystem, IntentType, PersonaType,
    DataSourceType, IntentAnalysis, AgentResponse, CoffeeBriefing,
    ChainOfThought, ContextState
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
    """Enhanced Whizzy Bot with Advanced Intelligent Agentic System"""

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

        # Initialize Enhanced Intelligent Agentic System
        self.enhanced_system = EnhancedIntelligentAgenticSystem()

        # User context tracking (now handled by the enhanced system)
        self.user_mapping = {}  # Map Slack user IDs to internal user IDs

        logger.info("🚀 Enhanced Whizzy Bot initialized with Advanced Intelligent Agentic System")
        logger.info(f"🔍 App Token: {self.app_token[:30]}...")
        logger.info(f"🔍 Bot Token: {self.bot_token[:30]}...")
        logger.info("🧠 Advanced Thinking and Reasoning: ENABLED")
        logger.info("🔗 Chain of Thought Processing: ENABLED")
        logger.info("📊 Context Management: ENABLED")

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
        """Handle Socket Mode requests with enhanced intelligent processing"""
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
                    immediate_response = "🧠 **Enhanced Whizzy**: Processing your request with advanced thinking and reasoning..."
                    try:
                        self.web_client.chat_postMessage(channel=channel, text=immediate_response)
                        logger.info("✅ Sent immediate response")
                    except Exception as e:
                        logger.error(f"❌ Error sending immediate response: {e}")

                    # Process in background with enhanced intelligent system
                    threading.Thread(target=self._process_enhanced_response, args=(text, channel, user)).start()
            else:
                logger.info(f"⏭️ Non-events_api request: {req.type}")

        except Exception as e:
            logger.error(f"❌ Error handling request: {e}")

    def _process_enhanced_response(self, text: str, channel: str, user: str):
        """Process query with enhanced intelligent agentic system"""
        try:
            if not text.strip():
                return

            logger.info(f"🧠 Processing enhanced intelligent response: '{text}'")

            # Get or create user mapping
            internal_user_id = self.user_mapping.get(user, f"slack_user_{user}")
            if user not in self.user_mapping:
                self.user_mapping[user] = internal_user_id

            # Get user context from enhanced system
            context_state = self.enhanced_system._get_context_state(internal_user_id)

            # Process with enhanced intelligent system
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                agent_response = loop.run_until_complete(
                    self.enhanced_system.process_query(text, {}, internal_user_id)
                )

                # Format and send enhanced response
                formatted_response = self._format_enhanced_response(agent_response, text, context_state)
                self._send_enhanced_response(channel, formatted_response)

            finally:
                loop.close()

        except Exception as e:
            logger.error(f"❌ Error in enhanced intelligent response processing: {e}")
            error_response = "🤖 **Enhanced Whizzy**: I encountered an error processing your request. Please try again."
            try:
                self.web_client.chat_postMessage(channel=channel, text=error_response)
            except Exception as send_error:
                logger.error(f"❌ Error sending error response: {send_error}")

    def _format_enhanced_response(self, agent_response: AgentResponse, original_query: str, context_state: ContextState) -> str:
        """Format enhanced response with thinking and context insights"""
        try:
            # Base response
            response_parts = [agent_response.response_text]

            # Add thinking process if available
            if agent_response.chain_of_thought:
                response_parts.append(f"""
🧠 **Thinking Process**:
**Chain of Thought Steps**: {len(agent_response.chain_of_thought.thinking_steps)}
**Reasoning Path**: {agent_response.chain_of_thought.reasoning_path[:200]}...
**Final Confidence**: {agent_response.chain_of_thought.final_confidence:.1%}
""")

            # Add quality metrics if confidence is high
            if agent_response.confidence_score > 0.8:
                response_parts.append(f"""
📊 **Enhanced Quality Metrics**:
• Confidence: {agent_response.confidence_score:.1%}
• Persona Alignment: {agent_response.persona_alignment:.1%}
• Actionability: {agent_response.actionability_score:.1%}
• Context Awareness: {agent_response.quality_metrics.get('context_awareness', 0):.1%}
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

            # Add context insights
            if context_state.conversation_history:
                response_parts.append(f"""
📈 **Context Insights**:
• Conversation History: {len(context_state.conversation_history)} interactions
• Session Duration: {(time.time() - context_state.session_start.timestamp()):.0f} seconds
• Preferred Persona: {context_state.current_context.get('last_persona', 'Unknown')}
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
        """Schedule enhanced coffee briefings with context awareness"""
        try:
            # This would integrate with a scheduler like APScheduler
            # For now, we'll just log the capability
            logger.info("☕ Enhanced coffee briefing scheduler initialized")
            logger.info("🧠 Context-aware briefings enabled")

            # Example briefing schedule with context:
            # - VP Sales: Daily at 8 AM with strategic context
            # - Account Executives: Weekly on Monday with deal context
            # - CDO: Monthly on first Monday with technical context
            # - Sales Managers: Daily at 9 AM with team context

        except Exception as e:
            logger.error(f"❌ Error setting up enhanced coffee briefings: {e}")

    def _send_enhanced_coffee_briefing(self, channel: str, persona: PersonaType, frequency: str, user_id: str = None):
        """Send scheduled enhanced coffee briefing with context"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # Get context state for personalized briefing
                context_state = None
                if user_id:
                    context_state = self.enhanced_system._get_context_state(user_id)

                # Generate enhanced coffee briefing
                briefing = loop.run_until_complete(
                    self.enhanced_system._generate_coffee_briefing(persona, frequency)
                )

                # Format with context awareness
                formatted_briefing = self.enhanced_system._format_coffee_briefing(briefing)

                # Add context insights if available
                if context_state:
                    context_insights = f"""
📊 **Personalized Context**:
• Previous Interactions: {len(context_state.conversation_history)}
• Preferred Data Sources: {[ds.value for ds in context_state.data_source_preferences]}
• Session Duration: {(time.time() - context_state.session_start.timestamp()):.0f} seconds
"""
                    formatted_briefing += context_insights

                self.web_client.chat_postMessage(channel=channel, text=formatted_briefing)

                logger.info(f"☕ Sent {frequency} enhanced coffee briefing for {persona.value}")

            finally:
                loop.close()

        except Exception as e:
            logger.error(f"❌ Error sending enhanced coffee briefing: {e}")

    def get_enhanced_system_metrics(self) -> Dict[str, Any]:
        """Get enhanced system performance metrics with thinking analysis"""
        try:
            # Get enhanced intelligent system metrics
            enhanced_metrics = self.enhanced_system.get_enhanced_quality_metrics()

            # Get bot metrics
            bot_metrics = {
                "total_requests": self.request_count,
                "active_users": len(self.user_mapping),
                "uptime": time.time() - getattr(self, '_start_time', time.time())
            }

            return {
                "enhanced_intelligent_system": enhanced_metrics,
                "bot_performance": bot_metrics,
                "thinking_capabilities": {
                    "thinking_rate": enhanced_metrics.get("thinking_rate", 0),
                    "context_awareness": enhanced_metrics.get("average_context_awareness", 0),
                    "chain_of_thought_enabled": True,
                    "context_management": True
                },
                "overall_health": "enhanced_healthy" if self.request_count > 0 else "initializing"
            }

        except Exception as e:
            logger.error(f"❌ Error getting enhanced system metrics: {e}")
            return {"error": str(e)}

    def start(self):
        """Start the enhanced Whizzy bot"""
        try:
            logger.info("🚀 Starting Enhanced Whizzy Bot...")

            # Set start time for metrics
            self._start_time = time.time()

            # Initialize enhanced coffee briefing scheduler
            self._schedule_coffee_briefings()

            self.client = SocketModeClient(
                app_token=self.app_token,
                web_client=self.web_client
            )

            self.client.socket_mode_request_listeners.append(self.handle_socket_mode_request)

            logger.info("✅ Enhanced Whizzy Bot is now listening for requests!")
            logger.info("🧠 Enhanced Intelligent Agentic System: ACTIVE")
            logger.info("🔗 Chain of Thought Processing: ENABLED")
            logger.info("📊 Context Management: ENABLED")
            logger.info("☕ Enhanced Coffee Briefings: SCHEDULED")
            logger.info("📈 Enhanced Quality Evaluation: ENABLED")
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
