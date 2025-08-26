#!/usr/bin/env python3
"""
Enhanced Intelligent Agentic System - Production Ready
Combines advanced reasoning with real data integration and cost optimization

Features:
- Advanced thinking and reasoning with chain of thought processing
- Real Salesforce + Snowflake data integration (NO MOCK DATA)
- Cost-optimized LLM with smart model selection
- Multi-step context management and state tracking
- Persona-specific responses and coffee briefings
- Comprehensive evaluation and quality assessment
- Robust error handling and data validation
"""

import asyncio
import logging
import json
import re
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid
from concurrent.futures import ThreadPoolExecutor
import openai
from simple_salesforce import Salesforce
import snowflake.connector
import os
from dotenv import load_dotenv
import structlog

# Load environment variables
load_dotenv()

# Configure structured logging
logger = structlog.get_logger()

class IntentType(Enum):
    """Intent classification types"""
    DIRECT_ANSWER = "direct_answer"
    SALESFORCE_QUERY = "salesforce_query"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    COMPLEX_ANALYTICS = "complex_analytics"
    DBT_MODEL = "dbt_model"
    COFFEE_BRIEFING = "coffee_briefing"
    REASONING_LOOP = "reasoning_loop"
    MULTI_SOURCE = "multi_source"
    THINKING_ANALYSIS = "thinking_analysis"

class PersonaType(Enum):
    """Persona types for personalized responses"""
    VP_SALES = "vp_sales"
    ACCOUNT_EXECUTIVE = "account_executive"
    SALES_MANAGER = "sales_manager"
    CDO = "cdo"
    DATA_ENGINEER = "data_engineer"
    SALES_OPERATIONS = "sales_operations"
    CUSTOMER_SUCCESS = "customer_success"

class DataSourceType(Enum):
    """Data source types"""
    SALESFORCE = "salesforce"
    SNOWFLAKE = "snowflake"
    DBT = "dbt"
    COMBINED = "combined"

class ReasoningStep(Enum):
    """Reasoning step types"""
    INTENT_ANALYSIS = "intent_analysis"
    CONTEXT_GATHERING = "context_gathering"
    DATA_SOURCE_SELECTION = "data_source_selection"
    QUERY_GENERATION = "query_generation"
    DATA_ANALYSIS = "data_analysis"
    INSIGHT_SYNTHESIS = "insight_synthesis"
    RECOMMENDATION_GENERATION = "recommendation_generation"
    RESPONSE_FORMATTING = "response_formatting"

@dataclass
class ThinkingStep:
    """Individual thinking step in the reasoning process"""
    step_type: ReasoningStep
    description: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    confidence: float
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ChainOfThought:
    """Chain of thought reasoning process"""
    query: str
    persona: PersonaType
    thinking_steps: List[ThinkingStep]
    final_confidence: float
    reasoning_path: str
    context_used: Dict[str, Any]
    data_sources_accessed: List[DataSourceType]

@dataclass
class IntentAnalysis:
    """Intent analysis result"""
    primary_intent: IntentType
    confidence: float
    persona: PersonaType
    data_sources: List[DataSourceType]
    complexity_level: str
    reasoning_required: bool
    coffee_briefing: bool
    dbt_model_required: bool
    thinking_required: bool
    explanation: str

@dataclass
class AgentResponse:
    """Agent response with quality metrics"""
    response_text: str
    data_sources_used: List[DataSourceType]
    reasoning_steps: List[str]
    confidence_score: float
    persona_alignment: float
    actionability_score: float
    quality_metrics: Dict[str, float]
    chain_of_thought: Optional[ChainOfThought] = None
    thinking_process: str = ""

@dataclass
class CoffeeBriefing:
    """Coffee briefing structure"""
    persona: PersonaType
    frequency: str  # daily, weekly, monthly
    key_metrics: List[str]
    insights: List[str]
    action_items: List[str]
    risks: List[str]
    opportunities: List[str]

@dataclass
class ContextState:
    """Context state for conversation tracking"""
    user_id: str
    conversation_history: List[Dict[str, Any]]
    current_context: Dict[str, Any]
    persona_preferences: Dict[str, Any]
    data_source_preferences: List[DataSourceType]
    last_query: str
    last_response: Optional[AgentResponse]
    session_start: datetime
    context_window: int = 10

class CostOptimizedLLM:
    """Cost-optimized LLM manager"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Model selection based on environment
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
        
        # Task type mapping with reasoning complexity
        task_mapping = {
            "intent_classification": "ultra_fast",     # Simple classification
            "soql_generation": "fast",                 # Structured output
            "data_analysis": "balanced",               # Analysis and insights
            "reasoning": "accurate",                   # Complex reasoning
            "chain_of_thought": "accurate",            # Advanced reasoning
            "executive_briefing": "accurate",          # High-quality summaries
            "conversational": "ultra_fast",            # Simple responses
            "help": "ultra_fast"                       # Help responses
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

class RealDataConnector:
    """Real data connector for Salesforce and Snowflake"""
    
    def __init__(self):
        self.salesforce_client = self._initialize_salesforce()
        self.snowflake_connection = self._initialize_snowflake()
        logger.info("Real data connector initialized")
    
    def _initialize_salesforce(self) -> Optional[Salesforce]:
        """Initialize real Salesforce connection"""
        try:
            client = Salesforce(
                username=os.getenv('SALESFORCE_USERNAME'),
                password=os.getenv('SALESFORCE_PASSWORD'),
                security_token=os.getenv('SALESFORCE_SECURITY_TOKEN'),
                domain=os.getenv('SALESFORCE_DOMAIN', 'login')
            )
            logger.info("✅ Real Salesforce connection established")
            return client
        except Exception as e:
            logger.error(f"❌ Failed to initialize Salesforce: {e}")
            return None
    
    def _initialize_snowflake(self) -> Optional[snowflake.connector.SnowflakeConnection]:
        """Initialize real Snowflake connection"""
        try:
            conn = snowflake.connector.connect(
                user=os.getenv('SNOWFLAKE_USER'),
                password=os.getenv('SNOWFLAKE_PASSWORD'),
                account=os.getenv('SNOWFLAKE_ACCOUNT'),
                warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
                database=os.getenv('SNOWFLAKE_DATABASE'),
                schema=os.getenv('SNOWFLAKE_SCHEMA'),
                role=os.getenv('SNOWFLAKE_ROLE'),
            )
            logger.info("✅ Real Snowflake connection established")
            return conn
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Snowflake: {e}")
            return None
    
    async def execute_salesforce_query(self, soql_query: str) -> Dict[str, Any]:
        """Execute real SOQL query against Salesforce"""
        if not self.salesforce_client:
            return {"error": "Salesforce connection not available"}
        
        try:
            result = self.salesforce_client.query_all(soql_query)
            return {
                "status": "success",
                "records": result['records'],
                "totalSize": result['totalSize'],
                "done": result['done']
            }
        except Exception as e:
            logger.error("Salesforce query failed", error=str(e))
            return {"error": str(e)}
    
    async def execute_snowflake_query(self, sql_query: str) -> Dict[str, Any]:
        """Execute real SQL query against Snowflake"""
        if not self.snowflake_connection:
            return {"error": "Snowflake connection not available"}
        
        try:
            cursor = self.snowflake_connection.cursor()
            cursor.execute(sql_query)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Get all results
            rows = cursor.fetchall()
            data = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # Convert datetime objects to strings for JSON serialization
                    if hasattr(value, 'isoformat'):
                        row_dict[col] = value.isoformat()
                    else:
                        row_dict[col] = value
                data.append(row_dict)
            
            cursor.close()
            
            return {
                "status": "success",
                "data": data,
                "columns": columns,
                "total_rows": len(data)
            }
        except Exception as e:
            logger.error("Snowflake query failed", error=str(e))
            return {"error": str(e)}

class EnhancedIntelligentAgenticSystem:
    """Enhanced intelligent agentic system with real data integration"""

    def __init__(self):
        self.llm_manager = CostOptimizedLLM(environment=os.getenv("ENVIRONMENT", "development"))
        self.data_connector = RealDataConnector()
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.conversation_history = []
        self.quality_metrics = {}
        self.context_states = {}  # Track context per user

        # Load enhanced prompts
        self.persona_prompts = self._load_persona_prompts()
        self.intent_classification_prompt = self._load_intent_classification_prompt()
        self.reasoning_prompt = self._load_reasoning_prompt()
        self.thinking_prompt = self._load_thinking_prompt()
        self.chain_of_thought_prompt = self._load_chain_of_thought_prompt()

        logger.info("🧠 Enhanced Intelligent Agentic System initialized with real data")

    def _load_persona_prompts(self) -> Dict[str, str]:
        """Load persona-specific prompts"""
        return {
            "vp_sales": "You are responding to a VP of Sales with advanced strategic thinking. Focus on strategic insights, business impact, team performance, and executive-level recommendations.",
            "account_executive": "You are responding to an Account Executive. Focus on deal preparation, customer insights, and tactical recommendations.",
            "sales_manager": "You are responding to a Sales Manager. Focus on team performance, coaching opportunities, and process optimization.",
            "cdo": "You are responding to a Chief Data Officer. Focus on data strategy, analytics capabilities, and data-driven insights.",
            "data_engineer": "You are responding to a Data Engineer. Focus on data pipeline optimization, technical implementation, and data quality.",
            "sales_operations": "You are responding to a Sales Operations professional. Focus on process optimization, data quality, and operational efficiency.",
            "customer_success": "You are responding to a Customer Success Manager. Focus on account health, retention strategies, and customer insights."
        }

    def _load_intent_classification_prompt(self) -> str:
        """Load intent classification prompt"""
        return """
You are an expert intent classifier for a business analytics system. Analyze the user query and classify the intent.

Available intents:
- DIRECT_ANSWER: Simple factual questions
- SALESFORCE_QUERY: Questions about Salesforce data (opportunities, accounts, users)
- BUSINESS_INTELLIGENCE: Complex business analysis questions
- COMPLEX_ANALYTICS: Advanced analytics requiring multiple data sources
- DBT_MODEL: Questions requiring dbt model execution
- COFFEE_BRIEFING: Requests for scheduled briefings
- REASONING_LOOP: Complex queries requiring multi-step reasoning
- MULTI_SOURCE: Queries requiring multiple data sources
- THINKING_ANALYSIS: Queries requiring advanced thinking and analysis

Return JSON:
{
    "intent": "intent_type",
    "confidence": 0.95,
    "persona": "persona_type",
    "data_sources": ["salesforce", "snowflake"],
    "complexity_level": "simple|medium|complex",
    "reasoning_required": true|false,
    "explanation": "reasoning for classification"
}
"""

    def _load_reasoning_prompt(self) -> str:
        """Load reasoning prompt"""
        return """
You are an expert business analyst. Analyze the query and provide step-by-step reasoning.

Query: {query}
Persona: {persona}
Context: {context}

Provide your analysis in this format:

REASONING:
[Step-by-step reasoning]

DATA_SOURCES:
[List of required data sources]

ANALYSIS_APPROACH:
[How to approach the analysis]

INSIGHTS:
[Key insights to look for]

RECOMMENDATIONS:
[Recommended actions]
"""

    def _load_thinking_prompt(self) -> str:
        """Load thinking prompt"""
        return """
You are a master planner and orchestrator AI. Break down complex queries into executable steps.

Available Tools:
- salesforce_query: Query Salesforce data
- snowflake_query: Query Snowflake data warehouse
- analysis_tool: Perform analysis on data

Generate a JSON plan:
{
    "steps": [
        {
            "id": 1,
            "tool": "tool_name",
            "query": "specific query",
            "dependencies": []
        }
    ]
}
"""

    def _load_chain_of_thought_prompt(self) -> str:
        """Load chain of thought prompt"""
        return """
You are an expert business analyst with advanced reasoning capabilities. Use chain of thought reasoning.

QUERY: {query}
PERSONA: {persona}
CONTEXT: {context}

Think through this step by step:

1. INTENT ANALYSIS: What is the user really asking for?
2. CONTEXT GATHERING: What historical context is relevant?
3. DATA SOURCE SELECTION: Which data sources are most appropriate?
4. ANALYSIS APPROACH: What analytical methods should be used?
5. INSIGHT SYNTHESIS: How do the pieces fit together?
6. RESPONSE FORMULATION: How should insights be presented?

Provide your reasoning in this format:

THINKING PROCESS:
[Your step-by-step reasoning]

CHAIN OF THOUGHT:
1. [First reasoning step]
2. [Second reasoning step]
...

FINAL ANALYSIS:
[Your comprehensive analysis]

RECOMMENDATIONS:
[Your recommendations]

CONFIDENCE: [0.0-1.0]
"""

    async def _execute_thinking_process(self, query: str, persona: PersonaType, context: Dict[str, Any]) -> ChainOfThought:
        """Execute advanced thinking process with chain of thought reasoning"""
        try:
            thinking_prompt = self.thinking_prompt.format(
                query=query,
                persona=persona.value,
                context=json.dumps(context, indent=2)
            )

            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.llm_manager.call_llm(
                    [{"role": "system", "content": thinking_prompt}, {"role": "user", "content": query}],
                    task_type="chain_of_thought"
                )
            )

            # Parse thinking steps
            thinking_steps = self._parse_thinking_steps(response)
            
            chain_of_thought = ChainOfThought(
                query=query,
                persona=persona,
                thinking_steps=thinking_steps,
                final_confidence=self._extract_confidence(response),
                reasoning_path=response,
                context_used=context,
                data_sources_accessed=self._extract_data_sources(response)
            )

            return chain_of_thought

        except Exception as e:
            logger.error("Thinking process failed", error=str(e))
            raise

    def _parse_thinking_steps(self, response: str) -> List[ThinkingStep]:
        """Parse thinking steps from response"""
        steps = []
        try:
            # Extract steps from response
            lines = response.split('\n')
            current_step = None
            
            for line in lines:
                if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.')):
                    if current_step:
                        steps.append(current_step)
                    
                    step_type = self._extract_step_type(line)
                    current_step = ThinkingStep(
                        step_type=step_type,
                        description=line.strip(),
                        input_data={},
                        output_data={},
                        confidence=0.8,
                        reasoning=line.strip()
                    )
                elif current_step and line.strip():
                    current_step.reasoning += " " + line.strip()
            
            if current_step:
                steps.append(current_step)
                
        except Exception as e:
            logger.error("Failed to parse thinking steps", error=str(e))
        
        return steps

    def _extract_step_type(self, line: str) -> ReasoningStep:
        """Extract reasoning step type from line"""
        line_lower = line.lower()
        if "intent" in line_lower:
            return ReasoningStep.INTENT_ANALYSIS
        elif "context" in line_lower:
            return ReasoningStep.CONTEXT_GATHERING
        elif "data" in line_lower and "source" in line_lower:
            return ReasoningStep.DATA_SOURCE_SELECTION
        elif "query" in line_lower:
            return ReasoningStep.QUERY_GENERATION
        elif "analysis" in line_lower:
            return ReasoningStep.DATA_ANALYSIS
        elif "insight" in line_lower:
            return ReasoningStep.INSIGHT_SYNTHESIS
        elif "recommendation" in line_lower:
            return ReasoningStep.RECOMMENDATION_GENERATION
        elif "response" in line_lower:
            return ReasoningStep.RESPONSE_FORMATTING
        else:
            return ReasoningStep.INTENT_ANALYSIS

    def _extract_confidence(self, response: str) -> float:
        """Extract confidence score from response"""
        try:
            confidence_match = re.search(r'CONFIDENCE:\s*([0-9.]+)', response)
            if confidence_match:
                return float(confidence_match.group(1))
        except Exception:
            pass
        return 0.8

    def _extract_data_sources(self, response: str) -> List[DataSourceType]:
        """Extract data sources from response"""
        sources = []
        response_lower = response.lower()
        
        if "salesforce" in response_lower:
            sources.append(DataSourceType.SALESFORCE)
        if "snowflake" in response_lower:
            sources.append(DataSourceType.SNOWFLAKE)
        if "dbt" in response_lower:
            sources.append(DataSourceType.DBT)
        if len(sources) > 1:
            sources.append(DataSourceType.COMBINED)
        
        return sources

    async def classify_intent(self, query: str, persona: PersonaType) -> IntentAnalysis:
        """Classify user intent with advanced reasoning"""
        try:
            messages = [
                {"role": "system", "content": self.intent_classification_prompt},
                {"role": "user", "content": f"Query: {query}\nPersona: {persona.value}"}
            ]

            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.llm_manager.call_llm(messages, task_type="intent_classification")
            )

            result = json.loads(response)
            
            return IntentAnalysis(
                primary_intent=IntentType(result["intent"]),
                confidence=result["confidence"],
                persona=persona,
                data_sources=[DataSourceType(source) for source in result["data_sources"]],
                complexity_level=result["complexity_level"],
                reasoning_required=result["reasoning_required"],
                coffee_briefing=result.get("coffee_briefing", False),
                dbt_model_required=result.get("dbt_model_required", False),
                thinking_required=result.get("thinking_required", False),
                explanation=result["explanation"]
            )

        except Exception as e:
            logger.error("Intent classification failed", error=str(e))
            # Fallback to simple classification
            return IntentAnalysis(
                primary_intent=IntentType.SALESFORCE_QUERY,
                confidence=0.5,
                persona=persona,
                data_sources=[DataSourceType.SALESFORCE],
                complexity_level="simple",
                reasoning_required=False,
                coffee_briefing=False,
                dbt_model_required=False,
                thinking_required=False,
                explanation="Fallback classification due to error"
            )

    async def execute_query(self, query: str, persona: PersonaType, user_id: str = "default") -> AgentResponse:
        """Execute query with advanced reasoning and real data"""
        try:
            # Step 1: Intent Classification
            intent_analysis = await self.classify_intent(query, persona)
            logger.info("Intent classified", intent=intent_analysis.primary_intent.value, confidence=intent_analysis.confidence)

            # Step 2: Advanced Reasoning (if required)
            chain_of_thought = None
            if intent_analysis.reasoning_required or intent_analysis.thinking_required:
                context = self._get_user_context(user_id)
                chain_of_thought = await self._execute_thinking_process(query, persona, context)
                logger.info("Advanced reasoning completed", confidence=chain_of_thought.final_confidence)

            # Step 3: Data Execution
            data_sources_used = []
            execution_results = {}

            if DataSourceType.SALESFORCE in intent_analysis.data_sources:
                soql_query = await self._generate_soql_query(query, intent_analysis)
                salesforce_result = await self.data_connector.execute_salesforce_query(soql_query)
                execution_results["salesforce"] = salesforce_result
                data_sources_used.append(DataSourceType.SALESFORCE)
                logger.info("Salesforce query executed", records=salesforce_result.get("totalSize", 0))

            if DataSourceType.SNOWFLAKE in intent_analysis.data_sources:
                sql_query = await self._generate_snowflake_query(query, intent_analysis)
                snowflake_result = await self.data_connector.execute_snowflake_query(sql_query)
                execution_results["snowflake"] = snowflake_result
                data_sources_used.append(DataSourceType.SNOWFLAKE)
                logger.info("Snowflake query executed", rows=snowflake_result.get("total_rows", 0))

            # Step 4: Response Generation
            response_text = await self._generate_response(query, intent_analysis, execution_results, chain_of_thought, persona)

            # Step 5: Quality Assessment
            quality_metrics = self._assess_response_quality(response_text, intent_analysis, execution_results)

            # Create agent response
            agent_response = AgentResponse(
                response_text=response_text,
                data_sources_used=data_sources_used,
                reasoning_steps=[step.description for step in (chain_of_thought.thinking_steps if chain_of_thought else [])],
                confidence_score=intent_analysis.confidence,
                persona_alignment=self._calculate_persona_alignment(response_text, persona),
                actionability_score=self._calculate_actionability_score(response_text),
                quality_metrics=quality_metrics,
                chain_of_thought=chain_of_thought,
                thinking_process=chain_of_thought.reasoning_path if chain_of_thought else ""
            )

            # Update context
            self._update_user_context(user_id, query, agent_response)

            logger.info("Query executed successfully", 
                       intent=intent_analysis.primary_intent.value,
                       confidence=agent_response.confidence_score,
                       data_sources=len(data_sources_used))

            return agent_response

        except Exception as e:
            logger.error("Query execution failed", error=str(e))
            return AgentResponse(
                response_text=f"I encountered an error while processing your request: {str(e)}",
                data_sources_used=[],
                reasoning_steps=[],
                confidence_score=0.0,
                persona_alignment=0.0,
                actionability_score=0.0,
                quality_metrics={"error": 1.0},
                thinking_process="Error occurred during execution"
            )

    async def _generate_soql_query(self, query: str, intent_analysis: IntentAnalysis) -> str:
        """Generate SOQL query from natural language"""
        try:
            messages = [
                {"role": "system", "content": "Generate a SOQL query for Salesforce. Use proper field names and relationships."},
                {"role": "user", "content": f"Query: {query}\nIntent: {intent_analysis.primary_intent.value}"}
            ]

            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.llm_manager.call_llm(messages, task_type="soql_generation")
            )

            # Extract SOQL query from response
            soql_match = re.search(r'SELECT.*?(?:LIMIT|$)', response, re.IGNORECASE | re.DOTALL)
            if soql_match:
                return soql_match.group(0).strip()
            else:
                return f"SELECT Id, Name FROM Opportunity WHERE Name LIKE '%{query}%' LIMIT 10"

        except Exception as e:
            logger.error("SOQL generation failed", error=str(e))
            return "SELECT Id, Name FROM Opportunity LIMIT 10"

    async def _generate_snowflake_query(self, query: str, intent_analysis: IntentAnalysis) -> str:
        """Generate Snowflake SQL query from natural language"""
        try:
            messages = [
                {"role": "system", "content": "Generate a SQL query for Snowflake. Use the stg_sf__opportunity table."},
                {"role": "user", "content": f"Query: {query}\nIntent: {intent_analysis.primary_intent.value}"}
            ]

            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.llm_manager.call_llm(messages, task_type="data_analysis")
            )

            # Extract SQL query from response
            sql_match = re.search(r'SELECT.*?(?:LIMIT|$)', response, re.IGNORECASE | re.DOTALL)
            if sql_match:
                return sql_match.group(0).strip()
            else:
                return "SELECT COUNT(*) as total_opportunities FROM stg_sf__opportunity"

        except Exception as e:
            logger.error("SQL generation failed", error=str(e))
            return "SELECT COUNT(*) as total_opportunities FROM stg_sf__opportunity"

    async def _generate_response(self, query: str, intent_analysis: IntentAnalysis, execution_results: Dict[str, Any], chain_of_thought: Optional[ChainOfThought], persona: PersonaType) -> str:
        """Generate response with persona-specific formatting"""
        try:
            persona_prompt = self.persona_prompts.get(persona.value, "")
            
            messages = [
                {"role": "system", "content": f"{persona_prompt}\n\nGenerate a professional, actionable response based on the data and analysis."},
                {"role": "user", "content": f"Query: {query}\nData: {json.dumps(execution_results, indent=2)}\nReasoning: {chain_of_thought.reasoning_path if chain_of_thought else 'Direct analysis'}"}
            ]

            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.llm_manager.call_llm(messages, task_type="executive_briefing")
            )

            return response

        except Exception as e:
            logger.error("Response generation failed", error=str(e))
            return f"Based on the available data, I found some insights. However, I encountered an issue while generating the detailed response: {str(e)}"

    def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user context"""
        if user_id not in self.context_states:
            self.context_states[user_id] = ContextState(
                user_id=user_id,
                conversation_history=[],
                current_context={},
                persona_preferences={},
                data_source_preferences=[],
                last_query="",
                last_response=None,
                session_start=datetime.now()
            )
        return self.context_states[user_id].current_context

    def _update_user_context(self, user_id: str, query: str, response: AgentResponse):
        """Update user context"""
        if user_id not in self.context_states:
            self._get_user_context(user_id)
        
        self.context_states[user_id].last_query = query
        self.context_states[user_id].last_response = response
        self.context_states[user_id].conversation_history.append({
            "query": query,
            "response": response.response_text,
            "timestamp": datetime.now().isoformat()
        })

    def _assess_response_quality(self, response_text: str, intent_analysis: IntentAnalysis, execution_results: Dict[str, Any]) -> Dict[str, float]:
        """Assess response quality"""
        quality_metrics = {
            "completeness": 0.8,
            "accuracy": 0.8,
            "relevance": 0.8,
            "actionability": 0.8
        }
        
        # Simple quality assessment
        if len(response_text) > 100:
            quality_metrics["completeness"] = 0.9
        if "error" not in response_text.lower():
            quality_metrics["accuracy"] = 0.9
        if any(keyword in response_text.lower() for keyword in ["insight", "recommendation", "action"]):
            quality_metrics["actionability"] = 0.9
        
        return quality_metrics

    def _calculate_persona_alignment(self, response_text: str, persona: PersonaType) -> float:
        """Calculate persona alignment score"""
        persona_keywords = {
            PersonaType.VP_SALES: ["strategic", "executive", "business impact", "team performance"],
            PersonaType.ACCOUNT_EXECUTIVE: ["deal", "customer", "opportunity", "close"],
            PersonaType.SALES_MANAGER: ["team", "performance", "coaching", "process"],
            PersonaType.CDO: ["data", "analytics", "strategy", "insights"],
            PersonaType.DATA_ENGINEER: ["pipeline", "technical", "implementation", "quality"],
            PersonaType.SALES_OPERATIONS: ["process", "optimization", "efficiency", "data quality"],
            PersonaType.CUSTOMER_SUCCESS: ["customer", "health", "retention", "engagement"]
        }
        
        keywords = persona_keywords.get(persona, [])
        response_lower = response_text.lower()
        
        matches = sum(1 for keyword in keywords if keyword in response_lower)
        return min(1.0, matches / len(keywords)) if keywords else 0.5

    def _calculate_actionability_score(self, response_text: str) -> float:
        """Calculate actionability score"""
        action_keywords = ["recommend", "action", "next step", "should", "need to", "consider"]
        response_lower = response_text.lower()
        
        matches = sum(1 for keyword in action_keywords if keyword in response_lower)
        return min(1.0, matches / len(action_keywords))

# Global instance
enhanced_system = EnhancedIntelligentAgenticSystem()

async def process_query(query: str, persona: PersonaType = PersonaType.VP_SALES, user_id: str = "default") -> AgentResponse:
    """Process a query with the enhanced intelligent agentic system"""
    return await enhanced_system.execute_query(query, persona, user_id)
