import re
from app.core.database import SessionLocal, init_db_engine
from app.models.sql_models import CodingProblemModel

CATEGORIES = [
    "Basic Programming",
    "Python",
    "Java",
    "C",
    "C++",
    "JavaScript",
    "SQL",
    "Data Structures",
    "Algorithms",
    "Problem Solving"
]

EXAMPLE_PROBLEMS = [
    {
        "id": "cp_example_01",
        "title": "Hello World",
        "slug": "hello-world",
        "difficulty": "easy",
        "topic": "Basic Syntax",
        "category": "Basic Programming",
        "description": "Write a program that prints 'Hello, World!' to the standard output. This is the classic starting problem for learning any programming language.",
        "input_format": "No input is required for this problem.",
        "output_format": "Print 'Hello, World!' exactly as shown.",
        "constraints": ["No input values.", "Output must match casing and punctuation exactly."],
        "examples": [
            {
                "input": "",
                "output": "Hello, World!",
                "explanation": "The program should simply print the greeting."
            }
        ],
        "sample_test_cases": [
            {"input": "", "expected_output": "Hello, World!", "is_hidden": False, "explanation": "Basic greeting test"}
        ],
        "hidden_test_cases": [
            {"input": "", "expected_output": "Hello, World!", "is_hidden": True, "explanation": "Validation test"}
        ],
        "starter_codes": [
            {"language": "python", "code": "# Print 'Hello, World!'\nprint(\"Hello, World!\")\n"},
            {"language": "javascript", "code": "// Print 'Hello, World!'\nconsole.log(\"Hello, World!\");\n"},
            {"language": "java", "code": "public class Solution {\n    public static void main(String[] args) {\n        System.out.println(\"Hello, World!\");\n    }\n}\n"},
            {"language": "c", "code": "#include <stdio.h>\n\nint main() {\n    printf(\"Hello, World!\\n\");\n    return 0;\n}\n"},
            {"language": "cpp", "code": "#include <iostream>\n\nint main() {\n    std::cout << \"Hello, World!\" << std::endl;\n    return 0;\n}\n"}
        ]
    },
    {
        "id": "cp_example_02",
        "title": "Sum of Two Numbers",
        "slug": "sum-of-two-numbers",
        "difficulty": "easy",
        "topic": "Math & Numbers",
        "category": "Basic Programming",
        "description": "Given two integers A and B from standard input, calculate and print their sum.",
        "input_format": "A single line containing two space-separated integers A and B.",
        "output_format": "Print the sum of A and B.",
        "constraints": ["-10^9 <= A, B <= 10^9"],
        "examples": [
            {
                "input": "3 5",
                "output": "8",
                "explanation": "3 + 5 = 8"
            }
        ],
        "sample_test_cases": [
            {"input": "3 5", "expected_output": "8", "is_hidden": False, "explanation": "Sample addition"},
            {"input": "-2 7", "expected_output": "5", "is_hidden": False, "explanation": "Negative number"}
        ],
        "hidden_test_cases": [
            {"input": "100 250", "expected_output": "350", "is_hidden": True},
            {"input": "0 0", "expected_output": "0", "is_hidden": True},
            {"input": "-50 -50", "expected_output": "-100", "is_hidden": True}
        ],
        "starter_codes": [
            {"language": "python", "code": "# Read space-separated integers A and B\nline = input().split()\nif line:\n    a, b = int(line[0]), int(line[1])\n    print(a + b)\n"},
            {"language": "javascript", "code": "const fs = require('fs');\nconst input = fs.readFileSync(0, 'utf-8').trim().split(/\\s+/);\nif (input.length >= 2) {\n    const a = parseInt(input[0], 10);\n    const b = parseInt(input[1], 10);\n    console.log(a + b);\n}\n"},
            {"language": "java", "code": "import java.util.Scanner;\n\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        if (sc.hasNextInt()) {\n            int a = sc.nextInt();\n            int b = sc.nextInt();\n            System.out.println(a + b);\n        }\n    }\n}\n"}
        ]
    },
    {
        "id": "cp_example_03",
        "title": "Palindrome Check",
        "slug": "palindrome-check",
        "difficulty": "easy",
        "topic": "Strings",
        "category": "Problem Solving",
        "description": "Given a string S, determine whether it is a palindrome. A string is a palindrome if it reads the same backward as forward (case-insensitive). Print 'YES' if it is a palindrome, otherwise 'NO'.",
        "input_format": "A single string S.",
        "output_format": "Print 'YES' or 'NO'.",
        "constraints": ["1 <= length of S <= 10^5", "String contains alphanumeric characters."],
        "examples": [
            {"input": "racecar", "output": "YES", "explanation": "'racecar' reversed is 'racecar'"},
            {"input": "hello", "output": "NO", "explanation": "'hello' reversed is 'olleh'"}
        ],
        "sample_test_cases": [
            {"input": "racecar", "expected_output": "YES", "is_hidden": False},
            {"input": "hello", "expected_output": "NO", "is_hidden": False}
        ],
        "hidden_test_cases": [
            {"input": "Madam", "expected_output": "YES", "is_hidden": True},
            {"input": "12321", "expected_output": "YES", "is_hidden": True},
            {"input": "coding", "expected_output": "NO", "is_hidden": True}
        ],
        "starter_codes": [
            {"language": "python", "code": "s = input().strip().lower()\nif s == s[::-1]:\n    print('YES')\nelse:\n    print('NO')\n"},
            {"language": "javascript", "code": "const fs = require('fs');\nconst s = fs.readFileSync(0, 'utf-8').trim().toLowerCase();\nconst rev = s.split('').reverse().join('');\nconsole.log(s === rev ? 'YES' : 'NO');\n"}
        ]
    },
    {
        "id": "cp_example_04",
        "title": "Fibonacci Series",
        "slug": "fibonacci-series",
        "difficulty": "medium",
        "topic": "Algorithms",
        "category": "Algorithms",
        "description": "Given an integer N, print the first N numbers of the Fibonacci sequence separated by spaces. The sequence starts with 0 and 1: F(0)=0, F(1)=1, F(n) = F(n-1) + F(n-2).",
        "input_format": "A single integer N (N >= 1).",
        "output_format": "Print first N numbers separated by spaces.",
        "constraints": ["1 <= N <= 30"],
        "examples": [
            {"input": "5", "output": "0 1 1 2 3", "explanation": "First 5 Fibonacci numbers."}
        ],
        "sample_test_cases": [
            {"input": "5", "expected_output": "0 1 1 2 3", "is_hidden": False},
            {"input": "1", "expected_output": "0", "is_hidden": False}
        ],
        "hidden_test_cases": [
            {"input": "7", "expected_output": "0 1 1 2 3 5 8", "is_hidden": True},
            {"input": "2", "expected_output": "0 1", "is_hidden": True}
        ],
        "starter_codes": [
            {"language": "python", "code": "n = int(input().strip())\nif n == 1:\n    print(0)\nelse:\n    fib = [0, 1]\n    for i in range(2, n):\n        fib.append(fib[-1] + fib[-2])\n    print(' '.join(map(str, fib[:n])))\n"}
        ]
    },
    {
        "id": "cp_example_05",
        "title": "Find Maximum in an Array",
        "slug": "find-maximum-in-an-array",
        "difficulty": "easy",
        "topic": "Lists & Arrays",
        "category": "Data Structures",
        "description": "Given an integer N followed by N space-separated integers, find and print the maximum value in the array.",
        "input_format": "Line 1: An integer N.\nLine 2: N space-separated integers.",
        "output_format": "Print the maximum integer.",
        "constraints": ["1 <= N <= 10^5", "-10^9 <= array[i] <= 10^9"],
        "examples": [
            {"input": "5\n1 4 2 9 5", "output": "9", "explanation": "The maximum number is 9."}
        ],
        "sample_test_cases": [
            {"input": "5\n1 4 2 9 5", "expected_output": "9", "is_hidden": False},
            {"input": "3\n-10 -3 -20", "expected_output": "-3", "is_hidden": False}
        ],
        "hidden_test_cases": [
            {"input": "4\n100 500 200 50", "expected_output": "500", "is_hidden": True},
            {"input": "1\n42", "expected_output": "42", "is_hidden": True}
        ],
        "starter_codes": [
            {"language": "python", "code": "n = int(input().strip())\nnums = list(map(int, input().split()))\nprint(max(nums))\n"}
        ]
    },
    {
        "id": "cp_example_06",
        "title": "Binary Search",
        "slug": "binary-search",
        "difficulty": "medium",
        "topic": "Lists & Search",
        "category": "Algorithms",
        "description": "Given a sorted array of N distinct integers and a target integer K, perform binary search to find the 0-based index of K in the array. If K is not present, print -1.",
        "input_format": "Line 1: Two space-separated integers N and K.\nLine 2: N sorted space-separated integers.",
        "output_format": "Print the 0-based index of K, or -1 if not found.",
        "constraints": ["1 <= N <= 10^5", "-10^9 <= K, array[i] <= 10^9"],
        "examples": [
            {"input": "5 7\n1 3 5 7 9", "output": "3", "explanation": "7 is found at index 3."}
        ],
        "sample_test_cases": [
            {"input": "5 7\n1 3 5 7 9", "expected_output": "3", "is_hidden": False},
            {"input": "5 4\n1 3 5 7 9", "expected_output": "-1", "is_hidden": False}
        ],
        "hidden_test_cases": [
            {"input": "6 1\n1 2 4 6 8 10", "expected_output": "0", "is_hidden": True},
            {"input": "6 10\n1 2 4 6 8 10", "expected_output": "5", "is_hidden": True},
            {"input": "4 20\n2 5 8 12", "expected_output": "-1", "is_hidden": True}
        ],
        "starter_codes": [
            {"language": "python", "code": "n, k = map(int, input().split())\narr = list(map(int, input().split()))\nleft, right = 0, n - 1\nans = -1\nwhile left <= right:\n    mid = (left + right) // 2\n    if arr[mid] == k:\n        ans = mid\n        break\n    elif arr[mid] < k:\n        left = mid + 1\n    else:\n        right = mid - 1\nprint(ans)\n"}
        ]
    }
]

def map_problem_category(problem: CodingProblemModel) -> str:
    """Intelligently assigns a problem to one of the 10 prompt categories."""
    t = (problem.topic or "").lower()
    title = (problem.title or "").lower()

    if "sql" in t or "sql" in title or "database" in t:
        return "SQL"
    elif "search" in t or "sort" in t or "pointer" in t or "two pointer" in t:
        return "Algorithms"
    elif "array" in t or "list" in t or "hash" in t or "dict" in t or "set" in t:
        return "Data Structures"
    elif "pattern" in t or "ciphers" in t or "encoding" in t or "bit" in t:
        return "Problem Solving"
    elif "syntax" in t or "formatting" in t or "loops" in t:
        return "Basic Programming"
    elif "string" in t:
        return "Problem Solving"
    elif "math" in t or "number" in t:
        return "Basic Programming"
    return "Problem Solving"

def seed_categories_and_problems():
    init_db_engine()
    db = SessionLocal()
    try:
        # 1. Add any missing example problems
        for ex in EXAMPLE_PROBLEMS:
            existing = db.query(CodingProblemModel).filter(
                (CodingProblemModel.id == ex["id"]) | (CodingProblemModel.slug == ex["slug"])
            ).first()
            if not existing:
                new_p = CodingProblemModel(
                    id=ex["id"],
                    title=ex["title"],
                    slug=ex["slug"],
                    difficulty=ex["difficulty"],
                    topic=ex["topic"],
                    category=ex["category"],
                    description=ex["description"],
                    constraints=ex["constraints"],
                    examples=ex["examples"],
                    input_format=ex["input_format"],
                    output_format=ex["output_format"],
                    hints=["Think about the edge cases.", "Check standard library functions."],
                    time_limit_seconds=2.0,
                    memory_limit_mb=128,
                    starter_codes=ex["starter_codes"],
                    tags=[ex["topic"], ex["category"]],
                    sample_test_cases=ex["sample_test_cases"],
                    hidden_test_cases=ex["hidden_test_cases"],
                    supported_languages=["python", "javascript", "java", "c", "cpp"],
                    is_published=True,
                    is_solved=False
                )
                db.add(new_p)
                print(f"Added example problem: {ex['title']}")

        db.commit()

        # 2. Update categories for all existing problems so all 10 categories have problems
        all_probs = db.query(CodingProblemModel).all()
        # Round-robin distribution for language-specific categories
        lang_categories = ["Python", "Java", "C", "C++", "JavaScript", "SQL"]
        for idx, p in enumerate(all_probs):
            if not p.supported_languages:
                p.supported_languages = ["python", "javascript", "java", "c", "cpp"]
            p.is_published = True

            # If category is default or missing, assign intelligently
            if not p.category or p.category == "Basic Programming":
                mapped = map_problem_category(p)
                # Ensure distribution across Python, Java, C, C++, JavaScript, SQL
                if idx % 7 == 1:
                    p.category = "Python"
                elif idx % 7 == 2:
                    p.category = "Java"
                elif idx % 7 == 3:
                    p.category = "C"
                elif idx % 7 == 4:
                    p.category = "C++"
                elif idx % 7 == 5:
                    p.category = "JavaScript"
                elif idx % 7 == 6:
                    p.category = "SQL"
                else:
                    p.category = mapped

        db.commit()

        # Print category counts
        print("\n--- Category Breakdown ---")
        for cat in CATEGORIES:
            cnt = db.query(CodingProblemModel).filter(CodingProblemModel.category == cat).count()
            print(f"{cat}: {cnt} problems")

        total = db.query(CodingProblemModel).count()
        print(f"\nTotal Coding Problems in MySQL: {total}")

    except Exception as e:
        print("Error during seeding:", e)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_categories_and_problems()
