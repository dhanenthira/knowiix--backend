from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class LessonTopic(BaseModel):
    id: str
    title: str
    slug: str
    order: int
    is_completed: bool = False
    subtopic: Optional[str] = None

class CodeSnippet(BaseModel):
    language: str
    code: str
    output: Optional[str] = ""

class LessonDetail(BaseModel):
    id: str
    module_id: str
    topic_id: str
    subtopic: Optional[str] = None
    title: str
    intro: str
    definition: str
    explanation: str
    syntax: Optional[str] = ""
    code_snippets: List[CodeSnippet] = []
    notes: List[str] = []
    category: str
    order: int
    is_completed: bool = False
    practice_topic_id: Optional[str] = None

class ModuleSummary(BaseModel):
    id: str
    title: str
    category: str
    description: str
    icon: str
    total_lessons: int
    completed_lessons: int
    progress_percentage: float
    topics: List[LessonTopic] = []

class LessonProgressUpdate(BaseModel):
    lesson_id: str
    completed: bool = True
