from uuid import uuid4
from langgraph.graph import StateGraph, END, START
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
from resume2practice.models.schema import TaskGeneratorState
from resume2practice.agent.nodes import (
  ResumeProfiler,
  JobDescriptionProfiler,
  ScorecardGenerator,
  TaskGenerator
)
from resume2practice.agent.error import AgentExecutionError
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class Resume2Practice:
  def __init__(self, 
               resume_profiler_chain: ResumeProfiler,
               job_description_profiler_chain: JobDescriptionProfiler,
               scorecard_generator_chain: ScorecardGenerator,
               task_generator_chain: TaskGenerator,
               config: Optional[Dict[str, Any]] = None, 
               checkpointer: Optional[Any] = None):
    if config is None:
      config = {
          "configurable": {
              "thread_id": str(uuid4())
          }
      }
    self.config = config
    self.resume_profiler_agent = resume_profiler_chain
    self.job_description_profiler = job_description_profiler_chain
    self.scorecard_generator = scorecard_generator_chain
    self.task_generator = task_generator_chain
    self.checkpointer = checkpointer if checkpointer else MemorySaver()
    self.graph = None
    self.build_graph()

  async def resume_profiler_node(self, state: TaskGeneratorState, config: Optional[Dict[str, Any]] = None):
    logger.info("Resume Profiler: Generating profile from resume...")
    resume_profile = await self.resume_profiler_agent.ainvoke(state["resume"])
    logger.info("Resume Profiler: Resume profile complete!")
    return Command(
        update={"resume_profile": resume_profile.model_dump_json()}, goto="job_description_profiler"
    )

  async def job_description_profiler_node(self, state: TaskGeneratorState, config: Optional[Dict[str, Any]] = None):
    logger.info("Job Description Profiler: Generating profile from job description..")
    job_description_profile = await self.job_description_profiler.ainvoke(state["job_description"])
    logger.info("Job Description Profiler: Job description profile complete!")
    return Command(
        update={"job_description_profile": job_description_profile.model_dump_json()}, goto="scorecard_generator"
    )

  async def scorecard_generator_node(self, state: TaskGeneratorState, config: Optional[Dict[str, Any]] = None):
    logger.info("Scorecard Generator: Generating scorecard...")
    context = {
        "resume_profile": state["resume_profile"],
        "job_description_profile": state["job_description_profile"]
    }
    # Generate list of initial questions to help fill in the blanks
    precheck_list = await self.scorecard_generator.intake.ainvoke(context)
    added_context = interrupt(precheck_list.model_dump_json())
    logger.info(f"Added context: {added_context}")
    context.update({"additional_context": added_context})
    scorecard = await self.scorecard_generator.ainvoke(context)
    logger.info("Scorecard Generator: Scorecard generated!")
    return Command(
        update={"scorecard": scorecard.model_dump_json()}, goto="task_generator"
    )

  async def task_generator_node(self, state: TaskGeneratorState, config: Optional[Dict[str, Any]] = None):
    logger.info("Task Generator: Creating tasks...")
    context = {
        "job_description_profile": state["job_description_profile"],
        "scorecard": state["scorecard"]
    }
    task_list = await self.task_generator.ainvoke(context)
    logger.info("Task Generator: Tasks created!")
    return Command(
        update={"task_list": task_list.model_dump_json()}, goto=END
    )


  def build_graph(self) -> None:
    graph = StateGraph(TaskGeneratorState)
    graph.add_node("resume_profiler", self.resume_profiler_node)
    graph.add_node("job_description_profiler", self.job_description_profiler_node)
    graph.add_node("scorecard_generator", self.scorecard_generator_node)
    graph.add_node("task_generator", self.task_generator_node)
    graph.add_edge(START, "resume_profiler")
    graph.add_edge(START, "job_description_profiler")
    graph.add_edge("resume_profiler", "scorecard_generator")
    graph.add_edge("job_description_profiler", "scorecard_generator")
    graph.add_edge("scorecard_generator", "task_generator")
    graph.add_edge("task_generator", END)
    self.graph = graph.compile(checkpointer=self.checkpointer)

  def invoke(self, context: Dict[str, Any], config: Optional[Dict[str, Any]] = None):
    try:
      if config is None:
        config = self.config
      return self.graph.invoke(context, config)
    except Exception as e:
      raise AgentExecutionError(
        f"An exception occurred while trying to process the following context: {context}\n"
        f"Config: {self.config}\n"
        f"Error Message: {str(e)}"
      )
  
  async def ainvoke(self, context: Dict[str, Any], config: Optional[Dict[str, Any]] = None ):
    try:
      if config is None:
        config = self.config
      result = await self.graph.ainvoke(context, self.config)
      return result
    except Exception as e:
      raise AgentExecutionError(
        f"An exception occurred while trying to process the following context: {context}\n"
        f"Config: {self.config}\n"
        f"Error Message: {str(e)}"
      )
