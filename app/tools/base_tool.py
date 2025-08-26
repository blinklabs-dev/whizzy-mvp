from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    """
    Abstract base class for a tool that the agent can use.
    """
    name: str
    description: str

    @abstractmethod
    async def run(self, query: str) -> Dict[str, Any]:
        """
        Run the tool with a given query.

        Args:
            query: The natural language query or instruction for the tool.

        Returns:
            A dictionary containing the result from the tool.
        """
        pass
