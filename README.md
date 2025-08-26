# Whizzy Bot - Intelligent Agentic Analytics System

> **Advanced AI-powered Salesforce analytics bot with intelligent orchestration, multi-source analytics, and persona-specific insights**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

## 🚀 **Quick Start**

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your credentials

# Run the enhanced bot
python app/enhanced_whizzy_bot.py
```

## 🧠 **Intelligent Agentic System Features**

### **Advanced Intent Classification**
- **LLM-powered understanding** of natural language queries
- **8 intent types**: Direct answers, Salesforce queries, Business Intelligence, Complex Analytics, dbt models, Coffee briefings, Reasoning loops, Multi-source analysis
- **7 persona types**: VP Sales, Account Executive, Sales Manager, CDO, Data Engineer, Sales Operations, Customer Success
- **Confidence scoring** and fallback mechanisms

### **Multi-Agent Orchestration**
- **Intelligent routing** based on query complexity and intent
- **Parallel processing** with ThreadPoolExecutor
- **Reasoning loops** for complex multi-step analysis
- **Quality evaluation** with comprehensive metrics

### **Text-to-Technical Conversion**
- **Text-to-SOQL**: Natural language to Salesforce queries
- **Text-to-dbt**: Natural language to dbt model generation
- **Text-to-Business Intelligence**: Natural language to analytics insights

### **Multi-Source Analytics**
- **Salesforce Integration**: Real-time data queries and analysis
- **Snowflake Integration**: Data warehouse analytics (placeholder)
- **dbt Integration**: Model deployment and management (placeholder)
- **Cross-platform correlation** and insights

### **Coffee Briefing System**
- **Automated scheduling** for different personas
- **Personalized insights** based on role and frequency
- **Action items** and recommendations
- **Risk assessment** and opportunity identification

## 📊 **Quality Evaluation Framework**

### **Response Quality Metrics**
- **Confidence Score**: Overall response confidence (0.0-1.0)
- **Persona Alignment**: Role-specific relevance (0.0-1.0)
- **Actionability Score**: Practical recommendations (0.0-1.0)
- **Technical Accuracy**: SOQL/dbt correctness
- **Reasoning Quality**: Logical analysis steps

### **Performance Targets**
- **Simple queries**: < 2 seconds
- **Complex analytics**: < 5 seconds
- **Coffee briefings**: < 3 seconds
- **dbt model generation**: < 10 seconds
- **Overall success rate**: > 90%

## 🏗️ **Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                INTELLIGENT AGENTIC SYSTEM                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   User Query    │───▶│  Intent         │                │
│  │   (Natural      │    │  Classification │                │
│  │   Language)     │    │  (LLM)          │                │
│  └─────────────────┘    └─────────┬───────┘                │
│                                   │                        │
│                                   ▼                        │
│                          ┌─────────────────┐                │
│                          │   Orchestration │                │
│                          │   Engine        │                │
│                          └─────────┬───────┘                │
│                                   │                        │
│                                   ▼                        │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   Response      │◀───│   Multi-Agent   │                │
│  │   Generation    │    │   Processing    │                │
│  │   (Formatted)   │    │   (Parallel)    │                │
│  └─────────────────┘    └─────────────────┘                │
│                                   │                        │
│                                   ▼                        │
│                          ┌─────────────────┐                │
│                          │   Data Sources  │                │
│                          │  (Salesforce,   │                │
│                          │   Snowflake,    │                │
│                          │   dbt)          │                │
│                          └─────────────────┘                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 **Use Cases**

### **VP Sales**
- Strategic resource allocation analysis
- Team performance insights
- Pipeline health assessment
- Executive-level recommendations

### **Account Executive**
- Deal preparation assistance
- Customer insights and trends
- Personal performance metrics
- Call preparation guidance

### **CDO**
- Data strategy and governance
- dbt model creation and deployment
- Analytics infrastructure insights
- Technical architecture decisions

### **Sales Manager**
- Team coaching opportunities
- Process optimization insights
- Individual rep performance
- Resource allocation guidance

## 🔧 **Development**

### **Setup Development Environment**
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Run linting
black app/ tests/
flake8 app/ tests/
```

### **Testing Strategy**
- **Unit Tests**: Core functionality validation
- **Integration Tests**: End-to-end workflow testing
- **Quality Tests**: Response quality assessment
- **Persona Tests**: Role-specific scenario testing
- **Performance Tests**: System performance validation

### **Code Quality**
- **Type Hints**: Full type annotation coverage
- **Documentation**: Comprehensive docstrings
- **Error Handling**: Graceful fallbacks and recovery
- **Logging**: Structured logging with different levels

## 📈 **Analytics Infrastructure**

### **dbt Models**
- **Staging Models**: Data cleaning and standardization
- **Dimension Models**: Customer, product, and time dimensions
- **Fact Models**: Sales, pipeline, and performance facts
- **Mart Models**: Business-ready aggregated data

### **Snowflake Integration**
- **Data Warehouse**: Centralized analytics platform
- **Performance Optimization**: Query optimization and caching
- **Data Governance**: Security, access control, and audit trails

### **Advanced Analytics**
- **Predictive Modeling**: Win rate prediction, churn analysis
- **Customer Segmentation**: RFM analysis, behavior clustering
- **Performance Attribution**: Campaign effectiveness, channel analysis

## 🔐 **Security & Compliance**

### **Data Protection**
- **Encryption**: Data in transit and at rest
- **Access Control**: Role-based permissions
- **Audit Logging**: Complete activity tracking
- **GDPR Compliance**: Data privacy and consent management

### **Integration Security**
- **OAuth 2.0**: Secure API authentication
- **API Rate Limiting**: Protection against abuse
- **Input Validation**: SQL injection prevention
- **Error Handling**: Secure error messages

## 🚀 **Deployment**

### **Production Setup**
```bash
# Environment configuration
export SLACK_APP_TOKEN=xapp-your-token
export SLACK_BOT_TOKEN=xoxb-your-token
export OPENAI_API_KEY=your-openai-key
export SALESFORCE_USERNAME=your-username
export SALESFORCE_PASSWORD=your-password
export SALESFORCE_SECURITY_TOKEN=your-token

# Run with process manager
pm2 start app/enhanced_whizzy_bot.py --name whizzy-bot
```

### **Monitoring & Observability**
- **Health Checks**: System status monitoring
- **Performance Metrics**: Response times and throughput
- **Quality Metrics**: Confidence scores and success rates
- **Error Tracking**: Comprehensive error logging and alerting

## 🤝 **Contributing**

### **Development Guidelines**
1. **Fork** the repository
2. **Create** a feature branch
3. **Implement** with tests
4. **Submit** a pull request

### **Code Standards**
- **Python**: PEP 8 compliance
- **Testing**: >90% coverage
- **Documentation**: Clear and comprehensive
- **Performance**: Optimized for production

## 📞 **Support**

### **Documentation**
- [Architecture Guide](docs/INTELLIGENT_AGENTIC_SYSTEM.md)
- [API Reference](docs/API_REFERENCE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

### **Community**
- **Issues**: GitHub issue tracker
- **Discussions**: GitHub discussions
- **Wiki**: Project documentation

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **OpenAI**: GPT-4 integration for intelligent processing
- **Salesforce**: API integration and data access
- **Slack**: Real-time communication platform
- **dbt**: Data transformation and modeling
- **Snowflake**: Cloud data warehouse platform

---

**Built with ❤️ for intelligent business analytics**
