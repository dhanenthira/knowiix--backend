from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

class DifficultyEnum(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

class TestCase(BaseModel):
    input: str
    expected_output: str
    is_hidden: bool = False
    explanation: Optional[str] = ""

class StarterCode(BaseModel):
    language: str # python, javascript, cpp, java, c
    code: str

class CodingCategoryResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str
    problem_count: int = 0
    icon: str = "code-2"

class CodingProblemListItem(BaseModel):
    id: str
    title: str
    slug: str
    difficulty: str
    topic: str
    category: str = "Basic Programming"
    supported_languages: List[str] = ["python", "javascript", "java", "c", "cpp"]
    is_solved: bool = False
    total_submissions: int = 0
    acceptance_rate: float = 0.0

class PaginatedCodingProblemsResponse(BaseModel):
    items: List[CodingProblemListItem]
    total: int
    page: int
    page_size: int
    total_pages: int

class CodingProblemResponse(BaseModel):
    id: str
    title: str
    slug: str
    difficulty: str
    topic: str
    category: str = "Basic Programming"
    description: str
    constraints: List[str] = []
    examples: List[Dict[str, Any]] = []
    input_format: str = ""
    output_format: str = ""
    hints: List[str] = []
    time_limit_seconds: float = 2.0
    memory_limit_mb: int = 128
    starter_codes: List[StarterCode] = []
    tags: List[str] = []
    sample_test_cases: List[TestCase] = []
    supported_languages: List[str] = ["python", "javascript", "java", "c", "cpp"]
    is_solved: bool = False
    total_submissions: int = 0
    acceptance_rate: float = 0.0

class CodeExecutionRequest(BaseModel):
    problem_id: str
    language: str
    code: str
    custom_input: Optional[str] = None

class TestCaseEvaluation(BaseModel):
    test_case_number: int
    is_hidden: bool
    status: str # Passed, Wrong Answer, Time Limit Exceeded, Runtime Error, Compilation Error
    input: Optional[str] = None
    expected_output: Optional[str] = None
    actual_output: Optional[str] = None
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0

class CodeExecutionResult(BaseModel):
    status: str # Accepted, Wrong Answer, Compilation Error, Runtime Error, Time Limit Exceeded
    total_test_cases: int
    passed_test_cases: int
    execution_time_ms: float
    memory_used_kb: float
    evaluations: List[TestCaseEvaluation] = []
    stdout: Optional[str] = ""
    stderr: Optional[str] = ""
    points_awarded: int = 0

class CodingSubmissionResponse(BaseModel):
    id: str
    user_id: str
    problem_id: str
    problem_title: Optional[str] = ""
    language: str
    code: Optional[str] = None
    status: str
    passed_test_cases: int = 0
    total_test_cases: int = 0
    execution_time_ms: float = 0.0
    memory_used_mb: float = 0.0
    score: float = 0.0
    submitted_at: datetime

class CodingProgressResponse(BaseModel):
    total_problems: int = 0
    problems_solved: int = 0
    attempted_problems: int = 0
    current_streak: int = 0
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0
    easy_total: int = 0
    medium_total: int = 0
    hard_total: int = 0
    preferred_language: Optional[str] = "python"
    recent_submissions: List[CodingSubmissionResponse] = []

class ProblemStatusResponse(BaseModel):
    problem_id: str
    is_solved: bool = False
    is_attempted: bool = False
    attempts_count: int = 0
    last_status: Optional[str] = None
