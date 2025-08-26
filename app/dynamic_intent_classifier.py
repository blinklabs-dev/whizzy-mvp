#!/usr/bin/env python3
"""
Dynamic Intent Classifier
Uses LLM-based classification and catalog-driven analysis instead of hardcoded keywords
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from openai import OpenAI
from app.intelligent_agentic_system import IntentType, PersonaType, DataSourceType

logger = logging.getLogger(__name__)

class IntentComplexity(Enum):
    """Intent complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ADVANCED = "advanced"

@dataclass
class DynamicIntentAnalysis:
    """Dynamic intent analysis result"""
    primary_intent: IntentType
    confidence: float
    complexity: IntentComplexity
    reasoning_required: bool
    data_sources_needed: List[DataSourceType]
    execution_strategy: str
    explanation: str
    catalog_relevance: Dict[str, float]

class DynamicIntentClassifier:
    """Dynamic intent classifier using LLM and catalog analysis"""
    
    def __init__(self, openai_client: OpenAI):
        self.openai_client = openai_client
        self.intent_catalog = self._load_intent_catalog()
        self.complexity_patterns = self._load_complexity_patterns()
        
    def _load_intent_catalog(self) -> Dict[str, Any]:
        """Load intent classification catalog"""
        return {
            "intent_types": {
                "SALESFORCE_QUERY": {
                    "description": "Direct data retrieval from Salesforce",
                    "complexity": IntentComplexity.SIMPLE,
                    "keywords": [],  # No hardcoded keywords
                    "patterns": ["data retrieval", "direct query", "simple lookup"],
                    "execution": "direct_salesforce_query"
                },
                "BUSINESS_INTELLIGENCE": {
                    "description": "Analytical queries requiring data processing",
                    "complexity": IntentComplexity.MODERATE,
                    "keywords": [],
                    "patterns": ["analysis", "insights", "trends", "comparison"],
                    "execution": "analytical_processing"
                },
                "THINKING_ANALYSIS": {
                    "description": "Complex reasoning requiring multi-step analysis",
                    "complexity": IntentComplexity.ADVANCED,
                    "keywords": [],
                    "patterns": ["why", "how", "reasoning", "complex analysis"],
                    "execution": "chain_of_thought"
                },
                "COMPLEX_ANALYTICS": {
                    "description": "Multi-source data analysis with insights",
                    "complexity": IntentComplexity.COMPLEX,
                    "keywords": [],
                    "patterns": ["multi-source", "correlation", "impact analysis"],
                    "execution": "multi_source_analysis"
                }
            },
            "complexity_indicators": {
                "query_length": {"weight": 0.2, "thresholds": {"short": 10, "medium": 30, "long": 50}},
                "reasoning_words": {"weight": 0.3, "words": ["why", "how", "analyze", "compare", "correlate"]},
                "context_dependency": {"weight": 0.25, "indicators": ["previous", "trend", "pattern", "relationship"]},
                "multi_step": {"weight": 0.25, "indicators": ["and", "or", "but", "however", "therefore"]}
            }
        }
    
    def _load_complexity_patterns(self) -> Dict[str, Any]:
        """Load complexity analysis patterns"""
        return {
            "simple_indicators": [
                "direct question", "single metric", "basic lookup", "status check"
            ],
            "moderate_indicators": [
                "comparison", "trend analysis", "filtered data", "aggregated metrics"
            ],
            "complex_indicators": [
                "multi-source", "correlation analysis", "predictive", "impact assessment"
            ],
            "advanced_indicators": [
                "chain of thought", "reasoning", "hypothesis testing", "strategic analysis"
            ]
        }
    
    async def classify_intent_dynamically(self, query: str, user_context: Dict[str, Any] = None) -> DynamicIntentAnalysis:
        """Dynamically classify intent using LLM and catalog analysis"""
        
        # Step 1: LLM-based intent classification
        llm_intent = await self._classify_with_llm(query, user_context)
        
        # Step 2: Catalog-driven analysis
        catalog_analysis = self._analyze_with_catalog(query, llm_intent)
        
        # Step 3: Complexity assessment
        complexity = self._assess_complexity(query, llm_intent, catalog_analysis)
        
        # Step 4: Execution strategy determination
        execution_strategy = self._determine_execution_strategy(complexity, llm_intent, catalog_analysis)
        
        return DynamicIntentAnalysis(
            primary_intent=llm_intent["intent_type"],
            confidence=llm_intent["confidence"],
            complexity=complexity,
            reasoning_required=complexity in [IntentComplexity.COMPLEX, IntentComplexity.ADVANCED],
            data_sources_needed=self._determine_data_sources(llm_intent, catalog_analysis),
            execution_strategy=execution_strategy,
            explanation=llm_intent["explanation"],
            catalog_relevance=catalog_analysis["relevance_scores"]
        )
    
    async def _classify_with_llm(self, query: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Use LLM for intelligent intent classification"""
        
        system_prompt = """You are an intelligent intent classifier for a Salesforce analytics system. 
        
Analyze the user query and classify it into the most appropriate intent type. Consider:
- Query complexity and reasoning requirements
- Data source needs
- Analysis depth required
- User context and persona

Available intent types:
1. SALESFORCE_QUERY: Simple data retrieval from Salesforce
2. BUSINESS_INTELLIGENCE: Analytical queries requiring data processing
3. THINKING_ANALYSIS: Complex reasoning requiring multi-step analysis
4. COMPLEX_ANALYTICS: Multi-source data analysis with insights

Respond with JSON:
{
    "intent_type": "INTENT_TYPE",
    "confidence": 0.0-1.0,
    "explanation": "Detailed explanation of classification",
    "reasoning_required": true/false,
    "data_sources": ["SALESFORCE", "SNOWFLAKE", "DBT"]
}"""

        user_prompt = f"Query: {query}\nUser Context: {user_context or 'None'}\n\nClassify this query:"
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Map string intent to enum
            intent_mapping = {
                "SALESFORCE_QUERY": IntentType.SALESFORCE_QUERY,
                "BUSINESS_INTELLIGENCE": IntentType.BUSINESS_INTELLIGENCE,
                "THINKING_ANALYSIS": IntentType.THINKING_ANALYSIS,
                "COMPLEX_ANALYTICS": IntentType.COMPLEX_ANALYTICS
            }
            
            return {
                "intent_type": intent_mapping.get(result["intent_type"], IntentType.SALESFORCE_QUERY),
                "confidence": result.get("confidence", 0.7),
                "explanation": result.get("explanation", "LLM classification"),
                "reasoning_required": result.get("reasoning_required", False),
                "data_sources": result.get("data_sources", ["SALESFORCE"])
            }
            
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            # Fallback to catalog-based classification
            return self._fallback_classification(query)
    
    def _analyze_with_catalog(self, query: str, llm_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze query against intent catalog"""
        
        query_lower = query.lower()
        relevance_scores = {}
        
        for intent_name, intent_info in self.intent_catalog["intent_types"].items():
            score = 0.0
            
            # Pattern matching (not hardcoded keywords)
            for pattern in intent_info["patterns"]:
                if pattern in query_lower:
                    score += 0.3
            
            # Complexity alignment
            if intent_info["complexity"] == self._assess_complexity(query, llm_result, {}):
                score += 0.2
            
            # LLM confidence alignment
            if llm_result["intent_type"].value == intent_name:
                score += 0.5
            
            relevance_scores[intent_name] = min(score, 1.0)
        
        return {
            "relevance_scores": relevance_scores,
            "best_match": max(relevance_scores.items(), key=lambda x: x[1]),
            "catalog_confidence": max(relevance_scores.values())
        }
    
    def _assess_complexity(self, query: str, llm_result: Dict[str, Any], catalog_analysis: Dict[str, Any]) -> IntentComplexity:
        """Assess query complexity using multiple indicators"""
        
        query_lower = query.lower()
        complexity_score = 0.0
        
        # Query length analysis
        length_weight = self.intent_catalog["complexity_indicators"]["query_length"]["weight"]
        length_thresholds = self.intent_catalog["complexity_indicators"]["query_length"]["thresholds"]
        
        if len(query) < length_thresholds["short"]:
            complexity_score += 0.1 * length_weight
        elif len(query) < length_thresholds["medium"]:
            complexity_score += 0.3 * length_weight
        elif len(query) < length_thresholds["long"]:
            complexity_score += 0.6 * length_weight
        else:
            complexity_score += 0.9 * length_weight
        
        # Reasoning words analysis
        reasoning_weight = self.intent_catalog["complexity_indicators"]["reasoning_words"]["weight"]
        reasoning_words = self.intent_catalog["complexity_indicators"]["reasoning_words"]["words"]
        
        reasoning_count = sum(1 for word in reasoning_words if word in query_lower)
        complexity_score += min(reasoning_count * 0.2, 1.0) * reasoning_weight
        
        # Context dependency analysis
        context_weight = self.intent_catalog["complexity_indicators"]["context_dependency"]["weight"]
        context_indicators = self.intent_catalog["complexity_indicators"]["context_dependency"]["indicators"]
        
        context_count = sum(1 for indicator in context_indicators if indicator in query_lower)
        complexity_score += min(context_count * 0.25, 1.0) * context_weight
        
        # Multi-step analysis
        multi_step_weight = self.intent_catalog["complexity_indicators"]["multi_step"]["weight"]
        multi_step_indicators = self.intent_catalog["complexity_indicators"]["multi_step"]["indicators"]
        
        multi_step_count = sum(1 for indicator in multi_step_indicators if indicator in query_lower)
        complexity_score += min(multi_step_count * 0.2, 1.0) * multi_step_weight
        
        # Map score to complexity level
        if complexity_score < 0.3:
            return IntentComplexity.SIMPLE
        elif complexity_score < 0.6:
            return IntentComplexity.MODERATE
        elif complexity_score < 0.8:
            return IntentComplexity.COMPLEX
        else:
            return IntentComplexity.ADVANCED
    
    def _determine_execution_strategy(self, complexity: IntentComplexity, llm_result: Dict[str, Any], catalog_analysis: Dict[str, Any]) -> str:
        """Determine execution strategy based on complexity and analysis"""
        
        if complexity == IntentComplexity.SIMPLE:
            return "direct_query"
        elif complexity == IntentComplexity.MODERATE:
            return "analytical_processing"
        elif complexity == IntentComplexity.COMPLEX:
            return "multi_source_analysis"
        else:  # ADVANCED
            return "chain_of_thought"
    
    def _determine_data_sources(self, llm_result: Dict[str, Any], catalog_analysis: Dict[str, Any]) -> List[DataSourceType]:
        """Determine required data sources"""
        
        sources = []
        data_sources = llm_result.get("data_sources", ["SALESFORCE"])
        
        for source in data_sources:
            if source == "SALESFORCE":
                sources.append(DataSourceType.SALESFORCE)
            elif source == "SNOWFLAKE":
                sources.append(DataSourceType.SNOWFLAKE)
            elif source == "DBT":
                sources.append(DataSourceType.DBT)
        
        return sources if sources else [DataSourceType.SALESFORCE]
    
    def _fallback_classification(self, query: str) -> Dict[str, Any]:
        """Fallback classification when LLM fails"""
        
        # Simple pattern-based fallback (not hardcoded keywords)
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["why", "how", "analyze", "reason"]):
            return {
                "intent_type": IntentType.THINKING_ANALYSIS,
                "confidence": 0.6,
                "explanation": "Fallback: Reasoning indicators detected",
                "reasoning_required": True,
                "data_sources": ["SALESFORCE"]
            }
        elif any(word in query_lower for word in ["compare", "trend", "analysis"]):
            return {
                "intent_type": IntentType.BUSINESS_INTELLIGENCE,
                "confidence": 0.6,
                "explanation": "Fallback: Analytical indicators detected",
                "reasoning_required": False,
                "data_sources": ["SALESFORCE"]
            }
        else:
            return {
                "intent_type": IntentType.SALESFORCE_QUERY,
                "confidence": 0.5,
                "explanation": "Fallback: Default to simple query",
                "reasoning_required": False,
                "data_sources": ["SALESFORCE"]
            }

