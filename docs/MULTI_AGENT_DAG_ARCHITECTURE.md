# 🕸️ Multi-Agent DAG Architecture

## Overview

The Whizzy Bot now uses a **true multi-agent DAG (Directed Acyclic Graph)** architecture similar to LangChain's approach, with intelligent routing, parallel execution, and sophisticated data fusion.

## 🏗️ Architecture Diagram

```
User Query
    ↓
┌─────────────────┐
│ Intent Router   │ → Determines execution path
└─────────────────┘
    ↓
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ SOQL Generator  │    │ DBT Selector    │    │ Context Builder │
└─────────────────┘    └─────────────────┘    └─────────────────┘
    ↓                        ↓                        ↓
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Data Fetcher    │    │ DBT Executor    │    │ Schema Analyzer │
└─────────────────┘    └─────────────────┘    └─────────────────┘
    ↓                        ↓                        ↓
┌─────────────────────────────────────────────────────────────┐
│                    Data Fusion Agent                        │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────┐
│ Response Gen    │
└─────────────────┘
```

## 🔄 Agent Flow

### 1. **Intent Router Agent**
- **Purpose**: Determines optimal execution path
- **Output**: Intent classification + execution path
- **Execution Paths**:
  - `SIMPLE_QUERY`: Direct Salesforce data
  - `ANALYTICS_DEEP`: Complex analysis
  - `EXECUTIVE_BRIEFING`: Executive insights
  - `HELP_REQUEST`: Capabilities
  - `CONVERSATIONAL`: Casual interaction

### 2. **Parallel Agent Execution**
```
Intent Router
    ↓
┌─────────────────┐    ┌─────────────────┐
│ SOQL Generator  │    │ DBT Selector    │
│ (if needed)     │    │ (if needed)     │
└─────────────────┘    └─────────────────┘
    ↓                        ↓
┌─────────────────┐    ┌─────────────────┐
│ Data Fetcher    │    │ DBT Executor    │
│ (parallel)      │    │ (parallel)      │
└─────────────────┘    └─────────────────┘
```

### 3. **Data Fusion Agent**
- **Purpose**: Combines Salesforce + DBT data
- **Capabilities**:
  - Pattern recognition
  - Correlation analysis
  - Executive summaries
  - Key metrics extraction

### 4. **Response Generator Agent**
- **Purpose**: Creates natural language responses
- **Styles**:
  - Executive: High-level insights
  - Analytics: Detailed metrics
  - Simple: Direct answers
  - Help: Comprehensive overview

## 🚀 Key Features

### **Parallel Execution**
```python
# Agents run in parallel when possible
await asyncio.gather(
    self._execute_agent(AgentType.SOQL_GENERATOR, context),
    self._execute_agent(AgentType.DBT_SELECTOR, context)
)
```

### **Intelligent Routing**
```python
# Intent determines execution path
if context.intent == "EXECUTIVE_BRIEFING":
    # Execute: SOQL + DBT + Fusion + Response
elif context.intent == "SIMPLE_QUERY":
    # Execute: SOQL + Response (skip DBT)
```

### **Context Flow**
```python
@dataclass
class DAGContext:
    user_query: str
    conversation_history: List[Dict]
    salesforce_schema: str
    execution_id: str
    
    # Agent outputs
    intent: Optional[str] = None
    soql_queries: List[str] = field(default_factory=list)
    salesforce_data: Dict[str, Any] = field(default_factory=dict)
    dbt_models: List[str] = field(default_factory=list)
    dbt_data: Dict[str, Any] = field(default_factory=dict)
    fused_data: Optional[Dict[str, Any]] = None
    final_response: Optional[str] = None
    
    # Metadata
    execution_path: List[AgentType] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
```

### **Error Handling**
- Each agent has individual error handling
- Graceful degradation when agents fail
- Comprehensive error logging
- Fallback responses

## 📊 Execution Examples

### **Executive Briefing Query**
```
"vp sales briefing"
    ↓
Intent Router: EXECUTIVE_BRIEFING
    ↓
┌─────────────────┐    ┌─────────────────┐
│ SOQL Generator  │    │ DBT Selector    │
│ - Pipeline      │    │ - m_forecast    │
│ - Win Rate      │    │ - a_win_rate    │
│ - Top Deals     │    │ - a_slippage    │
└─────────────────┘    └─────────────────┘
    ↓                        ↓
┌─────────────────┐    ┌─────────────────┐
│ Data Fetcher    │    │ DBT Executor    │
│ (3 queries)     │    │ (3 models)      │
└─────────────────┘    └─────────────────┘
    ↓
Data Fusion Agent
    ↓
Response Generator: Executive summary
```

### **Simple Query**
```
"What's our win rate?"
    ↓
Intent Router: SIMPLE_QUERY
    ↓
SOQL Generator: Win rate calculation
    ↓
Data Fetcher: Execute query
    ↓
Response Generator: Direct answer
```

## 🔧 Configuration

### **Agent Dependencies**
```python
self.dependencies = {
    AgentType.INTENT_ROUTER: set(),
    AgentType.SOQL_GENERATOR: {AgentType.INTENT_ROUTER},
    AgentType.DBT_SELECTOR: {AgentType.INTENT_ROUTER},
    AgentType.DATA_FETCHER: {AgentType.SOQL_GENERATOR},
    AgentType.DBT_EXECUTOR: {AgentType.DBT_SELECTOR},
    AgentType.DATA_FUSION: {AgentType.DATA_FETCHER, AgentType.DBT_EXECUTOR},
    AgentType.RESPONSE_GENERATOR: {AgentType.DATA_FUSION},
}
```

### **Available DBT Models**
- `m_forecast`: Revenue forecasting
- `m_slippage_impact_quarter`: Slippage analysis
- `m_stage_velocity_quarter`: Stage velocity
- `a_win_rate_trend_analysis`: Win rate trends
- `a_slippage_pattern_analysis`: Slippage patterns
- `a_comprehensive_slippage_analysis`: Comprehensive slippage
- `a_win_rate_by_owner`: Win rate by owner
- `a_win_rate_by_industry`: Win rate by industry

## 🎯 Benefits

### **vs. Linear Chain**
- ✅ **Parallel Execution**: Multiple agents run simultaneously
- ✅ **Intelligent Routing**: Only necessary agents execute
- ✅ **Better Error Handling**: Individual agent failures don't break the flow
- ✅ **Scalability**: Easy to add new agents
- ✅ **Performance**: Faster execution through parallelism

### **vs. Traditional If-Else**
- ✅ **No Hardcoding**: Everything is LLM-driven
- ✅ **Context Awareness**: Agents understand conversation history
- ✅ **Flexible Routing**: Dynamic execution paths
- ✅ **Intelligent Fallbacks**: Graceful degradation

## 🧪 Testing

Run the DAG test:
```bash
python test_dag.py
```

This will test various query types and verify the DAG execution flow.

## 🚀 Future Enhancements

1. **Agent Caching**: Cache agent outputs for similar queries
2. **Dynamic Agent Loading**: Load agents on-demand
3. **Agent Monitoring**: Real-time performance metrics
4. **Custom Agent Types**: User-defined agents
5. **Agent Composition**: Combine agents into workflows
