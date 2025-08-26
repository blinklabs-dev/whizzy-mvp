#!/usr/bin/env python3
"""
Smart Intent Router
Simple solutions for simple problems, sophisticated solutions only when needed
"""

import re
from typing import Dict, Any, List, Tuple
from enum import Enum

class IntentType(Enum):
    """Intent types with complexity levels"""
    SIMPLE_QUERY = "simple_query"           # Direct data lookup
    COMPLEX_ANALYSIS = "complex_analysis"   # Multi-step reasoning
    EXECUTIVE_BRIEFING = "executive_briefing"  # Strategic insights
    ADVANCED_REASONING = "advanced_reasoning"  # Chain of thought

class SmartIntentRouter:
    """Smart intent router with intelligent complexity detection"""
    
    def __init__(self):
        # Simple patterns for direct queries
        self.simple_patterns = {
            "pipeline_status": [
                r"pipeline\s+status",
                r"pipeline\s+overview", 
                r"pipeline\s+summary",
                r"how\s+many\s+opportunities"
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
            "help": [
                r"what\s+can\s+you\s+do",
                r"help",
                r"capabilities"
            ]
        }
        
        # Complex patterns requiring advanced reasoning
        self.complex_patterns = {
            "deal_slippage_analysis": [
                r"why\s+are\s+deals\s+slipping",
                r"deal\s+slippage",
                r"why\s+deals\s+are\s+delayed"
            ],
            "risk_assessment": [
                r"accounts?\s+at\s+risk",
                r"risk\s+analysis",
                r"which\s+accounts?\s+are\s+risky"
            ],
            "velocity_optimization": [
                r"sales\s+velocity",
                r"deal\s+velocity",
                r"how\s+to\s+improve\s+velocity",
                r"velocity\s+optimization"
            ],
            "strategic_insights": [
                r"strategic\s+insights",
                r"business\s+impact",
                r"strategic\s+recommendations"
            ]
        }
        
        # Executive patterns
        self.executive_patterns = {
            "vp_briefing": [
                r"vp\s+briefing",
                r"executive\s+briefing",
                r"leadership\s+update"
            ],
            "quarterly_review": [
                r"quarterly\s+review",
                r"q\d+\s+review",
                r"quarter\s+performance"
            ]
        }
    
    def analyze_intent(self, query: str) -> Tuple[IntentType, str, Dict[str, Any]]:
        """
        Analyze query intent and determine complexity level
        Returns: (IntentType, specific_intent, metadata)
        """
        query_lower = query.lower().strip()
        
        # Check for simple patterns first
        for intent, patterns in self.simple_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return IntentType.SIMPLE_QUERY, intent, {
                        "complexity": "low",
                        "requires_llm": False,
                        "direct_query": True,
                        "pattern_matched": pattern
                    }
        
        # Check for complex patterns
        for intent, patterns in self.complex_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return IntentType.COMPLEX_ANALYSIS, intent, {
                        "complexity": "high",
                        "requires_llm": True,
                        "requires_reasoning": True,
                        "pattern_matched": pattern
                    }
        
        # Check for executive patterns
        for intent, patterns in self.executive_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return IntentType.EXECUTIVE_BRIEFING, intent, {
                        "complexity": "medium",
                        "requires_llm": True,
                        "requires_insights": True,
                        "pattern_matched": pattern
                    }
        
        # Check for advanced reasoning keywords
        reasoning_keywords = [
            "why", "how", "what should", "recommend", "analyze", "insights",
            "patterns", "trends", "strategy", "optimize", "improve"
        ]
        
        if any(keyword in query_lower for keyword in reasoning_keywords):
            return IntentType.ADVANCED_REASONING, "general_analysis", {
                "complexity": "high",
                "requires_llm": True,
                "requires_reasoning": True,
                "keywords_found": [k for k in reasoning_keywords if k in query_lower]
            }
        
        # Default to simple query
        return IntentType.SIMPLE_QUERY, "general_query", {
            "complexity": "low",
            "requires_llm": False,
            "direct_query": True,
            "fallback": True
        }
    
    def get_solution_strategy(self, intent_type: IntentType, specific_intent: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get solution strategy based on intent analysis
        """
        if intent_type == IntentType.SIMPLE_QUERY:
            return {
                "approach": "direct_query",
                "llm_required": False,
                "cache_strategy": "query_cache",
                "timeout": 5,
                "fallback": "help_response"
            }
        
        elif intent_type == IntentType.COMPLEX_ANALYSIS:
            return {
                "approach": "enhanced_reasoning",
                "llm_required": True,
                "cache_strategy": "prompt_cache",
                "timeout": 15,
                "fallback": "basic_analysis"
            }
        
        elif intent_type == IntentType.EXECUTIVE_BRIEFING:
            return {
                "approach": "executive_insights",
                "llm_required": True,
                "cache_strategy": "insight_cache",
                "timeout": 10,
                "fallback": "data_summary"
            }
        
        elif intent_type == IntentType.ADVANCED_REASONING:
            return {
                "approach": "chain_of_thought",
                "llm_required": True,
                "cache_strategy": "reasoning_cache",
                "timeout": 20,
                "fallback": "enhanced_analysis"
            }
        
        return {
            "approach": "direct_query",
            "llm_required": False,
            "cache_strategy": "query_cache",
            "timeout": 5,
            "fallback": "help_response"
        }
    
    def route_query(self, query: str) -> Dict[str, Any]:
        """
        Complete query routing with intent analysis and solution strategy
        """
        intent_type, specific_intent, metadata = self.analyze_intent(query)
        strategy = self.get_solution_strategy(intent_type, specific_intent, metadata)
        
        return {
            "query": query,
            "intent_type": intent_type.value,
            "specific_intent": specific_intent,
            "metadata": metadata,
            "strategy": strategy,
            "recommended_approach": strategy["approach"]
        }

# Example usage and testing
if __name__ == "__main__":
    router = SmartIntentRouter()
    
    test_queries = [
        "What's our pipeline status?",
        "Show me top 10 opportunities",
        "What's our win rate?",
        "Why are deals slipping?",
        "Give me a VP briefing",
        "How can we improve sales velocity?",
        "What can you do?"
    ]
    
    for query in test_queries:
        result = router.route_query(query)
        print(f"\nQuery: {query}")
        print(f"Intent: {result['intent_type']}")
        print(f"Specific: {result['specific_intent']}")
        print(f"Approach: {result['recommended_approach']}")
        print(f"LLM Required: {result['strategy']['llm_required']}")

