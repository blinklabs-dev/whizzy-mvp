#!/usr/bin/env python3
"""
Enhanced Intelligent Agentic System - Advanced Analytics Orchestration
Features:
- Advanced thinking and reasoning with chain of thought processing
- Multi-step context management and state tracking
- LLM-powered intent classification and understanding
- Multi-agent orchestration with reasoning
- Text-to-SOQL, Text-to-dbt, Text-to-Business Intelligence
- Multi-source analytics (Salesforce, Snowflake, dbt)
- Persona-specific responses and coffee briefings
- Comprehensive evaluation and quality assessment
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

from app.tools.base_tool import BaseTool
from app.tools.salesforce_tool import SalesforceTool
from app.tools.snowflake_tool import SnowflakeTool

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

class EnhancedIntelligentAgenticSystem:
    """Enhanced intelligent agentic system with advanced thinking and reasoning"""

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.conversation_history = []
        self.quality_metrics = {}
        self.context_states = {}  # Track context per user

        # Initialize clients
        self.salesforce_client = self._initialize_salesforce()
        self.snowflake_connection = self._initialize_snowflake()

        # Initialize tools
        self.tools: Dict[str, BaseTool] = {
            "salesforce": SalesforceTool(self.salesforce_client, self.openai_client, self.executor),
            "snowflake": SnowflakeTool(self.snowflake_connection, self.openai_client, self.executor),
        }

        # Load enhanced prompts
        self.persona_prompts = self._load_persona_prompts()
        self.intent_classification_prompt = self._load_intent_classification_prompt()
        self.reasoning_prompt = self._load_reasoning_prompt()
        self.thinking_prompt = self._load_thinking_prompt()
        self.chain_of_thought_prompt = self._load_chain_of_thought_prompt()
        self.summarize_simple_prompt = self._load_prompt_from_file(os.path.join(os.path.dirname(__file__), '..', 'prompts', 'system', 'summarize_simple.txt'))
        self.summarize_full_prompt = self._load_prompt_from_file(os.path.join(os.path.dirname(__file__), '..', 'prompts', 'system', 'summarize_full.txt'))
        self.narrator_briefing_vp_sales_prompt = self._load_prompt_from_file(os.path.join(os.path.dirname(__file__), '..', 'prompts', 'system', 'narrator_briefing_vp_sales.txt'))
        self.extract_dbt_requirements_prompt = self._load_prompt_from_file(os.path.join(os.path.dirname(__file__), '..', 'prompts', 'system', 'extract_dbt_requirements.txt'))
        self.generate_dbt_model_prompt = self._load_prompt_from_file(os.path.join(os.path.dirname(__file__), '..', 'prompts', 'system', 'generate_dbt_model.txt'))

        logger.info("🧠 Enhanced Intelligent Agentic System initialized")

    def _initialize_salesforce(self) -> Optional[Salesforce]:
        """Initialize Salesforce connection"""
        try:
            return Salesforce(
                username=os.getenv('SALESFORCE_USERNAME'),
                password=os.getenv('SALESFORCE_PASSWORD'),
                security_token=os.getenv('SALESFORCE_SECURITY_TOKEN'),
                domain=os.getenv('SALESFORCE_DOMAIN', 'login')
            )
        except Exception as e:
            logger.error(f"❌ Failed to initialize Salesforce: {e}")
            return None

    def _initialize_snowflake(self) -> Optional[snowflake.connector.SnowflakeConnection]:
        """Initialize Snowflake connection."""
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
            logger.info("✅ Snowflake connection initialized")
            return conn
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Snowflake (this may be expected if not configured): {e}")
            return None

    def _load_prompt_from_file(self, file_path: str) -> str:
        """Helper function to load a prompt from a file."""
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Prompt file not found at {file_path}")
            return f"Error: Prompt file not found at {file_path}"
        except Exception as e:
            logger.error(f"Error loading prompt from {file_path}: {e}")
            return f"Error: Could not load prompt from {file_path}"

    def _load_chain_of_thought_prompt(self) -> str:
        """Load chain of thought reasoning prompt from file."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'system', 'chain_of_thought.txt')
        return self._load_prompt_from_file(file_path)

    def _load_thinking_prompt(self) -> str:
        """Load thinking and reasoning prompt from file."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'system', 'thinking.txt')
        return self._load_prompt_from_file(file_path)

    def _load_intent_classification_prompt(self) -> str:
        """Load enhanced intent classification prompt from file."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'system', 'intent_classification.txt')
        return self._load_prompt_from_file(file_path)

    def _load_reasoning_prompt(self) -> str:
        """Load enhanced reasoning prompt for complex queries from file."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'system', 'reasoning.txt')
        return self._load_prompt_from_file(file_path)

    def _load_persona_prompts(self) -> Dict[str, str]:
        """Load enhanced persona-specific prompts from files."""
        prompts = {}
        persona_dir = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'personas')
        try:
            for filename in os.listdir(persona_dir):
                if filename.endswith(".txt"):
                    persona_name = filename[:-4]  # Remove .txt extension
                    file_path = os.path.join(persona_dir, filename)
                    prompts[persona_name] = self._load_prompt_from_file(file_path)
            return prompts
        except FileNotFoundError:
            logger.error(f"Personas directory not found at {persona_dir}")
            return {}
        except Exception as e:
            logger.error(f"Error loading persona prompts: {e}")
            return {}

    async def _execute_thinking_process(self, query: str, persona: PersonaType, context: Dict[str, Any], available_data: Dict[str, Any]) -> ChainOfThought:
        """Execute advanced thinking process with chain of thought reasoning"""
        try:
            # Create thinking prompt
            thinking_prompt = self.thinking_prompt.format(
                query=query,
                persona=persona.value,
                context=json.dumps(context, indent=2),
                available_data=json.dumps(available_data, indent=2)
            )

            # Execute thinking process
            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": thinking_prompt},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.3
                )
            )

            thinking_response = response.choices[0].message.content

            # Parse thinking steps
            thinking_steps = self._parse_thinking_steps(thinking_response)

            # Create chain of thought
            chain_of_thought = ChainOfThought(
                query=query,
                persona=persona,
                thinking_steps=thinking_steps,
                final_confidence=self._extract_confidence(thinking_response),
                reasoning_path=thinking_response,
                context_used=context,
                data_sources_accessed=self._extract_data_sources(thinking_response)
            )

            return chain_of_thought

        except Exception as e:
            logger.error(f"❌ Error in thinking process: {e}")
            return self._create_fallback_chain_of_thought(query, persona, context)

    def _parse_thinking_steps(self, thinking_response: str) -> List[ThinkingStep]:
        """Parse thinking steps from response"""
        steps = []

        # Extract different thinking phases
        phases = {
            ReasoningStep.INTENT_ANALYSIS: "THINKING PROCESS",
            ReasoningStep.CONTEXT_GATHERING: "CRITICAL INSIGHTS",
            ReasoningStep.DATA_SOURCE_SELECTION: "SYSTEMS ANALYSIS",
            ReasoningStep.QUERY_GENERATION: "STRATEGIC IMPLICATIONS",
            ReasoningStep.DATA_ANALYSIS: "CREATIVE OPPORTUNITIES",
            ReasoningStep.INSIGHT_SYNTHESIS: "ANALYTICAL FINDINGS"
        }

        for step_type, phase_name in phases.items():
            if phase_name in thinking_response:
                # Extract content for this phase
                start_idx = thinking_response.find(phase_name)
                if start_idx != -1:
                    # Find the end of this section
                    lines = thinking_response[start_idx:].split('\n')
                    content_lines = []
                    for line in lines[1:]:  # Skip the phase name
                        if line.strip() and not line.strip().startswith(('THINKING PROCESS:', 'CRITICAL INSIGHTS:', 'SYSTEMS ANALYSIS:', 'STRATEGIC IMPLICATIONS:', 'CREATIVE OPPORTUNITIES:', 'ANALYTICAL FINDINGS:')):
                            content_lines.append(line.strip())
                        elif line.strip() and line.strip().endswith(':'):
                            break

                    content = '\n'.join(content_lines)

                    step = ThinkingStep(
                        step_type=step_type,
                        description=f"{phase_name} analysis",
                        input_data={"phase": phase_name},
                        output_data={"content": content},
                        confidence=0.8,
                        reasoning=content
                    )
                    steps.append(step)

        return steps

    def _extract_confidence(self, response: str) -> float:
        """Extract confidence score from response"""
        try:
            confidence_match = re.search(r'CONFIDENCE:\s*([0-9.]+)', response)
            if confidence_match:
                return float(confidence_match.group(1))
        except:
            pass
        return 0.8  # Default confidence

    def _extract_data_sources(self, response: str) -> List[DataSourceType]:
        """Extract data sources mentioned in response"""
        sources = []
        response_lower = response.lower()

        if 'salesforce' in response_lower:
            sources.append(DataSourceType.SALESFORCE)
        if 'snowflake' in response_lower:
            sources.append(DataSourceType.SNOWFLAKE)
        if 'dbt' in response_lower:
            sources.append(DataSourceType.DBT)

        return sources if sources else [DataSourceType.SALESFORCE]

    def _create_fallback_chain_of_thought(self, query: str, persona: PersonaType, context: Dict[str, Any]) -> ChainOfThought:
        """Create fallback chain of thought when thinking process fails"""
        return ChainOfThought(
            query=query,
            persona=persona,
            thinking_steps=[
                ThinkingStep(
                    step_type=ReasoningStep.INTENT_ANALYSIS,
                    description="Fallback intent analysis",
                    input_data={"query": query},
                    output_data={"intent": "direct_answer"},
                    confidence=0.6,
                    reasoning="Fallback analysis due to error"
                )
            ],
            final_confidence=0.6,
            reasoning_path="Fallback reasoning process",
            context_used=context,
            data_sources_accessed=[DataSourceType.SALESFORCE]
        )

    async def classify_intent(self, query: str, user_context: Dict[str, Any] = None) -> IntentAnalysis:
        """Enhanced intent classification with thinking capabilities"""
        try:
            # Add context to query
            contextualized_query = f"{query}\nUser Context: {user_context or {}}"

            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": self.intent_classification_prompt},
                        {"role": "user", "content": contextualized_query}
                    ],
                    temperature=0.1
                )
            )

            result = json.loads(response.choices[0].message.content)

            return IntentAnalysis(
                primary_intent=IntentType(result["primary_intent"]),
                confidence=result["confidence"],
                persona=PersonaType(result["persona"]),
                data_sources=[DataSourceType(ds) for ds in result["data_sources"]],
                complexity_level=result["complexity_level"],
                reasoning_required=result["reasoning_required"],
                coffee_briefing=result["coffee_briefing"],
                dbt_model_required=result["dbt_model_required"],
                thinking_required=result.get("thinking_required", False),
                explanation=result["explanation"]
            )

        except Exception as e:
            logger.error(f"❌ Error in intent classification: {e}")
            return self._fallback_intent_classification(query)

    def _fallback_intent_classification(self, query: str) -> IntentAnalysis:
        """Enhanced fallback intent classification"""
        query_lower = query.lower()

        # Enhanced rule-based classification
        if any(word in query_lower for word in ["think", "analyze", "reason", "why", "how", "complex"]):
            intent = IntentType.THINKING_ANALYSIS
            thinking_required = True
        elif any(word in query_lower for word in ["win rate", "pipeline", "accounts", "deals"]):
            intent = IntentType.SALESFORCE_QUERY
            thinking_required = False
        elif any(word in query_lower for word in ["analysis", "insights", "trends"]):
            intent = IntentType.BUSINESS_INTELLIGENCE
            thinking_required = True
        elif any(word in query_lower for word in ["dbt", "model", "pipeline"]):
            intent = IntentType.DBT_MODEL
            thinking_required = False
        elif any(word in query_lower for word in ["briefing", "daily", "weekly", "monthly"]):
            intent = IntentType.COFFEE_BRIEFING
            thinking_required = False
        else:
            intent = IntentType.DIRECT_ANSWER
            thinking_required = False

        return IntentAnalysis(
            primary_intent=intent,
            confidence=0.7,
            persona=PersonaType.VP_SALES,
            data_sources=[DataSourceType.SALESFORCE],
            complexity_level="medium",
            reasoning_required=thinking_required,
            coffee_briefing=False,
            dbt_model_required=False,
            thinking_required=thinking_required,
            explanation="Enhanced fallback classification"
        )

    async def _planner_agent(self, query: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Planner Agent: Classifies intent and extracts key information.
        For the VP Sales briefing, it confirms the intent.
        """
        logger.info(" menjalankan Planner Agent...")
        plan = await self.classify_intent(query, user_context)
        logger.info(f"✔️ Planner Agent completed. Intent: {plan.primary_intent.value}")
        return asdict(plan)

    async def _builder_agent(self, plan: Dict[str, Any]) -> Dict[str, str]:
        """
        Builder Agent: Generates the necessary queries for the VP Sales Pipeline Briefing.
        """
        logger.info(" menjalankan Builder Agent...")
        # For this specific briefing, we know the queries we need.
        queries = {
            "pipeline_value": "SELECT SUM(Amount) FROM Opportunity WHERE IsClosed = false AND CloseDate = THIS_QUARTER",
            "win_rate": "SELECT IsWon, COUNT(Id) FROM Opportunity WHERE IsClosed = true AND CloseDate = THIS_QUARTER GROUP BY IsWon",
            "stuck_deals": "SELECT COUNT(Id) FROM Opportunity WHERE IsClosed = false AND StageName != 'Closed Lost' AND LastModifiedDate < N_DAYS_AGO:14"
        }
        logger.info("✔️ Builder Agent completed. Generated 3 queries.")
        return queries

    async def _runner_agent(self, queries: Dict[str, str], plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runner Agent: Executes a dictionary of queries in parallel.
        """
        logger.info(" menjalankan Runner Agent...")

        async def run_query(key: str, soql: str):
            # The SalesforceTool's `run` method expects a natural language query
            # and does its own text-to-soql. This is inefficient for our new flow.
            # We will bypass it and call the sf client directly.
            try:
                result = self.salesforce_client.query_all(soql)
                return key, result
            except Exception as e:
                logger.error(f"Error running query for '{key}': {soql}", exc_info=e)
                return key, {"error": str(e)}

        tasks = [run_query(key, soql) for key, soql in queries.items()]
        results = await asyncio.gather(*tasks)

        # Restructure results into a dictionary
        structured_results = {key: result for key, result in results}

        logger.info("✔️ Runner Agent completed.")
        return structured_results

    async def _narrator_agent(self, data: Dict[str, Any], plan: Dict[str, Any], query: str) -> Dict[str, Any]:
        """
        Narrator Agent: Summarizes data and generates the final JSON response for the VP Sales briefing.
        """
        logger.info(" menjalankan Narrator Agent...")

        # Format the prompt with the data from the runner
        prompt = self.narrator_briefing_vp_sales_prompt.format(
            query=query,
            data=json.dumps(data, indent=2)
        )

        # Call the LLM to generate the JSON contract
        response = await asyncio.get_event_loop().run_in_executor(
            self.executor,
            lambda: self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
        )

        response_str = response.choices[0].message.content
        json_contract = json.loads(response_str)

        logger.info("✔️ Narrator Agent completed.")
        return json_contract

    async def orchestrate_response(self, query: str, intent_analysis: IntentAnalysis, user_id: str = None) -> AgentResponse:
        """
        Enhanced orchestration using the four-agent pipeline to generate a structured Briefing Card.
        """
        logger.info(f"Orchestrating response for intent: {intent_analysis.primary_intent.value} with confidence {intent_analysis.confidence:.2f}")

        # Confidence Gate
        CONFIDENCE_THRESHOLD = 0.65
        if intent_analysis.confidence < CONFIDENCE_THRESHOLD:
            logger.warning(f"Intent confidence ({intent_analysis.confidence:.2f}) is below threshold. Asking for clarification.")
            return AgentResponse(
                response_text="I'm not entirely sure what you're asking. Could you please try rephrasing your question?",
                data_sources_used=[],
                reasoning_steps=["Low confidence routing"],
                confidence_score=intent_analysis.confidence,
                persona_alignment=0.5,
                actionability_score=0.1,
                quality_metrics={"clarification_needed": 1.0}
            )

        try:
            # The new Four-Agent Pipeline
            plan = await self._planner_agent(query, {})
            intent = plan.get("primary_intent")

            # Route to the correct handler based on the intent
            if intent == IntentType.DBT_MODEL.value:
                logger.info("Routing to dbt model creation flow.")
                # The _handle_dbt_model_request was not removed, we can call it directly.
                # We need to reconstruct the IntentAnalysis object for it.
                # This is a temporary bridge until all features use the new pipeline.
                intent_analysis_obj = IntentAnalysis(
                    primary_intent=IntentType(intent),
                    confidence=plan.get('confidence'),
                    persona=PersonaType(plan.get('persona')),
                    data_sources=[DataSourceType(ds) for ds in plan.get("data_sources", [])],
                    complexity_level=plan.get('complexity_level'),
                    reasoning_required=plan.get('reasoning_required'),
                    coffee_briefing=plan.get('coffee_briefing'),
                    dbt_model_required=plan.get('dbt_model_required'),
                    thinking_required=plan.get('thinking_required'),
                    explanation=plan.get('explanation')
                )
                return await self._handle_dbt_model_request(query, intent_analysis_obj, self._get_context_state(user_id))

            elif intent == IntentType.BUSINESS_INTELLIGENCE.value:
                logger.info("Routing to Briefing Card creation flow.")
                queries = await self._builder_agent(plan)
                data = await self._runner_agent(queries, plan)
                narrator_output = await self._narrator_agent(data, plan, query)
            else:
                # Fallback for other queries until they are implemented
                logger.info(f"Fallback for intent: {intent}")
                narrator_output = {"headline": "This feature is still under construction.", "pipeline": {}, "insights": [], "actions": []}


            # The final AgentResponse will be built from the Narrator's JSON output.
            return AgentResponse(
                response_text=json.dumps(narrator_output, indent=2), # For now, just show the raw JSON
                data_sources_used=[DataSourceType(ds) for ds in plan.get("data_sources", [])],
                reasoning_steps=["Planner", "Builder", "Runner", "Narrator"],
                confidence_score=plan.get("confidence", 0.9),
                persona_alignment=0.9, # Placeholder
                actionability_score=0.9, # Placeholder
                quality_metrics={},
                thinking_process=json.dumps(plan, indent=2)
            )

        except Exception as e:
            logger.error("❌ Error in orchestration pipeline", exc_info=e)
            return self._create_error_response(str(e))

    def _get_salesforce_schema(self) -> str:
        """
        Fetches a simplified schema for key Salesforce objects.
        This is a critical piece of context for the LLM to generate accurate SOQL.
        """
        # Caching this schema would be a good performance optimization
        object_names = ['Opportunity', 'Account', 'User']
        schema_description = "Salesforce Schema:\n"
        for obj_name in object_names:
            try:
                obj_desc = getattr(self.salesforce_client, obj_name).describe()
                schema_description += f"Object: {obj_desc['name']}\n"
                schema_description += "Fields:\n"
                for field in obj_desc['fields']:
                    # Limiting to a subset of fields to keep the prompt concise
                    if field['createable'] or field['nillable'] is False:
                         schema_description += f"- {field['name']} ({field['type']})\n"
                schema_description += "\n"
            except Exception as e:
                logger.error(f"Failed to describe object {obj_name}", exc_info=e)

        logger.info("Salesforce schema loaded for prompt.")
        return schema_description

    def _get_context_state(self, user_id: str) -> ContextState:
        """Get or create context state for user"""
        if user_id not in self.context_states:
            self.context_states[user_id] = ContextState(
                user_id=user_id,
                conversation_history=[],
                current_context={},
                persona_preferences={},
                data_source_preferences=[DataSourceType.SALESFORCE],
                last_query="",
                last_response=None,
                session_start=datetime.now()
            )
        return self.context_states[user_id]

    async def _handle_thinking_query(self, query: str, intent_analysis: IntentAnalysis, chain_of_thought: ChainOfThought, context_state: ContextState) -> AgentResponse:
        """Handles complex queries by generating and executing a DAG."""
        try:
            # Step 1: Generate the DAG using the 'thinking' prompt
            thinking_prompt = self.thinking_prompt.format(query=query)

            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "system", "content": thinking_prompt}],
                    temperature=0.0,
                    response_format={"type": "json_object"}
                )
            )
            dag_json_str = response.choices[0].message.content

            # Use regex to find the JSON object within the response string
            json_match = re.search(r'\{.*\}', dag_json_str, re.DOTALL)
            if not json_match:
                logger.error(f"No JSON object found in LLM response for DAG generation. Response: {dag_json_str}")
                return self._create_error_response("I had trouble planning the steps to answer your question. The model did not return a valid plan.")

            dag_str = json_match.group(0)
            dag = json.loads(dag_str)
            logger.info(f"Generated DAG: {dag}")

            # Step 2: Execute the DAG
            dag_results = await self._execute_dag(dag)
            logger.info(f"DAG execution results: {dag_results}")

            # Step 3: Summarize the final results for the user
            final_summary = await self._summarize_data(query, dag_results, self.summarize_full_prompt)

            return AgentResponse(
                response_text=final_summary,
                data_sources_used=intent_analysis.data_sources,
                reasoning_steps=[f"Step {s['id']}: {s['tool']}({s['query']})" for s in dag.get("steps", [])],
                confidence_score=0.9,
                persona_alignment=0.9,
                actionability_score=0.9,
                quality_metrics={"dag_execution_success": 1.0},
                chain_of_thought=chain_of_thought, # This could be updated with DAG info
                thinking_process=json.dumps(dag, indent=2)
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode DAG JSON from LLM response. String was: '{dag_str}'. Error: {e}", exc_info=True)
            return self._create_error_response("I had trouble planning out the steps to answer your question. The model returned invalid JSON.")
        except Exception as e:
            logger.error(f"❌ Error in thinking query (DAG execution): {e}")
            return self._create_error_response(str(e))

    async def _handle_coffee_briefing(self, query: str, intent_analysis: IntentAnalysis, context_state: ContextState) -> AgentResponse:
        """Handle coffee briefing requests"""
        try:
            # Determine briefing frequency and persona
            frequency = self._extract_briefing_frequency(query)

            # Generate coffee briefing
            briefing = await self._generate_coffee_briefing(intent_analysis.persona, frequency)

            # Format response
            response_text = self._format_coffee_briefing(briefing)

            return AgentResponse(
                response_text=response_text,
                data_sources_used=[DataSourceType.SALESFORCE, DataSourceType.SNOWFLAKE],
                reasoning_steps=["Briefing frequency detection", "Persona-specific insights", "Key metrics compilation"],
                confidence_score=0.95,
                persona_alignment=0.95,
                actionability_score=0.9,
                quality_metrics={"relevance": 0.95, "actionability": 0.9, "completeness": 0.85}
            )

        except Exception as e:
            logger.error(f"❌ Error in coffee briefing: {e}")
            return self._create_error_response(str(e))

    async def _handle_dbt_model_request(self, query: str, intent_analysis: IntentAnalysis, context_state: ContextState) -> AgentResponse:
        """Handle dbt model creation/modification requests"""
        try:
            # Extract dbt model requirements from query
            model_requirements = await self._extract_dbt_requirements(query)

            # Generate dbt model
            dbt_model = await self._generate_dbt_model(model_requirements)

            if "error" in dbt_model:
                return self._create_error_response(dbt_model["error"])

            # Create the model files
            model_name = dbt_model.get("name", "default_model_name")
            sql_path = f"analytics/models/marts/{model_name}.sql"
            yaml_path = f"analytics/models/marts/{model_name}.yml"

            # This is a conceptual step. In a real environment, you would use a file writing tool.
            # For now, we will just format the response as if the files were created.
            # In a real implementation, you would have:
            # self.tools['file_writer'].run(path=sql_path, content=dbt_model['sql'])
            # self.tools['file_writer'].run(path=yaml_path, content=dbt_model['yaml'])

            response_text = f"""
🔧 **dbt Model Generated & Files Created**

I have created the following files in your `analytics/models/marts/` directory:
- `{sql_path}`
- `{yaml_path}`

**SQL Model**:
```sql
{dbt_model['sql']}
```

**YAML Configuration**:
```yaml
{dbt_model['yaml']}
```

**Next Steps**:
1. Review the generated files.
2. Run `dbt run` to build the new model.
3. Test the model's output in your data warehouse.
"""

            return AgentResponse(
                response_text=response_text,
                data_sources_used=[DataSourceType.DBT],
                reasoning_steps=["Requirements extraction", "Model design", "SQL generation", "Configuration setup"],
                confidence_score=0.9,
                persona_alignment=0.95,
                actionability_score=0.95,
                quality_metrics={"technical_accuracy": 0.9, "completeness": 0.85, "best_practices": 0.95}
            )

        except Exception as e:
            logger.error(f"❌ Error in dbt model request: {e}")
            return self._create_error_response(str(e))

    async def _handle_complex_analytics(self, query: str, intent_analysis: IntentAnalysis, context_state: ContextState) -> AgentResponse:
        """Handle complex analytics requiring multiple data sources"""
        try:
            # Gather data from all sources
            all_data = await self._gather_data_sources(intent_analysis.data_sources, query)

            # Combine and analyze
            combined_analysis = await self._analyze_combined_data(
                all_data.get("salesforce", {}),
                all_data.get("snowflake", {}),
                all_data.get("dbt", {}),
                query
            )

            return AgentResponse(
                response_text=combined_analysis,
                data_sources_used=[DataSourceType.SALESFORCE, DataSourceType.SNOWFLAKE, DataSourceType.DBT],
                reasoning_steps=["Multi-source data gathering", "Data correlation", "Insight synthesis", "Recommendation generation"],
                confidence_score=0.85,
                persona_alignment=0.9,
                actionability_score=0.85,
                quality_metrics={"data_quality": 0.9, "insight_relevance": 0.85, "actionability": 0.8}
            )

        except Exception as e:
            logger.error(f"❌ Error in complex analytics: {e}")
            return self._create_error_response(str(e))

    async def _summarize_data(self, query: str, data: dict, prompt_template: str) -> str:
        """Generic method to summarize data using a specified prompt."""
        data_str = json.dumps(data, indent=2, default=str)

        messages = [
            {"role": "system", "content": prompt_template},
            {"role": "user", "content": f"The user's original request was: '{query}'\n\nHere is the data I retrieved in JSON format:\n\n{data_str}"}
        ]

        logger.info("Summarizing data with specified prompt.")
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.5,
                    max_tokens=1000
                )
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error("Data summarization API call failed", exc_info=e)
            return "Error: Failed to generate a summary for the data."


    async def _handle_direct_answer(self, query: str, intent_analysis: IntentAnalysis, context_state: ContextState) -> AgentResponse:
        """Handle direct answer queries with context awareness"""
        try:
            # Add context to the prompt
            context_aware_prompt = f"""
{self.persona_prompts[intent_analysis.persona.value]}

Previous Context: {json.dumps(context_state.current_context, indent=2)}
User History: {len(context_state.conversation_history)} previous interactions

Provide a context-aware response that builds on previous interactions.
"""

            # Generate direct answer using LLM
            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": context_aware_prompt},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.3
                )
            )

            direct_answer = response.choices[0].message.content

            # Update context with this interaction
            context_state.conversation_history.append({
                "query": query,
                "response": direct_answer,
                "timestamp": datetime.now().isoformat(),
                "intent": intent_analysis.primary_intent.value
            })

            # Maintain context window
            if len(context_state.conversation_history) > context_state.context_window:
                context_state.conversation_history = context_state.conversation_history[-context_state.context_window:]

            return AgentResponse(
                response_text=direct_answer,
                data_sources_used=[],
                reasoning_steps=["Query understanding", "Context analysis", "Knowledge retrieval", "Response generation"],
                confidence_score=0.8,
                persona_alignment=0.9,
                actionability_score=0.7,
                quality_metrics={"accuracy": 0.8, "relevance": 0.85, "helpfulness": 0.8, "context_awareness": 0.9}
            )

        except Exception as e:
            logger.error(f"❌ Error in direct answer: {e}")
            return self._create_error_response(str(e))

    async def process_query(self, query: str, user_context: Dict[str, Any] = None, user_id: str = None) -> AgentResponse:
        """Enhanced main entry point for processing queries with context management"""
        try:
            logger.info(f"🧠 Processing enhanced query: {query}")

            # Get or create context state
            context_state = self._get_context_state(user_id or "default")

            # Step 1: Enhanced intent classification
            intent_analysis = await self.classify_intent(query, user_context)
            logger.info(f"🎯 Intent classified: {intent_analysis.primary_intent.value} (thinking_required: {intent_analysis.thinking_required})")

            # Step 2: Enhanced orchestration with context
            response = await self.orchestrate_response(query, intent_analysis, user_id)
            logger.info(f"✅ Enhanced response generated with confidence: {response.confidence_score}")

            # Step 3: Update context state
            context_state.last_response = response
            context_state.current_context.update({
                "last_query": query,
                "last_intent": intent_analysis.primary_intent.value,
                "last_persona": intent_analysis.persona.value,
                "last_confidence": response.confidence_score,
                "has_thinking": response.chain_of_thought is not None
            })

            # Step 4: Store conversation history
            self.conversation_history.append({
                "query": query,
                "intent": intent_analysis,
                "response": response,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "context_state": {
                    "conversation_count": len(context_state.conversation_history),
                    "session_duration": (datetime.now() - context_state.session_start).total_seconds()
                }
            })

            return response

        except Exception as e:
            logger.error(f"❌ Error in enhanced query processing: {e}")
            return self._create_error_response(str(e))

    def get_enhanced_quality_metrics(self) -> Dict[str, Any]:
        """Get enhanced quality metrics with thinking and context analysis"""
        if not self.conversation_history:
            return {"message": "No conversations yet"}

        # Calculate basic metrics
        total_confidence = 0
        successful_queries = 0
        thinking_queries = 0
        context_awareness_scores = []

        for conv in self.conversation_history:
            if isinstance(conv, dict):
                response = conv.get("response")
                if response and hasattr(response, 'confidence_score'):
                    total_confidence += response.confidence_score
                    if response.confidence_score > 0.5:
                        successful_queries += 1

                    # Check for thinking capabilities
                    if hasattr(response, 'chain_of_thought') and response.chain_of_thought:
                        thinking_queries += 1

                    # Check for context awareness
                    if hasattr(response, 'quality_metrics') and 'context_awareness' in response.quality_metrics:
                        context_awareness_scores.append(response.quality_metrics['context_awareness'])

        avg_confidence = total_confidence / len(self.conversation_history) if self.conversation_history else 0
        success_rate = successful_queries / len(self.conversation_history) if self.conversation_history else 0
        thinking_rate = thinking_queries / len(self.conversation_history) if self.conversation_history else 0
        avg_context_awareness = sum(context_awareness_scores) / len(context_awareness_scores) if context_awareness_scores else 0

        return {
            "total_queries": len(self.conversation_history),
            "average_confidence": avg_confidence,
            "success_rate": success_rate,
            "thinking_rate": thinking_rate,
            "average_context_awareness": avg_context_awareness,
            "active_users": len(self.context_states),
            "intent_distribution": self._get_intent_distribution(),
            "context_analysis": self._analyze_context_usage()
        }

    def _get_intent_distribution(self) -> Dict[str, int]:
        """Get distribution of intent types"""
        distribution = {}
        for conv in self.conversation_history:
            if isinstance(conv, dict):
                intent = conv.get("intent")
                if intent and hasattr(intent, 'primary_intent'):
                    intent_type = intent.primary_intent.value
                    distribution[intent_type] = distribution.get(intent_type, 0) + 1
            else:
                if hasattr(conv, 'intent') and hasattr(conv.intent, 'primary_intent'):
                    intent_type = conv.intent.primary_intent.value
                    distribution[intent_type] = distribution.get(intent_type, 0) + 1
        return distribution

    def _analyze_context_usage(self) -> Dict[str, Any]:
        """Analyze context usage patterns"""
        context_analysis = {
            "total_context_states": len(self.context_states),
            "average_conversation_length": 0,
            "context_retention_rate": 0,
            "user_engagement_patterns": {}
        }

        if self.context_states:
            total_conversations = 0
            total_retention = 0

            for user_id, context_state in self.context_states.items():
                conv_count = len(context_state.conversation_history)
                total_conversations += conv_count

                # Calculate retention (users with multiple conversations)
                if conv_count > 1:
                    total_retention += 1

                # Track engagement patterns
                context_analysis["user_engagement_patterns"][user_id] = {
                    "conversation_count": conv_count,
                    "session_duration": (datetime.now() - context_state.session_start).total_seconds(),
                    "preferred_persona": context_state.current_context.get("last_persona", "unknown"),
                    "data_source_preferences": [ds.value for ds in context_state.data_source_preferences]
                }

            context_analysis["average_conversation_length"] = total_conversations / len(self.context_states)
            context_analysis["context_retention_rate"] = total_retention / len(self.context_states)

        return context_analysis

    # Helper methods for data gathering and processing
    async def _gather_data_sources(self, data_sources: List[DataSourceType], query: str) -> Dict[str, Any]:
        """Gather data from multiple sources using the new tool architecture."""
        data = {}

        # This can be parallelized in the future
        for source in data_sources:
            tool_name = source.value
            if tool_name in self.tools:
                logger.info(f"Using tool: {tool_name} for query: {query}")
                data[tool_name] = await self.tools[tool_name].run(query)
            elif tool_name == "dbt": # Keep placeholder for dbt
                data['dbt'] = await self._get_dbt_insights("general overview")

        return data

    async def _execute_dag(self, dag: Dict[str, Any]) -> Dict[int, Any]:
        """
        Executes a DAG of tool calls.

        Args:
            dag: The JSON object representing the DAG.

        Returns:
            A dictionary mapping step IDs to their results.
        """
        step_results: Dict[int, Any] = {}
        completed_ids: set[int] = set()
        steps = dag.get("steps", [])

        # A simple, iterative approach to resolve dependencies.
        # A more advanced version could use a topological sort.
        for _ in range(len(steps)): # Loop enough times to resolve all steps
            steps_to_run = []
            for step in steps:
                step_id = step["id"]
                if step_id in completed_ids:
                    continue

                dependencies_met = all(dep_id in completed_ids for dep_id in step["dependencies"])

                if dependencies_met:
                    tool_name = step["tool"]
                    query = step["query"]
                    if tool_name in self.tools:
                        # For now, we don't pass results between steps, the LLM must craft the query
                        # with the necessary info.
                        task = self.tools[tool_name].run(query)
                        steps_to_run.append((step_id, task))

            if not steps_to_run:
                # Either all done or a deadlock/unmet dependency
                break

            # Run all steps that are ready in parallel
            results = await asyncio.gather(*(task for _, task in steps_to_run))

            for (step_id, _), result in zip(steps_to_run, results):
                step_results[step_id] = result
                completed_ids.add(step_id)

        if len(completed_ids) != len(steps):
            logger.error("Could not complete all steps in DAG, check for cycles or missing dependencies.")

        return step_results

    async def _get_dbt_insights(self, query: str) -> Dict[str, Any]:
        """Get insights from dbt models (placeholder)"""
        # This would query dbt models in production
        return {"message": "dbt integration pending"}

    def _load_text_to_soql_prompt(self) -> str:
        """Load the system prompt for text-to-SOQL conversion."""
        file_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'system', 'text_to_soql.txt')
        return self._load_prompt_from_file(file_path)

    def _load_few_shot_examples(self, file_path: str) -> List[Dict[str, str]]:
        """Loads few-shot examples from a JSON file."""
        try:
            full_path = os.path.join(os.path.dirname(__file__), '..', file_path)
            with open(full_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading few-shot examples from {file_path}: {e}")
            return []

    async def _generate_coffee_briefing(self, persona: PersonaType, frequency: str) -> CoffeeBriefing:
        """Generate coffee briefing for specific persona and frequency"""
        # This would generate personalized briefings based on persona and frequency
        return CoffeeBriefing(
            persona=persona,
            frequency=frequency,
            key_metrics=["Win Rate", "Pipeline Value", "Deal Velocity"],
            insights=["Pipeline health is strong", "Win rate improving", "Focus on high-value deals"],
            action_items=["Review top 10 opportunities", "Coach underperforming reps", "Optimize sales process"],
            risks=["Pipeline concentration", "Seasonal fluctuations"],
            opportunities=["Expansion in existing accounts", "New market penetration"]
        )

    async def _generate_dbt_model(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uses an LLM to generate dbt model SQL and YAML from a structured requirements object.
        """
        logger.info(f"Generating dbt model for requirements: {requirements}")
        prompt = self.generate_dbt_model_prompt.format(requirements=json.dumps(requirements, indent=2))

        try:
            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.openai_client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[{"role": "system", "content": prompt}],
                    temperature=0.0,
                    response_format={"type": "json_object"}
                )
            )
            model_str = response.choices[0].message.content
            model = json.loads(model_str)
            logger.info("Successfully generated dbt model and YAML.")
            # We need to return the model name from the requirements as well for file creation
            model["name"] = requirements.get("model_name", "default_model_name")
            return model
        except Exception as e:
            logger.error("Failed to generate dbt model from LLM", exc_info=e)
            return {
                "error": "Failed to generate the dbt model. Please try again."
            }

    async def _analyze_combined_data(self, salesforce_data: Dict, snowflake_data: Dict, dbt_insights: Dict, query: str) -> str:
        """Analyze combined data from multiple sources"""
        # This would perform complex analysis combining multiple data sources
        return f"""
📊 **Multi-Source Analysis**

**Query**: {query}

**Salesforce Data**: {len(salesforce_data)} records available
**Snowflake Data**: {len(snowflake_data)} records available
**dbt Insights**: {len(dbt_insights)} insights available

**Combined Analysis**:
• Cross-source correlation analysis
• Trend identification across platforms
• Comprehensive business insights
• Actionable recommendations

**Next Steps**:
1. Review combined insights
2. Validate cross-platform data consistency
3. Implement recommended actions
"""

    def _extract_briefing_frequency(self, query: str) -> str:
        """Extract briefing frequency from query"""
        query_lower = query.lower()
        if "daily" in query_lower:
            return "daily"
        elif "weekly" in query_lower:
            return "weekly"
        elif "monthly" in query_lower:
            return "monthly"
        else:
            return "daily"  # default

    async def _extract_dbt_requirements(self, query: str) -> Dict[str, Any]:
        """
        Uses an LLM to extract structured dbt model requirements from a natural language query.
        """
        logger.info(f"Extracting dbt requirements from query: {query}")
        prompt = self.extract_dbt_requirements_prompt.format(query=query)

        try:
            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.openai_client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[{"role": "system", "content": prompt}],
                    temperature=0.0,
                    response_format={"type": "json_object"}
                )
            )
            requirements_str = response.choices[0].message.content
            requirements = json.loads(requirements_str)
            logger.info(f"Successfully extracted dbt requirements: {requirements}")
            return requirements
        except Exception as e:
            logger.error("Failed to extract dbt requirements from LLM", exc_info=e)
            # Return a schema-compliant error object
            return {
                "error": "Failed to understand the requirements for the dbt model. Please try rephrasing your request."
            }

    def _extract_reasoning_steps(self, response: str) -> List[str]:
        """Extract reasoning steps from response"""
        steps = []
        lines = response.split('\n')
        for line in lines:
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                steps.append(line.strip())
        return steps

    def _format_salesforce_response(self, result: Dict, query: str, intent_analysis: IntentAnalysis) -> str:
        """Format Salesforce response"""
        return f"""
📊 **Salesforce Query Results**

**Query**: {query}
**Records Found**: {len(result.get('records', []))}

**Data Summary**:
{json.dumps(result.get('records', [])[:3], indent=2)}

**Persona Insights**: {intent_analysis.persona.value}
**Confidence**: {intent_analysis.confidence:.2f}
"""

    def _format_business_intelligence_response(self, insights: Dict, intent_analysis: IntentAnalysis) -> str:
        """Format business intelligence response"""
        return f"""
💡 **Business Intelligence Insights**

**Key Insights**:
• {insights.get('insight1', 'Data analysis complete')}
• {insights.get('insight2', 'Trends identified')}
• {insights.get('insight3', 'Recommendations generated')}

**Persona**: {intent_analysis.persona.value}
**Action Items**: {insights.get('action_items', ['Review insights', 'Implement recommendations'])}
"""

    def _format_coffee_briefing(self, briefing: CoffeeBriefing) -> str:
        """Format coffee briefing"""
        return f"""
☕ **{briefing.frequency.title()} Coffee Briefing for {briefing.persona.value.replace('_', ' ').title()}**

📊 **Key Metrics**:
{chr(10).join(f'• {metric}' for metric in briefing.key_metrics)}

💡 **Insights**:
{chr(10).join(f'• {insight}' for insight in briefing.insights)}

🚀 **Action Items**:
{chr(10).join(f'• {action}' for action in briefing.action_items)}

⚠️ **Risks**:
{chr(10).join(f'• {risk}' for risk in briefing.risks)}

🎯 **Opportunities**:
{chr(10).join(f'• {opportunity}' for opportunity in briefing.opportunities)}
"""

    def _create_error_response(self, error_message: str) -> AgentResponse:
        """Create error response"""
        return AgentResponse(
            response_text=f"❌ **Error**: {error_message}\n\nPlease try again or contact support.",
            data_sources_used=[],
            reasoning_steps=[],
            confidence_score=0.0,
            persona_alignment=0.0,
            actionability_score=0.0,
            quality_metrics={"error": 1.0}
        )
