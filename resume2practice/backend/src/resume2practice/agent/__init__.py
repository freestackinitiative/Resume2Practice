import logging 
import asyncio 

logger = logging.getLogger(__name__)

try:
    from resume2practice.models.factory import model_factory
except ImportError:
    logger.error("Unable to import custom module")
    raise

from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Callable

class BaseAgent(ABC):
    """The base class used for implementing agents."""
    def __init__(self,
                vendor: Optional[str] = None, 
                model_id: Optional[str] = None, 
                role: str = "You are a helpful AI agent.",
                prompt_template: Optional[str] = "{messages}",
                tools: Optional[List[Callable[..., Any]]] = None,
                response_format: BaseModel = None,
                settings: Optional[Dict[str, Any]] = None):
        self._llm: Any = model_factory.get_model(vendor=vendor, model_id=model_id, settings=settings)
        self._model_id: str = model_id
        self._vendor: str = vendor
        self._role: str = role
        self._prompt_template: str = prompt_template
        self._tools: Optional[List[Callable[..., Any]]] = tools or []
        self._response_format = response_format
        self._settings: Optional[Dict[str, Any]] = settings or {}

    @abstractmethod
    def init_agent(self, *args, **kwargs) -> None:
        """Code to initialize an agentic chain"""
        pass

    @abstractmethod
    def invoke(self, context: Optional[Dict[str, Any] | str]) -> Any:
        """Invokes the language model or agent workflow"""
        pass
    
    @abstractmethod
    async def ainvoke(self, context: Optional[Dict[str, Any] | str]) -> Any:
        """Invokes the language model or agent workflow (async)"""
        return await asyncio.to_thread(self.invoke, context)
    
