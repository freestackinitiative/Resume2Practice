from resume2practice.agent import BaseAgent
from resume2practice.agent.error import AgentExecutionError
from resume2practice.agent.roles import (
    RESUME_PROFILER, 
    JOB_DESCRIPTION_PROFILER, 
    SCORECARD_INTAKE, 
    SCORECARD_GENERATOR, 
    TASK_GENERATOR
)
from resume2practice.models.schema import (
    ResumeProfile,
    JobDescriptionProfile,
    ScorecardIntake,
    Scorecard,
    TaskList
)
from pydantic import BaseModel
from typing_extensions import override
from typing import Optional, Dict, List, Callable, Any
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage


class ResumeProfiler(BaseAgent):
    def __init__(self, 
                vendor: Optional[str] = None, 
                model_id: Optional[str] = None, 
                role: str = RESUME_PROFILER,
                tools: Optional[List[Callable[..., Any]]] = None,
                response_format: Optional[BaseModel] = ResumeProfile, 
                settings: Optional[Dict[str, Any]] = None):
        super().__init__(vendor=vendor, model_id=model_id, role=role, tools=tools, settings=settings)
        self._agent = None
        self._response_format = response_format
        self.init_agent()
        self.metadata = {}

    @override
    def init_agent(self):
        if not self._llm:
            raise ValueError("Language model not initialized. Check model_factory")
        
        if self._response_format is not None and isinstance(self._response_format, BaseModel):
            self._llm = self._llm.with_structured_output(self._response_format)
        resume_profiler_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self._role),
            ("human", "{resume}")
        ])
        if self._agent is None:
            self._agent = resume_profiler_prompt | self._llm

    @override
    def invoke(self, context: Dict[str, Any]) -> Any:
        try:
            return self._agent.invoke(context)
        except Exception as ex:
            raise AgentExecutionError(
                f"An exception occurred while trying to invoke the following context: {context}\n{(str(ex))}"
            )
        
    @override
    async def ainvoke(self, context: Dict[str, Any]) -> Any:
        try:
            result = await self._agent.ainvoke(context)
            return result
        except Exception as ex:
            raise AgentExecutionError(
                f"An exception occurred while trying to invoke the following context: {context}\n{(str(ex))}"
            )
        
class JobDescriptionProfiler(BaseAgent):
    def __init__(self, 
                vendor: Optional[str] = None, 
                model_id: Optional[str] = None, 
                role: str = JOB_DESCRIPTION_PROFILER,
                tools: Optional[List[Callable[..., Any]]] = None,
                response_format: Optional[BaseModel] = JobDescriptionProfile, 
                settings: Optional[Dict[str, Any]] = None):
        super().__init__(vendor=vendor, model_id=model_id, role=role, tools=tools, settings=settings)
        self._agent = None
        self._response_format = response_format
        self.init_agent()
        self.metadata = {}

    @override
    def init_agent(self):
        if not self._llm:
            raise ValueError("Language model not initialized. Check model_factory")
        
        if self._response_format is not None and isinstance(self._response_format, BaseModel):
            self._llm = self._llm.with_structured_output(self._response_format)
        jd_profiler_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self._role),
            ("human", "{job_description}")
        ])
        if self._agent is None:
            self._agent = jd_profiler_prompt | self._llm

    @override
    def invoke(self, context: Dict[str, Any]) -> Any:
        try:
            return self._agent.invoke(context)
        except Exception as ex:
            raise AgentExecutionError(
                f"An exception occurred while trying to invoke the following context: {context}\n{(str(ex))}"
            )
        
    @override
    async def ainvoke(self, context: Dict[str, Any]) -> Any:
        try:
            result = await self._agent.ainvoke(context)
            return result
        except Exception as ex:
            raise AgentExecutionError(
                f"An exception occurred while trying to invoke the following context: {context}\n{(str(ex))}"
            )
        

class ScorecardGenerator(BaseAgent):
    def __init__(self, 
                vendor: Optional[str] = None, 
                model_id: Optional[str] = None, 
                role: str = SCORECARD_GENERATOR,
                tools: Optional[List[Callable[..., Any]]] = None,
                response_format: Optional[BaseModel] = Scorecard, 
                settings: Optional[Dict[str, Any]] = None):
        super().__init__(vendor=vendor, model_id=model_id, role=role, tools=tools, settings=settings)
        self._agent = None
        self.intake = None
        self._setup_intake()
        self._response_format = response_format
        self.init_agent()
        self.metadata = {}

    def _setup_intake(self) -> None:
        """Sets up the internal workflow to generate questions to ask the user to help with Scorecard generation"""
        scorecard_precheck_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=SCORECARD_INTAKE),
            ("human", "{resume_profile} {job_description_profile}")
        ])
        self.intake = scorecard_precheck_prompt | self._llm.with_structured_output(ScorecardIntake)

    @override
    def init_agent(self):
        if not self._llm:
            raise ValueError("Language model not initialized. Check model_factory")
        
        if self._response_format is not None and isinstance(self._response_format, BaseModel):
            self._llm = self._llm.with_structured_output(self._response_format)
        scorecard_generator_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self._role),
            ("human", "{resume_profile} {job_description_profile}")
        ])
        if self._agent is None:
            self._agent = scorecard_generator_prompt | self._llm

    @override
    def invoke(self, context: Dict[str, Any]) -> Any:
        try:
            return self._agent.invoke(context)
        except Exception as ex:
            raise AgentExecutionError(
                f"An exception occurred while trying to invoke the following context: {context}\n{(str(ex))}"
            )
        
    @override
    async def ainvoke(self, context: Dict[str, Any]) -> Any:
        try:
            result = await self._agent.ainvoke(context)
            return result
        except Exception as ex:
            raise AgentExecutionError(
                f"An exception occurred while trying to invoke the following context: {context}\n{(str(ex))}"
            )
        

class TaskGenerator(BaseAgent):
    def __init__(self, 
                vendor: Optional[str] = None, 
                model_id: Optional[str] = None, 
                role: str = TASK_GENERATOR,
                tools: Optional[List[Callable[..., Any]]] = None,
                response_format: Optional[BaseModel] = TaskList, 
                settings: Optional[Dict[str, Any]] = None):
        super().__init__(vendor=vendor, model_id=model_id, role=role, tools=tools, settings=settings)
        self._agent = None
        self._response_format = response_format
        self.init_agent()
        self.metadata = {}

    @override
    def init_agent(self):
        if not self._llm:
            raise ValueError("Language model not initialized. Check model_factory")
        
        if self._response_format is not None and isinstance(self._response_format, BaseModel):
            self._llm = self._llm.with_structured_output(self._response_format)
        task_generator_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self._role),
            ("human", "{job_description_profile} {scorecard}")
        ])
        if self._agent is None:
            self._agent = task_generator_prompt | self._llm

    @override
    def invoke(self, context: Dict[str, Any]) -> Any:
        try:
            return self._agent.invoke(context)
        except Exception as ex:
            raise AgentExecutionError(
                f"An exception occurred while trying to invoke the following context: {context}\n{(str(ex))}"
            )
        
    @override
    async def ainvoke(self, context: Dict[str, Any]) -> Any:
        try:
            result = await self._agent.ainvoke(context)
            return result
        except Exception as ex:
            raise AgentExecutionError(
                f"An exception occurred while trying to invoke the following context: {context}\n{(str(ex))}"
            )
    


        


    