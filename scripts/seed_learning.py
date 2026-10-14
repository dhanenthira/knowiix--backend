import logging
from app.core.database import SessionLocal, init_db_engine
from app.models.sql_models import LearningModuleModel, LessonModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_learning")

def seed_learning_data():
    init_db_engine()
    db = SessionLocal()
    if not db:
        logger.error("Could not obtain DB session")
        return

    try:
        modules_data = [
            {
                "id": "mod_python",
                "title": "Python Programming & Core Concepts",
                "category": "python",
                "description": "Master Python syntax, object-oriented programming, data structures, and standard libraries with executable code examples and placement tips.",
                "icon": "code-2",
                "topics": [
                    {"id": "py_intro", "title": "1. Python Introduction & Setup", "slug": "python-intro", "order": 1, "is_completed": True},
                    {"id": "py_syntax", "title": "2. Syntax, Variables & Data Types", "slug": "python-syntax", "order": 2, "is_completed": True},
                    {"id": "py_control", "title": "3. Control Flow & Loops", "slug": "python-control", "order": 3, "is_completed": False},
                    {"id": "py_functions", "title": "4. Functions & Lambda Expressions", "slug": "python-functions", "order": 4, "is_completed": False},
                    {"id": "py_oop", "title": "5. Object-Oriented Programming (OOP)", "slug": "python-oop", "order": 5, "is_completed": False}
                ],
                "lessons": [
                    {
                        "id": "py_intro",
                        "topic_id": "py_intro",
                        "title": "Python Introduction & Getting Started",
                        "intro": "Python is a high-level, interpreted, dynamically-typed programming language created by Guido van Rossum in 1991.",
                        "definition": "Python emphasizes code readability and programmer productivity with clean indentation-based syntax.",
                        "explanation": "Python is versatile and widely used in web development, backend microservices, data science, artificial intelligence, automation scripting, and placement coding assessments.",
                        "syntax": "# Printing to console\nprint('Welcome to SkillPrep Student Arena!')",
                        "code_snippets": [
                            {
                                "language": "python",
                                "code": "# Simple Hello World program\nuser_name = 'SkillPrep Student'\nprint(f'Hello {user_name}, welcome to your learning path!')",
                                "output": "Hello SkillPrep Student, welcome to your learning path!"
                            }
                        ],
                        "notes": [
                            "Python uses 4 spaces indentation instead of curly brackets { } to define code blocks.",
                            "Everything in Python is an object, including functions and primitive types.",
                            "Interpreted language: executes code line-by-line via the CPython runtime."
                        ],
                        "category": "python",
                        "order": 1,
                        "is_completed": True,
                        "practice_topic_id": "q_tech_01"
                    },
                    {
                        "id": "py_syntax",
                        "topic_id": "py_syntax",
                        "title": "Python Syntax, Variables & Data Types",
                        "intro": "Variables are containers for storing values. In Python, variables do not require explicit type declarations.",
                        "definition": "Python is dynamically typed: the variable type is inferred at runtime when assigned.",
                        "explanation": "Core built-in types include int, float, str, bool, list, tuple, dict, and set. Memory allocation is automatic via reference counting and garbage collection.",
                        "syntax": "x = 42          # int\npi = 3.14159    # float\nname = 'Alice'  # str\nis_valid = True # bool",
                        "code_snippets": [
                            {
                                "language": "python",
                                "code": "student_scores = {'math': 95, 'physics': 88, 'coding': 99}\nfor subject, score in student_scores.items():\n    print(f'{subject.capitalize()}: {score}/100')",
                                "output": "Math: 95/100\nPhysics: 88/100\nCoding: 99/100"
                            }
                        ],
                        "notes": [
                            "Lists are mutable [1, 2, 3], while tuples are immutable (1, 2, 3).",
                            "Dictionary lookups have O(1) average time complexity due to hashing.",
                            "Variable names cannot begin with numbers or contain spaces."
                        ],
                        "category": "python",
                        "order": 2,
                        "is_completed": True,
                        "practice_topic_id": "q_tech_01"
                    },
                    {
                        "id": "py_control",
                        "topic_id": "py_control",
                        "title": "Control Flow, Conditionals & Loops",
                        "intro": "Control flow statements direct the order of execution based on conditional evaluations and iterations.",
                        "definition": "if, elif, and else statements evaluate boolean conditions; for and while statements execute repetitive code blocks.",
                        "explanation": "Python's `for...in` loop iterates seamlessly over iterables. The `range()` function generates arithmetic progressions efficiently using generators.",
                        "syntax": "if score >= 90:\n    grade = 'A'\nelif score >= 75:\n    grade = 'B'\nelse:\n    grade = 'C'",
                        "code_snippets": [
                            {
                                "language": "python",
                                "code": "even_squares = [n ** 2 for n in range(1, 11) if n % 2 == 0]\nprint('Even squares 1-10:', even_squares)",
                                "output": "Even squares 1-10: [4, 16, 36, 64, 100]"
                            }
                        ],
                        "notes": [
                            "List comprehensions `[expr for item in list if cond]` are faster and more idiomatic than standard loops.",
                            "`break` terminates the loop immediately; `continue` skips the current iteration.",
                            "The `else` clause in a for/while loop executes only if the loop was NOT terminated by `break`."
                        ],
                        "category": "python",
                        "order": 3,
                        "is_completed": False,
                        "practice_topic_id": "q_tech_02"
                    },
                    {
                        "id": "py_functions",
                        "topic_id": "py_functions",
                        "title": "Functions, Scope & Lambda Expressions",
                        "intro": "Functions are reusable blocks of code that perform specific tasks and help structure clean software architectures.",
                        "definition": "Defined using the `def` keyword or anonymously using `lambda` for single-expression callables.",
                        "explanation": "Supports positional arguments, default arguments, variable positional args (*args), and keyword arguments (**kwargs).",
                        "syntax": "def calculate_net_salary(base, bonus=0):\n    return base + bonus\n\nsquare = lambda x: x * x",
                        "code_snippets": [
                            {
                                "language": "python",
                                "code": "def find_max_min(*numbers):\n    return max(numbers), min(numbers)\n\nhigh, low = find_max_min(15, 82, 3, 99, 44)\nprint(f'Highest: {high}, Lowest: {low}')",
                                "output": "Highest: 99, Lowest: 3"
                            }
                        ],
                        "notes": [
                            "Functions in Python are first-class citizens: they can be passed as arguments and returned from other functions.",
                            "Scope resolution follows the LEGB rule: Local, Enclosing, Global, Built-in.",
                            "Avoid mutable default arguments like `def append_to(item, target=[])` because the list persists across calls."
                        ],
                        "category": "python",
                        "order": 4,
                        "is_completed": False,
                        "practice_topic_id": "q_tech_02"
                    },
                    {
                        "id": "py_oop",
                        "topic_id": "py_oop",
                        "title": "Object-Oriented Programming (Classes & Inheritance)",
                        "intro": "OOP structures software by bundling related properties and behaviors into individual objects.",
                        "definition": "The four pillars of OOP: Encapsulation, Abstraction, Inheritance, and Polymorphism.",
                        "explanation": "Classes define blueprints using the `class` keyword. The `__init__` constructor initializes instance attributes, and `self` references the current instance.",
                        "syntax": "class Student:\n    def __init__(self, name, roll_no):\n        self.name = name\n        self.roll_no = roll_no",
                        "code_snippets": [
                            {
                                "language": "python",
                                "code": "class Account:\n    def __init__(self, owner, balance=0):\n        self.owner = owner\n        self._balance = balance\n\n    def deposit(self, amount):\n        self._balance += amount\n        return f'Balance: ${self._balance}'\n\nacc = Account('Devi', 500)\nprint(acc.deposit(250))",
                                "output": "Balance: $750"
                            }
                        ],
                        "notes": [
                            "`__init__` is the constructor method called automatically when creating an object.",
                            "Single underscore `_var` indicates protected convention; double underscore `__var` triggers name mangling for private variables.",
                            "`super()` is used to call parent class methods."
                        ],
                        "category": "python",
                        "order": 5,
                        "is_completed": False,
                        "practice_topic_id": "q_tech_02"
                    }
                ]
            },
            {
                "id": "mod_dsa",
                "title": "Data Structures & Algorithms (Interview Prep)",
                "category": "dsa",
                "description": "Master Arrays, Linked Lists, Stacks, Queues, Binary Trees, and Dynamic Programming with time & space complexity formulas.",
                "icon": "layers",
                "topics": [
                    {"id": "dsa_arrays", "title": "1. Arrays & Two-Pointer Patterns", "slug": "dsa-arrays", "order": 1, "is_completed": False},
                    {"id": "dsa_linkedlist", "title": "2. Singly & Doubly Linked Lists", "slug": "dsa-linkedlist", "order": 2, "is_completed": False},
                    {"id": "dsa_stack_queue", "title": "3. Stacks, Queues & Monotonic Patterns", "slug": "dsa-stack-queue", "order": 3, "is_completed": False},
                    {"id": "dsa_trees", "title": "4. Binary Search Trees & Traversals", "slug": "dsa-trees", "order": 4, "is_completed": False}
                ],
                "lessons": [
                    {
                        "id": "dsa_arrays",
                        "topic_id": "dsa_arrays",
                        "title": "Arrays & Two-Pointer Patterns",
                        "intro": "Arrays store elements in contiguous memory locations, providing O(1) random access by index.",
                        "definition": "Two-pointer technique uses two indices traversing an array (e.g., from opposite ends or fast/slow speeds) to solve problems in O(N) time with O(1) space.",
                        "explanation": "Ideal for sorted pair sum, palindrome verification, trapping rainwater, and removing duplicates in-place.",
                        "syntax": "left = 0\nright = len(arr) - 1\nwhile left < right:\n    # evaluate condition\n    left += 1\n    right -= 1",
                        "code_snippets": [
                            {
                                "language": "python",
                                "code": "def two_sum_sorted(numbers, target):\n    l, r = 0, len(numbers) - 1\n    while l < r:\n        s = numbers[l] + numbers[r]\n        if s == target: return [l, r]\n        elif s < target: l += 1\n        else: r -= 1\n    return []\n\nprint('Indices found:', two_sum_sorted([2, 7, 11, 15], 9))",
                                "output": "Indices found: [0, 1]"
                            }
                        ],
                        "notes": [
                            "Time Complexity: O(N) single pass instead of brute force O(N^2).",
                            "Space Complexity: O(1) auxiliary space.",
                            "Prerequisite: Array must be sorted for opposite-end pointers."
                        ],
                        "category": "dsa",
                        "order": 1,
                        "is_completed": False,
                        "practice_topic_id": "q_tech_01"
                    },
                    {
                        "id": "dsa_linkedlist",
                        "topic_id": "dsa_linkedlist",
                        "title": "Singly & Doubly Linked Lists",
                        "intro": "A linked list is a linear data structure where elements (nodes) contain data and pointers to the next node.",
                        "definition": "Unlike arrays, linked lists have dynamic sizing and O(1) insertions/deletions at the head without memory reallocation.",
                        "explanation": "Standard interview problems include reversing a linked list, cycle detection (Floyd's Tortoise and Hare), and merging two sorted lists.",
                        "syntax": "class ListNode:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next",
                        "code_snippets": [
                            {
                                "language": "python",
                                "code": "# Reversing a Linked List iteratively\ndef reverse_list(head):\n    prev, curr = None, head\n    while curr:\n        nxt = curr.next\n        curr.next = prev\n        prev = curr\n        curr = nxt\n    return prev\n\nprint('Linked List reversal algorithm verified: O(N) time, O(1) space')",
                                "output": "Linked List reversal algorithm verified: O(N) time, O(1) space"
                            }
                        ],
                        "notes": [
                            "Cycle detection: Fast pointer moves 2 steps, slow pointer moves 1 step. If they meet, a cycle exists.",
                            "Access by index is O(N) since you must traverse sequentially from head.",
                            "Always use a dummy node (`dummy = ListNode(0)`) to simplify edge cases when modifying the list head."
                        ],
                        "category": "dsa",
                        "order": 2,
                        "is_completed": False,
                        "practice_topic_id": "q_tech_01"
                    },
                    {
                        "id": "dsa_stack_queue",
                        "topic_id": "dsa_stack_queue",
                        "title": "Stacks, Queues & Monotonic Patterns",
                        "intro": "Stacks operate on LIFO (Last-In-First-Out); Queues operate on FIFO (First-In-First-Out).",
                        "definition": "A Monotonic Stack maintains elements in strictly ascending or descending order to find Next Greater Elements in O(N).",
                        "explanation": "Used in balanced parenthesis validation, browser history navigation, Dijkstra's shunting-yard algorithm, and daily temperature questions.",
                        "syntax": "stack = []\nstack.append(x) # Push O(1)\nstack.pop()      # Pop O(1)",
                        "code_snippets": [
                            {
                                "language": "python",
                                "code": "def is_valid_brackets(s: str) -> bool:\n    mapping = {')': '(', '}': '{', ']': '['}\n    stack = []\n    for char in s:\n        if char in mapping:\n            top = stack.pop() if stack else '#'\n            if mapping[char] != top: return False\n        else:\n            stack.append(char)\n    return not stack\n\nprint('Valid parentheses check [()]{}:', is_valid_brackets('[()]{}'))",
                                "output": "Valid parentheses check [()]{}: True"
                            }
                        ],
                        "notes": [
                            "Python `list` works as a stack using `append()` and `pop()`.",
                            "For queues, use `collections.deque` instead of `list` because `list.pop(0)` is O(N), whereas `deque.popleft()` is O(1).",
                            "Recursion internally utilizes the system call stack."
                        ],
                        "category": "dsa",
                        "order": 3,
                        "is_completed": False,
                        "practice_topic_id": "q_tech_01"
                    },
                    {
                        "id": "dsa_trees",
                        "topic_id": "dsa_trees",
                        "title": "Binary Search Trees & Traversals",
                        "intro": "A Binary Search Tree (BST) is a hierarchical tree data structure where each node has at most two children.",
                        "definition": "BST Property: For any node X, all values in its left subtree are < X.val, and all values in its right subtree are > X.val.",
                        "explanation": "Traversals: In-order (Left, Root, Right) gives sorted order; Pre-order (Root, Left, Right); Post-order (Left, Right, Root); Level-order (BFS via Queue).",
                        "syntax": "class TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right",
                        "code_snippets": [
                            {
                                "language": "python",
                                "code": "def inorder_traversal(root):\n    return inorder_traversal(root.left) + [root.val] + inorder_traversal(root.right) if root else []\n\nprint('BST in-order traversal yields strictly sorted sequence in O(N)')",
                                "output": "BST in-order traversal yields strictly sorted sequence in O(N)"
                            }
                        ],
                        "notes": [
                            "Average search/insert/delete in balanced BST is O(log N). Worst case for skewed BST is O(N).",
                            "Balanced BST implementations include AVL Trees and Red-Black Trees.",
                            "Height of balanced BST: h = floor(log2(N))."
                        ],
                        "category": "dsa",
                        "order": 4,
                        "is_completed": False,
                        "practice_topic_id": "q_tech_01"
                    }
                ]
            },
            {
                "id": "mod_sql",
                "title": "Database & SQL Mastery",
                "category": "sql",
                "description": "Relational database concepts, SQL queries, JOINs, aggregations, indexing, and normalization for placement interviews.",
                "icon": "database",
                "topics": [
                    {"id": "sql_basics", "title": "1. SQL Queries: SELECT, WHERE, GROUP BY", "slug": "sql-basics", "order": 1, "is_completed": False},
                    {"id": "sql_joins", "title": "2. SQL Joins: INNER, LEFT, RIGHT, FULL", "slug": "sql-joins", "order": 2, "is_completed": False},
                    {"id": "sql_indexes", "title": "3. Indexing, B-Trees & ACID Transactions", "slug": "sql-indexes", "order": 3, "is_completed": False}
                ],
                "lessons": [
                    {
                        "id": "sql_basics",
                        "topic_id": "sql_basics",
                        "title": "SQL Queries: SELECT, WHERE, GROUP BY & HAVING",
                        "intro": "SQL (Structured Query Language) is the standard language for storing, manipulating, and retrieving data in relational databases.",
                        "definition": "Query clauses execute in a specific order: FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY -> LIMIT.",
                        "explanation": "Aggregate functions (COUNT, SUM, AVG, MAX, MIN) summarize data. `HAVING` filters aggregated groups, whereas `WHERE` filters individual rows.",
                        "syntax": "SELECT department, AVG(salary) as avg_sal\nFROM employees\nWHERE status = 'active'\nGROUP BY department\nHAVING avg_sal > 60000\nORDER BY avg_sal DESC;",
                        "code_snippets": [
                            {
                                "language": "sql",
                                "code": "-- Finding top 3 highest scoring students\nSELECT name, college_name, total_points \nFROM users \nWHERE role = 'student' \nORDER BY total_points DESC \nLIMIT 3;",
                                "output": "1. Priya Sharma - 2450 pts\n2. Rahul Verma - 2120 pts\n3. Ananya Kumar - 1980 pts"
                            }
                        ],
                        "notes": [
                            "WHERE filters rows BEFORE grouping; HAVING filters rows AFTER grouping.",
                            "NULL values are ignored by aggregate functions (except COUNT(*)).",
                            "Use LIKE '%pattern%' for wildcard searches; ILIKE for case-insensitive search."
                        ],
                        "category": "sql",
                        "order": 1,
                        "is_completed": False,
                        "practice_topic_id": "q_tech_02"
                    },
                    {
                        "id": "sql_joins",
                        "topic_id": "sql_joins",
                        "title": "SQL Joins: INNER, LEFT, RIGHT & FULL OUTER",
                        "intro": "Joins combine columns from two or more tables based on a related column between them.",
                        "definition": "INNER JOIN returns matching rows only; LEFT JOIN returns all rows from left table plus matching rows from right; RIGHT JOIN returns right table rows; FULL OUTER combines both.",
                        "explanation": "Critical in multi-table schema designs like Users -> Submissions -> Questions.",
                        "syntax": "SELECT u.name, s.score, s.submitted_at\nFROM users u\nINNER JOIN submissions s ON u.id = s.user_id\nWHERE s.status = 'accepted';",
                        "code_snippets": [
                            {
                                "language": "sql",
                                "code": "-- Left Join to find students who haven't submitted any problems\nSELECT u.name, u.email\nFROM users u\nLEFT JOIN submissions s ON u.id = s.user_id\nWHERE s.id IS NULL;",
                                "output": "Empty set (All verified students have submissions)"
                            }
                        ],
                        "notes": [
                            "Always ensure foreign keys are indexed for fast join performance.",
                            "Cross Join produces a Cartesian product (M * N rows) - use with caution.",
                            "Self Join joins a table to itself (e.g., Employee and Manager hierarchy)."
                        ],
                        "category": "sql",
                        "order": 2,
                        "is_completed": False,
                        "practice_topic_id": "q_tech_02"
                    },
                    {
                        "id": "sql_indexes",
                        "topic_id": "sql_indexes",
                        "title": "Indexing, B-Trees & ACID Transactions",
                        "intro": "Indexes are specialized data structures that speed up query search operations at the cost of slower writes and additional disk space.",
                        "definition": "Relational engines (MySQL InnoDB) use B+ Tree indexes where leaf nodes contain pointers to data rows.",
                        "explanation": "ACID Properties: Atomicity (All or Nothing), Consistency (Valid states), Isolation (Concurrent safety), Durability (Committed data survives crashes).",
                        "syntax": "CREATE INDEX idx_user_email ON users(email);\n\nSTART TRANSACTION;\nUPDATE accounts SET balance = balance - 100 WHERE id = 1;\nUPDATE accounts SET balance = balance + 100 WHERE id = 2;\nCOMMIT;",
                        "code_snippets": [
                            {
                                "language": "sql",
                                "code": "-- EXPLAIN query execution plan\nEXPLAIN SELECT * FROM questions WHERE category = 'aptitude';",
                                "output": "type: ref | key: idx_questions_category | rows: 12 | Extra: Using index condition"
                            }
                        ],
                        "notes": [
                            "Clustered Index: The table itself is ordered by the Primary Key (one per table).",
                            "Non-Clustered / Secondary Index: Separate structure containing key value and PK reference.",
                            "Avoid over-indexing tables with high write/insert volumes."
                        ],
                        "category": "sql",
                        "order": 3,
                        "is_completed": False,
                        "practice_topic_id": "q_tech_02"
                    }
                ]
            },
            {
                "id": "mod_aptitude",
                "title": "Campus Placement Aptitude Formulas & Notes",
                "category": "aptitude",
                "description": "Essential quantitative formulas, mental math shortcuts, and problem-solving rules for campus placement recruitment drives (TCS, Infosys, Cognizant, Wipro).",
                "icon": "brain",
                "topics": [
                    {"id": "apt_time_work", "title": "1. Time & Work, Pipes & Cisterns", "slug": "apt-time-work", "order": 1, "is_completed": False},
                    {"id": "apt_speed_dist", "title": "2. Time, Speed & Distance (Trains & Boats)", "slug": "apt-speed-dist", "order": 2, "is_completed": False},
                    {"id": "apt_profit_loss", "title": "3. Profit, Loss, Discount & Percentage", "slug": "apt-profit-loss", "order": 3, "is_completed": False}
                ],
                "lessons": [
                    {
                        "id": "apt_time_work",
                        "topic_id": "apt_time_work",
                        "title": "Time & Work, Pipes & Cisterns Shortcuts",
                        "intro": "Work is inversely proportional to time: if A completes a work in 'n' days, then A's 1 day work = 1/n.",
                        "definition": "LCM Method: Assume total work = LCM of individual days taken by workers. Efficiency = Total Work / Days taken.",
                        "explanation": "If A takes 10 days and B takes 15 days, LCM(10, 15) = 30 units of work. A efficiency = 3 units/day, B efficiency = 2 units/day. Combined = 5 units/day -> 30/5 = 6 days.",
                        "syntax": "Total Work = Efficiency * Time\nCombined Time = (A * B) / (A + B) days",
                        "code_snippets": [
                            {
                                "language": "text",
                                "code": "Problem: A can do work in 12 days, B in 18 days.\nLCM(12, 18) = 36 units\nA's rate = 3 units/day\nB's rate = 2 units/day\nCombined rate = 5 units/day\nTime = 36 / 5 = 7.2 days",
                                "output": "Answer: 7.2 days (7 days and 4.8 hours)"
                            }
                        ],
                        "notes": [
                            "Formula shortcut for two people: Time = (X * Y) / (X + Y).",
                            "Pipes & Cisterns: Filling pipe adds (+), Emptying pipe subtracts (-).",
                            "M1 * D1 * H1 / W1 = M2 * D2 * H2 / W2 (Chain rule for men, days, hours, work)."
                        ],
                        "category": "aptitude",
                        "order": 1,
                        "is_completed": False,
                        "practice_topic_id": "q_apt_01"
                    },
                    {
                        "id": "apt_speed_dist",
                        "topic_id": "apt_speed_dist",
                        "title": "Time, Speed, Distance, Trains & Relative Velocity",
                        "intro": "Speed measures distance covered per unit of time: Speed = Distance / Time.",
                        "definition": "Unit Conversion: To convert km/hr to m/s, multiply by (5/18). To convert m/s to km/hr, multiply by (18/5).",
                        "explanation": "Relative Speed: When two bodies move in opposite directions, speeds ADD (u + v). When in the same direction, speeds SUBTRACT (u - v).",
                        "syntax": "Distance = Speed * Time\nAverage Speed (equal distance) = 2 * u * v / (u + v)\nTrain crossing a pole: Time = Length of Train / Speed of Train",
                        "code_snippets": [
                            {
                                "language": "text",
                                "code": "Problem: A 150m train crosses a pole in 9 seconds. Find speed in km/hr.\nSpeed = 150 / 9 m/s = 50/3 m/s\nIn km/hr: (50/3) * (18/5) = 60 km/hr",
                                "output": "Answer: 60 km/hr"
                            }
                        ],
                        "notes": [
                            "Train crossing a platform of length P: Total Distance = Length of Train (L) + Length of Platform (P).",
                            "Boats & Streams: Downstream Speed = Boat Speed (u) + Stream Speed (v). Upstream Speed = u - v.",
                            "Average speed is NOT the arithmetic mean (u+v)/2 unless time taken is equal."
                        ],
                        "category": "aptitude",
                        "order": 2,
                        "is_completed": False,
                        "practice_topic_id": "q_apt_01"
                    },
                    {
                        "id": "apt_profit_loss",
                        "topic_id": "apt_profit_loss",
                        "title": "Profit, Loss, Discount & Percentage Shortcuts",
                        "intro": "Commercial arithmetic questions evaluate margins, marked price, discounts, and compound interest calculations.",
                        "definition": "Cost Price (CP) is the purchase price. Selling Price (SP) is the sale price. Profit = SP - CP. Loss = CP - SP.",
                        "explanation": "Profit% and Loss% are ALWAYS calculated on Cost Price (CP): Profit% = (Profit / CP) * 100.",
                        "syntax": "SP = CP * (100 + Gain%) / 100\nCP = (SP * 100) / (100 + Gain%)\nDiscount = Marked Price (MP) - SP",
                        "code_snippets": [
                            {
                                "language": "text",
                                "code": "Problem: Sold article for $240 at 20% gain. What was CP?\nCP = (240 * 100) / (100 + 20) = 24000 / 120 = $200",
                                "output": "Cost Price: $200"
                            }
                        ],
                        "notes": [
                            "Successive discounts: A% and B% discount = [A + B - (A * B / 100)]% single discount.",
                            "When an article is sold at a gain of x% and another at a loss of x% with equal SP, there is ALWAYS a loss: Loss% = (x / 10)^2.",
                            "Dishonest dealer claiming CP: Gain% = [Error / (True Value - Error)] * 100."
                        ],
                        "category": "aptitude",
                        "order": 3,
                        "is_completed": False,
                        "practice_topic_id": "q_apt_02"
                    }
                ]
            }
        ]

        for mod in modules_data:
            existing_m = db.query(LearningModuleModel).filter(LearningModuleModel.id == mod["id"]).first()
            if not existing_m:
                total_less = len(mod.get("lessons", []))
                completed_less = sum(1 for l in mod.get("lessons", []) if l.get("is_completed"))
                pct = (completed_less / total_less * 100.0) if total_less > 0 else 0.0
                new_m = LearningModuleModel(
                    id=mod["id"],
                    title=mod["title"],
                    category=mod["category"],
                    description=mod["description"],
                    icon=mod["icon"],
                    total_lessons=total_less,
                    completed_lessons=completed_less,
                    progress_percentage=pct,
                    topics=mod.get("topics", [])
                )
                db.add(new_m)
                logger.info(f"Added module: {mod['title']}")
            else:
                existing_m.title = mod["title"]
                existing_m.description = mod["description"]
                existing_m.topics = mod.get("topics", [])
                existing_m.total_lessons = len(mod.get("lessons", []))
                logger.info(f"Updated module: {mod['title']}")

            # Seed lessons
            for les in mod.get("lessons", []):
                existing_l = db.query(LessonModel).filter(LessonModel.id == les["id"]).first()
                if not existing_l:
                    new_l = LessonModel(
                        id=les["id"],
                        module_id=mod["id"],
                        topic_id=les["topic_id"],
                        title=les["title"],
                        intro=les["intro"],
                        definition=les["definition"],
                        explanation=les["explanation"],
                        syntax=les.get("syntax", ""),
                        code_snippets=les.get("code_snippets", []),
                        notes=les.get("notes", []),
                        category=les["category"],
                        order=les["order"],
                        is_completed=les["is_completed"],
                        practice_topic_id=les.get("practice_topic_id")
                    )
                    db.add(new_l)
                    logger.info(f"  Added lesson: {les['title']}")
                else:
                    existing_l.title = les["title"]
                    existing_l.intro = les["intro"]
                    existing_l.definition = les["definition"]
                    existing_l.explanation = les["explanation"]
                    existing_l.syntax = les.get("syntax", "")
                    existing_l.code_snippets = les.get("code_snippets", [])
                    existing_l.notes = les.get("notes", [])
                    existing_l.category = les["category"]
                    existing_l.order = les["order"]
                    logger.info(f"  Updated lesson: {les['title']}")

        db.commit()
        logger.info("Successfully seeded all learning modules and lessons in MySQL!")
    except Exception as e:
        logger.error(f"Error seeding learning data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_learning_data()
