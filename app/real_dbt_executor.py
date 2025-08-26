#!/usr/bin/env python3
"""
Real DBT Executor with Snowflake Integration
Executes actual DBT models against Snowflake warehouse
"""

import os
import json
import asyncio
import subprocess
import logging
from typing import Dict, List, Optional, Any
import snowflake.connector
import structlog
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = structlog.get_logger()

class RealDbtExecutor:
    """Real DBT executor with Snowflake integration"""
    
    def __init__(self):
        self.dbt_project_path = Path("analytics")
        self.snowflake_config = {
            "account": os.getenv("SNOWFLAKE_ACCOUNT"),
            "user": os.getenv("SNOWFLAKE_USER"),
            "password": os.getenv("SNOWFLAKE_PASSWORD"),
            "role": os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
            "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "XSMALL"),
            "database": os.getenv("SNOWFLAKE_DATABASE"),
            "schema": os.getenv("SNOWFLAKE_SCHEMA")
        }
        
        # Validate Snowflake connection
        self._test_snowflake_connection()
    
    def _test_snowflake_connection(self):
        """Test Snowflake connection"""
        try:
            conn = snowflake.connector.connect(**self.snowflake_config)
            cursor = conn.cursor()
            cursor.execute("SELECT CURRENT_VERSION()")
            version = cursor.fetchone()[0]
            logger.info("Snowflake connection successful", version=version)
            conn.close()
        except Exception as e:
            logger.error("Snowflake connection failed", error=str(e))
            raise
    
    async def execute_dbt_model(self, model_name: str) -> Dict[str, Any]:
        """Execute a DBT model against Snowflake"""
        
        try:
            # Change to DBT project directory
            original_cwd = os.getcwd()
            os.chdir(self.dbt_project_path)
            
            # Execute DBT run for specific model
            cmd = [
                "dbt", "run", 
                "--models", model_name,
                "--target", "snowflake",
                "--vars", json.dumps({"target_database": self.snowflake_config["database"]})
            ]
            
            logger.info("Executing DBT model", model_name=model_name, cmd=" ".join(cmd))
            
            # Run DBT command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                # Parse DBT output for execution details
                execution_info = self._parse_dbt_output(result.stdout)
                
                # Query the executed model for data
                model_data = await self._query_model_data(model_name)
                
                logger.info("DBT model executed successfully", 
                           model_name=model_name,
                           rows_affected=execution_info.get("rows_affected", 0))
                
                return {
                    "status": "success",
                    "model_name": model_name,
                    "execution_info": execution_info,
                    "data_preview": model_data,
                    "dbt_output": result.stdout[-500:]  # Last 500 chars
                }
            else:
                logger.error("DBT execution failed", 
                           model_name=model_name,
                           error=result.stderr)
                return {
                    "status": "error",
                    "model_name": model_name,
                    "error": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            logger.error("DBT execution timed out", model_name=model_name)
            return {
                "status": "timeout",
                "model_name": model_name,
                "error": "Execution timed out after 5 minutes"
            }
        except Exception as e:
            logger.error("DBT execution failed", model_name=model_name, error=str(e))
            return {
                "status": "error",
                "model_name": model_name,
                "error": str(e)
            }
        finally:
            # Restore original directory
            os.chdir(original_cwd)
    
    def _parse_dbt_output(self, output: str) -> Dict[str, Any]:
        """Parse DBT output for execution details"""
        try:
            # Look for execution statistics
            lines = output.split('\n')
            rows_affected = 0
            execution_time = "0s"
            
            for line in lines:
                if "rows affected" in line.lower():
                    # Extract number of rows
                    import re
                    match = re.search(r'(\d+)\s+rows?\s+affected', line.lower())
                    if match:
                        rows_affected = int(match.group(1))
                elif "completed successfully" in line.lower():
                    # Extract execution time
                    import re
                    match = re.search(r'completed successfully in (\d+\.?\d*s?)', line.lower())
                    if match:
                        execution_time = match.group(1)
            
            return {
                "rows_affected": rows_affected,
                "execution_time": execution_time,
                "status": "completed"
            }
        except Exception as e:
            logger.warning("Failed to parse DBT output", error=str(e))
            return {"status": "completed", "rows_affected": 0, "execution_time": "unknown"}
    
    async def _query_model_data(self, model_name: str) -> Dict[str, Any]:
        """Query the executed model for data preview"""
        try:
            conn = snowflake.connector.connect(**self.snowflake_config)
            cursor = conn.cursor()
            
            # Query the model (assuming it's in the same schema)
            query = f"SELECT * FROM {model_name} LIMIT 10"
            cursor.execute(query)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Get data
            rows = cursor.fetchall()
            data = [dict(zip(columns, row)) for row in rows]
            
            conn.close()
            
            return {
                "total_records": len(data),
                "columns": columns,
                "sample_data": data
            }
            
        except Exception as e:
            logger.warning("Failed to query model data", model_name=model_name, error=str(e))
            return {
                "total_records": 0,
                "columns": [],
                "sample_data": [],
                "error": str(e)
            }
    
    async def execute_multiple_models(self, model_names: List[str]) -> Dict[str, Any]:
        """Execute multiple DBT models"""
        results = {}
        
        for model_name in model_names:
            logger.info("Executing DBT model", model_name=model_name)
            result = await self.execute_dbt_model(model_name)
            results[model_name] = result
            
            # Add delay between executions to avoid overwhelming Snowflake
            await asyncio.sleep(2)
        
        return results
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test the complete DBT + Snowflake setup"""
        try:
            # Test Snowflake connection
            conn = snowflake.connector.connect(**self.snowflake_config)
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_WAREHOUSE()")
            db_info = cursor.fetchone()
            
            # Test DBT project
            cursor.execute("SHOW TABLES LIKE '%dbt%'")
            dbt_tables = cursor.fetchall()
            
            conn.close()
            
            return {
                "status": "success",
                "database": db_info[0],
                "schema": db_info[1],
                "warehouse": db_info[2],
                "dbt_tables_found": len(dbt_tables)
            }
            
        except Exception as e:
            logger.error("Connection test failed", error=str(e))
            return {
                "status": "error",
                "error": str(e)
            }

# Example usage
async def test_real_dbt():
    """Test the real DBT executor"""
    executor = RealDbtExecutor()
    
    # Test connection
    connection_test = await executor.test_connection()
    print(f"Connection Test: {json.dumps(connection_test, indent=2)}")
    
    # Test model execution (if connection successful)
    if connection_test["status"] == "success":
        result = await executor.execute_dbt_model("m_pipeline_health")
        print(f"Model Execution: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_real_dbt())
