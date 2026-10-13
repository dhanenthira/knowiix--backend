import os
import re
import sys
import logging
from datetime import datetime

# Add parent directory to path so app models can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, init_db_engine
from app.models.sql_models import CodingProblemModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("import_demo")

DEMO_DIR = r"D:\nanga project panna poram\project\demo doc"
FILES = [
    ("python_simplequestions.md", 1, 20),
    ("python_practice_problems_part2.md", 21, 40),
    ("python_practice_problems_part3.md", 41, 60),
]

TOPIC_MAP = {
    # Part 1 (1-20)
    1: "Math & Numbers",
    2: "Strings",
    3: "Strings",
    4: "Basic Syntax",
    5: "Math & Numbers",
    6: "Lists & Arrays",
    7: "Basic Syntax",
    8: "Lists & Arrays",
    9: "Strings",
    10: "Math & Numbers",
    11: "Lists & Arrays",
    12: "Math & Numbers",
    13: "Lists & Arrays",
    14: "Math & Numbers",
    15: "Strings",
    16: "Lists & Arrays",
    17: "Math & Numbers",
    18: "Lists & Arrays",
    19: "Dictionary & Hash Table",
    20: "Lists & Comprehensions",

    # Part 2 (21-40)
    21: "Number Theory",
    22: "Number Theory",
    23: "Number Theory",
    24: "Math & Numbers",
    25: "Strings",
    26: "Strings",
    27: "Pattern Printing",
    28: "Strings",
    29: "Strings",
    30: "Lists & Arrays",
    31: "Dictionary & Hash Table",
    32: "Strings",
    33: "Pattern Printing",
    34: "Pattern Printing",
    35: "Strings",
    36: "Math & Numbers",
    37: "Strings",
    38: "Formatting & Loops",
    39: "Number Theory",
    40: "Dictionary & Frequency",

    # Part 3 (41-60)
    41: "Bit Manipulation & Bases",
    42: "Logic & Math",
    43: "Number Theory",
    44: "Strings",
    45: "Lists & Slicing",
    46: "Bit Manipulation & Bases",
    47: "Lists & Sets",
    48: "Number Theory",
    49: "Strings",
    50: "Two Pointers & Lists",
    51: "Bit Manipulation & Bases",
    52: "Lists & Arrays",
    53: "Strings",
    54: "Lists & Sorting",
    55: "Lists & Search",
    56: "Lists & Arrays",
    57: "Statistics & Math",
    58: "Lists & Two Pointers",
    59: "Sets & Counting",
    60: "Ciphers & Encoding",
}

def clean_section(text):
    return text.strip()

def make_slug(title, num):
    s = re.sub(r'[^a-zA-Z0-9\s-]', '', title).strip().lower()
    s = re.sub(r'[\s_]+', '-', s)
    return f"{s}-{num}"

def parse_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    splits = re.split(r'\n(?=## Problem \d+:)', content)
    problems = []

    for chunk in splits:
        chunk = chunk.strip()
        if not chunk.startswith("## Problem"):
            continue

        footer_match = re.search(r'\n---\s*\n##\s+(?:Tips|What\'s|Next Steps|Recommended|Difficulty Breakdown)', chunk)
        if footer_match:
            chunk = chunk[:footer_match.start()]
        
        chunk = re.sub(r'\n---\s*$', '', chunk).strip()

        m_head = re.search(r'^## Problem (\d+):\s*(.+)$', chunk, re.M)
        if not m_head:
            continue
        prob_num = int(m_head.group(1))
        title = m_head.group(2).strip()

        m_diff = re.search(r'\*\*Difficulty:\*\*\s*([^\n\r]+)', chunk)
        difficulty = m_diff.group(1).strip().lower() if m_diff else "easy"

        m_in = re.search(r'\*\*Input Format:\*\*\s*(.*?)(?=\n\*\*[A-Za-z ]+:\*\*|\Z)', chunk, re.S)
        input_format = clean_section(m_in.group(1)) if m_in else ""

        m_out = re.search(r'\*\*Output Format:\*\*\s*(.*?)(?=\n\*\*[A-Za-z ]+:\*\*|\Z)', chunk, re.S)
        output_format = clean_section(m_out.group(1)) if m_out else ""

        m_const = re.search(r'\*\*Constraints:\*\*\s*(.*?)(?=\n\*\*[A-Za-z ]+:\*\*|\Z)', chunk, re.S)
        constraints_raw = clean_section(m_const.group(1)) if m_const else ""
        constraints = [c.strip("- *").strip() for c in constraints_raw.splitlines() if c.strip("- *").strip()]

        m_rules = re.search(r'\*\*(?:Rules|Note|Example):\*\*\s*(.*?)(?=\n\*\*[A-Za-z ]+:\*\*|\Z)', chunk, re.S)
        extra_note = clean_section(m_rules.group(1)) if m_rules else ""

        m_sin = re.search(r'\*\*Sample Input:\*\*[\s\r\n]*```[a-zA-Z]*\n?(.*?)```', chunk, re.S)
        sample_input = m_sin.group(1).rstrip("\r\n") if m_sin else ""

        m_sout = re.search(r'\*\*Sample Output:\*\*[\s\r\n]*```[a-zA-Z]*\n?(.*?)```', chunk, re.S)
        sample_output = m_sout.group(1).rstrip("\r\n") if m_sout else ""

        desc = ""
        diff_end = m_diff.end() if m_diff else m_head.end()
        after_diff = chunk[diff_end:]
        first_section = re.search(r'\n\*\*(?:Input Format|Example|Rules|Constraints|Note):', after_diff)
        if first_section:
            desc = after_diff[:first_section.start()].strip()
        else:
            desc = after_diff.strip()

        if extra_note and extra_note not in desc:
            desc = f"{desc}\n\nNote: {extra_note}".strip()

        problems.append({
            "number": prob_num,
            "title": title,
            "difficulty": difficulty,
            "description": desc,
            "input_format": input_format,
            "output_format": output_format,
            "constraints": constraints,
            "sample_input": sample_input,
            "sample_output": sample_output,
        })

    return problems

def import_all_problems():
    logger.info("Initializing database connection...")
    init_db_engine()
    db = SessionLocal()
    if not db:
        logger.error("Failed to connect to database session.")
        return False

    all_parsed = []
    for fname, _, _ in FILES:
        fpath = os.path.join(DEMO_DIR, fname)
        if not os.path.exists(fpath):
            logger.error(f"File not found: {fpath}")
            continue
        parsed = parse_file(fpath)
        logger.info(f"Loaded {len(parsed)} problems from {fname}")
        all_parsed.extend(parsed)

    logger.info(f"Total problems to import: {len(all_parsed)}")

    inserted_count = 0
    updated_count = 0

    try:
        for p in all_parsed:
            prob_num = p["number"]
            prob_id = f"cp_py_{prob_num:02d}"
            slug = make_slug(p["title"], prob_num)
            topic = TOPIC_MAP.get(prob_num, "Python Fundamentals")

            examples = [
                {
                    "input": p["sample_input"],
                    "output": p["sample_output"],
                    "explanation": f"Input: {p['sample_input']} -> Expected: {p['sample_output']}"
                }
            ]

            sample_test_cases = [
                {
                    "input": p["sample_input"],
                    "expected_output": p["sample_output"],
                    "is_hidden": False,
                    "explanation": "Sample test case"
                }
            ]

            hidden_test_cases = [
                {
                    "input": p["sample_input"],
                    "expected_output": p["sample_output"],
                    "is_hidden": True,
                    "explanation": "Hidden test case"
                }
            ]

            py_starter = (
                f"# Problem {prob_num}: {p['title']}\n"
                "# Write your solution below:\n\n"
                "import sys\n\n"
                "def solve():\n"
                "    lines = sys.stdin.read().splitlines()\n"
                "    if not lines:\n"
                "        return\n"
                "    # TODO: Implement your logic here\n\n"
                "if __name__ == '__main__':\n"
                "    solve()\n"
            )
            js_starter = (
                f"// Problem {prob_num}: {p['title']}\n"
                "const fs = require('fs');\n"
                "const input = fs.readFileSync('/dev/stdin', 'utf-8').trim();\n\n"
                "function solve() {\n"
                "    // TODO: Implement logic\n"
                "}\n"
                "solve();\n"
            )
            cpp_starter = (
                f"// Problem {prob_num}: {p['title']}\n"
                "#include <iostream>\n"
                "#include <string>\n"
                "#include <vector>\n"
                "using namespace std;\n\n"
                "int main() {\n"
                "    // TODO: Implement logic\n"
                "    return 0;\n"
                "}\n"
            )

            starter_codes = [
                {"language": "python", "code": py_starter},
                {"language": "javascript", "code": js_starter},
                {"language": "cpp", "code": cpp_starter}
            ]

            hints = [
                f"Carefully observe the input format: {p['input_format'] or 'standard input'}",
                f"Make sure your output matches the exact format: {p['output_format'] or 'standard output'}"
            ]

            tags = ["Python", topic]
            if p["difficulty"] == "easy":
                tags.append("Beginner Friendly")

            existing = db.query(CodingProblemModel).filter(
                (CodingProblemModel.id == prob_id) | (CodingProblemModel.slug == slug)
            ).first()

            if existing:
                existing.title = p["title"]
                existing.slug = slug
                existing.difficulty = p["difficulty"]
                existing.topic = topic
                existing.description = p["description"]
                existing.constraints = p["constraints"]
                existing.examples = examples
                existing.input_format = p["input_format"]
                existing.output_format = p["output_format"]
                existing.hints = hints
                existing.starter_codes = starter_codes
                existing.tags = tags
                existing.sample_test_cases = sample_test_cases
                existing.hidden_test_cases = hidden_test_cases
                updated_count += 1
            else:
                new_problem = CodingProblemModel(
                    id=prob_id,
                    title=p["title"],
                    slug=slug,
                    difficulty=p["difficulty"],
                    topic=topic,
                    description=p["description"],
                    constraints=p["constraints"],
                    examples=examples,
                    input_format=p["input_format"],
                    output_format=p["output_format"],
                    hints=hints,
                    time_limit_seconds=2.0,
                    memory_limit_mb=128,
                    starter_codes=starter_codes,
                    tags=tags,
                    sample_test_cases=sample_test_cases,
                    hidden_test_cases=hidden_test_cases,
                    is_solved=False,
                    total_submissions=0,
                    acceptance_rate=85.0,
                    created_at=datetime.utcnow()
                )
                db.add(new_problem)
                inserted_count += 1

        db.commit()
        logger.info(f"Database import complete! Inserted: {inserted_count}, Updated: {updated_count}, Total in batch: {len(all_parsed)}")
        
        total_in_db = db.query(CodingProblemModel).count()
        logger.info(f"Total coding problems now in MySQL: {total_in_db}")
        return True

    except Exception as e:
        logger.error(f"Error during import: {e}", exc_info=True)
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = import_all_problems()
    if success:
        print("\nALL 60 DEMO PROBLEMS SUCCESSFULLY IMPORTED INTO DATABASE!")
    else:
        print("\nFailed to import demo problems.")
        sys.exit(1)
