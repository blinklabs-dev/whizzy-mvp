import os
import json
import asyncio
import logging
from typing import List, Dict, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import openai
import structlog
from concurrent.futures import ThreadPoolExecutor, as_completed
from dynamic_dbt_generator import DynamicDbtGenerator
from real_dbt_executor import RealDbtExecutor
from real_snowflake_mcp import RealSnowflakeMCP
from cost_optimized_llm import get_llm_manager

# Configure structured logging
logger = structlog.get_logger()

class AgentType(Enum):
    """All available agent types in the DAG"""
    INTENT_ROUTER = "intent_router"
    SOQL_GENERATOR = "soql_generator"
    DBT_SELECTOR = "dbt_selector"
    DATA_FETCHER = "data_fetcher"
    DBT_EXECUTOR = "dbt_executor"
    SNOWFLAKE_MCP = "snowflake_mcp"
    DYNAMIC_DBT_GENERATOR = "dynamic_dbt_generator"
    CONTEXT_BUILDER = "context_builder"
    SCHEMA_ANALYZER = "schema_analyzer"
    DATA_FUSION = "data_fusion"
    RESPONSE_GENERATOR = "response_generator"
    ERROR_HANDLER = "error_handler"

class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class AgentNode:
    """Represents a node in the DAG"""
    agent_type: AgentType
    agent: 'BaseAgent'
    dependencies: Set[AgentType] = field(default_factory=set)
    dependents: Set[AgentType] = field(default_factory=set)
    status: ExecutionStatus = ExecutionStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None

@dataclass
class DAGContext:
    """Context that flows through the DAG"""
    user_query: str
    conversation_history: List[Dict[str, str]]
    salesforce_schema: str
    execution_id: str
    
    # Agent outputs
    intent: Optional[str] = None
    confidence: float = 0.0
    reasoning: str = ""
    user_persona: str = "general"
    
    # Data outputs
    soql_queries: List[str] = field(default_factory=list)
    salesforce_data: Dict[str, Any] = field(default_factory=dict)
    dbt_models: List[str] = field(default_factory=list)
    dbt_data: Dict[str, Any] = field(default_factory=dict)
    snowflake_data: Dict[str, Any] = field(default_factory=dict)
    dynamic_dbt_data: Dict[str, Any] = field(default_factory=dict)
    context_data: Dict[str, Any] = field(default_factory=dict)
    
    # Final outputs
    fused_data: Optional[Dict[str, Any]] = None
    final_response: Optional[str] = None
    
    # Metadata
    execution_path: List[AgentType] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

class BaseAgent(ABC):
    """Base class for all agents in the DAG"""
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    @abstractmethod
    async def execute(self, context: DAGContext) -> DAGContext:
        """Execute the agent's logic"""
        pass
    
    def _call_llm(self, messages: List[Dict], temperature: float = 0.1, max_tokens: int = 1000, task_type: str = "balanced") -> str:
        """Make LLM call with cost optimization"""
        try:
            llm_manager = get_llm_manager()
            return llm_manager.call_llm(messages, task_type, max_tokens).strip()
        except Exception as e:
            logger.error(f"LLM call failed for {self.agent_type.value}", error=str(e))
            raise

class IntentRouterAgent(BaseAgent):
    """Routes user intent and determines execution path"""
    
    def __init__(self):
        super().__init__(AgentType.INTENT_ROUTER)
    
    async def execute(self, context: DAGContext) -> DAGContext:
        system_prompt = """
You are an intelligent intent router that determines the optimal execution path for user queries.

**Available Execution Paths:**
1. **SIMPLE_QUERY**: Direct Salesforce data retrieval
2. **ANALYTICS_DEEP**: Complex analysis with multiple data sources
3. **EXECUTIVE_BRIEFING**: Executive-level insights with forecasting
4. **HELP_REQUEST**: Capabilities and guidance
5. **CONVERSATIONAL**: Casual interaction

**Routing Logic:**
- Executive terms (vp, executive, briefing) → EXECUTIVE_BRIEFING
- Analysis terms (analyze, insights, trends) → ANALYTICS_DEEP
- Specific data requests → SIMPLE_QUERY
- Help/info requests → HELP_REQUEST
- Greetings/casual → CONVERSATIONAL

Return JSON: {"intent": "...", "confidence": 0.95, "execution_path": ["agent1", "agent2"], "reasoning": "..."}
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Query: {context.user_query}\nHistory: {context.conversation_history}"}
        ]
        
        response = self._call_llm(messages, task_type="intent_classification")
        result = json.loads(response)
        
        context.intent = result["intent"]
        context.confidence = result["confidence"]
        context.reasoning = result["reasoning"]
        context.execution_path = result.get("execution_path", [])
        
        logger.info("Intent routed", intent=context.intent, confidence=context.confidence, path=context.execution_path)
        return context

class SOQLGeneratorAgent(BaseAgent):
    """Generates SOQL queries based on intent"""
    
    def __init__(self):
        super().__init__(AgentType.SOQL_GENERATOR)
    
    async def execute(self, context: DAGContext) -> DAGContext:
        if context.intent in ["HELP_REQUEST", "CONVERSATIONAL"]:
            return context  # Skip SOQL generation
        
        system_prompt = f"""
Generate optimal SOQL queries for: {context.intent}

**Schema Available:**
{context.salesforce_schema}

**Salesforce SOQL Guidelines:**
- Use LIMIT clauses for large datasets
- Handle null values appropriately
- Use relationship queries: SELECT Id, Name, Account.Name, Account.AnnualRevenue FROM Opportunity
- NEVER use INNER JOIN or JOIN syntax
- Use proper field references: Account.Name, Account.AnnualRevenue, Owner.Name
- For Account data: SELECT Id, Name, AnnualRevenue, Industry FROM Account
- For Opportunity data: SELECT Id, Name, Amount, StageName, CloseDate, IsWon, IsClosed, AccountId FROM Opportunity
- For User data: SELECT Id, Name FROM User

**Example Valid Queries:**
- SELECT Id, Name, AnnualRevenue FROM Account ORDER BY AnnualRevenue DESC LIMIT 10
- SELECT Id, Name, Amount, Account.Name, Account.AnnualRevenue FROM Opportunity WHERE IsClosed = true
- SELECT Id, Name, (SELECT Id, Name FROM Opportunities) FROM Account

Return JSON array of queries: [{{"name": "...", "soql": "...", "purpose": "..."}}]
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Query: {context.user_query}\nIntent: {context.intent}"}
        ]
        
        response = self._call_llm(messages, task_type="soql_generation")
        queries = json.loads(response)
        
        context.soql_queries = [q["soql"] for q in queries]
        logger.info("SOQL generated", query_count=len(context.soql_queries))
        return context

class DBTSelectorAgent(BaseAgent):
    """Selects relevant DBT models"""
    
    def __init__(self):
        super().__init__(AgentType.DBT_SELECTOR)
        self.available_models = [
            # Marts (Core business metrics)
            "m_forecast", "m_slippage_impact_quarter", "m_stage_velocity_quarter",
            "m_pipeline_health", "m_deal_velocity_analysis", "m_revenue_forecasting",
            
            # Analytics (Advanced insights)
            "a_win_rate_trend_analysis", "a_slippage_pattern_analysis", 
            "a_comprehensive_slippage_analysis", "a_win_rate_by_owner", 
            "a_win_rate_by_industry", "a_executive_dashboard"
        ]
    
    async def execute(self, context: DAGContext) -> DAGContext:
        if context.intent not in ["ANALYTICS_DEEP", "EXECUTIVE_BRIEFING"]:
            return context  # Skip DBT selection
        
        system_prompt = f"""
Select relevant DBT models for: {context.intent}

**Available Models:**
{self.available_models}

**Selection Guidelines:**
- Executive briefings: m_pipeline_health + a_executive_dashboard + m_revenue_forecasting
- Slippage analysis: m_slippage_impact_quarter + a_slippage_pattern_analysis
- Performance analysis: a_win_rate_by_owner + a_win_rate_by_industry
- Pipeline health: m_pipeline_health + m_deal_velocity_analysis
- Revenue forecasting: m_revenue_forecasting + m_forecast
- Deal velocity: m_deal_velocity_analysis + m_stage_velocity_quarter

Return JSON: {{"models": ["model1", "model2"], "reasoning": "..."}}
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Query: {context.user_query}\nIntent: {context.intent}"}
        ]
        
        response = self._call_llm(messages, task_type="dbt_generation")
        result = json.loads(response)
        
        context.dbt_models = result["models"]
        logger.info("DBT models selected", models=context.dbt_models)
        return context

class DataFetcherAgent(BaseAgent):
    """Executes SOQL queries against Salesforce"""
    
    def __init__(self):
        super().__init__(AgentType.DATA_FETCHER)
        from simple_salesforce import Salesforce
        self.sf = Salesforce(
            username=os.getenv("SALESFORCE_USERNAME"),
            password=os.getenv("SALESFORCE_PASSWORD"),
            security_token=os.getenv("SALESFORCE_SECURITY_TOKEN")
        )
    
    async def execute(self, context: DAGContext) -> DAGContext:
        if not context.soql_queries:
            return context
        
        # Execute queries in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_query = {
                executor.submit(self._execute_query, query): query 
                for query in context.soql_queries
            }
            
            for future in as_completed(future_to_query):
                query = future_to_query[future]
                try:
                    result = future.result()
                    context.salesforce_data[query] = result
                except Exception as e:
                    context.errors.append(f"Query failed: {str(e)}")
                    logger.error("Query execution failed", query=query, error=str(e))
        
        logger.info("Data fetched", query_count=len(context.salesforce_data))
        return context
    
    def _execute_query(self, query: str) -> Dict:
        """Execute a single SOQL query"""
        result = self.sf.query_all(query)
        return {
            "records": result['records'],
            "totalSize": result['totalSize'],
            "done": result['done']
        }

class DBTExecutorAgent(BaseAgent):
    """Executes DBT models with real Snowflake integration"""
    
    def __init__(self):
        super().__init__(AgentType.DBT_EXECUTOR)
        try:
            self.dbt_executor = RealDbtExecutor()
            self.real_execution = True
            logger.info("Real DBT executor initialized")
        except Exception as e:
            logger.warning("Real DBT executor failed, using simulation", error=str(e))
            self.real_execution = False
    
    async def execute(self, context: DAGContext) -> DAGContext:
        if not context.dbt_models:
            return context
        
        if self.real_execution:
            # Real DBT execution
            try:
                dbt_results = await self.dbt_executor.execute_multiple_models(context.dbt_models)
                context.dbt_data = dbt_results
                logger.info("Real DBT models executed", model_count=len(context.dbt_models))
            except Exception as e:
                logger.error("Real DBT execution failed, falling back to simulation", error=str(e))
                # Fallback to simulation
                dbt_results = self._simulate_dbt_execution(context.dbt_models)
                context.dbt_data = dbt_results
        else:
            # Simulated DBT execution
            dbt_results = self._simulate_dbt_execution(context.dbt_models)
            context.dbt_data = dbt_results
        
        return context
    
    def _simulate_dbt_execution(self, models: List[str]) -> Dict[str, Any]:
        """Simulate DBT model execution"""
        dbt_results = {}
        for model in models:
            dbt_results[model] = {
                "status": "success",
                "rows_affected": 100,  # Simulated
                "execution_time": "2.5s",  # Simulated
                "data_preview": {
                    "total_records": 100,
                    "sample_data": [
                        {"metric": "value1", "count": 50},
                        {"metric": "value2", "count": 30},
                        {"metric": "value3", "count": 20}
                    ]
                }
            }
        return dbt_results

class SnowflakeMCPAgent(BaseAgent):
    """Real Snowflake MCP agent for complex analytics"""
    
    def __init__(self):
        super().__init__(AgentType.SNOWFLAKE_MCP)
        try:
            self.snowflake_mcp = RealSnowflakeMCP()
            self.real_execution = True
            logger.info("Real Snowflake MCP initialized")
        except Exception as e:
            logger.warning("Real Snowflake MCP failed, using simulation", error=str(e))
            self.real_execution = False
    
    async def execute(self, context: DAGContext) -> DAGContext:
        if context.intent not in ["ANALYTICS_DEEP", "EXECUTIVE_BRIEFING"]:
            return context
        
        if self.real_execution:
            try:
                # Real Snowflake analytics execution
                result = await self.snowflake_mcp.execute_complex_analytics(
                    context.intent, 
                    context.dbt_models
                )
                context.snowflake_data = result
                logger.info("Real Snowflake analytics executed", 
                           intent=context.intent, 
                           total_rows=result.get("total_rows", 0))
            except Exception as e:
                logger.error("Real Snowflake execution failed, falling back to simulation", error=str(e))
                # Fallback to simulation
                context.snowflake_data = self._simulate_snowflake_execution(context)
        else:
            # Simulated Snowflake execution
            context.snowflake_data = self._simulate_snowflake_execution(context)
        
        return context
    
    def _simulate_snowflake_execution(self, context: DAGContext) -> Dict[str, Any]:
        """Simulate Snowflake execution"""
        return {
            "query": "Simulated complex analytics query",
            "result": {
                "forecast_accuracy": 0.87,
                "slippage_trend": -0.12,
                "win_rate_volatility": 0.08,
                "revenue_forecast": 1250000,
                "risk_deals": 15
            },
            "status": "success"
        }


class DynamicDbtGeneratorAgent(BaseAgent):
    """Dynamic DBT model generator agent"""
    
    def __init__(self):
        super().__init__(AgentType.DYNAMIC_DBT_GENERATOR)
        self.dbt_generator = DynamicDbtGenerator()
    
    async def execute(self, context: DAGContext) -> DAGContext:
        # Only run for complex analytics requests
        if context.intent not in ["ANALYTICS_DEEP", "EXECUTIVE_BRIEFING"]:
            return context
        
        try:
            # Check if existing DBT models can handle the request
            if context.dbt_models and len(context.dbt_models) > 0:
                logger.info("Using existing DBT models", models=context.dbt_models)
                return context
            
            # Analyze if we need a new model
            context_dict = {
                "user_persona": context.user_persona,
                "intent": context.intent,
                "existing_models": context.dbt_models
            }
            
            result = await self.dbt_generator.process_complex_analytics_request(
                context.user_query, 
                context_dict
            )
            
            if result["action"] == "new_model_created":
                context.dynamic_dbt_data = {
                    "new_model_created": True,
                    "model_name": result["model_name"],
                    "model_description": result["model_description"],
                    "execution_result": result["execution_result"],
                    "message": result["message"]
                }
                
                # Add the new model to the DBT models list
                context.dbt_models.append(result["model_name"])
                
                logger.info("New DBT model created", 
                           model_name=result["model_name"],
                           description=result["model_description"])
            else:
                context.dynamic_dbt_data = {
                    "new_model_created": False,
                    "message": result.get("message", "No new model needed")
                }
                
        except Exception as e:
            logger.error("Dynamic DBT generation failed", error=str(e))
            context.dynamic_dbt_data = {"error": str(e)}
        
        return context

class DataFusionAgent(BaseAgent):
    """Fuses data from multiple sources"""
    
    def __init__(self):
        super().__init__(AgentType.DATA_FUSION)
    
    async def execute(self, context: DAGContext) -> DAGContext:
        system_prompt = """
Fuse data from Salesforce and DBT models into a comprehensive analysis.

**Fusion Guidelines:**
- Combine real-time Salesforce data with historical DBT insights
- Identify patterns and correlations
- Create executive-level summaries
- Highlight key metrics and trends

Return JSON: {"summary": "...", "key_metrics": {...}, "insights": [...], "recommendations": [...]}
"""
        
        # Limit data size to avoid rate limits
        salesforce_summary = str(context.salesforce_data)[:800] if context.salesforce_data else "No Salesforce data"
        dbt_summary = str(context.dbt_data)[:800] if context.dbt_data else "No DBT data"
        snowflake_summary = str(context.snowflake_data)[:800] if context.snowflake_data else "No Snowflake data"
        dynamic_dbt_summary = str(context.dynamic_dbt_data)[:800] if context.dynamic_dbt_data else "No dynamic DBT data"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Salesforce: {salesforce_summary}\nDBT: {dbt_summary}\nSnowflake: {snowflake_summary}\nDynamic DBT: {dynamic_dbt_summary}\nIntent: {context.intent}"}
        ]
        
        try:
            response = self._call_llm(messages, max_tokens=800, task_type="data_analysis")
            fused_data = json.loads(response)
            context.fused_data = fused_data
            logger.info("Data fused", summary_length=len(fused_data.get("summary", "")))
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            context.fused_data = {
                "summary": response[:500],
                "key_metrics": {},
                "insights": [],
                "recommendations": []
            }
            logger.warning("JSON parsing failed, using fallback response")
        except Exception as e:
            logger.error("Data fusion failed", error=str(e))
            context.fused_data = {
                "summary": "Unable to fuse data due to technical issues",
                "key_metrics": {},
                "insights": [],
                "recommendations": []
            }
        
        return context

class ResponseGeneratorAgent(BaseAgent):
    """Generates final user response"""
    
    def __init__(self):
        super().__init__(AgentType.RESPONSE_GENERATOR)
    
    async def execute(self, context: DAGContext) -> DAGContext:
        system_prompt = """
Generate a natural, conversational response based on the fused data and user intent.

**Response Guidelines:**
- Be concise and actionable
- Use natural language, not technical jargon
- Include key insights and metrics
- Provide context and recommendations when appropriate
- Handle errors gracefully

**Response Style:**
- Executive briefings: High-level insights with strategic recommendations
- Analytics: Detailed analysis with specific metrics
- Simple queries: Direct answers with context
- Help requests: Comprehensive capabilities overview
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Intent: {context.intent}\nFused Data: {context.fused_data}\nOriginal Query: {context.user_query}"}
        ]
        
        response = self._call_llm(messages, task_type="executive_briefing")
        context.final_response = response
        
        logger.info("Response generated", response_length=len(response))
        return context

class MultiAgentDAG:
    """Main DAG orchestrator"""
    
    def __init__(self):
        self.agents = {
            AgentType.INTENT_ROUTER: IntentRouterAgent(),
            AgentType.SOQL_GENERATOR: SOQLGeneratorAgent(),
            AgentType.DBT_SELECTOR: DBTSelectorAgent(),
            AgentType.DATA_FETCHER: DataFetcherAgent(),
            AgentType.DBT_EXECUTOR: DBTExecutorAgent(),
            AgentType.SNOWFLAKE_MCP: SnowflakeMCPAgent(),
            AgentType.DYNAMIC_DBT_GENERATOR: DynamicDbtGeneratorAgent(),
            AgentType.DATA_FUSION: DataFusionAgent(),
            AgentType.RESPONSE_GENERATOR: ResponseGeneratorAgent(),
        }
        
        # Define DAG dependencies
        self.dependencies = {
            AgentType.INTENT_ROUTER: set(),
            AgentType.SOQL_GENERATOR: {AgentType.INTENT_ROUTER},
            AgentType.DBT_SELECTOR: {AgentType.INTENT_ROUTER},
            AgentType.DYNAMIC_DBT_GENERATOR: {AgentType.DBT_SELECTOR},
            AgentType.DATA_FETCHER: {AgentType.SOQL_GENERATOR},
            AgentType.DBT_EXECUTOR: {AgentType.DBT_SELECTOR, AgentType.DYNAMIC_DBT_GENERATOR},
            AgentType.SNOWFLAKE_MCP: {AgentType.DBT_SELECTOR},
            AgentType.DATA_FUSION: {AgentType.DATA_FETCHER, AgentType.DBT_EXECUTOR, AgentType.SNOWFLAKE_MCP, AgentType.DYNAMIC_DBT_GENERATOR},
            AgentType.RESPONSE_GENERATOR: {AgentType.DATA_FUSION},
        }
    
    async def execute(self, user_query: str, conversation_history: List[Dict], salesforce_schema: str) -> str:
        """Execute the complete DAG"""
        
        # Initialize context
        context = DAGContext(
            user_query=user_query,
            conversation_history=conversation_history,
            salesforce_schema=salesforce_schema,
            execution_id=f"exec_{hash(user_query)}"
        )
        
        logger.info("Starting DAG execution", query=user_query, execution_id=context.execution_id)
        
        try:
            # Execute agents based on dependencies
            await self._execute_agent(AgentType.INTENT_ROUTER, context)
            
            # Parallel execution of independent agents
            await asyncio.gather(
                self._execute_agent(AgentType.SOQL_GENERATOR, context),
                self._execute_agent(AgentType.DBT_SELECTOR, context)
            )
            
            # Dynamic DBT generation (if needed)
            await self._execute_agent(AgentType.DYNAMIC_DBT_GENERATOR, context)
            
            # Parallel data fetching and analytics
            await asyncio.gather(
                self._execute_agent(AgentType.DATA_FETCHER, context),
                self._execute_agent(AgentType.DBT_EXECUTOR, context),
                self._execute_agent(AgentType.SNOWFLAKE_MCP, context)
            )
            
            # Final processing
            await self._execute_agent(AgentType.DATA_FUSION, context)
            await self._execute_agent(AgentType.RESPONSE_GENERATOR, context)
            
            logger.info("DAG execution completed", execution_id=context.execution_id)
            return context.final_response or "I encountered an error processing your request."
            
        except Exception as e:
            logger.error("DAG execution failed", error=str(e), execution_id=context.execution_id)
            return f"I encountered an error: {str(e)}"
    
    async def _execute_agent(self, agent_type: AgentType, context: DAGContext) -> None:
        """Execute a single agent"""
        if agent_type not in self.agents:
            logger.warning(f"Agent {agent_type.value} not found")
            return
        
        agent = self.agents[agent_type]
        logger.info(f"Executing agent: {agent_type.value}")
        
        try:
            context = await agent.execute(context)
            context.execution_path.append(agent_type)
        except Exception as e:
            context.errors.append(f"{agent_type.value} failed: {str(e)}")
            logger.error(f"Agent {agent_type.value} failed", error=str(e))
            raise
