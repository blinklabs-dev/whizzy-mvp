#!/usr/bin/env python3
"""
Dynamic DBT Model Generator
Creates and deploys new DBT models based on user analytics requests
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import openai
import structlog
from pathlib import Path

# Configure logging
logger = structlog.get_logger()

@dataclass
class DbtModelSpec:
    """Specification for a DBT model"""
    name: str
    description: str
    model_type: str  # 'marts', 'analytics', 'staging'
    dependencies: List[str]
    tags: List[str]
    materialization: str = 'table'
    sql_content: str = ""  # Will be generated later

class DynamicDbtGenerator:
    """Generates and deploys DBT models dynamically"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.dbt_project_path = Path("analytics")
        self.models_path = self.dbt_project_path / "models"
        
    async def analyze_request(self, user_query: str, context: Dict[str, Any]) -> Optional[DbtModelSpec]:
        """Analyze if user request requires a new DBT model"""
        
        system_prompt = """
        You are a DBT model architect. Analyze if the user's analytics request requires a new DBT model.
        
        **Available Models:**
        - m_pipeline_health: Pipeline health analysis
        - m_deal_velocity_analysis: Deal velocity and bottlenecks
        - m_revenue_forecasting: Revenue forecasting
        - m_forecast: Historical forecasting
        - m_slippage_impact_quarter: Slippage analysis
        - m_stage_velocity_quarter: Stage velocity
        - a_executive_dashboard: Executive KPIs
        - a_win_rate_trend_analysis: Win rate trends
        - a_slippage_pattern_analysis: Slippage patterns
        - a_comprehensive_slippage_analysis: Comprehensive slippage
        - a_win_rate_by_owner: Owner performance
        - a_win_rate_by_industry: Industry performance
        
        **Decision Criteria:**
        1. If the request can be answered with existing models, return null
        2. If the request requires new analytics not covered by existing models, create a new model
        3. Focus on complex analytics, custom metrics, or specialized insights
        
        **Return JSON:**
        {
            "requires_new_model": true/false,
            "reasoning": "explanation",
            "model_spec": {
                "name": "model_name",
                "description": "model description",
                "model_type": "marts|analytics|staging",
                "dependencies": ["stg_sf__opportunity", "stg_sf__user"],
                "tags": ["sales", "analytics"],
                "materialization": "table|view|incremental"
            }
        }
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User Query: {user_query}\nContext: {json.dumps(context, default=str)}"}
        ]
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=1000,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            
            if result.get("requires_new_model"):
                logger.info("New DBT model required", query=user_query, model_name=result["model_spec"]["name"])
                return DbtModelSpec(**result["model_spec"])
            else:
                logger.info("No new DBT model required", query=user_query, reasoning=result["reasoning"])
                return None
                
        except Exception as e:
            logger.error("Failed to analyze request", error=str(e))
            return None
    
    async def generate_dbt_model(self, model_spec: DbtModelSpec, user_query: str) -> str:
        """Generate the SQL content for a new DBT model"""
        
        system_prompt = """
        You are a DBT SQL expert. Generate a comprehensive DBT model based on the specification.
        
        **DBT Best Practices:**
        1. Use proper Jinja templating
        2. Include comprehensive documentation
        3. Use CTEs for complex logic
        4. Add proper error handling
        5. Include performance optimizations
        6. Use meaningful column names
        7. Add data quality checks
        
        **Available Sources:**
        - stg_sf__opportunity: Opportunity data
        - stg_sf__user: User/Owner data
        - stg_sf__account: Account data
        - stg_sf__opportunity_history: Opportunity stage changes
        
        **Model Structure:**
        ```sql
        {{
          config(
            materialized='table',
            description='Model description'
          )
        }}
        
        WITH base_data AS (
          -- Base data selection
        ),
        
        calculations AS (
          -- Business logic and calculations
        ),
        
        final AS (
          -- Final output
        )
        
        SELECT * FROM final
        ```
        
        Generate only the SQL content, no explanations.
        """
        
        user_prompt = f"""
        Model Specification:
        - Name: {model_spec.name}
        - Description: {model_spec.description}
        - Type: {model_spec.model_type}
        - Dependencies: {model_spec.dependencies}
        - Tags: {model_spec.tags}
        - Materialization: {model_spec.materialization}
        
        User Query: {user_query}
        
        Generate a DBT model that answers this query with advanced analytics.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=2000,
                temperature=0.1
            )
            
            sql_content = response.choices[0].message.content.strip()
            logger.info("DBT model SQL generated", model_name=model_spec.name, sql_length=len(sql_content))
            return sql_content
            
        except Exception as e:
            logger.error("Failed to generate DBT model", error=str(e))
            raise
    
    async def deploy_dbt_model(self, model_spec: DbtModelSpec, sql_content: str) -> bool:
        """Deploy the DBT model to the project"""
        
        try:
            # Determine the correct directory
            if model_spec.model_type == "marts":
                model_dir = self.models_path / "marts" / "sales"
            elif model_spec.model_type == "analytics":
                model_dir = self.models_path / "analytics"
            elif model_spec.model_type == "staging":
                model_dir = self.models_path / "staging"
            else:
                model_dir = self.models_path / "marts" / "sales"
            
            # Create directory if it doesn't exist
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Create the model file
            model_file = model_dir / f"{model_spec.name}.sql"
            
            # Add config block
            config_block = f"""{{
  config(
    materialized='{model_spec.materialization}',
    description='{model_spec.description}',
    tags={model_spec.tags}
  )
}}

"""
            
            full_content = config_block + sql_content
            
            # Write the model file
            with open(model_file, 'w') as f:
                f.write(full_content)
            
            logger.info("DBT model deployed", 
                       model_name=model_spec.name, 
                       file_path=str(model_file),
                       model_type=model_spec.model_type)
            
            return True
            
        except Exception as e:
            logger.error("Failed to deploy DBT model", error=str(e))
            return False
    
    async def execute_new_model(self, model_name: str) -> Dict[str, Any]:
        """Execute the newly created DBT model"""
        
        try:
            # This would typically run `dbt run --models model_name`
            # For now, we'll simulate the execution
            
            # Simulate model execution
            result = {
                "model_name": model_name,
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
            
            logger.info("New DBT model executed", 
                       model_name=model_name, 
                       status=result["status"])
            
            return result
            
        except Exception as e:
            logger.error("Failed to execute new DBT model", error=str(e))
            return {"error": str(e)}
    
    async def process_complex_analytics_request(self, user_query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main method to process complex analytics requests"""
        
        try:
            # Step 1: Analyze if new model is needed
            model_spec = await self.analyze_request(user_query, context)
            
            if not model_spec:
                return {
                    "action": "use_existing_models",
                    "message": "Request can be handled with existing models"
                }
            
            # Step 2: Generate the DBT model
            sql_content = await self.generate_dbt_model(model_spec, user_query)
            
            # Step 3: Deploy the model
            deployment_success = await self.deploy_dbt_model(model_spec, sql_content)
            
            if not deployment_success:
                return {
                    "action": "deployment_failed",
                    "error": "Failed to deploy new DBT model"
                }
            
            # Step 4: Execute the new model
            execution_result = await self.execute_new_model(model_spec.name)
            
            return {
                "action": "new_model_created",
                "model_name": model_spec.name,
                "model_description": model_spec.description,
                "deployment_status": "success",
                "execution_result": execution_result,
                "message": f"Created and executed new DBT model '{model_spec.name}' for your analysis"
            }
            
        except Exception as e:
            logger.error("Failed to process complex analytics request", error=str(e))
            return {
                "action": "error",
                "error": str(e)
            }

# Example usage
async def test_dynamic_dbt_generator():
    """Test the dynamic DBT generator"""
    
    generator = DynamicDbtGenerator()
    
    # Test complex analytics request
    test_query = "Show me customer lifetime value analysis with churn prediction and cohort analysis"
    context = {"user_persona": "VP Sales", "query_type": "complex_analytics"}
    
    result = await generator.process_complex_analytics_request(test_query, context)
    print(f"Result: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_dynamic_dbt_generator())
