#!/usr/bin/env python3
"""
Real Snowflake MCP Integration
Connects to actual Snowflake and executes complex analytics queries
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
import snowflake.connector
import structlog
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = structlog.get_logger()

class RealSnowflakeMCP:
    """Real Snowflake MCP integration"""
    
    def __init__(self):
        self.snowflake_config = {
            "account": os.getenv("SNOWFLAKE_ACCOUNT"),
            "user": os.getenv("SNOWFLAKE_USER"),
            "password": os.getenv("SNOWFLAKE_PASSWORD"),
            "role": os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
            "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "XSMALL"),
            "database": os.getenv("SNOWFLAKE_DATABASE"),
            "schema": os.getenv("SNOWFLAKE_SCHEMA")
        }
        
        # Test connection on initialization
        self._test_connection()
    
    def _test_connection(self):
        """Test Snowflake connection"""
        try:
            conn = snowflake.connector.connect(**self.snowflake_config)
            cursor = conn.cursor()
            cursor.execute("SELECT CURRENT_VERSION(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
            version, database, schema = cursor.fetchone()
            logger.info("Snowflake MCP connection successful", 
                       version=version, database=database, schema=schema)
            conn.close()
        except Exception as e:
            logger.error("Snowflake MCP connection failed", error=str(e))
            raise
    
    async def execute_analytics_query(self, query: str) -> Dict[str, Any]:
        """Execute a complex analytics query against Snowflake"""
        
        try:
            conn = snowflake.connector.connect(**self.snowflake_config)
            cursor = conn.cursor()
            
            logger.info("Executing Snowflake analytics query", query_length=len(query))
            
            # Execute the query
            cursor.execute(query)
            
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
            
            # Calculate statistics
            total_rows = len(data)
            execution_time = cursor.sfqid  # Snowflake query ID for tracking
            
            conn.close()
            
            logger.info("Snowflake analytics query completed", 
                       total_rows=total_rows, execution_time=execution_time)
            
            return {
                "status": "success",
                "query": query,
                "total_rows": total_rows,
                "columns": columns,
                "data": data,
                "execution_id": execution_time,
                "summary": self._generate_summary(data, columns)
            }
            
        except Exception as e:
            logger.error("Snowflake analytics query failed", error=str(e))
            return {
                "status": "error",
                "query": query,
                "error": str(e)
            }
    
    def _generate_summary(self, data: List[Dict], columns: List[str]) -> Dict[str, Any]:
        """Generate summary statistics from query results"""
        if not data:
            return {"message": "No data returned"}
        
        summary = {
            "total_records": len(data),
            "columns": columns,
            "sample_records": data[:5]  # First 5 records
        }
        
        # Add numeric column statistics
        numeric_columns = []
        for col in columns:
            if data and isinstance(data[0].get(col), (int, float)):
                numeric_columns.append(col)
        
        if numeric_columns:
            summary["numeric_columns"] = numeric_columns
            summary["statistics"] = {}
            
            for col in numeric_columns:
                values = [row[col] for row in data if row[col] is not None]
                if values:
                    summary["statistics"][col] = {
                        "min": min(values),
                        "max": max(values),
                        "avg": sum(values) / len(values),
                        "count": len(values)
                    }
        
        return summary
    
    async def execute_complex_analytics(self, intent: str, dbt_models: List[str]) -> Dict[str, Any]:
        """Execute complex analytics based on intent and available DBT models"""
        
        # Generate appropriate query based on intent
        if intent == "EXECUTIVE_BRIEFING":
            query = self._generate_executive_briefing_query(dbt_models)
        elif intent == "ANALYTICS_DEEP":
            query = self._generate_deep_analytics_query(dbt_models)
        else:
            query = self._generate_general_analytics_query(dbt_models)
        
        return await self.execute_analytics_query(query)
    
    def _generate_executive_briefing_query(self, dbt_models: List[str]) -> str:
        """Generate executive briefing query using staging tables"""
        
        # Use staging tables since DBT models may not exist yet
        return """
        SELECT 
            'Executive Briefing' as report_type,
            CURRENT_TIMESTAMP() as generated_at,
            COUNT(*) as total_opportunities,
            SUM(OPPORTUNITY_AMOUNT) as total_pipeline_value,
            AVG(OPPORTUNITY_AMOUNT) as avg_deal_size,
            COUNT(CASE WHEN STAGE_NAME = 'Closed Won' THEN 1 END) as won_opportunities,
            COUNT(CASE WHEN STAGE_NAME = 'Closed Won' THEN 1 END) / NULLIF(COUNT(*), 0) as win_rate,
            AVG(DATEDIFF('day', CREATED_DATE, CLOSE_DATE)) as avg_days_to_close,
            COUNT(CASE WHEN CLOSE_DATE < CURRENT_DATE AND STAGE_NAME NOT IN ('Closed Won', 'Closed Lost') THEN 1 END) as overdue_opportunities,
            SUM(CASE WHEN CLOSE_DATE < CURRENT_DATE AND STAGE_NAME NOT IN ('Closed Won', 'Closed Lost') THEN OPPORTUNITY_AMOUNT ELSE 0 END) as overdue_value
        FROM stg_sf__opportunity 
        WHERE OPPORTUNITY_AMOUNT > 0
        """
    
    def _generate_deep_analytics_query(self, dbt_models: List[str]) -> str:
        """Generate deep analytics query"""
        
        return """
        WITH opportunity_metrics AS (
            SELECT 
                DATE_TRUNC('month', CLOSE_DATE) as month,
                STAGE_NAME,
                COUNT(*) as opportunity_count,
                SUM(OPPORTUNITY_AMOUNT) as total_amount,
                AVG(OPPORTUNITY_AMOUNT) as avg_amount,
                COUNT(CASE WHEN STAGE_NAME = 'Closed Won' THEN 1 END) as won_count,
                SUM(CASE WHEN STAGE_NAME = 'Closed Won' THEN OPPORTUNITY_AMOUNT ELSE 0 END) as won_amount
            FROM stg_sf__opportunity
            WHERE OPPORTUNITY_AMOUNT > 0
            GROUP BY 1, 2
        ),
        
        trend_analysis AS (
            SELECT 
                month,
                SUM(opportunity_count) as total_opportunities,
                SUM(total_amount) as total_pipeline,
                SUM(won_amount) as total_won,
                AVG(avg_amount) as avg_deal_size,
                SUM(won_count) / NULLIF(SUM(opportunity_count), 0) as win_rate,
                LAG(SUM(won_amount)) OVER (ORDER BY month) as prev_month_won,
                (SUM(won_amount) - LAG(SUM(won_amount)) OVER (ORDER BY month)) / 
                NULLIF(LAG(SUM(won_amount)) OVER (ORDER BY month), 0) as growth_rate
            FROM opportunity_metrics
            GROUP BY 1
        )
        
        SELECT 
            month,
            total_opportunities,
            total_pipeline,
            total_won,
            avg_deal_size,
            win_rate,
            growth_rate,
            CASE 
                WHEN growth_rate > 0.1 THEN 'Strong Growth'
                WHEN growth_rate > 0 THEN 'Moderate Growth'
                WHEN growth_rate > -0.1 THEN 'Slight Decline'
                ELSE 'Significant Decline'
            END as trend_indicator
        FROM trend_analysis
        ORDER BY month DESC
        LIMIT 12
        """
    
    def _generate_general_analytics_query(self, dbt_models: List[str]) -> str:
        """Generate general analytics query"""
        
        return """
        SELECT 
            'General Analytics' as report_type,
            COUNT(*) as total_opportunities,
            SUM(OPPORTUNITY_AMOUNT) as total_pipeline_value,
            AVG(OPPORTUNITY_AMOUNT) as avg_deal_size,
            COUNT(CASE WHEN STAGE_NAME = 'Closed Won' THEN 1 END) as won_opportunities,
            SUM(CASE WHEN STAGE_NAME = 'Closed Won' THEN OPPORTUNITY_AMOUNT ELSE 0 END) as won_revenue,
            COUNT(CASE WHEN STAGE_NAME = 'Closed Won' THEN 1 END) / NULLIF(COUNT(*), 0) as win_rate,
            AVG(DATEDIFF('day', CREATED_DATE, CLOSE_DATE)) as avg_days_to_close
        FROM stg_sf__opportunity
        WHERE OPPORTUNITY_AMOUNT > 0
        """
    
    async def get_dbt_model_data(self, model_name: str) -> Dict[str, Any]:
        """Get data from a specific DBT model"""
        
        query = f"SELECT * FROM {model_name} LIMIT 100"
        return await self.execute_analytics_query(query)
    
    async def execute_custom_query(self, custom_query: str) -> Dict[str, Any]:
        """Execute a custom SQL query"""
        return await self.execute_analytics_query(custom_query)

# Example usage
async def test_real_snowflake_mcp():
    """Test the real Snowflake MCP"""
    mcp = RealSnowflakeMCP()
    
    # Test basic query
    result = await mcp.execute_analytics_query("SELECT COUNT(*) as total_opportunities FROM stg_sf__opportunity")
    print(f"Basic Query Result: {json.dumps(result, indent=2)}")
    
    # Test complex analytics
    complex_result = await mcp.execute_complex_analytics(
        "EXECUTIVE_BRIEFING", 
        ["m_pipeline_health", "a_executive_dashboard"]
    )
    print(f"Complex Analytics Result: {json.dumps(complex_result, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_real_snowflake_mcp())
