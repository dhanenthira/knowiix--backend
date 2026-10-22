from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    Text,
    DateTime,
    JSON,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, index=True)
    student_id = Column(String(64), unique=True, index=True, nullable=True)
    email = Column(String(128), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(128), nullable=False)
    username = Column(String(128), nullable=True)
    role = Column(String(32), default="student", index=True)
    college_name = Column(String(255), default="")
    department = Column(String(255), default="")
    graduation_year = Column(Integer, default=2026)
    bio = Column(Text, default="")
    avatar_url = Column(String(512), default="")
    full_name = Column(String(128), nullable=True)
    profile_image_url = Column(String(512), nullable=True)
    streak_days = Column(Integer, default=0)
    total_points = Column(Integer, default=0)
    problems_solved = Column(Integer, default=0)
    questions_solved = Column(Integer, default=0)
    overall_accuracy = Column(Float, default=0.0)
    coding_problems_solved = Column(Integer, default=0)
    battles_won = Column(Integer, default=0)
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class QuestionModel(Base):
    __tablename__ = "questions"

    id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(64), index=True, nullable=False)
    topic = Column(String(128), index=True, default="")
    difficulty = Column(String(32), default="easy")
    question_type = Column(String(32), default="mcq")
    options = Column(JSON, default=list)
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, default="")
    marks = Column(Integer, default=1)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


class CodingProblemModel(Base):
    __tablename__ = "coding_problems"

    id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), index=True, nullable=False)
    difficulty = Column(String(32), default="medium")
    topic = Column(String(128), default="General")
    category = Column(String(128), default="Basic Programming")
    description = Column(Text, nullable=False)
    constraints = Column(JSON, default=list)
    examples = Column(JSON, default=list)
    input_format = Column(Text, default="")
    output_format = Column(Text, default="")
    hints = Column(JSON, default=list)
    time_limit_seconds = Column(Float, default=2.0)
    memory_limit_mb = Column(Integer, default=256)
    starter_codes = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    sample_test_cases = Column(JSON, default=list)
    hidden_test_cases = Column(JSON, default=list)
    supported_languages = Column(JSON, default=lambda: ["python", "javascript", "java", "c", "cpp"])
    is_published = Column(Boolean, default=True)
    is_solved = Column(Boolean, default=False)
    total_submissions = Column(Integer, default=0)
    acceptance_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class ProblemSolvedModel(Base):
    __tablename__ = "problems_solved"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    problem_id = Column(String(64), ForeignKey("coding_problems.id", ondelete="CASCADE"), index=True, nullable=False)
    first_accepted_at = Column(DateTime, default=datetime.utcnow)


class QuestionSolvedModel(Base):
    __tablename__ = "questions_solved"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    question_id = Column(String(64), ForeignKey("questions.id", ondelete="CASCADE"), index=True, nullable=False)
    category = Column(String(64), default="aptitude")
    first_solved_at = Column(DateTime, default=datetime.utcnow)


class DailySetModel(Base):
    __tablename__ = "daily_sets"

    id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(64), default="aptitude")
    difficulty = Column(String(32), default="medium")
    question_count = Column(Integer, default=2)
    estimated_minutes = Column(Integer, default=10)
    marks_per_question = Column(Integer, default=1)
    total_marks = Column(Integer, default=2)
    is_completed = Column(Boolean, default=False)
    best_score = Column(Integer, default=0)
    created_date = Column(String(32), default="")
    question_ids = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


class AssessmentTestModel(Base):
    __tablename__ = "assessment_tests"

    id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    category = Column(String(64), default="mixed")
    difficulty = Column(String(32), default="medium")
    duration_minutes = Column(Integer, default=30)
    total_marks = Column(Integer, default=100)
    total_questions = Column(Integer, default=0)
    rules = Column(JSON, default=list)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String(32), default="active")
    is_attempted = Column(Boolean, default=False)
    score = Column(Integer, nullable=True)
    question_ids = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


class NotificationModel(Base):
    __tablename__ = "notifications"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(64), default="announcement")
    is_read = Column(Boolean, default=False)
    action_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserFollowModel(Base):
    __tablename__ = "user_follows"

    id = Column(String(64), primary_key=True, index=True)
    follower_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    following_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class SubmissionModel(Base):
    __tablename__ = "submissions"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    problem_id = Column(String(64), index=True, nullable=False)
    submission_type = Column(String(32), default="code")
    code = Column(Text, nullable=True)
    language = Column(String(32), nullable=True)
    status = Column(String(64), default="submitted")
    passed_test_cases = Column(Integer, default=0)
    total_test_cases = Column(Integer, default=0)
    execution_time_ms = Column(Float, default=0.0)
    memory_used_mb = Column(Float, default=0.0)
    score = Column(Float, default=0.0)
    max_score = Column(Float, default=0.0)
    answers = Column(JSON, nullable=True)
    reviews = Column(JSON, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)


class LearningModuleModel(Base):
    __tablename__ = "learning_modules"

    id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(64), index=True, nullable=False)
    description = Column(Text, default="")
    icon = Column(String(64), default="code")
    total_lessons = Column(Integer, default=0)
    completed_lessons = Column(Integer, default=0)
    progress_percentage = Column(Float, default=0.0)
    topics = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    lessons = relationship("LessonModel", back_populates="module", cascade="all, delete-orphan")


class LessonModel(Base):
    __tablename__ = "lessons"

    id = Column(String(64), primary_key=True, index=True)
    module_id = Column(String(64), ForeignKey("learning_modules.id", ondelete="CASCADE"), index=True, nullable=False)
    topic_id = Column(String(64), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    intro = Column(Text, default="")
    definition = Column(Text, default="")
    explanation = Column(Text, default="")
    syntax = Column(Text, default="")
    code_snippets = Column(JSON, default=list)
    notes = Column(JSON, default=list)
    category = Column(String(64), default="")
    order = Column(Integer, default=1)
    is_completed = Column(Boolean, default=False)
    practice_topic_id = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    module = relationship("LearningModuleModel", back_populates="lessons")
