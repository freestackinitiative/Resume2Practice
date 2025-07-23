from pydantic import BaseModel, Field
from typing import List, TypedDict, Optional

class ResumeProfile(BaseModel):
  name: str = Field(None, description="Name of the applicant")
  summary: str = Field(None, description="Summary of the applicant")
  skills: List[str] = Field(None, description="Skills of the applicant")
  education: str = Field(None, description="A summary of the applicant's education")
  career_level: str = Field(None, description="Assessed career level of the applicant")

class JobDescriptionProfile(BaseModel):
  job_title: str = Field(None, description="Title of the job")
  summary: str = Field(None, description="Summary of the job")
  responsibilities: List[str] = Field(None, description="Responsibilities of the job")
  industry: str = Field(None, description="Industry of the job")
  hard_requirements: List[str] = Field(None, description="Hard requirements of the job")
  soft_requirements: List[str] = Field(None, description="Soft requirements of the job")
  nice_to_haves: List[str] = Field(None, description="Nice to have skills of the job")
  career_level: str = Field(None, description="Assessed career level of the job")

class Scorecard(BaseModel):
  gap_analysis: str = Field(None, description="Gap analysis of the applicant compared to the job description")
  strengths: list[str] = Field(None, description="Strengths of the applicant")
  weaknesses: list[str] = Field(None, description="Weaknesses of the applicant")
  opportunity_for_growth: str = Field(None, description="Opportunity for growth of the applicant")
  readiness_score: float = Field(None, description="Overall score of the applicant")

class ScorecardIntake(BaseModel):
  questions: List[str] = Field(None, description="List of questions to ask for further clarification")

class Task(BaseModel):
  task_summary: str = Field(None, description="Summary of the task")
  task_description: str = Field(None, description="Description of the task")
  task_type: str = Field(None, description="Type of the task")
  evaluation_criteria: str = Field(None, description="Evaluation criteria for the task")
  task_data: Optional[str] = Field(None, description="Synthetic data used for the completion of the task")

class TaskList(BaseModel):
  tasks: List[Task] = Field(None, description="List of tasks")

class TaskGeneratorState(TypedDict):
  resume: str
  job_description: str
  resume_profile: ResumeProfile
  job_description_profile: JobDescriptionProfile
  scorecard: Scorecard
  task_list: TaskList