# 🏗️ DBT Pipeline Documentation

## Overview

The Whizzy Bot DBT pipeline provides comprehensive analytics capabilities through a series of carefully designed models that transform raw Salesforce data into actionable business intelligence.

## 📊 **Model Architecture**

```
Raw Salesforce Data
    ↓
┌─────────────────┐
│ Staging Models  │ → Data cleaning and validation
└─────────────────┘
    ↓
┌─────────────────┐
│ Dimension Models│ → Business entities (accounts, users)
└─────────────────┘
    ↓
┌─────────────────┐
│ Fact Models     │ → Business events (opportunities, stage transitions)
└─────────────────┘
    ↓
┌─────────────────┐
│ Mart Models     │ → Business metrics and KPIs
└─────────────────┘
    ↓
┌─────────────────┐
│ Analytics Models│ → Advanced insights and dashboards
└─────────────────┘
```

## 🎯 **Model Categories**

### **1. Mart Models (Core Business Metrics)**

#### **`m_pipeline_health`**
- **Purpose**: Comprehensive pipeline health analysis
- **Key Metrics**: 
  - Pipeline health score (0-100)
  - Win rate trends
  - Risk assessment
  - Quarter-over-quarter growth
- **Use Cases**: Executive reporting, pipeline optimization

#### **`m_deal_velocity_analysis`**
- **Purpose**: Track deal movement through pipeline stages
- **Key Metrics**:
  - Days in each stage
  - Bottleneck identification
  - Owner performance
  - Velocity trends
- **Use Cases**: Process optimization, sales coaching

#### **`m_revenue_forecasting`**
- **Purpose**: Predict future revenue using multiple models
- **Key Metrics**:
  - Multiple forecast models (trend, rolling avg, seasonal, pipeline)
  - Confidence intervals
  - Forecast accuracy metrics
  - Risk assessment
- **Use Cases**: Revenue planning, budget forecasting

#### **`m_forecast`** (Existing)
- **Purpose**: Historical win rates and velocity for forecasting
- **Key Metrics**: Win rates, deal velocity, historical trends

#### **`m_slippage_impact_quarter`** (Existing)
- **Purpose**: Quarterly slippage analysis
- **Key Metrics**: Slippage trends, impact assessment

#### **`m_stage_velocity_quarter`** (Existing)
- **Purpose**: Stage velocity by quarter
- **Key Metrics**: Stage progression, velocity trends

### **2. Analytics Models (Advanced Insights)**

#### **`a_executive_dashboard`**
- **Purpose**: High-level KPIs for leadership
- **Key Metrics**:
  - Revenue summary (QTD, MTD, YTD)
  - Performance metrics
  - Risk indicators
  - Health scores
  - Key insights and recommendations
- **Use Cases**: Executive briefings, strategic planning

#### **`a_win_rate_trend_analysis`** (Existing)
- **Purpose**: Win rate trends by industry and owner
- **Key Metrics**: Win rate changes, performance trends

#### **`a_slippage_pattern_analysis`** (Existing)
- **Purpose**: Slippage pattern identification
- **Key Metrics**: Slippage patterns, risk factors

#### **`a_comprehensive_slippage_analysis`** (Existing)
- **Purpose**: Comprehensive slippage insights
- **Key Metrics**: Slippage drivers, mitigation strategies

#### **`a_win_rate_by_owner`** (Existing)
- **Purpose**: Win rate analysis by sales rep
- **Key Metrics**: Individual performance, coaching opportunities

#### **`a_win_rate_by_industry`** (Existing)
- **Purpose**: Win rate analysis by industry
- **Key Metrics**: Industry performance, market insights

## 🔄 **Data Flow**

### **Pipeline Health Flow**
```
stg_sf__opportunity → m_pipeline_health → a_executive_dashboard
```

### **Velocity Analysis Flow**
```
stg_sf__opportunity + stg_sf__user → m_deal_velocity_analysis
```

### **Forecasting Flow**
```
stg_sf__opportunity → m_revenue_forecasting → a_executive_dashboard
```

## 📈 **Key Business Metrics**

### **Pipeline Health Score (0-100)**
- **Win Rate Component** (25 points)
  - 30%+ win rate: 25 points
  - 20-30% win rate: 20 points
  - 10-20% win rate: 15 points
  - <10% win rate: 10 points

- **Overdue Pipeline Component** (25 points)
  - <10% overdue: 25 points
  - 10-20% overdue: 20 points
  - 20-30% overdue: 15 points
  - >30% overdue: 10 points

- **Deal Size Component** (25 points)
  - $100k+ average: 25 points
  - $50-100k average: 20 points
  - $25-50k average: 15 points
  - <$25k average: 10 points

- **Pipeline Volume Component** (25 points)
  - 100+ opportunities: 25 points
  - 50-100 opportunities: 20 points
  - 25-50 opportunities: 15 points
  - <25 opportunities: 10 points

### **Forecast Models**
1. **Trend Projection**: Simple growth rate projection
2. **Rolling Average**: 3-month moving average
3. **Seasonal Adjustment**: Month-of-year patterns
4. **Pipeline-Based**: Probability-weighted pipeline
5. **Combined Forecast**: Weighted average of all models

### **Velocity Metrics**
- **Days in Stage**: Average time in each pipeline stage
- **Bottleneck Identification**: Stages with >30 days average
- **Owner Performance**: Individual velocity metrics
- **Quarterly Trends**: Velocity changes over time

## 🎯 **Use Cases by Query Type**

### **Executive Briefings**
- **Models**: `m_pipeline_health`, `a_executive_dashboard`, `m_revenue_forecasting`
- **Insights**: Overall health, revenue trends, strategic recommendations

### **Pipeline Analysis**
- **Models**: `m_pipeline_health`, `m_deal_velocity_analysis`
- **Insights**: Health score, bottlenecks, optimization opportunities

### **Revenue Forecasting**
- **Models**: `m_revenue_forecasting`, `m_forecast`
- **Insights**: Multiple forecast models, confidence intervals, risk assessment

### **Slippage Analysis**
- **Models**: `m_slippage_impact_quarter`, `a_slippage_pattern_analysis`
- **Insights**: Slippage trends, patterns, mitigation strategies

### **Performance Analysis**
- **Models**: `a_win_rate_by_owner`, `a_win_rate_by_industry`
- **Insights**: Individual and industry performance, coaching opportunities

## 🔧 **Model Dependencies**

```
stg_sf__opportunity
    ↓
├── m_pipeline_health
├── m_deal_velocity_analysis
├── m_revenue_forecasting
└── m_forecast
    ↓
├── a_executive_dashboard
├── a_win_rate_trend_analysis
└── a_slippage_pattern_analysis
```

## 📊 **Sample Queries**

### **Pipeline Health Query**
```sql
SELECT 
  quarter_label,
  pipeline_health_score,
  health_status,
  risk_level,
  key_insight
FROM m_pipeline_health
ORDER BY quarter DESC
LIMIT 5;
```

### **Velocity Analysis Query**
```sql
SELECT 
  dimension,
  avg_days_in_stage,
  bottleneck_level,
  monthly_value_impact
FROM m_deal_velocity_analysis
WHERE metric_type = 'stage_velocity'
ORDER BY avg_days_in_stage DESC;
```

### **Revenue Forecast Query**
```sql
SELECT 
  month_label,
  actual_revenue,
  combined_forecast,
  forecast_quality,
  forecast_risk
FROM m_revenue_forecasting
ORDER BY month DESC
LIMIT 12;
```

### **Executive Dashboard Query**
```sql
SELECT 
  qtd_won_revenue,
  current_pipeline_value,
  overall_win_rate,
  pipeline_health,
  key_insight,
  recommendation
FROM a_executive_dashboard
WHERE dashboard_type = 'executive_dashboard';
```

## 🚀 **Integration with Whizzy Bot**

The DBT models are integrated into the Whizzy Bot through the `DbtSelectorAgent` and `DbtExecutorAgent`:

1. **Intent Classification**: Bot determines if DBT analytics are needed
2. **Model Selection**: `DbtSelectorAgent` chooses relevant models
3. **Data Execution**: `DbtExecutorAgent` runs the models
4. **Data Fusion**: Results are combined with Salesforce data
5. **Response Generation**: Insights are presented to users

## 🔄 **Refresh Schedule**

- **Mart Models**: Daily refresh
- **Analytics Models**: Daily refresh
- **Executive Dashboard**: Real-time (on-demand)

## 📈 **Performance Optimization**

- **Materialization**: All models use table materialization for performance
- **Partitioning**: Models are partitioned by date where applicable
- **Indexing**: Key columns are indexed for fast queries
- **Caching**: Frequently accessed data is cached

## 🎯 **Future Enhancements**

1. **Machine Learning Models**: Predictive analytics for deal scoring
2. **Real-time Streaming**: Real-time data updates
3. **Advanced Visualizations**: Chart and dashboard generation
4. **Custom Metrics**: User-defined KPIs
5. **Alerting**: Automated alerts for key metrics

This DBT pipeline provides a solid foundation for advanced sales analytics and can be extended as business needs evolve.
