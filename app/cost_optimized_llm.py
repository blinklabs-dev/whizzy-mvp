#!/usr/bin/env python3
"""
Cost-Optimized LLM Manager
Uses cheaper models for development, gpt-4 only for production
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
import openai
import structlog

# Configure logging
logger = structlog.get_logger()

class CostOptimizedLLM:
    """Cost-optimized LLM manager with model selection"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Model selection based on environment with latest cost-effective models
        self.models = {
            "development": {
                "ultra_fast": "gpt-4o-mini",           # Fastest & cheapest
                "fast": "gpt-3.5-turbo",               # Fast & cheap
                "balanced": "gpt-4o",                  # Balanced performance
                "accurate": "gpt-4-turbo"              # High accuracy
            },
            "production": {
                "ultra_fast": "gpt-4o-mini",           # Fastest & cheapest
                "fast": "gpt-4o",                      # Fast & good quality
                "balanced": "gpt-4-turbo",             # Balanced performance
                "accurate": "gpt-4"                    # Highest accuracy
            }
        }
        
        logger.info("Cost-optimized LLM initialized", environment=environment)
    
    def get_model(self, task_type: str = "balanced") -> str:
        """Get appropriate model based on task and environment"""
        
        # Task type mapping with ultra-fast options
        task_mapping = {
            "intent_classification": "ultra_fast", # Simple classification
            "soql_generation": "fast",             # Structured output
            "data_analysis": "balanced",           # Analysis and insights
            "dbt_generation": "accurate",          # Complex SQL generation
            "executive_briefing": "accurate",      # High-quality summaries
            "conversational": "ultra_fast",        # Simple responses
            "help": "ultra_fast"                  # Help responses
        }
        
        model_type = task_mapping.get(task_type, "balanced")
        model = self.models[self.environment][model_type]
        
        logger.info("Model selected", task_type=task_type, model_type=model_type, model=model)
        return model
    
    def call_llm(self, messages: List[Dict], task_type: str = "balanced", max_tokens: int = 1000) -> str:
        """Call LLM with cost-optimized model selection"""
        
        model = self.get_model(task_type)
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            
            # Log token usage for cost tracking
            usage = response.usage
            logger.info("LLM call completed", 
                       model=model,
                       task_type=task_type,
                       prompt_tokens=usage.prompt_tokens,
                       completion_tokens=usage.completion_tokens,
                       total_tokens=usage.total_tokens)
            
            return result
            
        except Exception as e:
            logger.error("LLM call failed", model=model, task_type=task_type, error=str(e))
            raise
    
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """Estimate cost for token usage"""
        
        # OpenAI pricing (per 1K tokens) - latest pricing
        pricing = {
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},      # Ultra cheap
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},      # Cheap
            "gpt-4o": {"input": 0.005, "output": 0.015},              # Balanced
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},           # High quality
            "gpt-4": {"input": 0.03, "output": 0.06}                  # Premium
        }
        
        if model in pricing:
            cost = (prompt_tokens * pricing[model]["input"] + 
                   completion_tokens * pricing[model]["output"]) / 1000
            return cost
        
        return 0.0

# Global LLM instance
from dotenv import load_dotenv
load_dotenv()
llm_manager = CostOptimizedLLM(environment=os.getenv("ENVIRONMENT", "development"))

def get_llm_manager() -> CostOptimizedLLM:
    """Get the global LLM manager instance"""
    return llm_manager

# Example usage
if __name__ == "__main__":
    # Test different task types
    test_messages = [{"role": "user", "content": "What is 2+2?"}]
    
    print("🧪 Testing Cost-Optimized LLM")
    print("=" * 40)
    
    tasks = ["intent_classification", "soql_generation", "dbt_generation", "executive_briefing"]
    
    for task in tasks:
        try:
            model = llm_manager.get_model(task)
            print(f"Task: {task} -> Model: {model}")
        except Exception as e:
            print(f"Task: {task} -> Error: {e}")
    
    print("\n💡 Cost Optimization Tips:")
    print("- Use gpt-4o-mini for ultra-cheap simple tasks")
    print("- Use gpt-4o for balanced performance")
    print("- Use gpt-4 only for complex analysis")
    print("- Set ENVIRONMENT=production for premium models")
    print("- Monitor token usage in logs")
    
    print("\n💰 Cost Comparison (per 1K tokens):")
    print("- gpt-4o-mini: $0.00015 input, $0.0006 output (ULTRA CHEAP)")
    print("- gpt-3.5-turbo: $0.0015 input, $0.002 output (CHEAP)")
    print("- gpt-4o: $0.005 input, $0.015 output (BALANCED)")
    print("- gpt-4-turbo: $0.01 input, $0.03 output (HIGH QUALITY)")
    print("- gpt-4: $0.03 input, $0.06 output (PREMIUM)")
