# Whizzy Bot - Enhanced Intelligent Agentic Analytics System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Slack](https://img.shields.io/badge/Slack-Bot-green.svg)](https://slack.com)
[![Salesforce](https://img.shields.io/badge/Salesforce-Integration-orange.svg)](https://salesforce.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-purple.svg)](https://openai.com)
[![Enhanced AI](https://img.shields.io/badge/Enhanced-AI-red.svg)](https://github.com/blinklabs-dev/whizzy-mvp)

> **Advanced AI-powered Salesforce analytics bot with enhanced thinking, reasoning, and chain of thought capabilities**

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/blinklabs-dev/whizzy-mvp.git
cd whizzy-mvp

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run enhanced bot
python app/enhanced_whizzy_bot.py
```

## 🧠 Enhanced Intelligent Agentic System Features

### 🎯 Advanced Intent Classification & Orchestration
- **Multi-dimensional Intent Analysis**: Understands complex user queries with context awareness
- **Enhanced Orchestration**: Routes requests through specialized thinking processes
- **Chain of Thought Processing**: Step-by-step reasoning for complex analytical queries
- **Context Management**: Maintains conversation history and user preferences

### 🔗 Text-to-Technical Capabilities
- **Text-to-SOQL**: Natural language to Salesforce Object Query Language
- **Text-to-dbt**: Generate data transformation models through conversation
- **Text-to-Business Intelligence**: Create analytical insights from natural language
- **Multi-source Analytics**: Combine Salesforce, Snowflake, and dbt data

### ☕ Enhanced Coffee Briefing System
- **Persona-based Briefings**: Tailored insights for VP Sales, Account Executives, CDO
- **Context-aware Scheduling**: Personalized timing based on user behavior
- **Strategic Insights**: Morning briefings with actionable intelligence
- **Proactive Recommendations**: Anticipate user needs based on conversation history

### 📊 Advanced Quality Evaluation
- **Thinking Rate Analysis**: Measure reasoning depth and complexity
- **Context Awareness Metrics**: Track how well responses use conversation history
- **Persona Alignment Scoring**: Ensure responses match user role expectations
- **Actionability Assessment**: Evaluate practical value of responses

## 🏗️ Enhanced Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Enhanced Whizzy Bot                          │
├─────────────────────────────────────────────────────────────────┤
│  🧠 Enhanced Intelligent Agentic System                        │
│  ├── Chain of Thought Processing                               │
│  ├── Context State Management                                  │
│  ├── Advanced Reasoning Engine                                 │
│  └── Multi-dimensional Intent Classification                   │
├─────────────────────────────────────────────────────────────────┤
│  🔄 Orchestration Layer                                        │
│  ├── Thinking Process Execution                                │
│  ├── Context-aware Routing                                     │
│  ├── Multi-source Data Integration                             │
│  └── Quality Evaluation Engine                                 │
├─────────────────────────────────────────────────────────────────┤
│  📊 Data Sources                                               │
│  ├── Salesforce (Real-time queries)                            │
│  ├── Snowflake (Data warehouse)                                │
│  ├── dbt (Data transformations)                                │
│  └── Context History (User interactions)                       │
├─────────────────────────────────────────────────────────────────┤
│  🎯 Specialized Handlers                                       │
│  ├── Direct Answer Engine                                      │
│  ├── SOQL Generation                                           │
│  ├── dbt Model Creation                                        │
│  ├── Coffee Briefing Generator                                 │
│  └── Enhanced Reasoning Engine                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🧪 Enhanced Quality Evaluation Framework

### Comprehensive Testing Strategy
- **Functional Correctness**: Ensure all features work as expected
- **Response Quality**: Evaluate relevance, accuracy, and usefulness
- **Persona Alignment**: Test responses for different user roles
- **Thinking Process Validation**: Verify chain of thought reasoning
- **Context Awareness Testing**: Ensure proper use of conversation history

### UAT Test Suite
```bash
# Run comprehensive test suite
pytest tests/test_intelligent_agentic_system.py -v

# Test specific scenarios
pytest tests/test_intelligent_agentic_system.py::TestIntelligentAgenticSystemUAT -v
pytest tests/test_intelligent_agentic_system.py::TestPersonaBasedScenarios -v
```

## 🎯 Use Cases

### For VP Sales
- **Strategic Briefings**: Daily insights on pipeline health and trends
- **Complex Analytics**: Multi-dimensional analysis of sales performance
- **Predictive Insights**: Forecast opportunities and risks

### For Account Executives
- **Deal Intelligence**: Real-time insights on specific opportunities
- **Activity Tracking**: Monitor customer interactions and engagement
- **Performance Optimization**: Identify improvement opportunities

### For CDO/Data Teams
- **Pipeline Management**: Deploy dbt models through Slack commands
- **Data Quality Monitoring**: Track data pipeline health
- **Advanced Analytics**: Complex multi-source data analysis

## 🛠️ Development

### Enhanced System Components
- **`app/enhanced_whizzy_bot.py`**: Main bot with enhanced intelligent system integration
- **`app/intelligent_agentic_system.py`**: Core enhanced intelligent agentic system
- **`tests/test_intelligent_agentic_system.py`**: Comprehensive test suite
- **`docs/INTELLIGENT_AGENTIC_SYSTEM.md`**: Detailed system documentation

### Key Enhancements
- **Chain of Thought Processing**: Step-by-step reasoning for complex queries
- **Context State Management**: User-specific conversation history and preferences
- **Enhanced Quality Metrics**: Thinking rate, context awareness, persona alignment
- **Advanced Reasoning Engine**: Multi-dimensional analysis capabilities

## 📊 Analytics Infrastructure

### Preserved Components
- **dbt Models**: Data transformation pipeline templates
- **Snowflake Integration**: Data warehouse connectivity
- **Advanced Analytics**: Complex query capabilities

### Future Enhancements
- **Real-time dbt Deployment**: Text-to-dbt model generation
- **Advanced Snowflake Queries**: Complex analytical processing
- **Predictive Analytics**: Machine learning integration

## 🔒 Security & Compliance

- **Environment-based Configuration**: Secure credential management
- **User Context Isolation**: Separate context states per user
- **Audit Logging**: Comprehensive activity tracking
- **Data Privacy**: Secure handling of user interactions

## 🚀 Deployment

### Production Setup
```bash
# Environment configuration
export SLACK_APP_TOKEN="xapp-..."
export SLACK_BOT_TOKEN="xoxb-..."
export OPENAI_API_KEY="sk-..."
export SALESFORCE_USERNAME="..."
export SALESFORCE_PASSWORD="..."
export SALESFORCE_SECURITY_TOKEN="..."

# Run enhanced bot
python app/enhanced_whizzy_bot.py
```

### Monitoring
- **Enhanced Metrics**: Track thinking rate, context awareness, quality scores
- **Performance Monitoring**: Monitor response times and system health
- **Quality Evaluation**: Continuous assessment of response quality

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/enhanced-thinking`)
3. Commit changes (`git commit -am 'Add enhanced reasoning capabilities'`)
4. Push to branch (`git push origin feature/enhanced-thinking`)
5. Create Pull Request

## 📞 Support

- **Documentation**: See `docs/INTELLIGENT_AGENTIC_SYSTEM.md`
- **Issues**: [GitHub Issues](https://github.com/blinklabs-dev/whizzy-mvp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/blinklabs-dev/whizzy-mvp/discussions)

## 🙏 Acknowledgments

- **OpenAI**: Advanced language model capabilities
- **Slack**: Real-time messaging platform
- **Salesforce**: CRM data integration
- **dbt**: Data transformation framework
- **Snowflake**: Cloud data warehouse

---

**Enhanced Whizzy Bot** - Where advanced AI meets practical business intelligence with thinking and reasoning capabilities.
