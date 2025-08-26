#!/usr/bin/env python3
"""
Spectrum-Aware Smart Router
Three-layer approach: Fast Path → Smart Data Path → Deep Thinking Path
"""

import re
import time
from typing import Dict, Any, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass

class LayerType(Enum):
    """Three-layer spectrum for query processing"""
    FAST_PATH = "fast_path"                    # Instant responses, no AI
    SMART_DATA_PATH = "smart_data_path"        # Intent classification + direct queries
    DEEP_THINKING_PATH = "deep_thinking_path"  # Full DAG reasoning engine

class IntentType(Enum):
    """Intent types for smart data path"""
    SALESFORCE_QUERY = "salesforce_query"      # Simple data lookup
    BUSINESS_INTELLIGENCE = "business_intelligence"  # Analytical queries
    EXECUTIVE_BRIEFING = "executive_briefing"  # Strategic insights

@dataclass
class RoutingDecision:
    """Complete routing decision with metadata"""
    layer: LayerType
    intent_type: Optional[IntentType]
    specific_intent: str
    requires_llm: bool
    timeout_seconds: int
    cache_strategy: str
    fallback_strategy: str
    complexity_score: float  # 0.0 to 1.0
    reasoning: str

class SpectrumAwareRouter:
    """Spectrum-aware router with intelligent layer selection"""
    
    def __init__(self):
        # Layer 1: Fast Path Patterns (instant responses)
        self.fast_path_patterns = {
            "help": [
                r"what\s+can\s+you\s+do",
                r"help",
                r"capabilities",
                r"commands"
            ],
            "greeting": [
                r"hello",
                r"hi",
                r"hey",
                r"good\s+(morning|afternoon|evening)"
            ],
            "status": [
                r"status",
                r"are\s+you\s+working",
                r"bot\s+status"
            ]
        }
        
        # Layer 2: Smart Data Path Patterns
        self.smart_data_patterns = {
            # Simple Salesforce Queries
            "pipeline_status": [
                r"pipeline\s+status",
                r"pipeline\s+overview",
                r"how\s+many\s+opportunities",
                r"total\s+opportunities"
            ],
            "top_opportunities": [
                r"top\s+\d+\s+opportunities",
                r"top\s+opportunities",
                r"largest\s+deals",
                r"biggest\s+opportunities"
            ],
            "win_rate": [
                r"win\s+rate",
                r"win\s+percentage",
                r"close\s+rate"
            ],
            "stage_breakdown": [
                r"stage\s+breakdown",
                r"pipeline\s+by\s+stage",
                r"opportunities\s+by\s+stage"
            ],
            "account_lookup": [
                r"find\s+account",
                r"account\s+details",
                r"contact\s+info"
            ],
            
            # Business Intelligence Queries
            "win_rate_analysis": [
                r"win\s+rate\s+by\s+\w+",
                r"win\s+rate\s+trend",
                r"win\s+rate\s+analysis"
            ],
            "deal_velocity": [
                r"deal\s+velocity",
                r"sales\s+velocity",
                r"velocity\s+analysis"
            ],
            "quarterly_performance": [
                r"quarterly\s+performance",
                r"q\d+\s+performance",
                r"quarter\s+results"
            ],
            "industry_analysis": [
                r"by\s+industry",
                r"industry\s+performance",
                r"industry\s+analysis"
            ]
        }
        
        # Layer 3: Deep Thinking Path Patterns
        self.deep_thinking_patterns = {
            "multi_account_analysis": [
                r"compare\s+accounts",
                r"account\s+comparison",
                r"multiple\s+accounts"
            ],
            "risk_assessment": [
                r"accounts?\s+at\s+risk",
                r"risk\s+analysis",
                r"at\s+risk\s+customers"
            ],
            "strategic_insights": [
                r"strategic\s+insights",
                r"business\s+impact",
                r"strategic\s+recommendations"
            ],
            "complex_correlation": [
                r"correlation",
                r"relationship\s+between",
                r"impact\s+of.*on"
            ],
            "predictive_analysis": [
                r"predict",
                r"forecast",
                r"trend\s+prediction"
            ]
        }
        
        # Complexity indicators
        self.complexity_keywords = [
            "why", "how", "what should", "recommend", "analyze", "insights",
            "patterns", "trends", "strategy", "optimize", "improve", "compare",
            "correlation", "impact", "relationship", "predict", "forecast"
        ]
    
    def route_query(self, query: str) -> RoutingDecision:
        """
        Route query through the three-layer spectrum
        """
        query_lower = query.lower().strip()
        
        # Layer 1: Fast Path Check
        fast_path_result = self._check_fast_path(query_lower)
        if fast_path_result:
            return fast_path_result
        
        # Layer 2: Smart Data Path Check
        smart_data_result = self._check_smart_data_path(query_lower)
        if smart_data_result:
            return smart_data_result
        
        # Layer 3: Deep Thinking Path (default for complex queries)
        return self._check_deep_thinking_path(query_lower)
    
    def _check_fast_path(self, query: str) -> Optional[RoutingDecision]:
        """Check if query qualifies for fast path (Layer 1)"""
        for intent, patterns in self.fast_path_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    return RoutingDecision(
                        layer=LayerType.FAST_PATH,
                        intent_type=None,
                        specific_intent=intent,
                        requires_llm=False,
                        timeout_seconds=1,
                        cache_strategy="static_response",
                        fallback_strategy="help_response",
                        complexity_score=0.0,
                        reasoning=f"Fast path match: {pattern}"
                    )
        return None
    
    def _check_smart_data_path(self, query: str) -> Optional[RoutingDecision]:
        """Check if query qualifies for smart data path (Layer 2)"""
        for intent, patterns in self.smart_data_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    # Determine if it's simple query or business intelligence
                    if any(keyword in query for keyword in ["by", "trend", "analysis", "performance"]):
                        intent_type = IntentType.BUSINESS_INTELLIGENCE
                        complexity_score = 0.6
                        timeout = 8
                        cache_strategy = "query_cache"
                    else:
                        intent_type = IntentType.SALESFORCE_QUERY
                        complexity_score = 0.3
                        timeout = 5
                        cache_strategy = "query_cache"
                    
                    return RoutingDecision(
                        layer=LayerType.SMART_DATA_PATH,
                        intent_type=intent_type,
                        specific_intent=intent,
                        requires_llm=False,  # Direct Salesforce queries
                        timeout_seconds=timeout,
                        cache_strategy=cache_strategy,
                        fallback_strategy="basic_query",
                        complexity_score=complexity_score,
                        reasoning=f"Smart data path match: {pattern}"
                    )
        return None
    
    def _check_deep_thinking_path(self, query: str) -> RoutingDecision:
        """Check if query requires deep thinking path (Layer 3)"""
        # Check for deep thinking patterns
        for intent, patterns in self.deep_thinking_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    return RoutingDecision(
                        layer=LayerType.DEEP_THINKING_PATH,
                        intent_type=IntentType.BUSINESS_INTELLIGENCE,
                        specific_intent=intent,
                        requires_llm=True,
                        timeout_seconds=20,
                        cache_strategy="reasoning_cache",
                        fallback_strategy="enhanced_analysis",
                        complexity_score=0.9,
                        reasoning=f"Deep thinking pattern match: {pattern}"
                    )
        
        # Check for complexity keywords
        complexity_keywords_found = [k for k in self.complexity_keywords if k in query]
        if complexity_keywords_found:
            complexity_score = min(0.8, 0.4 + len(complexity_keywords_found) * 0.1)
            return RoutingDecision(
                layer=LayerType.DEEP_THINKING_PATH,
                intent_type=IntentType.BUSINESS_INTELLIGENCE,
                specific_intent="general_analysis",
                requires_llm=True,
                timeout_seconds=15,
                cache_strategy="reasoning_cache",
                fallback_strategy="enhanced_analysis",
                complexity_score=complexity_score,
                reasoning=f"Complexity keywords: {complexity_keywords_found}"
            )
        
        # Default to smart data path for unknown queries
        return RoutingDecision(
            layer=LayerType.SMART_DATA_PATH,
            intent_type=IntentType.SALESFORCE_QUERY,
            specific_intent="general_query",
            requires_llm=False,
            timeout_seconds=5,
            cache_strategy="query_cache",
            fallback_strategy="help_response",
            complexity_score=0.5,
            reasoning="Default routing for unknown query"
        )
    
    def get_execution_strategy(self, decision: RoutingDecision) -> Dict[str, Any]:
        """Get execution strategy based on routing decision"""
        if decision.layer == LayerType.FAST_PATH:
            return {
                "execution_type": "instant_response",
                "response_template": self._get_fast_path_response(decision.specific_intent),
                "processing_time": "< 1s",
                "cost": "free"
            }
        
        elif decision.layer == LayerType.SMART_DATA_PATH:
            return {
                "execution_type": "direct_query",
                "query_builder": self._get_query_builder(decision.specific_intent),
                "processing_time": "2-8s",
                "cost": "low"
            }
        
        elif decision.layer == LayerType.DEEP_THINKING_PATH:
            return {
                "execution_type": "enhanced_reasoning",
                "reasoning_engine": "dag_generation",
                "processing_time": "10-20s",
                "cost": "high"
            }
        
        return {
            "execution_type": "fallback",
            "processing_time": "5s",
            "cost": "low"
        }
    
    def _get_fast_path_response(self, intent: str) -> str:
        """Get instant response for fast path"""
        responses = {
            "help": """🤖 **Whizzy**: I'm your Salesforce Analytics Assistant! Here's what I can do:

📊 **Data Queries**
• Pipeline status and coverage
• Top opportunities and deals
• Win rate analysis
• Stage breakdown

🎯 **Quick Queries**
• "What's our pipeline status?"
• "Show me top 10 opportunities"
• "What's our win rate?"
• "Show pipeline breakdown by stage"

💡 **Pro Tips**
• Ask specific questions for better insights
• I'll provide actionable recommendations

Try asking me anything about your Salesforce data! 🚀""",
            
            "greeting": "🤖 **Whizzy**: Hello! I'm your Salesforce Analytics Assistant. How can I help you today?",
            
            "status": "🤖 **Whizzy**: I'm online and ready to help with your Salesforce analytics! 🚀"
        }
        return responses.get(intent, responses["help"])
    
    def _get_query_builder(self, intent: str) -> str:
        """Get query builder for smart data path"""
        query_builders = {
            "pipeline_status": "SELECT COUNT(Id) total, SUM(Amount) total_amount FROM Opportunity",
            "top_opportunities": "SELECT Name, Amount, StageName FROM Opportunity ORDER BY Amount DESC LIMIT 10",
            "win_rate": "SELECT StageName, COUNT(Id) count FROM Opportunity GROUP BY StageName",
            "stage_breakdown": "SELECT StageName, COUNT(Id) count, SUM(Amount) total_amount FROM Opportunity GROUP BY StageName"
        }
        return query_builders.get(intent, "SELECT COUNT(Id) FROM Opportunity")

# Example usage and testing
if __name__ == "__main__":
    router = SpectrumAwareRouter()
    
    test_queries = [
        "What can you do?",
        "Hello there!",
        "What's our pipeline status?",
        "Show me top 10 opportunities",
        "What's our win rate by industry?",
        "Why are deals slipping?",
        "Compare our top accounts' revenue with their engagement scores",
        "How can we improve sales velocity?",
        "Give me a VP briefing"
    ]
    
    print("🧠 Spectrum-Aware Smart Router Test Results\n")
    print("=" * 80)
    
    for query in test_queries:
        decision = router.route_query(query)
        strategy = router.get_execution_strategy(decision)
        
        print(f"\n📝 Query: {query}")
        print(f"🎯 Layer: {decision.layer.value}")
        print(f"🧠 Intent: {decision.intent_type.value if decision.intent_type else 'N/A'}")
        print(f"📊 Specific: {decision.specific_intent}")
        print(f"⚡ Complexity: {decision.complexity_score:.1f}")
        print(f"⏱️  Timeout: {decision.timeout_seconds}s")
        print(f"💰 Cost: {strategy['cost']}")
        print(f"🔍 Reasoning: {decision.reasoning}")
        print("-" * 40)

