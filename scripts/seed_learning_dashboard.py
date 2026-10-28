import os
import sys
import logging
from datetime import datetime, timedelta

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, init_db_engine, Base, engine
from app.models.category import CategoryModel
from app.models.tutorial import TutorialModel
from app.models.topic import TopicModel
from app.models.progress import UserProgressModel
from app.models.bookmark import BookmarkModel
from app.models.activity import LearningActivityModel
from app.models.sql_models import UserModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_learning_dashboard")

CATEGORIES_DATA = [
    {
        "id": "cat_html",
        "name": "HTML",
        "slug": "html",
        "description": "HyperText Markup Language: The standard foundation markup language for designing documents and structuring web pages.",
        "icon": "code",
        "display_order": 1,
        "tutorials": [
            {
                "id": "tut_html_fundamentals",
                "title": "HTML5 Fundamentals & Semantic Web",
                "slug": "html5-fundamentals",
                "description": "Learn modern HTML5 syntax, page structure, headings, paragraphs, lists, links, images, and semantic layout tags.",
                "difficulty": "Beginner",
                "estimated_minutes": 25,
                "topics": [
                    {
                        "id": "top_html_intro",
                        "title": "Introduction to HTML5 & Document Structure",
                        "content": "HTML (HyperText Markup Language) describes the structure of web pages using elements represented by tags. HTML5 introduces native audio/video support, responsive canvas elements, and semantic markup for accessibility.",
                        "code_example": "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n    <title>Hello HTML5</title>\n</head>\n<body>\n    <h1>Welcome to Web Development</h1>\n    <p>This is your very first structured HTML5 document.</p>\n</body>\n</html>",
                        "display_order": 1
                    },
                    {
                        "id": "top_html_semantics",
                        "title": "Semantic HTML: Header, Nav, Main & Footer",
                        "content": "Semantic HTML elements clearly describe their meaning to both the browser and the developer. Using elements like <header>, <nav>, <main>, <article>, <section>, and <footer> improves SEO and screen reader accessibility.",
                        "code_example": "<header>\n    <h1>Knowiix Learning</h1>\n    <nav>\n        <a href=\"#home\">Home</a>\n        <a href=\"#tutorials\">Tutorials</a>\n    </nav>\n</header>\n<main>\n    <article>\n        <h2>Semantic Architecture</h2>\n        <p>Accessible and search engine friendly markup.</p>\n    </article>\n</main>\n<footer>\n    <p>&copy; 2026 Knowiix. All rights reserved.</p>\n</footer>",
                        "display_order": 2
                    },
                    {
                        "id": "top_html_forms",
                        "title": "HTML5 Forms, Input Validation & Accessibility",
                        "content": "Modern forms support client-side input validations such as required, pattern, type='email', and type='number' alongside accessible label associations.",
                        "code_example": "<form action=\"/submit\" method=\"POST\">\n    <label for=\"email\">Email Address:</label>\n    <input type=\"email\" id=\"email\" name=\"email\" required placeholder=\"user@example.com\">\n    <button type=\"submit\">Subscribe</button>\n</form>",
                        "display_order": 3
                    }
                ]
            }
        ]
    },
    {
        "id": "cat_css",
        "name": "CSS",
        "slug": "css",
        "description": "Cascading Style Sheets: Style, layout, responsive design, Flexbox, CSS Grid, and fluid animations for modern UI.",
        "icon": "palette",
        "display_order": 2,
        "tutorials": [
            {
                "id": "tut_css_layout",
                "title": "CSS3 Flexbox & Grid Masterclass",
                "slug": "css-flexbox-grid",
                "description": "Master flexible box layouts, multi-dimensional grid systems, alignment, gap properties, and mobile-first responsive design.",
                "difficulty": "Beginner",
                "estimated_minutes": 30,
                "topics": [
                    {
                        "id": "top_css_flexbox",
                        "title": "Flexbox Direction, Justify-Content & Align-Items",
                        "content": "The Flexible Box Layout Module makes it easy to design flexible responsive layout structures without using float or positioning properties.",
                        "code_example": ".container {\n    display: flex;\n    justify-content: space-between;\n    align-items: center;\n    gap: 1.5rem;\n}\n.card {\n    flex: 1;\n    padding: 1rem;\n    background: #1e293b;\n    border-radius: 8px;\n}",
                        "display_order": 1
                    },
                    {
                        "id": "top_css_grid",
                        "title": "CSS Grid: repeat(), minmax() and auto-fit",
                        "content": "CSS Grid is a powerful 2-dimensional system enabling rows and columns. Creating fully responsive cards without media queries is effortless with auto-fit.",
                        "code_example": ".dashboard-grid {\n    display: grid;\n    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));\n    gap: 20px;\n}",
                        "display_order": 2
                    }
                ]
            }
        ]
    },
    {
        "id": "cat_javascript",
        "name": "JavaScript",
        "slug": "javascript",
        "description": "The programming language of the Web: ES6+ features, Async/Await, Promises, Closures, DOM manipulation, and Event Loop.",
        "icon": "zap",
        "display_order": 3,
        "tutorials": [
            {
                "id": "tut_js_modern",
                "title": "Modern JavaScript (ES6+ to ESNext)",
                "slug": "modern-javascript-es6",
                "description": "Arrow functions, destructuring, spread/rest operators, modules, closures, and async programming with Promises.",
                "difficulty": "Intermediate",
                "estimated_minutes": 35,
                "topics": [
                    {
                        "id": "top_js_es6_syntax",
                        "title": "Arrow Functions, Destructuring & Optional Chaining",
                        "content": "ES6 introduced cleaner syntax for defining functions, extracting nested properties from objects, and accessing nullable properties safely with optional chaining (?.).",
                        "code_example": "const user = { profile: { name: 'Ananya', points: 3450 } };\nconst { name, points } = user.profile;\nconst badge = user.achievements?.topRank ?? 'Rising Star';\nconsole.log(`${name} holds ${points} points with badge: ${badge}`);",
                        "display_order": 1
                    },
                    {
                        "id": "top_js_promises_async",
                        "title": "Asynchronous JavaScript: Promises & Async/Await",
                        "content": "Async/await syntax simplifies promise-based code by providing a synchronous-looking control flow with try/catch error handling.",
                        "code_example": "async function fetchUserDashboard() {\n    try {\n        const res = await fetch('/api/dashboard/summary');\n        const data = await res.json();\n        console.log('User stats loaded:', data);\n    } catch (err) {\n        console.error('Failed to load dashboard:', err);\n    }\n}",
                        "display_order": 2
                    }
                ]
            }
        ]
    },
    {
        "id": "cat_react",
        "name": "React.js",
        "slug": "react",
        "description": "Component-based UI library: Hooks, useState, useEffect, Context API, Virtual DOM, and state management architectures.",
        "icon": "layers",
        "display_order": 4,
        "tutorials": [
            {
                "id": "tut_react_hooks",
                "title": "React.js Component Architecture & Modern Hooks",
                "slug": "react-hooks-architecture",
                "description": "Build high-performance interactive SPAs using functional components, Custom Hooks, useMemo, useCallback, and Context API.",
                "difficulty": "Intermediate",
                "estimated_minutes": 40,
                "topics": [
                    {
                        "id": "top_react_state_effects",
                        "title": "Managing State with useState & Side Effects with useEffect",
                        "content": "State allows React components to change their output over time in response to user actions, network responses, and timers.",
                        "code_example": "import React, { useState, useEffect } from 'react';\n\nexport function Counter() {\n    const [count, setCount] = useState(0);\n    useEffect(() => {\n        document.title = `Clicked ${count} times`;\n    }, [count]);\n    return <button onClick={() => setCount(c => c + 1)}>Count: {count}</button>;\n}",
                        "display_order": 1
                    },
                    {
                        "id": "top_react_context",
                        "title": "Global State Management with Context API",
                        "content": "React Context provides a way to pass data through the component tree without having to pass props down manually at every level.",
                        "code_example": "import React, { createContext, useContext, useState } from 'react';\n\nconst AuthContext = createContext(null);\nexport const useAuth = () => useContext(AuthContext);\n\nexport function AuthProvider({ children }) {\n    const [user, setUser] = useState({ name: 'Alex Mercer', role: 'student' });\n    return <AuthContext.Provider value={{ user, setUser }}>{children}</AuthContext.Provider>;\n}",
                        "display_order": 2
                    }
                ]
            }
        ]
    },
    {
        "id": "cat_python",
        "name": "Python",
        "slug": "python",
        "description": "High-level programming: Clean syntax, OOP, List Comprehensions, Decorators, Generators, and standard library mastery.",
        "icon": "terminal",
        "display_order": 5,
        "tutorials": [
            {
                "id": "tut_python_core",
                "title": "Python Programming & Core Concepts",
                "slug": "python-core-concepts",
                "description": "Learn Python 3 from scratch to advanced OOP, functional programming tools, and clean architectural design.",
                "difficulty": "Beginner",
                "estimated_minutes": 30,
                "topics": [
                    {
                        "id": "top_py_intro",
                        "title": "Python Introduction, Syntax & Types",
                        "content": "Python is an interpreted, high-level, dynamically typed language emphasizing readability and developer productivity.",
                        "code_example": "# List comprehension and string interpolation\nnumbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]\neven_squares = [x**2 for x in numbers if x % 2 == 0]\nprint(f'Even squares: {even_squares}')",
                        "display_order": 1
                    },
                    {
                        "id": "top_py_oop",
                        "title": "Object-Oriented Programming (Classes & Inheritance)",
                        "content": "Classes bundle data and functionality together. Creating a new class creates a new type of object, allowing new instances of that type to be made.",
                        "code_example": "class Student:\n    def __init__(self, name: str, student_id: str):\n        self.name = name\n        self.student_id = student_id\n        self.completed_lessons = []\n\n    def complete(self, lesson_name: str):\n        self.completed_lessons.append(lesson_name)\n        return f'{self.name} completed {lesson_name}'",
                        "display_order": 2
                    }
                ]
            }
        ]
    },
    {
        "id": "cat_java",
        "name": "Java",
        "slug": "java",
        "description": "Enterprise-grade OOP: Strong typing, JVM internals, Collections framework, Multi-threading, and Spring ecosystems.",
        "icon": "coffee",
        "display_order": 6,
        "tutorials": [
            {
                "id": "tut_java_collections",
                "title": "Java Fundamentals & Collections Framework",
                "slug": "java-collections-framework",
                "description": "Master ArrayList, HashMap, LinkedList, HashSet, Generics, and Lambda Streams in modern Java.",
                "difficulty": "Intermediate",
                "estimated_minutes": 35,
                "topics": [
                    {
                        "id": "top_java_basics",
                        "title": "Java Class Anatomy & JVM Memory Model",
                        "content": "Java programs are compiled into bytecode (.class) which runs on the Java Virtual Machine (JVM). Memory is divided into Heap (objects) and Stack (frames).",
                        "code_example": "public class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Hello Knowiix Java Students!\");\n    }\n}",
                        "display_order": 1
                    },
                    {
                        "id": "top_java_streams",
                        "title": "Java 8+ Streams API & Lambdas",
                        "content": "The Stream API in Java 8+ provides a declarative approach to processing sequences of elements, enabling filter, map, and reduce pipelines.",
                        "code_example": "List<String> names = Arrays.asList(\"Ananya\", \"Alex\", \"Priya\", \"Dhane\");\nList<String> filtered = names.stream()\n    .filter(n -> n.startsWith(\"A\"))\n    .map(String::toUpperCase)\n    .collect(Collectors.toList());\nSystem.out.println(filtered);",
                        "display_order": 2
                    }
                ]
            }
        ]
    },
    {
        "id": "cat_c",
        "name": "C",
        "slug": "c",
        "description": "Procedural programming: Direct memory access, pointers, structs, manual malloc/free, and low-level computer architecture.",
        "icon": "cpu",
        "display_order": 7,
        "tutorials": [
            {
                "id": "tut_c_pointers",
                "title": "C Programming: Pointers & Dynamic Memory",
                "slug": "c-pointers-memory",
                "description": "Deep-dive into pointer arithmetic, memory addresses, heap allocation with malloc, and struct data structures.",
                "difficulty": "Intermediate",
                "estimated_minutes": 30,
                "topics": [
                    {
                        "id": "top_c_pointers",
                        "title": "Understanding Memory Addresses & Pointer Variables",
                        "content": "A pointer is a variable that stores the memory address of another variable. The address-of operator (&) and dereference operator (*) are fundamental.",
                        "code_example": "#include <stdio.h>\n\nint main() {\n    int score = 95;\n    int *ptr = &score;\n    printf(\"Score value: %d\\n\", score);\n    printf(\"Address in memory: %p\\n\", (void*)ptr);\n    printf(\"Dereferenced value: %d\\n\", *ptr);\n    return 0;\n}",
                        "display_order": 1
                    }
                ]
            }
        ]
    },
    {
        "id": "cat_cpp",
        "name": "C++",
        "slug": "cpp",
        "description": "Modern C++: High-performance systems programming, STL (Standard Template Library), vectors, maps, RAII, and smart pointers.",
        "icon": "binary",
        "display_order": 8,
        "tutorials": [
            {
                "id": "tut_cpp_stl",
                "title": "Modern C++ & STL for Competitive Programming",
                "slug": "cpp-stl-competitive",
                "description": "Master std::vector, std::map, std::priority_queue, sorting algorithms, and lambda expressions in C++17/20.",
                "difficulty": "Intermediate",
                "estimated_minutes": 35,
                "topics": [
                    {
                        "id": "top_cpp_stl_vectors",
                        "title": "C++ Vectors, Iterators & Fast I/O",
                        "content": "std::vector is a dynamic array that grows automatically. In competitive programming, fast I/O reduces execution time drastically.",
                        "code_example": "#include <iostream>\n#include <vector>\n#include <algorithm>\n\nint main() {\n    std::ios_base::sync_with_stdio(false);\n    std::cin.tie(NULL);\n    std::vector<int> nums = {45, 12, 85, 32, 89};\n    std::sort(nums.begin(), nums.end());\n    for (int n : nums) std::cout << n << \" \";\n    std::cout << \"\\n\";\n    return 0;\n}",
                        "display_order": 1
                    }
                ]
            }
        ]
    },
    {
        "id": "cat_sql",
        "name": "SQL",
        "slug": "sql",
        "description": "Structured Query Language: Relational databases, SELECT queries, JOINs, aggregations, GROUP BY, subqueries, and window functions.",
        "icon": "database",
        "display_order": 9,
        "tutorials": [
            {
                "id": "tut_sql_queries",
                "title": "SQL Mastery: JOINs, Aggregations & Subqueries",
                "slug": "sql-joins-aggregations",
                "description": "Write complex analytical SQL queries, multi-table INNER/LEFT/RIGHT JOINs, and conditional aggregations.",
                "difficulty": "Beginner",
                "estimated_minutes": 25,
                "topics": [
                    {
                        "id": "top_sql_joins",
                        "title": "INNER JOIN, LEFT JOIN & Table Aliases",
                        "content": "JOIN clauses combine rows from two or more tables based on a related column between them. INNER JOIN returns matching records only, while LEFT JOIN preserves all left table records.",
                        "code_example": "SELECT u.name, u.email, COUNT(p.id) as completed_count\nFROM users u\nLEFT JOIN user_progress p ON u.id = p.user_id AND p.is_completed = 1\nGROUP BY u.id, u.name, u.email\nORDER BY completed_count DESC;",
                        "display_order": 1
                    }
                ]
            }
        ]
    },
    {
        "id": "cat_mysql",
        "name": "MySQL",
        "slug": "mysql",
        "description": "World's most popular open-source RDBMS: InnoDB storage engine, B+ Tree indexing, transactions, ACID, and performance tuning.",
        "icon": "server",
        "display_order": 10,
        "tutorials": [
            {
                "id": "tut_mysql_admin",
                "title": "MySQL Architecture, Indexing & Transactions",
                "slug": "mysql-indexing-transactions",
                "description": "Understand MySQL execution plans (EXPLAIN), clustered vs secondary B+ Tree indexes, transactions, and foreign key constraints.",
                "difficulty": "Intermediate",
                "estimated_minutes": 30,
                "topics": [
                    {
                        "id": "top_mysql_indexes",
                        "title": "B+ Tree Indexes & Query Optimization with EXPLAIN",
                        "content": "Indexes allow MySQL to find rows matching WHERE conditions without reading the entire table. The EXPLAIN command displays the execution plan chosen by the query optimizer.",
                        "code_example": "-- Analyze query index coverage\nEXPLAIN SELECT * FROM tutorials WHERE category_id = 'cat_python' AND is_published = 1;\n\n-- Create compound index for fast lookups\nCREATE INDEX idx_tutorial_cat_pub ON tutorials (category_id, is_published);",
                        "display_order": 1
                    }
                ]
            }
        ]
    },
    {
        "id": "cat_fastapi",
        "name": "FastAPI",
        "slug": "fastapi",
        "description": "Modern, high-performance web framework for Python: Async endpoints, Pydantic validation, OpenAPI docs, and dependency injection.",
        "icon": "shield",
        "display_order": 11,
        "tutorials": [
            {
                "id": "tut_fastapi_rest",
                "title": "Building Production REST APIs with FastAPI & SQLAlchemy",
                "slug": "fastapi-rest-apis",
                "description": "Create secure, production-ready APIs with Pydantic schemas, dependency injection, OAuth2 tokens, and database sessions.",
                "difficulty": "Intermediate",
                "estimated_minutes": 30,
                "topics": [
                    {
                        "id": "top_fastapi_di",
                        "title": "FastAPI Dependency Injection & Database Sessions",
                        "content": "FastAPI features an extensible dependency injection system that automatically handles session creation, authentication checks, and cleanup.",
                        "code_example": "from fastapi import APIRouter, Depends, HTTPException\nfrom sqlalchemy.orm import Session\nfrom app.core.database import get_db\n\nrouter = APIRouter()\n\n@router.get(\"/api/categories\")\ndef read_categories(db: Session = Depends(get_db)):\n    return db.query(CategoryModel).all()",
                        "display_order": 1
                    }
                ]
            }
        ]
    },
    {
        "id": "cat_nodejs",
        "name": "Node.js",
        "slug": "nodejs",
        "description": "Asynchronous event-driven JavaScript runtime: Express.js, NPM ecosystem, file system, streams, and REST microservices.",
        "icon": "box",
        "display_order": 12,
        "tutorials": [
            {
                "id": "tut_nodejs_express",
                "title": "Backend Engineering with Node.js & Express",
                "slug": "nodejs-express-fundamentals",
                "description": "Build asynchronous HTTP servers, routing middleware, JSON parsers, and connect to relational databases.",
                "difficulty": "Beginner",
                "estimated_minutes": 25,
                "topics": [
                    {
                        "id": "top_nodejs_server",
                        "title": "Creating an Express REST Server with JSON Middleware",
                        "content": "Express is a minimalist web framework for Node.js providing a robust set of features for web and mobile applications.",
                        "code_example": "const express = require('express');\nconst app = express();\n\napp.use(express.json());\n\napp.get('/api/health', (req, res) => {\n    res.json({ status: 'healthy', platform: 'Knowiix' });\n});\n\napp.listen(3000, () => console.log('Server running on port 3000'));",
                        "display_order": 1
                    }
                ]
            }
        ]
    },
    {
        "id": "cat_git",
        "name": "Git and GitHub",
        "slug": "git",
        "description": "Distributed version control system: Git workflows, commits, branching, merges, rebasing, pull requests, and CI/CD pipelines.",
        "icon": "git-branch",
        "display_order": 13,
        "tutorials": [
            {
                "id": "tut_git_workflow",
                "title": "Git & GitHub Version Control Professional Workflow",
                "slug": "git-github-workflow",
                "description": "Master Git repositories, branching strategies, resolving merge conflicts, and contributing through pull requests.",
                "difficulty": "Beginner",
                "estimated_minutes": 20,
                "topics": [
                    {
                        "id": "top_git_commands",
                        "title": "Git Init, Branching, Staging & Remote Push",
                        "content": "Git tracks the history of changes as you work on code. Remote hosting platforms like GitHub allow team collaboration and review.",
                        "code_example": "# Initialize and push new branch\ngit checkout -b feature/learning-dashboard\ngit add .\ngit commit -m \"feat: complete W3Schools learning dashboard\"\ngit push -u origin feature/learning-dashboard",
                        "display_order": 1
                    }
                ]
            }
        ]
    }
]

def seed_learning_dashboard_data():
    """
    Creates tables if missing and seeds all 13 categories, tutorials, and topics.
    Also ensures starter bookmarks and progress records for demo student accounts.
    """
    init_db_engine()
    if engine is not None:
        Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    if not db:
        logger.error("Could not obtain DB session for seeding learning dashboard")
        return False

    try:
        # Seed categories, tutorials, and topics
        for cat_data in CATEGORIES_DATA:
            cat = db.query(CategoryModel).filter(CategoryModel.id == cat_data["id"]).first()
            if not cat:
                cat = CategoryModel(
                    id=cat_data["id"],
                    name=cat_data["name"],
                    slug=cat_data["slug"],
                    description=cat_data["description"],
                    icon=cat_data["icon"],
                    display_order=cat_data["display_order"],
                    is_active=True
                )
                db.add(cat)
                logger.info(f"Seeded category: {cat.name}")
            else:
                cat.name = cat_data["name"]
                cat.slug = cat_data["slug"]
                cat.description = cat_data["description"]
                cat.icon = cat_data["icon"]
                cat.display_order = cat_data["display_order"]

            db.flush()

            # Seed tutorials for this category
            for tut_data in cat_data.get("tutorials", []):
                tut = db.query(TutorialModel).filter(TutorialModel.id == tut_data["id"]).first()
                if not tut:
                    tut = TutorialModel(
                        id=tut_data["id"],
                        category_id=cat.id,
                        title=tut_data["title"],
                        slug=tut_data["slug"],
                        description=tut_data["description"],
                        difficulty=tut_data.get("difficulty", "Beginner"),
                        estimated_minutes=tut_data.get("estimated_minutes", 20),
                        is_published=True,
                        created_at=datetime.utcnow() - timedelta(days=10)
                    )
                    db.add(tut)
                    logger.info(f"  Seeded tutorial: {tut.title}")
                else:
                    tut.category_id = cat.id
                    tut.title = tut_data["title"]
                    tut.slug = tut_data["slug"]
                    tut.description = tut_data["description"]
                    tut.difficulty = tut_data.get("difficulty", "Beginner")
                    tut.estimated_minutes = tut_data.get("estimated_minutes", 20)

                db.flush()

                # Seed topics for this tutorial
                for top_data in tut_data.get("topics", []):
                    top = db.query(TopicModel).filter(TopicModel.id == top_data["id"]).first()
                    if not top:
                        top = TopicModel(
                            id=top_data["id"],
                            tutorial_id=tut.id,
                            title=top_data["title"],
                            content=top_data["content"],
                            code_example=top_data.get("code_example", ""),
                            display_order=top_data.get("display_order", 1)
                        )
                        db.add(top)
                        logger.info(f"    Seeded topic: {top.title}")
                    else:
                        top.title = top_data["title"]
                        top.content = top_data["content"]
                        top.code_example = top_data.get("code_example", "")
                        top.display_order = top_data.get("display_order", 1)

        db.commit()

        # Seed starter progress and bookmark for demo accounts (e.g. Alex Mercer, Ananya Kumar)
        demo_users = db.query(UserModel).filter(
            UserModel.email.in_(["student@knowiix.com", "student@skillprep.edu"])
        ).all()

        for user in demo_users:
            # 1. Bookmark Python and React
            for tut_id in ["tut_python_core", "tut_react_hooks"]:
                existing_bm = db.query(BookmarkModel).filter(
                    BookmarkModel.user_id == user.id,
                    BookmarkModel.tutorial_id == tut_id
                ).first()
                if not existing_bm:
                    db.add(BookmarkModel(user_id=user.id, tutorial_id=tut_id))

            # 2. Complete topic: top_py_intro & top_html_intro
            for top_id in ["top_py_intro", "top_html_intro"]:
                existing_prog = db.query(UserProgressModel).filter(
                    UserProgressModel.user_id == user.id,
                    UserProgressModel.topic_id == top_id
                ).first()
                if not existing_prog:
                    db.add(UserProgressModel(
                        user_id=user.id,
                        topic_id=top_id,
                        is_completed=True,
                        last_read_at=datetime.utcnow() - timedelta(hours=2),
                        completed_at=datetime.utcnow() - timedelta(hours=2)
                    ))

            # 3. Add activity
            if db.query(LearningActivityModel).filter(LearningActivityModel.user_id == user.id).count() == 0:
                db.add(LearningActivityModel(
                    user_id=user.id,
                    tutorial_id="tut_python_core",
                    topic_id="top_py_intro",
                    activity_type="completed_topic",
                    created_at=datetime.utcnow() - timedelta(hours=2)
                ))
                db.add(LearningActivityModel(
                    user_id=user.id,
                    tutorial_id="tut_react_hooks",
                    topic_id="top_react_state_effects",
                    activity_type="viewed_topic",
                    created_at=datetime.utcnow() - timedelta(hours=1)
                ))

        db.commit()
        logger.info("Successfully seeded all 13 Learning Dashboard categories and tutorials!")
        return True
    except Exception as e:
        logger.error(f"Error seeding dashboard data: {e}", exc_info=True)
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    seed_learning_dashboard_data()
