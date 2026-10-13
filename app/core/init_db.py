import logging
import pymysql
from datetime import datetime, timedelta
from sqlalchemy import text
from app.core.config import settings
from app.core.security import get_password_hash
from app.core.database import engine, Base, SessionLocal, init_db_engine
from app.models.sql_models import (
    UserModel,
    QuestionModel,
    CodingProblemModel,
    LearningModuleModel,
    LessonModel,
    DailySetModel,
    AssessmentTestModel,
    NotificationModel,
    UserFollowModel,
)

logger = logging.getLogger("codearena.init_db")

def create_database_if_not_exists():
    """
    Creates the MySQL database schema if it doesn't already exist.
    """
    try:
        conn = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD or "",
            autocommit=True
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{settings.MYSQL_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            logger.info(f"Database `{settings.MYSQL_DATABASE}` ensured in MySQL.")
        conn.close()
        return True
    except Exception as e:
        logger.warning(f"Could not auto-create database `{settings.MYSQL_DATABASE}`: {e}")
        return False

def seed_database_records():
    """
    Ensures essential system tables are ready and seeds initial starter records if missing.
    """
    if SessionLocal is None:
        init_db_engine()
    if SessionLocal is None:
        return

    db = SessionLocal()
    try:
        # 1. Ensure master administrator exists
        admin_user = db.query(UserModel).filter(UserModel.role == "admin").first()
        if not admin_user:
            admin_user = UserModel(
                id="user_admin_01",
                student_id="ADM-001",
                email="admin@codearena.com",
                password=get_password_hash("adminpassword123"),
                name="System Administrator",
                role="admin",
                college_name="CodeArena HQ",
                department="Platform Core",
                graduation_year=2024,
                bio="Platform Administrator",
                avatar_url="https://api.dicebear.com/7.x/bottts/svg?seed=admin",
                streak_days=45,
                total_points=12500,
                problems_solved=320,
                questions_solved=850,
                overall_accuracy=94.5,
                coding_problems_solved=140,
                battles_won=42,
                followers_count=128,
                following_count=12,
                is_active=True,
                created_at=datetime.utcnow() - timedelta(days=90)
            )
            db.add(admin_user)
            logger.info("Master Administrator verified in MySQL database.")

        skillprep_admin = db.query(UserModel).filter(UserModel.email == "admin@skillprep.edu").first()
        if not skillprep_admin:
            skillprep_admin = UserModel(
                id="user_admin_skillprep",
                student_id="ADM-002",
                email="admin@skillprep.edu",
                password=get_password_hash("admin123"),
                name="SkillPrep Administrator",
                role="admin",
                college_name="SkillPrep Institute",
                department="Administration",
                graduation_year=2026,
                bio="Master Administrator for SkillPrep Platform",
                avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=SkillPrepAdmin",
                is_active=True,
                created_at=datetime.utcnow() - timedelta(days=90)
            )
            db.add(skillprep_admin)
            logger.info("SkillPrep Administrator verified in MySQL database.")

        # 2. Ensure demo student account exists
        demo_student = db.query(UserModel).filter(UserModel.email == "student@codearena.com").first()
        if not demo_student:
            demo_student = UserModel(
                id="user_student_01",
                student_id="CA-2026-9042",
                email="student@codearena.com",
                password=get_password_hash("password123"),
                name="Alex Mercer",
                role="student",
                college_name="National Institute of Technology",
                department="Computer Science & Engineering",
                graduation_year=2026,
                bio="Passionate competitive programmer and full-stack enthusiast.",
                avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=Alex",
                streak_days=14,
                total_points=4850,
                problems_solved=142,
                questions_solved=380,
                overall_accuracy=88.2,
                coding_problems_solved=56,
                battles_won=19,
                followers_count=28,
                following_count=15,
                is_active=True,
                created_at=datetime.utcnow() - timedelta(days=45)
            )
            db.add(demo_student)
            logger.info("Demo Student account (Alex Mercer) verified in MySQL database.")

        # 3. Ensure starter questions exist
        if db.query(QuestionModel).count() == 0:
            starter_questions = [
                QuestionModel(
                    id="q_apt_01",
                    title="Train Speed & Distance",
                    content="A train running at the speed of 60 km/hr crosses a pole in 9 seconds. What is the length of the train in meters?",
                    category="aptitude",
                    topic="Time & Distance",
                    difficulty="easy",
                    question_type="mcq",
                    options=["120 metres", "150 metres", "180 metres", "324 metres"],
                    correct_answer="150 metres",
                    explanation="Speed = 60 * (5/18) m/sec = 50/3 m/sec. Length = Speed * Time = (50/3) * 9 = 150 metres.",
                    marks=1,
                    tags=["Aptitude", "Speed", "Trains"],
                    created_at=datetime.utcnow() - timedelta(days=10)
                ),
                QuestionModel(
                    id="q_apt_02",
                    title="Profit and Loss Calculation",
                    content="A shopkeeper sells an article for $240 and gains 20%. What was the cost price of the article?",
                    category="aptitude",
                    topic="Profit & Loss",
                    difficulty="easy",
                    question_type="mcq",
                    options=["$190", "$200", "$210", "$220"],
                    correct_answer="$200",
                    explanation="Cost Price = (Selling Price * 100) / (100 + Gain%) = (240 * 100) / 120 = $200.",
                    marks=1,
                    tags=["Aptitude", "Arithmetic", "Profit"],
                    created_at=datetime.utcnow() - timedelta(days=10)
                ),
                QuestionModel(
                    id="q_tech_01",
                    title="Time Complexity of Binary Search",
                    content="What is the worst-case time complexity of Binary Search on a sorted array of n elements?",
                    category="technical",
                    topic="Data Structures & Algorithms",
                    difficulty="easy",
                    question_type="mcq",
                    options=["O(1)", "O(n)", "O(log n)", "O(n log n)"],
                    correct_answer="O(log n)",
                    explanation="In each step, binary search halves the search space, giving a logarithmic time complexity of O(log n).",
                    marks=1,
                    tags=["DSA", "Binary Search", "Complexity"],
                    created_at=datetime.utcnow() - timedelta(days=9)
                ),
                QuestionModel(
                    id="q_tech_02",
                    title="JavaScript Event Loop Microtask",
                    content="Which function queue has higher priority in the JavaScript Event Loop?",
                    category="technical",
                    topic="JavaScript Fundamentals",
                    difficulty="medium",
                    question_type="mcq",
                    options=["setTimeout (Macrotask)", "Promise.then (Microtask)", "setInterval", "setImmediate"],
                    correct_answer="Promise.then (Microtask)",
                    explanation="Microtasks (like Promise callbacks and process.nextTick) are executed immediately after the current call stack clears and before any macrotask.",
                    marks=1,
                    tags=["JavaScript", "Event Loop", "Asynchronous"],
                    created_at=datetime.utcnow() - timedelta(days=8)
                )
            ]
            db.add_all(starter_questions)
            logger.info("Starter questions seeded.")

        # 4. Ensure Daily Sets exist
        if db.query(DailySetModel).count() == 0:
            daily_sets = [
                DailySetModel(
                    id="ds_apt_today",
                    title="Daily Aptitude Challenge - Set #42",
                    category="aptitude",
                    difficulty="medium",
                    question_count=2,
                    estimated_minutes=10,
                    marks_per_question=1,
                    total_marks=2,
                    is_completed=False,
                    created_date=datetime.utcnow().strftime("%Y-%m-%d"),
                    question_ids=["q_apt_01", "q_apt_02"],
                    created_at=datetime.utcnow()
                ),
                DailySetModel(
                    id="ds_tech_today",
                    title="Daily Technical Challenge - Set #42",
                    category="technical",
                    difficulty="easy",
                    question_count=2,
                    estimated_minutes=8,
                    marks_per_question=1,
                    total_marks=2,
                    is_completed=True,
                    best_score=2,
                    created_date=datetime.utcnow().strftime("%Y-%m-%d"),
                    question_ids=["q_tech_01", "q_tech_02"],
                    created_at=datetime.utcnow()
                )
            ]
            db.add_all(daily_sets)
            logger.info("Daily practice sets seeded.")

        # 5. Ensure Assessment Test exists
        if db.query(AssessmentTestModel).count() == 0:
            test = AssessmentTestModel(
                id="test_nationwide_01",
                title="All-India Coding & Aptitude Grand Assessment",
                description="National level screening test evaluating speed, logical reasoning, and computer science fundamentals.",
                category="mixed",
                difficulty="medium",
                duration_minutes=30,
                total_marks=40,
                total_questions=4,
                rules=[
                    "Once started, the countdown timer cannot be paused.",
                    "Full-screen mode recommended.",
                    "Questions carry 1 mark each with no negative marking.",
                    "Final score and detailed solutions will be unlocked after the assessment window."
                ],
                start_time=datetime.utcnow() - timedelta(hours=2),
                end_time=datetime.utcnow() + timedelta(days=5),
                status="active",
                is_attempted=False,
                question_ids=["q_apt_01", "q_apt_02", "q_tech_01", "q_tech_02"],
                created_at=datetime.utcnow()
            )
            db.add(test)
            logger.info("Grand Assessment test seeded.")

        # 6. Ensure demo coding problems are seeded
        if db.query(CodingProblemModel).count() <= 1:
            try:
                from scripts.import_demo_problems import import_all_problems
                import_all_problems()
            except Exception as ex:
                logger.warning(f"Could not auto-seed demo coding problems: {ex}")

        db.commit()
    except Exception as e:
        logger.warning(f"Error initializing seed records: {e}")
        db.rollback()
    finally:
        db.close()

def init_tables():
    """
    Creates all defined tables in MySQL and seeds initial records if needed.
    """
    try:
        create_database_if_not_exists()
        init_db_engine()
        if engine is not None:
            Base.metadata.create_all(bind=engine)
            logger.info("MySQL tables created / verified successfully.")
            seed_database_records()
            return True
    except Exception as e:
        logger.warning(f"Error initializing MySQL tables: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Connecting and initializing MySQL tables...")
    success = init_tables()
    if success:
        print(f"SUCCESS: MySQL database '{settings.MYSQL_DATABASE}' and tables ready!")
    else:
        print("NOTE: Make sure MySQL (XAMPP / MySQL Service) is running on port 3306.")
