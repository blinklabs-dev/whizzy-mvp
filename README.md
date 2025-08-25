# Whizzy Bot - Salesforce Analytics Bot

A production-ready Slack bot that provides real-time Salesforce analytics through natural language queries. Whizzy Bot transforms complex Salesforce data into actionable business insights with professional formatting and persona-specific responses.

## 🚀 **Quick Start**

### **1. Setup Environment**
```bash
# Clone the repository
git clone <repository-url>
cd whizzy-mvp

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.example .env

# Edit .env with your credentials
nano .env
```

### **2. Configure Environment Variables**
```bash
# Slack Configuration
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_BOT_TOKEN=xoxb-your-bot-token

# Salesforce Configuration
SALESFORCE_USERNAME=your_username@example.com
SALESFORCE_PASSWORD=your_password
SALESFORCE_SECURITY_TOKEN=your_security_token
SALESFORCE_DOMAIN=login  # 'login' for production, 'test' for sandbox

# Optional: Analytics Infrastructure
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ROLE=your_role
SNOWFLAKE_WAREHOUSE=XSMALL
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
```

### **3. Start the Bot**
```bash
# Run the bot
python app/whizzy_bot.py

# Or with environment path
PYTHONPATH=. python app/whizzy_bot.py
```

### **4. Test in Slack**
- Mention `@whizzy` in any channel
- Ask questions like:
  - "What's our win rate?"
  - "Show me the pipeline"
  - "Top 10 accounts by revenue"
  - "Give me an executive briefing"

## 🏗️ **Architecture**

### **System Overview**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Slack User    │───▶│  Whizzy Bot     │───▶│   Salesforce    │
│   (Natural      │    │  (Socket Mode)  │    │   (Real Data)   │
│   Language)     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Analytics     │
                       │  (dbt/Snowflake)│
                       │   (Future)      │
                       └─────────────────┘
```

### **Core Components**

#### **1. Whizzy Bot (`app/whizzy_bot.py`)**
- **Slack Integration**: Socket Mode for real-time communication
- **Salesforce Connection**: Direct API queries for live data
- **Query Processing**: Natural language to structured queries
- **Response Generation**: Professional, persona-specific insights
- **Error Handling**: Graceful fallbacks and logging

#### **2. Analytics Infrastructure (`analytics/`)**
- **dbt Models**: Staging, facts, dimensions, and marts
- **Snowflake Integration**: Data warehouse for advanced analytics
- **Forecasting Models**: Pipeline and revenue predictions
- **Performance Metrics**: KPIs and business intelligence

#### **3. Configuration**
- **Environment Variables**: Secure credential management
- **Logging**: Comprehensive request and error tracking
- **Signal Handling**: Graceful shutdown and restart

## 📊 **Features**

### **Real-Time Analytics**
- **Win Rate Analysis**: Current performance metrics
- **Pipeline Overview**: Stage-by-stage breakdown
- **Top Accounts**: Revenue-based rankings
- **Deal Analysis**: High-value opportunity insights
- **Performance Metrics**: KPIs and benchmarks

### **Strategic Insights**
- **Executive Briefings**: High-level strategic overview
- **Action Items**: Specific recommendations
- **Risk Assessment**: Pipeline and performance risks
- **Forecasting**: Data-driven predictions

### **Professional Formatting**
- **Rich Text**: Emojis and structured formatting
- **Persona-Specific**: Role-appropriate insights
- **Actionable**: Clear next steps and recommendations
- **Visual**: Easy-to-read data presentation

## 🎯 **Use Cases**

### **Sales Teams**
- **Account Executives**: Deal preparation and customer insights
- **Sales Managers**: Team performance and coaching opportunities
- **Sales Operations**: Process optimization and data quality

### **Leadership**
- **VP Sales**: Strategic insights and resource allocation
- **Executives**: High-level business intelligence
- **Finance**: Revenue forecasting and pipeline analysis

### **Customer Success**
- **Customer Success Managers**: Account health and retention
- **Support Teams**: Customer insights and engagement

## 🔧 **Development**

### **Project Structure**
```
whizzy-mvp/
├── app/
│   └── whizzy_bot.py              # Main bot application
├── analytics/                     # dbt models and analytics
│   ├── models/
│   │   ├── staging/              # Raw data staging
│   │   ├── facts/                # Fact tables
│   │   ├── dims/                 # Dimension tables
│   │   └── marts/                # Business marts
│   └── dbt_project.yml           # dbt configuration
├── docs/                         # Documentation
├── tests/                        # Test suite
├── .env                          # Environment variables
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation
```

### **Adding New Features**

#### **1. New Query Type**
```python
def _generate_response(self, text: str, user: str) -> str:
    text_lower = text.lower()
    
    # Add new condition
    if "your new query" in text_lower:
        return self._get_new_analysis()
    
    # ... existing code ...

def _get_new_analysis(self) -> str:
    """Get new analysis from Salesforce"""
    # Implement your analysis logic
    pass
```

#### **2. New Analytics Model**
```sql
-- analytics/models/your_new_model.sql
{{
  config(
    materialized='table'
  )
}}

SELECT 
  -- Your analysis logic
FROM {{ ref('your_source_table') }}
```

### **Testing**
```bash
# Run tests
pytest tests/

# Test specific functionality
python -m pytest tests/test_whizzy_bot.py -v
```

## 📈 **Analytics Infrastructure**

### **dbt Models**
- **Staging**: Raw Salesforce data preparation
- **Facts**: Core business metrics (opportunities, accounts)
- **Dimensions**: Reference data (owners, industries)
- **Marts**: Business-ready analytics (forecasting, performance)

### **Key Models**
- `fct_opportunity`: Core opportunity metrics
- `m_forecast`: Revenue forecasting
- `m_slippage_impact_quarter`: Pipeline analysis
- `m_stage_velocity_quarter`: Performance metrics

### **Running Analytics**
```bash
cd analytics

# Install dbt dependencies
dbt deps

# Run all models
dbt run

# Run specific model
dbt run --select m_forecast

# Test models
dbt test
```

## 🔒 **Security**

### **Best Practices**
- **Environment Variables**: Never hardcode credentials
- **Token Management**: Secure Slack and Salesforce tokens
- **Access Control**: Limit Salesforce API permissions
- **Logging**: Avoid logging sensitive data
- **Error Handling**: Sanitize error messages

### **Configuration**
```bash
# Required permissions
- Salesforce: Read access to Opportunities, Accounts, Users
- Slack: App mentions, message reading, posting
- Snowflake: Read access to analytics tables (future)
```

## 🚀 **Deployment**

### **Production Setup**
```bash
# 1. Set up environment
cp env.example .env
# Edit .env with production credentials

# 2. Install dependencies
pip install -r requirements.txt

# 3. Test connection
python -c "from app.whizzy_bot import WhizzyBot; bot = WhizzyBot()"

# 4. Start bot
python app/whizzy_bot.py
```

### **Process Management**
```bash
# Using systemd (Linux)
sudo systemctl enable whizzy-bot
sudo systemctl start whizzy-bot

# Using PM2 (Node.js process manager)
pm2 start app/whizzy_bot.py --name whizzy-bot
pm2 save
pm2 startup
```

### **Monitoring**
- **Logs**: Check application logs for errors
- **Performance**: Monitor response times
- **Uptime**: Ensure bot stays connected
- **Usage**: Track query patterns and volume

## 🤝 **Contributing**

### **Development Workflow**
1. **Fork** the repository
2. **Create** a feature branch
3. **Develop** your changes
4. **Test** thoroughly
5. **Submit** a pull request

### **Code Standards**
- **Python**: Follow PEP 8 guidelines
- **SQL**: Use dbt best practices
- **Documentation**: Update README and docstrings
- **Testing**: Add tests for new features

## 📞 **Support**

### **Common Issues**
- **Connection Errors**: Check Salesforce credentials
- **Slack Issues**: Verify bot tokens and permissions
- **Data Issues**: Confirm Salesforce data access
- **Performance**: Monitor query response times

### **Getting Help**
- **Documentation**: Check this README and architecture docs
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub discussions for questions
- **Contributions**: Submit pull requests for improvements

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Salesforce**: For the robust API and data platform
- **Slack**: For the excellent bot framework
- **dbt**: For the analytics transformation framework
- **Community**: For feedback and contributions

---

**Whizzy Bot** - Making Salesforce analytics accessible to everyone! 🚀
