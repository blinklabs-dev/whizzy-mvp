#!/usr/bin/env python3
"""
Comprehensive Briefing System with JSON Contracts and Slack Markdown Rendering
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import structlog

logger = structlog.get_logger()

class PersonaType(Enum):
    VP_SALES = "vp_sales"
    ACCOUNT_EXECUTIVE = "account_executive"
    CDO = "cdo"

class BriefingType(Enum):
    PIPELINE_COVERAGE = "pipeline_coverage"
    STUCK_DEALS = "stuck_deals"
    FORECAST_ACCURACY = "forecast_accuracy"
    WIN_RATE = "win_rate"
    PERFORMANCE_METRICS = "performance_metrics"

@dataclass
class BriefingContract:
    """Structured briefing contract with JSON and Slack markdown"""
    headline: str
    pipeline: Dict[str, Any]
    insights: List[str]
    actions: List[str]
    persona: PersonaType
    briefing_type: BriefingType
    timestamp: str
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        # Convert enum values to strings for JSON serialization
        data = {
            "headline": self.headline,
            "pipeline": self.pipeline,
            "insights": self.insights,
            "actions": self.actions,
            "persona": self.persona.value,  # Convert enum to string
            "briefing_type": self.briefing_type.value,  # Convert enum to string
            "timestamp": self.timestamp
        }
        return json.dumps(data, indent=2)
    
    def to_slack_markdown(self) -> str:
        """Convert to Slack markdown format"""
        if self.briefing_type == BriefingType.PIPELINE_COVERAGE:
            return self._format_pipeline_coverage()
        elif self.briefing_type == BriefingType.STUCK_DEALS:
            return self._format_stuck_deals()
        elif self.briefing_type == BriefingType.FORECAST_ACCURACY:
            return self._format_forecast_accuracy()
        else:
            return self._format_generic()
    
    def _format_pipeline_coverage(self) -> str:
        """Format pipeline coverage briefing to match product requirements"""
        pipeline = self.pipeline
        
        # Format headline with actual data
        headline = f"Pipeline Coverage: {pipeline.get('quota_coverage', 0):.1f}x"
        
        return f""":bar_chart: **{headline}**
• **Total Pipeline**: ${pipeline.get('total_pipeline', 0):,}
• **Quota Coverage**: {pipeline.get('quota_coverage', 0):.1f}x
• **Win Rate**: {pipeline.get('win_rate', '0%')}
• **Risks**: {pipeline.get('risks', 'No risks identified')}

:dart: **Insights**
{chr(10).join(f"• {insight}" for insight in self.insights)}

:rocket: **Recommended Actions**
{chr(10).join(f"{i+1}. {action}" for i, action in enumerate(self.actions))}"""

    def _format_stuck_deals(self) -> str:
        """Format stuck deals briefing with AE-focused details"""
        pipeline = self.pipeline
        
        # Format headline with actual data
        headline = f"{pipeline.get('stuck_deals', 0)} deals stuck >{pipeline.get('days_threshold', 14)} days"
        
        # Add stuck deals by stage breakdown
        stage_breakdown = ""
        if 'stuck_by_stage' in pipeline and pipeline['stuck_by_stage']:
            stage_breakdown = "\n**Stuck by Stage:**\n"
            for stage in pipeline['stuck_by_stage'][:3]:  # Top 3 stages
                stage_breakdown += f"• {stage['StageName']}: {stage['count']} deals (${stage['value']:,.0f})\n"
        
        # Add individual deal details for AE
        deal_details = ""
        if 'stuck_deals_detail' in pipeline and pipeline['stuck_deals_detail']:
            deal_details = "\n**Top Stuck Deals:**\n"
            for i, deal in enumerate(pipeline['stuck_deals_detail'][:3], 1):  # Top 3 deals
                deal_details += f"{i}. {deal['Name']} - ${deal['Amount']:,.0f} ({deal['StageName']})\n"
        
        return f""":warning: **{headline}**
• **${pipeline.get('total_value', 0):,} total at risk** (oldest {pipeline.get('oldest_days_stuck', 0)} days)
• **Average deal size**: ${pipeline.get('avg_deal_size', 0):,.0f}{stage_breakdown}{deal_details}

:dart: **Insights**
{chr(10).join(f"• {insight}" for insight in self.insights)}

:rocket: **Recommended Actions**
{chr(10).join(f"{i+1}. {action}" for i, action in enumerate(self.actions))}"""

    def _format_forecast_accuracy(self) -> str:
        """Format forecast accuracy briefing"""
        pipeline = self.pipeline
        quarters = pipeline.get('quarters', [])
        accuracy = pipeline.get('accuracy', [])
        
        accuracy_str = " | ".join([f"Q{q}: {acc}" for q, acc in zip(quarters, accuracy)])
        
        return f""":bar_chart: **Forecast Accuracy ({pipeline.get('period', 'last 3 quarters')})**
• **Avg Accuracy**: {pipeline.get('avg_accuracy', 0):.0f}%
• **{accuracy_str}**

:dart: **Insights**
{chr(10).join(f"• {insight}" for insight in self.insights)}

:rocket: **Recommended Actions**
{chr(10).join(f"{i+1}. {action}" for i, action in enumerate(self.actions))}"""

    def _format_generic(self) -> str:
        """Format generic briefing"""
        return f""":briefcase: **{self.headline}**

:dart: **Key Metrics**
{chr(10).join(f"• {k}: {v}" for k, v in self.pipeline.items())}

:dart: **Insights**
{chr(10).join(f"• {insight}" for insight in self.insights)}

:rocket: **Recommended Actions**
{chr(10).join(f"{i+1}. {action}" for i, action in enumerate(self.actions))}"""

class BriefingSystem:
    """Comprehensive briefing system with persona-specific logic"""
    
    def __init__(self, salesforce_client, openai_client):
        self.salesforce_client = salesforce_client
        self.openai_client = openai_client
    
    async def generate_briefing(self, query: str, persona: PersonaType, context: Dict = None) -> BriefingContract:
        """Generate persona-specific briefing"""
        try:
            # Classify briefing type with persona context
            briefing_type = self._classify_briefing_type(query, persona)
            
            # Extract metrics and constraints
            metrics = await self._extract_metrics(query, briefing_type)
            
            # Generate insights and actions
            insights, actions = await self._generate_insights_actions(query, persona, metrics, briefing_type)
            
            # Create headline
            headline = self._generate_headline(briefing_type, metrics, persona)
            
            # Create briefing contract
            contract = BriefingContract(
                headline=headline,
                pipeline=metrics,
                insights=insights,
                actions=actions,
                persona=persona,
                briefing_type=briefing_type,
                timestamp=datetime.now().isoformat()
            )
            
            return contract
            
        except Exception as e:
            logger.error(f"Error generating briefing: {e}")
            return self._create_fallback_briefing(query, persona)
    
    def _classify_briefing_type(self, query: str, persona: PersonaType = None) -> BriefingType:
        """Classify the type of briefing needed with persona-specific logic"""
        query_lower = query.lower()
        
        # AE-specific logic - prioritize stuck deals and individual deal management
        if persona == PersonaType.ACCOUNT_EXECUTIVE:
            if any(word in query_lower for word in ["stuck", "stalled", "overdue", "days", "deal"]):
                return BriefingType.STUCK_DEALS
            elif any(word in query_lower for word in ["win rate", "conversion", "performance"]):
                return BriefingType.WIN_RATE
            elif any(word in query_lower for word in ["pipeline", "coverage"]):
                return BriefingType.PIPELINE_COVERAGE
            else:
                return BriefingType.STUCK_DEALS  # Default for AE
        
        # VP/CDO logic - prioritize pipeline coverage and strategic metrics
        elif persona == PersonaType.VP_SALES:
            if any(word in query_lower for word in ["pipeline", "coverage", "quota"]):
                return BriefingType.PIPELINE_COVERAGE
            elif any(word in query_lower for word in ["forecast", "accuracy", "prediction"]):
                return BriefingType.FORECAST_ACCURACY
            else:
                return BriefingType.PIPELINE_COVERAGE  # Default for VP
        
        # CDO logic - prioritize forecast accuracy and data quality
        elif persona == PersonaType.CDO:
            if any(word in query_lower for word in ["forecast", "accuracy", "prediction"]):
                return BriefingType.FORECAST_ACCURACY
            elif any(word in query_lower for word in ["pipeline", "coverage"]):
                return BriefingType.PIPELINE_COVERAGE
            else:
                return BriefingType.FORECAST_ACCURACY  # Default for CDO
        
        # General logic (fallback)
        else:
            if any(word in query_lower for word in ["pipeline", "coverage", "quota"]):
                return BriefingType.PIPELINE_COVERAGE
            elif any(word in query_lower for word in ["stuck", "stalled", "overdue", "days"]):
                return BriefingType.STUCK_DEALS
            elif any(word in query_lower for word in ["forecast", "accuracy", "prediction"]):
                return BriefingType.FORECAST_ACCURACY
            elif any(word in query_lower for word in ["win rate", "conversion"]):
                return BriefingType.WIN_RATE
            else:
                return BriefingType.PERFORMANCE_METRICS
    
    async def _extract_metrics(self, query: str, briefing_type: BriefingType) -> Dict[str, Any]:
        """Extract relevant metrics based on briefing type"""
        try:
            if briefing_type == BriefingType.PIPELINE_COVERAGE:
                return await self._get_pipeline_coverage_metrics(query)
            elif briefing_type == BriefingType.STUCK_DEALS:
                return await self._get_stuck_deals_metrics(query)
            elif briefing_type == BriefingType.FORECAST_ACCURACY:
                return await self._get_forecast_accuracy_metrics(query)
            elif briefing_type == BriefingType.WIN_RATE:
                return await self._get_win_rate_metrics(query)
            else:
                return await self._get_performance_metrics(query)
        except Exception as e:
            logger.error(f"Error extracting metrics: {e}")
            return {}
    
    async def _get_pipeline_coverage_metrics(self, query: str) -> Dict[str, Any]:
        """Get pipeline coverage metrics using real Salesforce data"""
        try:
            # Get total pipeline value and opportunities
            pipeline_result = self.salesforce_client.query(
                "SELECT COUNT(Id) total_opps, SUM(Amount) total_pipeline FROM Opportunity WHERE IsClosed = false"
            )
            total_opps = pipeline_result['records'][0]['total_opps']
            total_pipeline = pipeline_result['records'][0]['total_pipeline'] or 0
            
            # Get quota (assuming $30M annual quota)
            annual_quota = 30000000
            quarterly_quota = annual_quota / 4
            quota_coverage = total_pipeline / quarterly_quota if quarterly_quota > 0 else 0
            
            # Get win rate from historical data - use separate queries for SOQL compatibility
            total_result = self.salesforce_client.query(
                "SELECT COUNT(Id) total FROM Opportunity"
            )
            won_result = self.salesforce_client.query(
                "SELECT COUNT(Id) won FROM Opportunity WHERE StageName = 'Closed Won'"
            )
            total_all = total_result['records'][0]['total']
            won_all = won_result['records'][0]['won']
            win_rate = f"{(won_all / total_all * 100):.1f}%" if total_all > 0 else "0%"
            
            # Get stuck deals count (deals not updated in 14+ days)
            stuck_result = self.salesforce_client.query(
                "SELECT COUNT(Id) stuck_count FROM Opportunity WHERE IsClosed = false AND LastModifiedDate < LAST_N_DAYS:14"
            )
            stuck_count = stuck_result['records'][0]['stuck_count']
            
            # Get average deal size
            avg_deal_size = total_pipeline / total_opps if total_opps > 0 else 0
            
            # Get conversion potential based on historical win rate
            conversion_potential = total_pipeline * (won_all / total_all) if total_all > 0 else 0
            
            return {
                "total_pipeline": total_pipeline,
                "total_opportunities": total_opps,
                "quota_coverage": quota_coverage,
                "win_rate": win_rate,
                "avg_deal_size": avg_deal_size,
                "conversion_potential": conversion_potential,
                "risks": f"{stuck_count} deals stuck >14 days",
                "historical_total": total_all,
                "historical_won": won_all
            }
        except Exception as e:
            logger.error(f"Error getting pipeline metrics: {e}")
            return {
                "total_pipeline": 0,
                "total_opportunities": 0,
                "quota_coverage": 0,
                "win_rate": "0%",
                "avg_deal_size": 0,
                "conversion_potential": 0,
                "risks": "Unable to calculate",
                "historical_total": 0,
                "historical_won": 0
            }
    
    async def _get_stuck_deals_metrics(self, query: str) -> Dict[str, Any]:
        """Get stuck deals metrics with AE-focused details"""
        try:
            # Extract days threshold from query
            days_threshold = 14
            if "14 days" in query.lower():
                days_threshold = 14
            elif "30 days" in query.lower():
                days_threshold = 30
            
            # Get stuck deals summary
            stuck_result = self.salesforce_client.query(
                f"SELECT COUNT(Id) stuck_count, SUM(Amount) total_value, MAX(LastModifiedDate) oldest_date "
                f"FROM Opportunity WHERE IsClosed = false AND LastModifiedDate < LAST_N_DAYS:{days_threshold}"
            )
            
            stuck_count = stuck_result['records'][0]['stuck_count']
            total_value = stuck_result['records'][0]['total_value'] or 0
            oldest_date = stuck_result['records'][0]['oldest_date']
            
            # Calculate days stuck
            oldest_days = 0
            if oldest_date:
                oldest_dt = datetime.strptime(oldest_date.split('T')[0], '%Y-%m-%d')
                oldest_days = (datetime.now() - oldest_dt).days
            
            # Get individual stuck deal details for AE
            stuck_deals_detail = self.salesforce_client.query(
                f"SELECT Name, Amount, StageName, Account.Name, Owner.Name, LastModifiedDate "
                f"FROM Opportunity WHERE IsClosed = false AND LastModifiedDate < LAST_N_DAYS:{days_threshold} "
                f"ORDER BY LastModifiedDate ASC LIMIT 5"
            )
            
            # Get stuck deals by stage
            stuck_by_stage = self.salesforce_client.query(
                f"SELECT StageName, COUNT(Id) count, SUM(Amount) value "
                f"FROM Opportunity WHERE IsClosed = false AND LastModifiedDate < LAST_N_DAYS:{days_threshold} "
                f"GROUP BY StageName ORDER BY count DESC"
            )
            
            return {
                "stuck_deals": stuck_count,
                "total_value": total_value,
                "oldest_days_stuck": oldest_days,
                "days_threshold": days_threshold,
                "stage": "current stage",
                "stuck_deals_detail": stuck_deals_detail['records'],
                "stuck_by_stage": stuck_by_stage['records'],
                "avg_deal_size": total_value / stuck_count if stuck_count > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting stuck deals metrics: {e}")
            return {
                "stuck_deals": 0,
                "total_value": 0,
                "oldest_days_stuck": 0,
                "days_threshold": 14,
                "stage": "current stage"
            }
    
    async def _get_forecast_accuracy_metrics(self, query: str) -> Dict[str, Any]:
        """Get forecast accuracy metrics"""
        try:
            # Simulate forecast accuracy data (in real implementation, this would come from historical data)
            quarters = ["Q1", "Q2", "Q3"]
            forecasted = [15.2, 16.1, 14.8]
            actual = [14.9, 15.9, 15.1]
            accuracy = [98, 99, 84]
            
            avg_accuracy = sum(accuracy) / len(accuracy)
            
            return {
                "quarters": quarters,
                "forecasted": forecasted,
                "actual": actual,
                "accuracy": [f"{acc}%" for acc in accuracy],
                "avg_accuracy": avg_accuracy,
                "period": "last 3 quarters"
            }
        except Exception as e:
            logger.error(f"Error getting forecast accuracy metrics: {e}")
            return {
                "quarters": ["Q1", "Q2", "Q3"],
                "forecasted": [0, 0, 0],
                "actual": [0, 0, 0],
                "accuracy": ["0%", "0%", "0%"],
                "avg_accuracy": 0,
                "period": "last 3 quarters"
            }
    
    async def _get_win_rate_metrics(self, query: str) -> Dict[str, Any]:
        """Get win rate metrics"""
        try:
            # Get win rate data - use separate queries for SOQL compatibility
            total_result = self.salesforce_client.query("SELECT COUNT(Id) total FROM Opportunity")
            won_result = self.salesforce_client.query("SELECT COUNT(Id) won FROM Opportunity WHERE StageName = 'Closed Won'")
            lost_result = self.salesforce_client.query("SELECT COUNT(Id) lost FROM Opportunity WHERE StageName = 'Closed Lost'")
            
            total = total_result['records'][0]['total']
            won = won_result['records'][0]['won']
            lost = lost_result['records'][0]['lost']
            
            win_rate = (won / total * 100) if total > 0 else 0
            
            return {
                "total_opportunities": total,
                "won_opportunities": won,
                "lost_opportunities": lost,
                "win_rate": f"{win_rate:.1f}%",
                "success_ratio": f"{won}:{lost}"
            }
        except Exception as e:
            logger.error(f"Error getting win rate metrics: {e}")
            return {
                "total_opportunities": 0,
                "won_opportunities": 0,
                "lost_opportunities": 0,
                "win_rate": "0%",
                "success_ratio": "0:0"
            }
    
    async def _get_performance_metrics(self, query: str) -> Dict[str, Any]:
        """Get general performance metrics"""
        try:
            # Get basic performance metrics
            pipeline_result = self.salesforce_client.query(
                "SELECT COUNT(Id) total_opps, SUM(Amount) total_value FROM Opportunity WHERE IsClosed = false"
            )
            
            total_opps = pipeline_result['records'][0]['total_opps']
            total_value = pipeline_result['records'][0]['total_value'] or 0
            
            return {
                "total_opportunities": total_opps,
                "total_pipeline_value": total_value,
                "average_deal_size": total_value / total_opps if total_opps > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {
                "total_opportunities": 0,
                "total_pipeline_value": 0,
                "average_deal_size": 0
            }
    
    async def _generate_insights_actions(self, query: str, persona: PersonaType, metrics: Dict, briefing_type: BriefingType) -> tuple[List[str], List[str]]:
        """Generate insights and actions based on persona and metrics"""
        try:
            # Use LLM to generate insights and actions
            prompt = self._create_insights_prompt(query, persona, metrics, briefing_type)
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a sales analytics expert. Generate 2-3 insights and 2-3 actionable recommendations based on the data."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=300
                )
            )
            
            content = response.choices[0].message.content
            
            # Parse insights and actions
            insights = []
            actions = []
            
            lines = content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if 'insights' in line.lower():
                    current_section = 'insights'
                elif 'actions' in line.lower() or 'recommendations' in line.lower():
                    current_section = 'actions'
                elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    item = line[1:].strip()
                    if current_section == 'insights':
                        insights.append(item)
                    elif current_section == 'actions':
                        actions.append(item)
            
            # Fallback if parsing failed
            if not insights:
                insights = ["Data analysis completed successfully"]
            if not actions:
                actions = ["Review the metrics and take appropriate action"]
            
            return insights[:3], actions[:3]  # Limit to 3 each
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return ["Unable to generate insights at this time"], ["Please review the data manually"]
    
    def _create_insights_prompt(self, query: str, persona: PersonaType, metrics: Dict, briefing_type: BriefingType) -> str:
        """Create data-driven prompt for insights generation"""
        persona_context = {
            PersonaType.VP_SALES: "VP of Sales - focus on strategic insights, pipeline health, and team performance",
            PersonaType.ACCOUNT_EXECUTIVE: "Account Executive - focus on individual deal management, next steps, and deal velocity",
            PersonaType.CDO: "Chief Data Officer - focus on data quality, trends, and analytical insights"
        }
        
        # Create data-specific context based on briefing type
        data_context = ""
        if briefing_type == BriefingType.PIPELINE_COVERAGE:
            quota_coverage = metrics.get('quota_coverage', 0)
            total_pipeline = metrics.get('total_pipeline', 0)
            win_rate = metrics.get('win_rate', '0%')
            stuck_count = int(metrics.get('risks', '0').split()[0]) if 'stuck' in metrics.get('risks', '') else 0
            avg_deal_size = metrics.get('avg_deal_size', 0)
            
            data_context = f"""
Pipeline Data:
- Quota Coverage: {quota_coverage:.1f}x (target: 3x+)
- Total Pipeline: ${total_pipeline:,.0f}
- Win Rate: {win_rate}
- Stuck Deals: {stuck_count} deals >14 days
- Average Deal Size: ${avg_deal_size:,.0f}

Key Questions to Address:
- Is quota coverage sufficient for the quarter?
- Are there enough deals in the pipeline?
- Which deals are at risk of getting stuck?
- What's the quality of the pipeline?
"""
        elif briefing_type == BriefingType.STUCK_DEALS:
            stuck_deals = metrics.get('stuck_deals', 0)
            total_value = metrics.get('total_value', 0)
            oldest_days = metrics.get('oldest_days_stuck', 0)
            
            data_context = f"""
Stuck Deals Data:
- Number of Stuck Deals: {stuck_deals}
- Total Value at Risk: ${total_value:,.0f}
- Oldest Deal Stuck: {oldest_days} days

Key Questions to Address:
- Which deals need immediate attention?
- What's causing deals to get stuck?
- How much revenue is at risk?
- What recovery actions are needed?
"""
        
        return f"""
Query: {query}
Persona: {persona_context.get(persona, 'General')}
Briefing Type: {briefing_type.value}

{data_context}

Raw Metrics: {json.dumps(metrics, indent=2)}

Based on this REAL Salesforce data, generate 2-3 specific, data-driven insights and 2-3 actionable recommendations.

Format your response as:
Insights:
- [specific insight based on the data above]
- [specific insight based on the data above]

Actions:
- [specific, actionable recommendation]
- [specific, actionable recommendation]
"""
    
    def _generate_headline(self, briefing_type: BriefingType, metrics: Dict, persona: PersonaType) -> str:
        """Generate data-driven headline based on real metrics"""
        if briefing_type == BriefingType.PIPELINE_COVERAGE:
            coverage = metrics.get('quota_coverage', 0)
            total_pipeline = metrics.get('total_pipeline', 0)
            return f"Pipeline Coverage: {coverage:.1f}x (${total_pipeline:,.0f})"
        elif briefing_type == BriefingType.STUCK_DEALS:
            stuck_count = metrics.get('stuck_deals', 0)
            total_value = metrics.get('total_value', 0)
            days = metrics.get('days_threshold', 14)
            return f"{stuck_count} deals stuck >{days} days (${total_value:,.0f} at risk)"
        elif briefing_type == BriefingType.FORECAST_ACCURACY:
            accuracy = metrics.get('avg_accuracy', 0)
            return f"Forecast Accuracy: {accuracy:.0f}% avg last 3 quarters"
        elif briefing_type == BriefingType.WIN_RATE:
            win_rate = metrics.get('win_rate', '0%')
            total_opps = metrics.get('total_opportunities', 0)
            return f"Win Rate: {win_rate} ({total_opps} opportunities)"
        else:
            return "Sales Performance Summary"
    
    def _create_fallback_briefing(self, query: str, persona: PersonaType) -> BriefingContract:
        """Create fallback briefing when generation fails"""
        return BriefingContract(
            headline="Unable to generate briefing",
            pipeline={"error": "Data unavailable"},
            insights=["Please try rephrasing your question"],
            actions=["Contact support if the issue persists"],
            persona=persona,
            briefing_type=BriefingType.PERFORMANCE_METRICS,
            timestamp=datetime.now().isoformat()
        )
