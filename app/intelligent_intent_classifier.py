#!/usr/bin/env python3
"""
Intelligent Intent Classifier - Uses semantic analysis instead of hardcoded keywords
"""

import re
import json
import asyncio
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import openai
from app.intelligent_agentic_system import IntentType, PersonaType, DataSourceType

@dataclass
class IntentPattern:
    """Pattern for intent classification"""
    intent: IntentType
    confidence: float
    reasoning: str
    complexity_score: float
    data_sources: List[DataSourceType]
    persona: PersonaType

class IntelligentIntentClassifier:
    """Intelligent intent classifier using semantic analysis"""
    
    def __init__(self, openai_client):
        self.openai_client = openai_client
        self.executor = None
        
        # Semantic patterns for intent classification
        self.semantic_patterns = {
            "data_query": [
                "what", "show", "get", "find", "list", "count", "how many",
                "total", "number", "amount", "value", "sum", "average"
            ],
            "analysis": [
                "analyze", "analysis", "insights", "trends", "patterns", "correlation",
                "factors", "reasons", "why", "how", "investigate", "examine"
            ],
            "forecasting": [
                "forecast", "predict", "projection", "outlook", "future", "trend",
                "prediction", "estimate", "anticipate", "expect"
            ],
            "risk": [
                "risk", "at risk", "danger", "threat", "vulnerable", "exposed",
                "slippage", "delay", "miss", "lose", "fail"
            ],
            "performance": [
                "performance", "metrics", "kpi", "productivity", "efficiency",
                "effectiveness", "success", "achievement", "results"
            ],
            "executive": [
                "executive", "briefing", "board", "leadership", "strategic",
                "overview", "summary", "high-level", "management"
            ],
            "complex": [
                "complex", "deep", "thorough", "comprehensive", "detailed",
                "investigation", "study", "research", "analysis"
            ]
        }
        
        # Intent classification prompt
        self.intent_classification_prompt = """
You are an intelligent intent classifier for a Salesforce analytics bot. Analyze the user's query and classify their intent.

Available intents:
- SALESFORCE_QUERY: Simple data retrieval (win rate, pipeline, accounts)
- BUSINESS_INTELLIGENCE: Analysis and insights (performance, trends, patterns)
- COMPLEX_ANALYTICS: Advanced analysis (correlations, forecasting, deep insights)
- COFFEE_BRIEFING: Executive summaries and strategic overviews
- DBT_MODEL: Data model requests
- DIRECT_ANSWER: Simple questions not requiring data

Available personas:
- VP_SALES: Sales leadership focus
- ACCOUNT_EXECUTIVE: Individual rep focus
- SALES_MANAGER: Team management focus
- CDO: Data strategy focus
- DATA_ENGINEER: Technical focus
- SALES_OPERATIONS: Process focus
- CUSTOMER_SUCCESS: Customer focus

Analyze the query and return a JSON response with:
{
    "primary_intent": "intent_name",
    "confidence": 0.95,
    "persona": "persona_name",
    "data_sources": ["salesforce"],
    "complexity_level": "low|medium|high",
    "reasoning_required": true|false,
    "coffee_briefing": true|false,
    "dbt_model_required": false,
    "thinking_required": false,
    "explanation": "Brief explanation of classification"
}

Focus on semantic meaning, not just keywords. Consider context and user intent.
"""

    async def classify_intent_intelligently(self, query: str, user_context: Dict = None) -> IntentPattern:
        """Classify intent using intelligent semantic analysis"""
        try:
            # Step 1: Semantic pattern analysis
            semantic_score = self._analyze_semantic_patterns(query)
            
            # Step 2: LLM-based classification
            llm_classification = await self._get_llm_classification(query, user_context)
            
            # Step 3: Combine and validate
            final_intent = self._combine_classifications(semantic_score, llm_classification, query)
            
            return final_intent
            
        except Exception as e:
            # Fallback to pattern-based classification
            return self._fallback_classification(query)
    
    def _analyze_semantic_patterns(self, query: str) -> Dict[str, float]:
        """Analyze semantic patterns in the query"""
        query_lower = query.lower()
        scores = {}
        
        for pattern_type, patterns in self.semantic_patterns.items():
            score = 0.0
            for pattern in patterns:
                if pattern in query_lower:
                    score += 0.3
                # Check for word boundaries
                if re.search(r'\b' + re.escape(pattern) + r'\b', query_lower):
                    score += 0.5
            
            scores[pattern_type] = min(score, 1.0)
        
        return scores
    
    async def _get_llm_classification(self, query: str, user_context: Dict = None) -> Dict:
        """Get LLM-based intent classification"""
        try:
            contextualized_query = f"{query}\nUser Context: {user_context or {}}"
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,  # Use default executor
                lambda: self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Use cheaper model for classification
                    messages=[
                        {"role": "system", "content": self.intent_classification_prompt},
                        {"role": "user", "content": contextualized_query}
                    ],
                    temperature=0.1,
                    max_tokens=300
                )
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            # Return fallback classification
            return {
                "primary_intent": "SALESFORCE_QUERY",
                "confidence": 0.5,
                "persona": "VP_SALES",
                "data_sources": ["salesforce"],
                "complexity_level": "medium",
                "reasoning_required": False,
                "coffee_briefing": False,
                "dbt_model_required": False,
                "thinking_required": False,
                "explanation": f"Fallback classification due to error: {e}"
            }
    
    def _combine_classifications(self, semantic_score: Dict, llm_classification: Dict, query: str) -> IntentPattern:
        """Combine semantic and LLM classifications"""
        
        # Map LLM intent to enum
        intent_mapping = {
            "SALESFORCE_QUERY": IntentType.SALESFORCE_QUERY,
            "BUSINESS_INTELLIGENCE": IntentType.BUSINESS_INTELLIGENCE,
            "COMPLEX_ANALYTICS": IntentType.COMPLEX_ANALYTICS,
            "COFFEE_BRIEFING": IntentType.COFFEE_BRIEFING,
            "DBT_MODEL": IntentType.DBT_MODEL,
            "DIRECT_ANSWER": IntentType.DIRECT_ANSWER
        }
        
        persona_mapping = {
            "VP_SALES": PersonaType.VP_SALES,
            "ACCOUNT_EXECUTIVE": PersonaType.ACCOUNT_EXECUTIVE,
            "SALES_MANAGER": PersonaType.SALES_MANAGER,
            "CDO": PersonaType.CDO,
            "DATA_ENGINEER": PersonaType.DATA_ENGINEER,
            "SALES_OPERATIONS": PersonaType.SALES_OPERATIONS,
            "CUSTOMER_SUCCESS": PersonaType.CUSTOMER_SUCCESS
        }
        
        # Get primary intent
        primary_intent = intent_mapping.get(llm_classification.get("primary_intent", "SALESFORCE_QUERY"), IntentType.SALESFORCE_QUERY)
        
        # Calculate confidence based on semantic patterns
        semantic_confidence = self._calculate_semantic_confidence(semantic_score, primary_intent)
        llm_confidence = llm_classification.get("confidence", 0.5)
        
        # Combine confidences
        final_confidence = (semantic_confidence * 0.3) + (llm_confidence * 0.7)
        
        # Determine complexity
        complexity_score = self._calculate_complexity_score(semantic_score, llm_classification)
        
        # Get persona
        persona = persona_mapping.get(llm_classification.get("persona", "VP_SALES"), PersonaType.VP_SALES)
        
        # Determine data sources
        data_sources = [DataSourceType.SALESFORCE]  # Default to Salesforce
        
        return IntentPattern(
            intent=primary_intent,
            confidence=final_confidence,
            reasoning=llm_classification.get("explanation", "Intelligent classification"),
            complexity_score=complexity_score,
            data_sources=data_sources,
            persona=persona
        )
    
    def _calculate_semantic_confidence(self, semantic_score: Dict, intent: IntentType) -> float:
        """Calculate confidence based on semantic patterns"""
        if intent == IntentType.SALESFORCE_QUERY:
            return semantic_score.get("data_query", 0.0)
        elif intent == IntentType.BUSINESS_INTELLIGENCE:
            return max(semantic_score.get("analysis", 0.0), semantic_score.get("performance", 0.0))
        elif intent == IntentType.COMPLEX_ANALYTICS:
            return max(semantic_score.get("complex", 0.0), semantic_score.get("forecasting", 0.0))
        elif intent == IntentType.COFFEE_BRIEFING:
            return semantic_score.get("executive", 0.0)
        else:
            return 0.5
    
    def _calculate_complexity_score(self, semantic_score: Dict, llm_classification: Dict) -> float:
        """Calculate complexity score"""
        complexity_level = llm_classification.get("complexity_level", "medium")
        
        if complexity_level == "high":
            base_score = 0.8
        elif complexity_level == "medium":
            base_score = 0.5
        else:
            base_score = 0.2
        
        # Adjust based on semantic patterns
        if semantic_score.get("complex", 0.0) > 0.5:
            base_score += 0.2
        if semantic_score.get("forecasting", 0.0) > 0.5:
            base_score += 0.1
        if semantic_score.get("analysis", 0.0) > 0.5:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _fallback_classification(self, query: str) -> IntentPattern:
        """Fallback classification when intelligent classification fails"""
        query_lower = query.lower()
        
        # Intelligent semantic fallback
        if any(word in query_lower for word in ["hello", "hi", "hey", "help", "status"]):
            intent = IntentType.DIRECT_ANSWER
            confidence = 0.8
        elif any(word in query_lower for word in ["analysis", "insights", "trends", "performance", "metrics"]):
            intent = IntentType.BUSINESS_INTELLIGENCE
            confidence = 0.7
        elif any(word in query_lower for word in ["forecast", "predict", "correlation", "deep", "comprehensive"]):
            intent = IntentType.COMPLEX_ANALYTICS
            confidence = 0.7
        elif any(word in query_lower for word in ["briefing", "executive", "board", "strategic"]):
            intent = IntentType.COFFEE_BRIEFING
            confidence = 0.7
        else:
            intent = IntentType.SALESFORCE_QUERY
            confidence = 0.6
        
        return IntentPattern(
            intent=intent,
            confidence=confidence,
            reasoning="Fallback pattern-based classification",
            complexity_score=0.5,
            data_sources=[DataSourceType.SALESFORCE],
            persona=PersonaType.VP_SALES
        )

    def is_static_command(self, query: str) -> bool:
        """Determine if query should be handled as static command"""
        query_lower = query.lower().strip()
        
        # Only very simple, non-data queries should be static
        static_patterns = [
            r"^(hello|hi|hey)$",
            r"^(help|what can you do|capabilities)$",
            r"^(status|are you working|bot status)$",
            r"^subscribe",
            r"^unsubscribe",
            r"^list subscriptions"
        ]
        
        for pattern in static_patterns:
            if re.match(pattern, query_lower):
                return True
        
        return False
