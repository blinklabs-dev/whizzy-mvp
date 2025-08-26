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
        
        # Initialize Enhanced Intelligent Agentic System
        try:
            from app.intelligent_agentic_system import EnhancedIntelligentAgenticSystem
            self.enhanced_system = EnhancedIntelligentAgenticSystem()
            logger.info("🧠 Enhanced Intelligent Agentic System initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Enhanced System: {e}")
            self.enhanced_system = None
        
        # Initialize Salesforce connection (fallback)
        self.salesforce_client = None
        self._initialize_salesforce()
        
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

                    if event_type == "app_mention":
                        bot_id = f"<@{event.get('bot_id', 'U09CPBX5T1N')}>"
                        text = text.replace(bot_id, "").strip()
                    
                    logger.info(f"📨 Channel: {channel}, User: {user}, Text: '{text}'")
                    
                    # Send immediate response
                    immediate_response = "🤖 **Whizzy**: Processing your request..."
                    try:
                        self.web_client.chat_postMessage(channel=channel, text=immediate_response)
                        logger.info("✅ Sent immediate response")
                    except Exception as e:
                        logger.error(f"❌ Error sending immediate response: {e}")
                    
                    # Process in background
                    threading.Thread(target=self._process_query, args=(text, channel, user)).start()
            else:
                logger.info(f"⏭️ Non-events_api request: {req.type}")
                
        except Exception as e:
            logger.error(f"❌ Error handling request: {e}")
    
    def _process_query(self, text: str, channel: str, user: str):
        """Process user query and generate response"""
        try:
            if not text.strip():
                return
            
            logger.info(f"🤖 Processing query: '{text}'")
            
            # Get response based on query type
            response = self._generate_response(text, user)
            
            # Send response
            try:
                self.web_client.chat_postMessage(channel=channel, text=response)
                logger.info("✅ Sent response")
            except Exception as e:
                logger.error(f"❌ Error sending response: {e}")
                
        except Exception as e:
            logger.error(f"❌ Error in query processing: {e}")
            error_response = "🤖 **Whizzy**: I encountered an error processing your request. Please try again."
            try:
                self.web_client.chat_postMessage(channel=channel, text=error_response)
            except Exception as send_error:
                logger.error(f"❌ Error sending error response: {send_error}")
    
    def _generate_response(self, text: str, user: str) -> str:
        """Generate response using Enhanced Intelligent Agentic System"""
        try:
            # Use Enhanced Intelligent Agentic System if available
            if self.enhanced_system:
                logger.info("🧠 Using Enhanced Intelligent Agentic System")
                
                # Import required components
                from app.intelligent_agentic_system import PersonaType
                import asyncio
                
                # Create event loop for async execution
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # Execute query with enhanced system
                    response = loop.run_until_complete(
                        self.enhanced_system.execute_query(text, PersonaType.VP_SALES, user)
                    )
                    
                    # Format response
                    if hasattr(response, 'response_text'):
                        return f"🤖 **Whizzy**: {response.response_text}"
                    else:
                        return f"🤖 **Whizzy**: {str(response)}"
                        
                finally:
                    loop.close()
            
            # Fallback to old system if enhanced system not available
            logger.info("⚠️ Using fallback system")
            text_lower = text.lower()

            if not self.salesforce_client:
                return "🤖 **Whizzy**: Salesforce connection not available. Please check configuration."

            # Win rate analysis
            if "win rate" in text_lower:
                return self._get_win_rate_analysis()

            # Pipeline overview
            elif "pipeline" in text_lower:
                return self._get_pipeline_overview()

            # Top accounts
            elif any(phrase in text_lower for phrase in ["top 10 accounts", "accounts by revenue", "top accounts"]):
                return self._get_top_accounts()

            # Executive briefing
            elif "briefing" in text_lower:
                return self._get_executive_briefing()

            # Deal analysis
            elif any(phrase in text_lower for phrase in ["biggest deals", "deal analysis", "top deals"]):
                return self._get_deal_analysis()

            # Performance metrics
            elif any(phrase in text_lower for phrase in ["performance", "metrics", "kpi"]):
                return self._get_performance_metrics()

            # Default response
            else:
                return self._get_help_response()

        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            return "🤖 **Whizzy**: I encountered an error accessing Salesforce data. Please try again."

    def _get_win_rate_analysis(self) -> str:
        """Get win rate analysis from Salesforce"""
        try:
            total_result = self.salesforce_client.query("SELECT COUNT(Id) total FROM Opportunity")
            won_result = self.salesforce_client.query("SELECT COUNT(Id) won FROM Opportunity WHERE StageName = 'Closed Won'")
            lost_result = self.salesforce_client.query("SELECT COUNT(Id) lost FROM Opportunity WHERE StageName = 'Closed Lost'")

            total = total_result['records'][0]['total']
            won = won_result['records'][0]['won']
            lost = lost_result['records'][0]['lost']
            win_rate = (won / total * 100) if total > 0 else 0

            return f"""🎯 **Win Rate Analysis**

📊 **Overall Performance:**
• Win Rate: {win_rate:.1f}%
• Total Opportunities: {total:,}
• Won: {won:,}
• Lost: {lost:,}

💡 **Insights:**
• Conversion ratio: {won}:{lost} (won:lost)
• Success rate: {win_rate:.1f}% of all opportunities
• Pipeline efficiency: {total - won - lost:,} opportunities still active

🎯 **Recommendations:**
• Focus on opportunities in negotiation stage
• Review lost deals for improvement opportunities
• Monitor pipeline velocity for forecasting"""

        except Exception as e:
            logger.error(f"❌ Error getting win rate: {e}")
            return "🤖 **Whizzy**: Unable to retrieve win rate data at this time."

    def _get_pipeline_overview(self) -> str:
        """Get pipeline overview from Salesforce"""
        try:
            result = self.salesforce_client.query(
                "SELECT StageName, COUNT(Id) total_count, SUM(Amount) total_amount "
                "FROM Opportunity WHERE IsClosed = false "
                "GROUP BY StageName ORDER BY total_amount DESC"
            )

            pipeline_data = []
            total_value = 0
            total_opportunities = 0

            for record in result['records']:
                stage = record['StageName']
                count = record['total_count']
                amount = record['total_amount'] or 0
                total_value += amount
                total_opportunities += count
                pipeline_data.append(f"• **{stage}**: {count:,} opportunities, ${amount:,.0f}")

            return f"""📊 **Pipeline Overview**

💰 **Total Pipeline Value**: ${total_value:,.0f}
📈 **Total Opportunities**: {total_opportunities:,}

**Stage Breakdown:**
{chr(10).join(pipeline_data[:5])}

💡 **Key Insights:**
• Average deal size: ${total_value / total_opportunities:,.0f} per opportunity
• Pipeline health: {len(pipeline_data)} active stages
• Focus areas: Top 3 stages represent highest value

🎯 **Strategic Actions:**
• Prioritize high-value stages
• Monitor pipeline velocity
• Forecast based on historical win rates"""

        except Exception as e:
            logger.error(f"❌ Error getting pipeline: {e}")
            return "🤖 **Whizzy**: Unable to retrieve pipeline data at this time."

    def _get_top_accounts(self) -> str:
        """Get top accounts by revenue"""
        try:
            result = self.salesforce_client.query(
                "SELECT Name, AnnualRevenue, Industry, BillingCity, BillingState "
                "FROM Account WHERE AnnualRevenue > 0 "
                "ORDER BY AnnualRevenue DESC LIMIT 10"
            )
            
            accounts = []
            total_revenue = 0
            
            for i, record in enumerate(result['records'], 1):
                name = record['Name']
                revenue = record['AnnualRevenue'] or 0
                industry = record['Industry'] or 'Unknown'
                city = record['BillingCity'] or 'Unknown'
                state = record['BillingState'] or 'Unknown'
                total_revenue += revenue

                accounts.append(f"{i}. **{name}**")
                accounts.append(f"   💰 Revenue: ${revenue:,.0f}")
                accounts.append(f"   🏭 Industry: {industry}")
                accounts.append(f"   📍 Location: {city}, {state}")
                accounts.append("")

            return f"""🏆 **Top 10 Accounts by Revenue**

💰 **Total Revenue**: ${total_revenue:,.0f}
📊 **Average Revenue**: ${total_revenue / len(result['records']):,.0f}

{chr(10).join(accounts)}

💡 **Insights:**
• Top account represents {result['records'][0]['AnnualRevenue'] / total_revenue * 100:.1f}% of total revenue
• Geographic distribution across {len(set(r['BillingState'] for r in result['records'] if r['BillingState']))} states
• Industry diversity: {len(set(r['Industry'] for r in result['records'] if r['Industry']))} industries

🎯 **Strategic Focus:**
• Nurture relationships with top accounts
• Identify expansion opportunities
• Target similar companies in same industries"""

        except Exception as e:
            logger.error(f"❌ Error getting top accounts: {e}")
            return "🤖 **Whizzy**: Unable to retrieve account data at this time."
    
    def _get_executive_briefing(self) -> str:
        """Get executive briefing with strategic insights"""
        try:
            # Get key metrics
            opp_result = self.salesforce_client.query(
                "SELECT COUNT(Id) total, SUM(Amount) total_value "
                "FROM Opportunity WHERE IsClosed = false"
            )

            win_rate_result = self.salesforce_client.query(
                "SELECT COUNT(Id) total, SUM(CASE WHEN StageName = 'Closed Won' THEN 1 ELSE 0 END) won "
                "FROM Opportunity"
            )

            opp_data = opp_result['records'][0]
            win_data = win_rate_result['records'][0]

            total_opps = opp_data['total']
            total_value = opp_data['total_value'] or 0
            total_all = win_data['total']
            won_all = win_data['won']
            win_rate = (won_all / total_all * 100) if total_all > 0 else 0

            return f"""📋 **Executive Briefing**

📊 **Key Metrics:**
• **Open Opportunities**: {total_opps:,}
• **Pipeline Value**: ${total_value:,.0f}
• **Overall Win Rate**: {win_rate:.1f}%
• **Total Historical**: {total_all:,} opportunities

🎯 **Strategic Insights:**
• Pipeline health: {total_opps:,} active opportunities
• Average deal size: ${total_value / total_opps:,.0f}
• Conversion potential: ${total_value * (win_rate / 100):,.0f} based on historical rates

📈 **Focus Areas:**
• High-value opportunities in negotiation stage
• Accounts with expansion potential
• Pipeline velocity optimization

🚀 **Action Items:**
• Review top 10 opportunities weekly
• Monitor win rate trends
• Forecast Q4 pipeline performance
• Identify resource allocation needs

💡 **Risk Assessment:**
• Pipeline concentration risk
• Win rate volatility
• Resource constraints

🎯 **Next Steps:**
• Weekly pipeline reviews
• Monthly forecasting updates
• Quarterly strategic planning"""

        except Exception as e:
            logger.error(f"❌ Error getting executive briefing: {e}")
            return "🤖 **Whizzy**: Unable to generate executive briefing at this time."

    def _get_deal_analysis(self) -> str:
        """Get deal analysis and insights"""
        try:
            result = self.salesforce_client.query(
                "SELECT Name, Amount, StageName, CloseDate, Account.Name, Owner.Name "
                "FROM Opportunity WHERE Amount > 0 "
                "ORDER BY Amount DESC LIMIT 10"
            )

            deals = []
            total_value = 0

            for i, record in enumerate(result['records'], 1):
                name = record['Name']
                amount = record['Amount'] or 0
                stage = record['StageName']
                close_date = record['CloseDate']
                account = record['Account']['Name'] if record['Account'] else 'Unknown'
                owner = record['Owner']['Name'] if record['Owner'] else 'Unknown'
                total_value += amount

                deals.append(f"{i}. **{name}**")
                deals.append(f"   💰 Amount: ${amount:,.0f}")
                deals.append(f"   📊 Stage: {stage}")
                deals.append(f"   🏢 Account: {account}")
                deals.append(f"   👤 Owner: {owner}")
                if close_date:
                    deals.append(f"   📅 Close Date: {close_date}")
                deals.append("")

            return f"""💼 **Top Deals Analysis**

💰 **Total Value**: ${total_value:,.0f}
📊 **Average Deal Size**: ${total_value / len(result['records']):,.0f}

{chr(10).join(deals)}

💡 **Key Insights:**
• Largest deal: ${result['records'][0]['Amount']:,.0f} ({result['records'][0]['Name']})
• Deal size range: ${result['records'][-1]['Amount']:,.0f} - ${result['records'][0]['Amount']:,.0f}
• Stage distribution: {len(set(r['StageName'] for r in result['records']))} active stages

🎯 **Strategic Actions:**
• Focus resources on high-value deals
• Monitor deal velocity
• Identify expansion opportunities
• Coach owners on deal management

📈 **Forecasting:**
• Pipeline potential: ${total_value:,.0f}
• Risk assessment: Monitor close dates
• Resource allocation: Prioritize by value"""

        except Exception as e:
            logger.error(f"❌ Error getting deal analysis: {e}")
            return "🤖 **Whizzy**: Unable to retrieve deal data at this time."

    def _get_performance_metrics(self) -> str:
        """Get performance metrics and KPIs"""
        try:
            # Get various performance metrics
            opp_count = self.salesforce_client.query("SELECT COUNT(Id) total FROM Opportunity")
            won_count = self.salesforce_client.query("SELECT COUNT(Id) won FROM Opportunity WHERE StageName = 'Closed Won'")
            open_count = self.salesforce_client.query("SELECT COUNT(Id) open FROM Opportunity WHERE IsClosed = false")

            total = opp_count['records'][0]['total']
            won = won_count['records'][0]['won']
            open_opps = open_count['records'][0]['open']
            win_rate = (won / total * 100) if total > 0 else 0

            return f"""📊 **Performance Metrics**

🎯 **Key Performance Indicators:**
• **Total Opportunities**: {total:,}
• **Won Opportunities**: {won:,}
• **Open Opportunities**: {open_opps:,}
• **Win Rate**: {win_rate:.1f}%
• **Conversion Rate**: {won / (total - open_opps) * 100:.1f}% (of closed deals)

📈 **Pipeline Metrics:**
• **Pipeline Coverage**: {open_opps:,} active opportunities
• **Pipeline Health**: {open_opps / total * 100:.1f}% of total opportunities
• **Deal Velocity**: Monitor average days in each stage

💡 **Performance Insights:**
• Success rate: {win_rate:.1f}% overall
• Pipeline efficiency: {open_opps:,} opportunities in progress
• Conversion optimization: Focus on closing open deals

🎯 **Improvement Areas:**
• Increase win rate through better qualification
• Reduce time in pipeline stages
• Improve deal velocity
• Enhance forecasting accuracy

📊 **Benchmarks:**
• Industry average win rate: 20-30%
• Target win rate: 25%+
• Pipeline coverage: 3-4x quota"""

        except Exception as e:
            logger.error(f"❌ Error getting performance metrics: {e}")
            return "🤖 **Whizzy**: Unable to retrieve performance data at this time."

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
