import logging
from typing import Any, Dict
from simple_salesforce import Salesforce
from .base_tool import BaseTool

logger = logging.getLogger(__name__)

class SalesforceTool(BaseTool):
    """A tool for interacting with Salesforce by executing SOQL queries."""
    name = "salesforce_tool"
    description = "Used for executing a SOQL query against Salesforce."

    def __init__(self, sf_client: Salesforce):
        self.sf = sf_client

    def run(self, soql_query: str) -> Dict[str, Any]:
        """
        Runs a pre-written SOQL query against Salesforce.

        Args:
            soql_query: The SOQL query string to execute.

        Returns:
            A dictionary containing the query result or an error.
        """
        if not self.sf:
            return {"error": "Salesforce client not initialized."}

        logger.info(f"Executing SOQL query: {soql_query}")
        try:
            result = self.sf.query_all(soql_query)
            return {"records": result.get('records', [])}
        except Exception as e:
            logger.error(f"Salesforce query failed: {e}", exc_info=True)
            return {"error": str(e), "query": soql_query}
