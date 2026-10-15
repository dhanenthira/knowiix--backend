import os
import re
import zipfile
import logging
import xml.etree.ElementTree as ET
from app.core.database import SessionLocal, init_db_engine
from app.models.sql_models import LearningModuleModel, LessonModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_complete_learning")

DOCX_PATH = r"d:\nanga project panna poram\project\demo doc\Complete_React_Tutorial_Study_Guide.docx"

def parse_react_docx():
    if not os.path.exists(DOCX_PATH):
        logger.error(f"Docx file not found at: {DOCX_PATH}")
        return []

    with zipfile.ZipFile(DOCX_PATH) as z:
        xml_content = z.read("word/document.xml")
    
    tree = ET.fromstring(xml_content)
    namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs = []
    for p in tree.iterfind(".//w:p", namespaces):
        texts = [node.text for node in p.iterfind(".//w:t", namespaces) if node.text]
        if texts:
            paragraphs.append("".join(texts).strip())

    topics = []
    current_part = "React Foundations"
    i = 0
    while i < len(paragraphs):
        p = paragraphs[i]
        if p.startswith("Part "):
            # Clean part name: e.g. "Part 1 – React foundations" -> "React Foundations"
            clean_part = re.sub(r"^Part\s*\d+\s*[\u2013\u2014\-–\?]+\s*", "", p).strip()
            if not clean_part:
                clean_part = p
            current_part = clean_part
            i += 1
            continue

        match = re.match(r"^(\d+)\.\s+(.*)$", p)
        if match:
            num = int(match.group(1))
            title = match.group(2).strip()
            explanation_parts = []
            code_parts = []
            official_link = ""

            i += 1
            while i < len(paragraphs) and not re.match(r"^(\d+)\.\s+", paragraphs[i]) and not paragraphs[i].startswith("Part "):
                line = paragraphs[i]
                if line.startswith("Official lesson:"):
                    official_link = line.replace("Official lesson:", "").strip()
                elif any(kw in line for kw in ["function ", "import ", "export ", "const ", "class ", "npm ", "<", "return ", "=>", "class Player"]):
                    code_parts.append(line)
                else:
                    explanation_parts.append(line)
                i += 1

            full_explanation = " ".join(explanation_parts).strip()
            full_code = "\n".join(code_parts).strip()

            # Generate sample output
            sample_output = f"// Rendered component: <{title.replace(' ', '')} />\n// Status: Active and running on React 18/19 DOM"
            if "npm " in full_code:
                sample_output = "Project initialized successfully.\nLocal: http://localhost:5173/\nNetwork: use --host to expose"
            elif "console.log" in full_code:
                sample_output = "Output logged to browser devtools console."
            elif "return" in full_code and "<h1>" in full_code:
                sample_output = "HTML Output: Rendered in #root container element"

            topics.append({
                "num": num,
                "title": title,
                "subtopic": current_part,
                "explanation": full_explanation or f"In-depth guide and best practices for {title} in modern React development.",
                "code": full_code,
                "official_link": official_link,
                "sample_output": sample_output
            })
        else:
            i += 1

    logger.info(f"Parsed {len(topics)} topics from React docx.")
    return topics

def get_python_curriculum():
    return [
        {
            "id": "py_intro",
            "topic_id": "py_intro",
            "title": "Introduction to Python",
            "subtopic": "Python Basics",
            "intro": "Python is a popular, high-level, interpreted programming language created by Guido van Rossum in 1991.",
            "definition": "Python is designed for code readability and developer efficiency with clean indentation-based syntax.",
            "explanation": "Python is versatile and widely used in web development (FastAPI, Django), data science, machine learning, software prototypes, automation scripting, and placement coding assessments. Its interactive interpreter allows instant execution without manual compilation.",
            "syntax": "# Python standard output\nprint(\"Hello, World!\")",
            "code_snippets": [
                {
                    "language": "python",
                    "code": "# Simple Hello World program\nuser_name = 'SkillPrep Student'\nprint(f'Hello {user_name}, welcome to your learning path!')\nversion = '3.12'\nprint(f'Running Python version: {version}')",
                    "output": "Hello SkillPrep Student, welcome to your learning path!\nRunning Python version: 3.12"
                }
            ],
            "notes": [
                "Python uses 4 spaces indentation instead of curly brackets { } to define code blocks.",
                "Everything in Python is an object, including primitive types and functions.",
                "Interpreted language: executes code line-by-line via the CPython runtime."
            ],
            "category": "python",
            "order": 1
        },
        {
            "id": "py_syntax",
            "topic_id": "py_syntax",
            "title": "Python Syntax",
            "subtopic": "Python Basics",
            "intro": "Python syntax refers to the set of rules that defines how a Python program is written and executed.",
            "definition": "Python syntax is clean and concise, using newlines to complete commands and standard 4-space indentation for code block scoping.",
            "explanation": "Unlike C, C++, or Java that require semicolons (;) and curly braces ({}), Python relies on whitespace indentation to define scope in loops, functions, conditionals, and classes. Comments start with # for single lines and triple quotes (''' or \"\"\") for docstrings.",
            "syntax": "# Python indentation example\nif 5 > 2:\n    print('Five is greater than two!')",
            "code_snippets": [
                {
                    "language": "python",
                    "code": "x = 10\ny = 20\nif y > x:\n    print('y is greater than x')\n    difference = y - x\n    print(f'Difference: {difference}')",
                    "output": "y is greater than x\nDifference: 10"
                }
            ],
            "notes": [
                "The standard indentation level is 4 spaces. Never mix tabs and spaces in the same file.",
                "Python statements can span multiple lines using parentheses (), brackets [], or backslashes \\.",
                "Docstrings are literal strings that occur as the first statement in a module, function, or class definition."
            ],
            "category": "python",
            "order": 2
        },
        {
            "id": "py_variables",
            "topic_id": "py_variables",
            "title": "Python Variables",
            "subtopic": "Python Basics",
            "intro": "Variables are containers for storing data values. In Python, variables are created the moment you first assign a value to them.",
            "definition": "Python has no command for declaring variable types; variables are dynamically bound to objects in memory.",
            "explanation": "Variable names must start with a letter or underscore, cannot begin with a number, and are case-sensitive (age, Age, and AGE are three different variables). Multiple variables can be assigned on a single line (x, y, z = 1, 2, 3). Global vs local scope is governed by where the variable is assigned and modified.",
            "syntax": "# Variable declaration and assignment\nx = 5\nname = 'Alice'\nis_valid = True",
            "code_snippets": [
                {
                    "language": "python",
                    "code": "user_name = 'Alex'\nuser_age = 21\nis_enrolled = True\n\nprint(f'Student: {user_name}, Age: {user_age}, Enrolled: {is_enrolled}')\n\n# Unpacking values\npoint = (10, 20)\nx_coord, y_coord = point\nprint(f'Coordinates: X={x_coord}, Y={y_coord}')",
                    "output": "Student: Alex, Age: 21, Enrolled: True\nCoordinates: X=10, Y=20"
                }
            ],
            "notes": [
                "Variables do not require type declarations and can be reassigned to different types dynamically.",
                "Follow PEP 8 naming conventions: use snake_case for variables and functions.",
                "The `global` keyword allows you to modify a variable outside of the current local scope."
            ],
            "category": "python",
            "order": 3
        },
        {
            "id": "py_datatypes",
            "topic_id": "py_datatypes",
            "title": "Python Data Types",
            "subtopic": "Python Basics",
            "intro": "In programming, data type is an important concept. Variables can store data of different types, and different types can do different things.",
            "definition": "Python has built-in data types categorized into Text (str), Numeric (int, float, complex), Sequence (list, tuple, range), Mapping (dict), Set (set), and Boolean (bool).",
            "explanation": "You can get the data type of any object by using the built-in type() function. Explicit type casting functions int(), float(), str(), and list() convert between compatible types.",
            "syntax": "# Checking and casting types\nx = 42\nprint(type(x))       # <class 'int'>\ny = float(x)         # 42.0",
            "code_snippets": [
                {
                    "language": "python",
                    "code": "val_int = 42\nval_float = 3.14159\nval_str = 'SkillPrep'\nval_bool = True\nval_none = None\n\nfor item in [val_int, val_float, val_str, val_bool, val_none]:\n    print(f'Value: {repr(item)} -> Type: {type(item).__name__}')",
                    "output": "Value: 42 -> Type: int\nValue: 3.14159 -> Type: float\nValue: 'SkillPrep' -> Type: str\nValue: True -> Type: bool\nValue: None -> Type: NoneType"
                }
            ],
            "notes": [
                "int in Python 3 has arbitrary precision, meaning it can grow as large as system memory permits without integer overflow.",
                "bool is a subclass of int where True == 1 and False == 0.",
                "None is a singleton object of NoneType used to signify the absence of a value."
            ],
            "category": "python",
            "order": 4
        },
        {
            "id": "py_strings",
            "topic_id": "py_strings",
            "title": "Python Strings",
            "subtopic": "Python Strings & Sequences",
            "intro": "Strings in Python are sequences of characters surrounded by either single quotation marks ('...') or double quotation marks (\"...\").",
            "definition": "Python strings are immutable sequences of Unicode code points. Once created, their individual characters cannot be modified in-place.",
            "explanation": "Strings support positive indexing (starting at 0) and negative indexing (starting at -1 for the last character). Slicing syntax string[start:stop:step] extracts substrings efficiently. Common methods include .upper(), .lower(), .strip(), .replace(), .split(), .join(), and .find(). F-strings (f'Hello {name}') provide concise and readable string interpolation.",
            "syntax": "# String declaration, indexing & slicing\ns = 'Python Programming'\nprint(s[0])       # 'P'\nprint(s[-1])      # 'g'\nprint(s[0:6])     # 'Python'\nprint(s[::-1])    # Reversed string",
            "code_snippets": [
                {
                    "language": "python",
                    "code": "text = '   Data Structures and Algorithms in Python   '\n\n# String cleanup and manipulation\ncleaned = text.strip()\nprint('Stripped:', cleaned)\nprint('Uppercase:', cleaned.upper())\nprint('Word count:', len(cleaned.split()))\n\n# Slicing examples\nprint('First 4 characters:', cleaned[:4])\nprint('Reversed slice:', cleaned[:15][::-1])\n\n# F-String formatting\nstudent = 'Priya'\nrank = 1\nprint(f'Top Performer: {student} (Rank #{rank})')",
                    "output": "Stripped: Data Structures and Algorithms in Python\nUppercase: DATA STRUCTURES AND ALGORITHMS IN PYTHON\nWord count: 6\nFirst 4 characters: Data\nReversed slice: rutcurtS ataD\nTop Performer: Priya (Rank #1)"
                },
                {
                    "language": "python",
                    "code": "message = 'Campus Placement Drive 2026'\n\n# Substring membership test\nif '2026' in message:\n    print('Eligible for upcoming 2026 batches')\n\n# Replace and split\nupdated = message.replace('Drive', 'Hiring Season')\nprint('Updated:', updated)\ntokens = updated.split(' ')\nprint('Tokens:', tokens)",
                    "output": "Eligible for upcoming 2026 batches\nUpdated: Campus Placement Hiring Season 2026\nTokens: ['Campus', 'Placement', 'Hiring', 'Season', '2026']"
                }
            ],
            "notes": [
                "Strings are immutable: s[0] = 'X' raises a TypeError.",
                "Use ''.join(list_of_strings) instead of repeated + concatenation inside loops for O(N) performance instead of O(N^2).",
                "Python has no distinct character type; a single character is simply a string with length 1.",
                "Triple quotes (''' or \"\"\") define multi-line strings preserving whitespace and newlines."
            ],
            "category": "python",
            "order": 5
        },
        {
            "id": "py_lists",
            "topic_id": "py_lists",
            "title": "Python Lists",
            "subtopic": "Python Collections",
            "intro": "Lists are used to store multiple items in a single variable. Lists are one of 4 built-in data types in Python used to store collections of data.",
            "definition": "Lists are ordered, changeable (mutable), and allow duplicate values. List items are indexed, with the first item having index [0].",
            "explanation": "Lists support dynamic resizing. Common operations include .append(x), .insert(i, x), .extend(iterable), .remove(x), .pop(i), .sort(), and list comprehensions [expr for x in iterable if cond].",
            "syntax": "# List creation and manipulation\nfruits = ['apple', 'banana', 'cherry']\nfruits.append('orange')\nfruits[1] = 'mango'",
            "code_snippets": [
                {
                    "language": "python",
                    "code": "scores = [85, 92, 78, 99, 88]\nscores.append(95)\nscores.sort()\nprint('Sorted scores:', scores)\nprint(f'Highest: {scores[-1]}, Lowest: {scores[0]}')\n\n# List comprehension\nhigh_scores = [s for s in scores if s >= 90]\nprint('Scores >= 90:', high_scores)",
                    "output": "Sorted scores: [78, 85, 88, 92, 95, 99]\nHighest: 99, Lowest: 78\nScores >= 90: [92, 95, 99]"
                }
            ],
            "notes": [
                "List append() is O(1) amortized, but insert(0, x) is O(N) because all subsequent elements must shift.",
                "List comprehensions are faster and more idiomatic than explicit for-loops with .append().",
                "Use list.copy() or arr[:] to make a shallow copy instead of assigning b = a (which copies reference)."
            ],
            "category": "python",
            "order": 6
        },
        {
            "id": "py_tuples",
            "topic_id": "py_tuples",
            "title": "Python Tuples",
            "subtopic": "Python Collections",
            "intro": "Tuples are used to store multiple items in a single variable. A tuple is a collection which is ordered and unchangeable.",
            "definition": "Tuples are written with round brackets (). They are ordered, immutable, and allow duplicate values.",
            "explanation": "Because tuples are immutable, they can be used as keys in dictionaries (provided their elements are hashable). Tuples consume less memory than lists and prevent accidental data alteration. Tuple packing and unpacking allow concise return values from functions.",
            "syntax": "# Tuple creation and unpacking\npoint = (10, 20)\nx, y = point",
            "code_snippets": [
                {
                    "language": "python",
                    "code": "def get_min_max(numbers):\n    return (min(numbers), max(numbers))\n\nresult = get_min_max([45, 12, 89, 33, 7])\nprint('Tuple returned:', result)\nminimum, maximum = result\nprint(f'Min: {minimum}, Max: {maximum}')",
                    "output": "Tuple returned: (7, 89)\nMin: 7, Max: 89"
                }
            ],
            "notes": [
                "To create a tuple with only one item, you MUST add a trailing comma: single = ('apple',).",
                "Tuples have only two built-in methods: .count() and .index().",
                "Tuples provide data integrity for fixed records (coordinates, database rows, configuration pairs)."
            ],
            "category": "python",
            "order": 7
        },
        {
            "id": "py_sets",
            "topic_id": "py_sets",
            "title": "Python Sets",
            "subtopic": "Python Collections",
            "intro": "Sets are used to store multiple items in a single variable. A set is a collection which is unordered, unchangeable, and unindexed.",
            "definition": "Sets are written with curly brackets {}. Set items are unique (duplicates are automatically discarded).",
            "explanation": "Sets support mathematical set operations like Union (|), Intersection (&), Difference (-), and Symmetric Difference (^). Checking if an element exists in a set (x in my_set) takes O(1) average time complexity because sets are implemented with hash tables.",
            "syntax": "# Set operations\nset_a = {1, 2, 3, 4}\nset_b = {3, 4, 5, 6}\nunion_set = set_a | set_b\ninter_set = set_a & set_b",
            "code_snippets": [
                {
                    "language": "python",
                    "code": "candidates_a = {'Rahul', 'Priya', 'Ananya', 'Vikram'}\ncandidates_b = {'Ananya', 'Vikram', 'Deepak', 'Sneha'}\n\n# Union: All unique candidates\nall_candidates = candidates_a | candidates_b\nprint('Total unique candidates:', len(all_candidates))\n\n# Intersection: Present in both batches\nboth = candidates_a & candidates_b\nprint('Present in both:', sorted(list(both)))",
                    "output": "Total unique candidates: 6\nPresent in both: ['Ananya', 'Vikram']"
                }
            ],
            "notes": [
                "Sets cannot contain mutable items like lists or dictionaries, but can contain tuples.",
                "To create an empty set, use set(), not {} (which creates an empty dictionary).",
                "Membership testing (item in set) is O(1) average time compared to O(N) in lists."
            ],
            "category": "python",
            "order": 8
        },
        {
            "id": "py_dictionaries",
            "topic_id": "py_dictionaries",
            "title": "Python Dictionaries",
            "subtopic": "Python Collections",
            "intro": "Dictionaries are used to store data values in key:value pairs. A dictionary is a collection which is ordered, changeable, and does not allow duplicate keys.",
            "definition": "Dictionaries are written with curly brackets, and have keys and values: {'name': 'Arun', 'branch': 'CSE'}.",
            "explanation": "Keys must be immutable and hashable (strings, numbers, tuples). Values can be of any data type. Dictionaries provide O(1) average time complexity for lookups, insertions, and deletions. Methods include .get(), .keys(), .values(), .items(), and dictionary comprehensions.",
            "syntax": "# Dictionary declaration and access\nstudent = {'name': 'Arun', 'score': 95}\nstudent['grade'] = 'A'\nscore = student.get('score', 0)",
            "code_snippets": [
                {
                    "language": "python",
                    "code": "profile = {\n    'name': 'Devi',\n    'skills': ['Python', 'SQL', 'React'],\n    'tests_completed': 14,\n    'rating': 1850\n}\n\n# Safe access with .get()\nscore = profile.get('ranking', 'Unranked')\nprint(f\"Student: {profile['name']} | Ranking: {score}\")\n\n# Iterating over items\nprint('Profile Details:')\nfor k, v in profile.items():\n    print(f'  {k}: {v}')",
                    "output": "Student: Devi | Ranking: Unranked\nProfile Details:\n  name: Devi\n  skills: ['Python', 'SQL', 'React']\n  tests_completed: 14\n  rating: 1850"
                }
            ],
            "notes": [
                "Starting in Python 3.7, dictionaries maintain insertion order.",
                "Use .get(key, default) to avoid KeyError when accessing a key that might not exist.",
                "Dictionary keys must be hashable objects (lists cannot be keys, but tuples can)."
            ],
            "category": "python",
            "order": 9
        },
        {
            "id": "py_conditions",
            "topic_id": "py_conditions",
            "title": "Python Conditions",
            "subtopic": "Python Control Flow",
            "intro": "Python supports the usual logical conditions from mathematics: equals (==), not equals (!=), less than (<), greater than (>), etc.",
            "definition": "Conditional statements allow decision making: if, elif, and else blocks execute conditionally based on boolean evaluations.",
            "explanation": "Logical operators and, or, and not combine conditional statements. Short-circuit evaluation evaluates expressions from left to right and stops as soon as the outcome is determined. Ternary operator a if condition else b provides concise inline evaluation.",
            "syntax": "# if, elif, else structure\nif score >= 90:\n    grade = 'A'\nelif score >= 75:\n    grade = 'B'\nelse:\n    grade = 'C'",
            "code_snippets": [
                {
                    "language": "python",
                    "code": "marks = 88\nif marks >= 90:\n    grade = 'A+'\nelif marks >= 80:\n    grade = 'A'\nelif marks >= 70:\n    grade = 'B'\nelse:\n    grade = 'C'\n\nprint(f'Marks: {marks} -> Grade: {grade}')\n\n# One-line ternary conditional\nstatus = 'Eligible' if marks >= 75 else 'Needs Improvement'\nprint('Placement Status:', status)",
                    "output": "Marks: 88 -> Grade: A\nPlacement Status: Eligible"
                }
            ],
            "notes": [
                "Indentation is strictly required to indicate the body of each conditional block.",
                "Empty strings, empty lists, empty dictionaries, 0, and None evaluate to False in boolean context.",
                "'is' tests object identity (same memory address), whereas '==' tests value equality."
            ],
            "category": "python",
            "order": 10
        },
        {
            "id": "py_loops",
            "topic_id": "py_loops",
            "title": "Python Loops",
            "subtopic": "Python Control Flow",
            "intro": "Python has two primitive loop commands: while loops and for loops.",
            "definition": "A while loop executes as long as a condition is true. A for loop iterates over a sequence (list, tuple, dictionary, set, string, or range()).",
            "explanation": "Loop control keywords: break terminates loop execution immediately; continue skips the rest of the current iteration; pass is a null statement used as a placeholder. The else block on loops executes when the loop finishes normally without encountering a break.",
            "syntax": "# for loop with range\nfor i in range(1, 6):\n    print(i)\n\n# while loop\ncount = 0\nwhile count < 3:\n    count += 1",
            "code_snippets": [
                {
                    "language": "python",
                    "code": "# Sum of numbers using a while loop\nn = 5\ntotal = 0\ni = 1\nwhile i <= n:\n    total += i\n    i += 1\nprint(f'Sum of first {n} numbers: {total}')\n\n# Enumerate in for loop\ntopics = ['Syntax', 'Variables', 'Strings', 'Lists']\nprint('Topic syllabus:')\nfor idx, topic in enumerate(topics, 1):\n    print(f'  {idx}. Python {topic}')",
                    "output": "Sum of first 5 numbers: 15\nTopic syllabus:\n  1. Python Syntax\n  2. Python Variables\n  3. Python Strings\n  4. Python Lists"
                }
            ],
            "notes": [
                "Use enumerate() when you need both the index and the item during iteration.",
                "Use zip() to iterate through multiple lists in parallel.",
                "range(start, stop, step) produces numbers up to but not including stop."
            ],
            "category": "python",
            "order": 11
        },
        {
            "id": "py_functions",
            "topic_id": "py_functions",
            "title": "Python Functions",
            "subtopic": "Python Functions & Scope",
            "intro": "A function is a block of code which only runs when it is called. You can pass data, known as parameters, into a function.",
            "definition": "Functions are defined using the def keyword. Functions can return data as a result using the return statement.",
            "explanation": "Supports positional arguments, keyword arguments, default parameter values, arbitrary arguments (*args), and arbitrary keyword arguments (**kwargs). Anonymous inline functions can be created using lambda expressions.",
            "syntax": "def calculate_net_salary(base, bonus=0):\n    return base + bonus\n\nsquare = lambda x: x * x",
            "code_snippets": [
                {
                    "language": "python",
                    "code": "def calculate_placement_score(mcq, coding, attendance=100):\n    '''Calculates weighted placement readiness score.'''\n    total = (mcq * 0.4) + (coding * 0.5) + (attendance * 0.1)\n    return round(total, 2)\n\nscore1 = calculate_placement_score(85, 90)\nscore2 = calculate_placement_score(92, 84, attendance=95)\nprint(f'Candidate 1 Score: {score1}/100')\nprint(f'Candidate 2 Score: {score2}/100')\n\n# Lambda sorting\nstudents = [('Rahul', 88), ('Priya', 95), ('Ananya', 92)]\nstudents.sort(key=lambda s: s[1], reverse=True)\nprint('Rankings:', students)",
                    "output": "Candidate 1 Score: 89.0/100\nCandidate 2 Score: 88.3/100\nRankings: [('Priya', 95), ('Ananya', 92), ('Rahul', 88)]"
                }
            ],
            "notes": [
                "Default parameter values are evaluated once at function definition time; avoid mutable default values like def foo(items=[]).",
                "*args collects positional arguments into a tuple; **kwargs collects keyword arguments into a dictionary.",
                "Scope resolution follows the LEGB rule: Local, Enclosing, Global, Built-in."
            ],
            "category": "python",
            "order": 12
        },
        {
            "id": "py_classes_objects",
            "topic_id": "py_classes_objects",
            "title": "Python Classes and Objects",
            "subtopic": "Python Object-Oriented Programming",
            "intro": "Python is an object-oriented programming language. Almost everything in Python is an object, with its properties and methods.",
            "definition": "A Class is like an object constructor, or a 'blueprint' for creating objects. An Object is an instance of a Class.",
            "explanation": "The __init__() method is called automatically every time the class is being used to create a new object. The self parameter is a reference to the current instance of the class and is used to access variables that belong to the class. Covers OOP principles: Encapsulation, Inheritance (class Child(Parent)), and Polymorphism.",
            "syntax": "class Student:\n    def __init__(self, name, roll_no):\n        self.name = name\n        self.roll_no = roll_no\n    \n    def get_details(self):\n        return f'{self.name} (Roll: {self.roll_no})'",
            "code_snippets": [
                {
                    "language": "python",
                    "code": "class StudentArena:\n    def __init__(self, name, student_id):\n        self.name = name\n        self.student_id = student_id\n        self.points = 0\n        self.completed_topics = []\n\n    def complete_topic(self, topic_name, xp=15):\n        self.completed_topics.append(topic_name)\n        self.points += xp\n        return f\"{self.name} completed '{topic_name}' (+{xp} XP). Total: {self.points} pts\"\n\nstudent = StudentArena('Priya Sharma', 'STU-2026-001')\nprint(student.complete_topic('Python Strings'))\nprint(student.complete_topic('Python Lists'))",
                    "output": "Priya Sharma completed 'Python Strings' (+15 XP). Total: 15 pts\nPriya Sharma completed 'Python Lists' (+15 XP). Total: 30 pts"
                }
            ],
            "notes": [
                "__init__ acts as the constructor method in Python classes.",
                "self must be explicitly listed as the first argument in instance methods, though it is passed automatically when calling.",
                "super() delegates method calls to the parent class, enabling clean inheritance hierarchies."
            ],
            "category": "python",
            "order": 13
        }
    ]

def seed_all():
    init_db_engine()
    db = SessionLocal()
    if not db:
        logger.error("Could not obtain DB session")
        return

    try:
        # 1. SEED / UPDATE PYTHON MODULE (13 TOPICS)
        python_lessons = get_python_curriculum()
        py_topics_meta = [
            {
                "id": l["id"],
                "title": l["title"],
                "slug": l["title"].lower().replace(" ", "-"),
                "order": l["order"],
                "is_completed": False,
                "subtopic": l["subtopic"]
            }
            for l in python_lessons
        ]

        mod_py = db.query(LearningModuleModel).filter(LearningModuleModel.id == "mod_python").first()
        if not mod_py:
            mod_py = LearningModuleModel(
                id="mod_python",
                title="Python Programming & Core Concepts",
                category="python",
                description="Master Python syntax, strings, data structures, control flow, functions, and OOP with executable code examples and placement tips.",
                icon="code-2",
                total_lessons=len(python_lessons),
                completed_lessons=0,
                progress_percentage=0.0,
                topics=py_topics_meta
            )
            db.add(mod_py)
            logger.info("Created mod_python")
        else:
            mod_py.title = "Python Programming & Core Concepts"
            mod_py.description = "Master Python syntax, strings, data structures, control flow, functions, and OOP with executable code examples and placement tips."
            mod_py.total_lessons = len(python_lessons)
            mod_py.topics = py_topics_meta
            logger.info("Updated mod_python metadata")

        for l in python_lessons:
            existing = db.query(LessonModel).filter(LessonModel.id == l["id"]).first()
            if not existing:
                new_lesson = LessonModel(
                    id=l["id"],
                    module_id="mod_python",
                    topic_id=l["topic_id"],
                    subtopic=l["subtopic"],
                    title=l["title"],
                    intro=l["intro"],
                    definition=l["definition"],
                    explanation=l["explanation"],
                    syntax=l["syntax"],
                    code_snippets=l["code_snippets"],
                    notes=l["notes"],
                    category=l["category"],
                    order=l["order"],
                    is_completed=False
                )
                db.add(new_lesson)
                logger.info(f"Added Python lesson: {l['title']}")
            else:
                existing.title = l["title"]
                existing.subtopic = l["subtopic"]
                existing.intro = l["intro"]
                existing.definition = l["definition"]
                existing.explanation = l["explanation"]
                existing.syntax = l["syntax"]
                existing.code_snippets = l["code_snippets"]
                # Keep any existing custom student notes while merging default notes
                existing_notes = list(existing.notes or [])
                for def_note in l["notes"]:
                    if def_note not in existing_notes:
                        existing_notes.append(def_note)
                existing.notes = existing_notes
                existing.order = l["order"]
                logger.info(f"Updated Python lesson: {l['title']}")

        # 2. SEED REACT MODULE (FROM Complete_React_Tutorial_Study_Guide.docx)
        react_topics = parse_react_docx()
        if react_topics:
            react_topics_meta = [
                {
                    "id": f"react_{t['num']}",
                    "title": t["title"],
                    "slug": f"react-{t['num']}-{t['title'].lower().replace(' ', '-')[:30]}",
                    "order": t["num"],
                    "is_completed": False,
                    "subtopic": t["subtopic"]
                }
                for t in react_topics
            ]

            mod_react = db.query(LearningModuleModel).filter(LearningModuleModel.id == "mod_react").first()
            if not mod_react:
                mod_react = LearningModuleModel(
                    id="mod_react",
                    title="React JS Complete Tutorial & Guide",
                    category="react",
                    description="Comprehensive W3Schools-aligned React study guide covering foundations, ES6, JSX, components, props, hooks, forms, and router.",
                    icon="layers",
                    total_lessons=len(react_topics),
                    completed_lessons=0,
                    progress_percentage=0.0,
                    topics=react_topics_meta
                )
                db.add(mod_react)
                logger.info("Created mod_react")
            else:
                mod_react.title = "React JS Complete Tutorial & Guide"
                mod_react.description = "Comprehensive W3Schools-aligned React study guide covering foundations, ES6, JSX, components, props, hooks, forms, and router."
                mod_react.total_lessons = len(react_topics)
                mod_react.topics = react_topics_meta
                logger.info("Updated mod_react metadata")

            for t in react_topics:
                l_id = f"react_{t['num']}"
                existing_r = db.query(LessonModel).filter(LessonModel.id == l_id).first()
                notes_list = [
                    f"Official W3Schools Reference: {t['official_link']}" if t['official_link'] else "Core React concept for frontend and full-stack development.",
                    f"Part Category: {t['subtopic']}",
                    "Type the code into your Vite/React project and inspect the rendered result in browser."
                ]
                code_snips = []
                if t["code"]:
                    code_snips.append({
                        "language": "jsx",
                        "code": t["code"],
                        "output": t["sample_output"]
                    })

                if not existing_r:
                    new_r = LessonModel(
                        id=l_id,
                        module_id="mod_react",
                        topic_id=l_id,
                        subtopic=t["subtopic"],
                        title=f"{t['num']}. {t['title']}",
                        intro=t["explanation"][:200] + ("..." if len(t["explanation"]) > 200 else ""),
                        definition=f"Topic {t['num']}: {t['title']} in {t['subtopic']}.",
                        explanation=t["explanation"],
                        syntax=t["code"] if len(t["code"]) < 200 else "",
                        code_snippets=code_snips,
                        notes=notes_list,
                        category="react",
                        order=t["num"],
                        is_completed=False
                    )
                    db.add(new_r)
                else:
                    existing_r.title = f"{t['num']}. {t['title']}"
                    existing_r.subtopic = t["subtopic"]
                    existing_r.explanation = t["explanation"]
                    if code_snips:
                        existing_r.code_snippets = code_snips
                    existing_r.order = t["num"]

        # 3. ENSURE SUBTOPICS FOR EXISTING DSA, SQL, AND APTITUDE MODULES
        dsa_lessons = db.query(LessonModel).filter(LessonModel.module_id == "mod_dsa").all()
        for dl in dsa_lessons:
            if not dl.subtopic:
                dl.subtopic = "Data Structures & Complexity"

        sql_lessons = db.query(LessonModel).filter(LessonModel.module_id == "mod_sql").all()
        for sl in sql_lessons:
            if not sl.subtopic:
                sl.subtopic = "Relational Databases & Queries"

        apt_lessons = db.query(LessonModel).filter(LessonModel.module_id == "mod_aptitude").all()
        for al in apt_lessons:
            if not al.subtopic:
                al.subtopic = "Quantitative Aptitude Formulas"

        db.commit()
        logger.info("Successfully seeded all learning modules and topics in MySQL!")
    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_all()
