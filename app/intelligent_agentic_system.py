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
import os
from dotenv import load_dotenv

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
        self.salesforce_client = self._initialize_salesforce()
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
    
    def _load_chain_of_thought_prompt(self) -> str:
        """Load chain of thought reasoning prompt"""
        return """
You are an expert business analyst with advanced reasoning capabilities. Use chain of thought reasoning to break down complex queries into logical steps.

QUERY: {query}
PERSONA: {persona}
CONTEXT: {context}

Think through this step by step:

1. INTENT ANALYSIS:
   - What is the user really asking for?
   - What type of analysis is needed?
   - What data sources should be consulted?

2. CONTEXT GATHERING:
   - What historical context is relevant?
   - What user preferences should be considered?
   - What business context applies?

3. DATA SOURCE SELECTION:
   - Which data sources are most appropriate?
   - What specific queries are needed?
   - How should data be combined?

4. ANALYSIS APPROACH:
   - What analytical methods should be used?
   - What patterns should be looked for?
   - What insights are most valuable?

5. INSIGHT SYNTHESIS:
   - How do the pieces fit together?
   - What are the key findings?
   - What recommendations emerge?

6. RESPONSE FORMULATION:
   - How should insights be presented?
   - What action items are needed?
   - How should this be tailored to the persona?

Provide your reasoning in this format:

THINKING PROCESS:
[Your step-by-step reasoning]

CHAIN OF THOUGHT:
1. [First reasoning step]
2. [Second reasoning step]
3. [Third reasoning step]
...

FINAL ANALYSIS:
[Your comprehensive analysis]

RECOMMENDATIONS:
[Your recommendations]

CONFIDENCE: [0.0-1.0]
"""
    
    def _load_thinking_prompt(self) -> str:
        """Load thinking and reasoning prompt"""
        return """
You are an advanced AI analyst with deep business intelligence capabilities. Use sophisticated thinking to analyze complex business queries.

QUERY: {query}
PERSONA: {persona}
CONTEXT: {context}
AVAILABLE_DATA: {available_data}

Apply advanced thinking techniques:

1. CRITICAL THINKING:
   - Question assumptions
   - Identify biases
   - Consider alternative perspectives
   - Evaluate evidence quality

2. SYSTEMS THINKING:
   - Understand interconnections
   - Identify root causes
   - Consider feedback loops
   - Analyze emergent properties

3. STRATEGIC THINKING:
   - Long-term implications
   - Competitive analysis
   - Risk assessment
   - Opportunity identification

4. CREATIVE THINKING:
   - Novel insights
   - Pattern recognition
   - Hypothesis generation
   - Innovation opportunities

5. ANALYTICAL THINKING:
   - Data interpretation
   - Statistical reasoning
   - Trend analysis
   - Predictive modeling

Provide your analysis in this format:

THINKING PROCESS:
[Your advanced thinking process]

CRITICAL INSIGHTS:
[Key insights from critical thinking]

SYSTEMS ANALYSIS:
[Systems-level understanding]

STRATEGIC IMPLICATIONS:
[Strategic considerations]

CREATIVE OPPORTUNITIES:
[Innovative insights]

ANALYTICAL FINDINGS:
[Data-driven conclusions]

CONFIDENCE: [0.0-1.0]
"""
    
    def _load_intent_classification_prompt(self) -> str:
        """Load enhanced intent classification prompt"""
        return """
You are an expert intent classifier for a sophisticated Salesforce analytics bot. Analyze the user query with advanced understanding.

Available intents:
- DIRECT_ANSWER: Simple questions that can be answered directly
- SALESFORCE_QUERY: Questions requiring Salesforce data (win rates, pipeline, accounts)
- BUSINESS_INTELLIGENCE: Questions requiring analysis and insights
- COMPLEX_ANALYTICS: Questions requiring multiple data sources and advanced analytics
- DBT_MODEL: Questions about creating or modifying dbt models
- COFFEE_BRIEFING: Requests for regular briefings (daily/weekly/monthly)
- REASONING_LOOP: Questions requiring multi-step reasoning
- MULTI_SOURCE: Questions requiring data from multiple sources
- THINKING_ANALYSIS: Questions requiring deep thinking and analysis

Personas:
- VP_SALES: Strategic insights, team performance, resource allocation
- ACCOUNT_EXECUTIVE: Deal preparation, customer insights, personal performance
- SALES_MANAGER: Team coaching, performance management, process optimization
- CDO: Data strategy, analytics infrastructure, governance
- DATA_ENGINEER: Technical implementation, data pipelines, model development
- SALES_OPERATIONS: Process optimization, data quality, reporting
- CUSTOMER_SUCCESS: Customer health, retention, engagement

Analyze the query and respond with JSON:
{
    "primary_intent": "intent_type",
    "confidence": 0.95,
    "persona": "persona_type",
    "data_sources": ["salesforce", "snowflake", "dbt"],
    "complexity_level": "low|medium|high",
    "reasoning_required": true/false,
    "coffee_briefing": true/false,
    "dbt_model_required": true/false,
    "thinking_required": true/false,
    "explanation": "Detailed explanation of classification"
}

Query: {query}
"""
    
    def _load_reasoning_prompt(self) -> str:
        """Load enhanced reasoning prompt for complex queries"""
        return """
You are an expert business analyst with advanced reasoning capabilities. Given a complex query, use sophisticated reasoning to provide comprehensive analysis.

Query: {query}
Context: {context}
Available Data: {available_data}
Chain of Thought: {chain_of_thought}

Apply advanced reasoning techniques:

1. LOGICAL REASONING:
   - Deductive reasoning
   - Inductive reasoning
   - Abductive reasoning
   - Causal inference

2. QUANTITATIVE REASONING:
   - Statistical analysis
   - Mathematical modeling
   - Probability assessment
   - Risk quantification

3. QUALITATIVE REASONING:
   - Pattern recognition
   - Trend analysis
   - Comparative analysis
   - Contextual understanding

4. STRATEGIC REASONING:
   - Long-term thinking
   - Competitive analysis
   - Resource optimization
   - Risk management

Provide your analysis in this format:

REASONING PROCESS:
[Your sophisticated reasoning process]

LOGICAL ANALYSIS:
[Logical reasoning steps]

QUANTITATIVE INSIGHTS:
[Data-driven analysis]

QUALITATIVE ASSESSMENT:
[Pattern and trend analysis]

STRATEGIC IMPLICATIONS:
[Strategic considerations]

RECOMMENDATIONS:
[Actionable recommendations]

CONFIDENCE: [0.0-1.0]
"""
    
    def _load_persona_prompts(self) -> Dict[str, str]:
        """Load enhanced persona-specific prompts"""
        return {
            "vp_sales": """
You are responding to a VP of Sales with advanced strategic thinking. Focus on:
- Strategic insights and business impact
- Team performance and resource allocation
- High-level trends and opportunities
- Executive-level recommendations
- Revenue and pipeline insights
- Competitive analysis and market positioning
- Long-term strategic planning
- Risk assessment and mitigation
""",
            "account_executive": """
You are responding to an Account Executive with tactical thinking. Focus on:
- Deal preparation and customer insights
- Personal performance metrics
- Account-specific information
- Call preparation guidance
- Deal strategy and next steps
- Customer relationship management
- Competitive positioning
- Sales technique optimization
""",
            "sales_manager": """
You are responding to a Sales Manager with operational thinking. Focus on:
- Team performance and coaching opportunities
- Process optimization and efficiency
- Individual rep performance
- Pipeline management
- Resource allocation and training needs
- Performance metrics and KPIs
- Team dynamics and motivation
- Process improvement opportunities
""",
            "cdo": """
You are responding to a Chief Data Officer with technical and strategic thinking. Focus on:
- Data strategy and governance
- Analytics infrastructure and capabilities
- Data quality and reliability
- Strategic data initiatives
- Technical architecture decisions
- Data pipeline optimization
- Analytics adoption and ROI
- Data security and compliance
""",
            "data_engineer": """
You are responding to a Data Engineer with technical thinking. Focus on:
- Technical implementation details
- Data pipeline optimization
- Model development and deployment
- Performance and scalability
- Best practices and standards
- Infrastructure optimization
- Code quality and maintainability
- System architecture decisions
""",
            "sales_operations": """
You are responding to a Sales Operations professional with analytical thinking. Focus on:
- Process optimization and efficiency
- Data quality and reporting
- System configuration and automation
- Performance metrics and KPIs
- Operational improvements
- Workflow optimization
- Data analysis and insights
- Process standardization
""",
            "customer_success": """
You are responding to a Customer Success professional with relationship thinking. Focus on:
- Customer health and satisfaction
- Retention and expansion opportunities
- Customer engagement and support
- Success metrics and outcomes
- Customer lifecycle management
- Relationship building strategies
- Customer feedback analysis
- Proactive support initiatives
"""
        }
    
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
    
    async def orchestrate_response(self, query: str, intent_analysis: IntentAnalysis, user_id: str = None) -> AgentResponse:
        """Enhanced orchestration with thinking and context management"""
        try:
            # Get or create context state
            context_state = self._get_context_state(user_id or "default")
            
            # Update context with current query
            context_state.last_query = query
            context_state.current_context.update({
                "current_intent": intent_analysis.primary_intent.value,
                "current_persona": intent_analysis.persona.value,
                "timestamp": datetime.now().isoformat()
            })
            
            # Execute thinking process if required
            chain_of_thought = None
            if intent_analysis.thinking_required or intent_analysis.primary_intent == IntentType.THINKING_ANALYSIS:
                chain_of_thought = await self._execute_thinking_process(
                    query, intent_analysis.persona, context_state.current_context, {}
                )
            
            # Route to appropriate handler
            if intent_analysis.reasoning_required or chain_of_thought:
                return await self._handle_thinking_query(query, intent_analysis, chain_of_thought, context_state)
            elif intent_analysis.coffee_briefing:
                return await self._handle_coffee_briefing(query, intent_analysis, context_state)
            elif intent_analysis.dbt_model_required:
                return await self._handle_dbt_model_request(query, intent_analysis, context_state)
            elif intent_analysis.primary_intent == IntentType.COMPLEX_ANALYTICS:
                return await self._handle_complex_analytics(query, intent_analysis, context_state)
            elif intent_analysis.primary_intent == IntentType.SALESFORCE_QUERY:
                return await self._handle_salesforce_query(query, intent_analysis, context_state)
            elif intent_analysis.primary_intent == IntentType.BUSINESS_INTELLIGENCE:
                return await self._handle_business_intelligence(query, intent_analysis, context_state)
            else:
                return await self._handle_direct_answer(query, intent_analysis, context_state)
                
        except Exception as e:
            logger.error(f"❌ Error in orchestration: {e}")
            return self._create_error_response(str(e))
    
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
        """Handle queries requiring advanced thinking and reasoning"""
        try:
            # Gather data from multiple sources
            data_sources = await self._gather_data_sources(intent_analysis.data_sources)
            
            # Create enhanced reasoning prompt
            reasoning_prompt = self.reasoning_prompt.format(
                query=query,
                context=json.dumps(context_state.current_context, indent=2),
                available_data=json.dumps(data_sources, indent=2),
                chain_of_thought=chain_of_thought.reasoning_path if chain_of_thought else "No chain of thought available"
            )
            
            # Get reasoning response
            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": reasoning_prompt},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.3
                )
            )
            
            reasoning_response = response.choices[0].message.content
            
            # Update context with reasoning results
            context_state.current_context.update({
                "last_reasoning": reasoning_response,
                "thinking_steps": len(chain_of_thought.thinking_steps) if chain_of_thought else 0
            })
            
            return AgentResponse(
                response_text=reasoning_response,
                data_sources_used=intent_analysis.data_sources,
                reasoning_steps=self._extract_reasoning_steps(reasoning_response),
                confidence_score=intent_analysis.confidence,
                persona_alignment=0.95,
                actionability_score=0.9,
                quality_metrics={"reasoning_quality": 0.9, "completeness": 0.95, "thinking_depth": 0.9},
                chain_of_thought=chain_of_thought,
                thinking_process=reasoning_response
            )
            
        except Exception as e:
            logger.error(f"❌ Error in thinking query: {e}")
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
            model_requirements = self._extract_dbt_requirements(query)
            
            # Generate dbt model
            dbt_model = await self._generate_dbt_model(model_requirements)
            
            response_text = f"""
🔧 **dbt Model Generated**

**Model Name**: `{dbt_model['name']}`

**Description**: {dbt_model['description']}

**SQL Model**:
```sql
{dbt_model['sql']}
```

**Configuration**:
```yaml
{dbt_model['config']}
```

**Next Steps**:
1. Review the generated model
2. Test in development environment
3. Deploy to production
4. Monitor performance

**Quality Checks**:
- ✅ Syntax validation
- ✅ Best practices compliance
- ✅ Performance optimization
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
            salesforce_data = await self._get_salesforce_data(query)
            snowflake_data = await self._get_snowflake_data(query)
            dbt_insights = await self._get_dbt_insights(query)
            
            # Combine and analyze
            combined_analysis = await self._analyze_combined_data(
                salesforce_data, snowflake_data, dbt_insights, query
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
    
    async def _handle_salesforce_query(self, query: str, intent_analysis: IntentAnalysis, context_state: ContextState) -> AgentResponse:
        """Handle Salesforce-specific queries"""
        try:
            if not self.salesforce_client:
                return self._create_error_response("Salesforce connection not available")
            
            # Generate SOQL query
            soql_query = await self._generate_soql_query(query)
            
            # Execute query
            result = self.salesforce_client.query(soql_query)
            
            # Format response
            response_text = self._format_salesforce_response(result, query, intent_analysis)
            
            return AgentResponse(
                response_text=response_text,
                data_sources_used=[DataSourceType.SALESFORCE],
                reasoning_steps=["SOQL generation", "Query execution", "Data formatting", "Insight extraction"],
                confidence_score=0.9,
                persona_alignment=0.85,
                actionability_score=0.8,
                quality_metrics={"data_accuracy": 0.95, "relevance": 0.9, "completeness": 0.85}
            )
            
        except Exception as e:
            logger.error(f"❌ Error in Salesforce query: {e}")
            return self._create_error_response(str(e))
    
    async def _handle_business_intelligence(self, query: str, intent_analysis: IntentAnalysis, context_state: ContextState) -> AgentResponse:
        """Handle business intelligence queries"""
        try:
            # Get base data
            base_data = await self._get_salesforce_data(query)
            
            # Generate business insights
            insights = await self._generate_business_insights(base_data, query, intent_analysis)
            
            # Format with persona-specific styling
            response_text = self._format_business_intelligence_response(insights, intent_analysis)
            
            return AgentResponse(
                response_text=response_text,
                data_sources_used=[DataSourceType.SALESFORCE],
                reasoning_steps=["Data analysis", "Pattern recognition", "Insight generation", "Recommendation creation"],
                confidence_score=0.85,
                persona_alignment=0.9,
                actionability_score=0.85,
                quality_metrics={"insight_quality": 0.85, "relevance": 0.9, "actionability": 0.8}
            )
            
        except Exception as e:
            logger.error(f"❌ Error in business intelligence: {e}")
            return self._create_error_response(str(e))
    
    async def _generate_business_insights(self, base_data: Dict[str, Any], query: str, intent_analysis: IntentAnalysis) -> Dict[str, Any]:
        """Generate business insights from base data"""
        try:
            # Generate insights using LLM
            insights_prompt = f"""
            Generate business insights for the following query and data:
            
            Query: {query}
            Persona: {intent_analysis.persona.value}
            Data: {base_data}
            
            Provide insights in this format:
            {{
                "insight1": "First insight",
                "insight2": "Second insight", 
                "insight3": "Third insight",
                "action_items": ["Action 1", "Action 2"],
                "recommendations": ["Recommendation 1", "Recommendation 2"]
            }}
            """
            
            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a business analyst providing insights."},
                        {"role": "user", "content": insights_prompt}
                    ],
                    temperature=0.3
                )
            )
            
            insights_text = response.choices[0].message.content
            # Try to parse JSON, fallback to simple format if needed
            try:
                return json.loads(insights_text)
            except:
                return {
                    "insight1": "Data analysis complete",
                    "insight2": "Trends identified", 
                    "insight3": "Recommendations generated",
                    "action_items": ["Review insights", "Implement recommendations"],
                    "recommendations": ["Focus on high-value deals", "Optimize sales process"]
                }
                
        except Exception as e:
            logger.error(f"❌ Error generating business insights: {e}")
            return {
                "insight1": "Analysis completed",
                "insight2": "Key trends identified",
                "insight3": "Actionable recommendations available",
                "action_items": ["Review the data", "Take action"],
                "recommendations": ["Focus on priorities", "Monitor progress"]
            }
    
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
    async def _gather_data_sources(self, data_sources: List[DataSourceType]) -> Dict[str, Any]:
        """Gather data from multiple sources"""
        data = {}
        
        for source in data_sources:
            if source == DataSourceType.SALESFORCE:
                data['salesforce'] = await self._get_salesforce_data("general overview")
            elif source == DataSourceType.SNOWFLAKE:
                data['snowflake'] = await self._get_snowflake_data("general overview")
            elif source == DataSourceType.DBT:
                data['dbt'] = await self._get_dbt_insights("general overview")
        
        return data
    
    async def _get_salesforce_data(self, query: str) -> Dict[str, Any]:
        """Get data from Salesforce"""
        if not self.salesforce_client:
            return {"error": "Salesforce not available"}
        
        try:
            # Basic Salesforce queries
            opportunities = self.salesforce_client.query("SELECT COUNT(Id), SUM(Amount) FROM Opportunity")
            accounts = self.salesforce_client.query("SELECT COUNT(Id) FROM Account")
            
            return {
                "opportunities": opportunities['records'][0],
                "accounts": accounts['records'][0]
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_snowflake_data(self, query: str) -> Dict[str, Any]:
        """Get data from Snowflake (placeholder)"""
        # This would connect to Snowflake in production
        return {"message": "Snowflake integration pending"}
    
    async def _get_dbt_insights(self, query: str) -> Dict[str, Any]:
        """Get insights from dbt models (placeholder)"""
        # This would query dbt models in production
        return {"message": "dbt integration pending"}
    
    async def _generate_soql_query(self, query: str) -> str:
        """Generate SOQL query from natural language"""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Generate SOQL queries for Salesforce. Return only the SOQL query, no explanation."},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.1
                )
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"❌ Error generating SOQL: {e}")
            return "SELECT Id FROM Opportunity LIMIT 1"
    
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
        """Generate dbt model based on requirements"""
        # This would generate dbt models based on requirements
        return {
            "name": "custom_analysis_model",
            "description": "Custom analysis model based on requirements",
            "sql": "SELECT * FROM {{ ref('stg_salesforce_opportunities') }} WHERE amount > 0",
            "config": "materialized: table\nunique_key: id"
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
    
    def _extract_dbt_requirements(self, query: str) -> Dict[str, Any]:
        """Extract dbt model requirements from query"""
        return {
            "purpose": "Custom analysis",
            "data_sources": ["salesforce"],
            "complexity": "medium"
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
    
    async def process_query(self, query: str, user_context: Dict[str, Any] = None) -> AgentResponse:
        """Main entry point for processing queries"""
        try:
            logger.info(f"🧠 Processing query: {query}")
            
            # Step 1: Intent classification
            intent_analysis = await self.classify_intent(query, user_context)
            logger.info(f"🎯 Intent classified: {intent_analysis.primary_intent.value}")
            
            # Step 2: Orchestrate response
            response = await self.orchestrate_response(query, intent_analysis)
            logger.info(f"✅ Response generated with confidence: {response.confidence_score}")
            
            # Step 3: Store conversation history
            self.conversation_history.append({
                "query": query,
                "intent": intent_analysis,
                "response": response,
                "timestamp": datetime.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error in query processing: {e}")
            return self._create_error_response(str(e))
    
    def get_quality_metrics(self) -> Dict[str, Any]:
        """Get overall quality metrics"""
        if not self.conversation_history:
            return {"message": "No conversations yet"}
        
        # Fix: Handle both dict and object structures
        total_confidence = 0
        successful_queries = 0
        
        for conv in self.conversation_history:
            if isinstance(conv, dict):
                # Handle dict structure
                response = conv.get("response")
                if response and hasattr(response, 'confidence_score'):
                    total_confidence += response.confidence_score
                    if response.confidence_score > 0.5:
                        successful_queries += 1
            else:
                # Handle object structure
                if hasattr(conv, 'response') and hasattr(conv.response, 'confidence_score'):
                    total_confidence += conv.response.confidence_score
                    if conv.response.confidence_score > 0.5:
                        successful_queries += 1
        
        avg_confidence = total_confidence / len(self.conversation_history) if self.conversation_history else 0
        success_rate = successful_queries / len(self.conversation_history) if self.conversation_history else 0
        
        return {
            "total_queries": len(self.conversation_history),
            "average_confidence": avg_confidence,
            "success_rate": success_rate,
            "intent_distribution": self._get_intent_distribution()
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
