import os
import re
import sys
import json

demo_dir = r"D:\nanga project panna poram\project\demo doc"
files = [
    ("python_simplequestions.md", 1, 20),
    ("python_practice_problems_part2.md", 21, 40),
    ("python_practice_problems_part3.md", 41, 60),
]

def clean_section(text):
    return text.strip()

def parse_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Split on ## Problem <digits>:
    splits = re.split(r'\n(?=## Problem \d+:)', content)
    problems = []

    for chunk in splits:
        chunk = chunk.strip()
        if not chunk.startswith("## Problem"):
            continue

        # Cut off any trailing footer guides like "## Tips for Solving..."
        footer_match = re.search(r'\n---\s*\n##\s+(?:Tips|What\'s|Next Steps|Recommended|Difficulty Breakdown)', chunk)
        if footer_match:
            chunk = chunk[:footer_match.start()]
        
        # Remove trailing ---
        chunk = re.sub(r'\n---\s*$', '', chunk).strip()

        # Extract Problem Number and Title
        m_head = re.search(r'^## Problem (\d+):\s*(.+)$', chunk, re.M)
        if not m_head:
            continue
        prob_num = int(m_head.group(1))
        title = m_head.group(2).strip()

        # Extract Difficulty
        m_diff = re.search(r'\*\*Difficulty:\*\*\s*([^\n\r]+)', chunk)
        difficulty = m_diff.group(1).strip().lower() if m_diff else "easy"

        # Extract Input Format
        m_in = re.search(r'\*\*Input Format:\*\*\s*(.*?)(?=\n\*\*[A-Za-z ]+:\*\*|\Z)', chunk, re.S)
        input_format = clean_section(m_in.group(1)) if m_in else ""

        # Extract Output Format
        m_out = re.search(r'\*\*Output Format:\*\*\s*(.*?)(?=\n\*\*[A-Za-z ]+:\*\*|\Z)', chunk, re.S)
        output_format = clean_section(m_out.group(1)) if m_out else ""

        # Extract Constraints
        m_const = re.search(r'\*\*Constraints:\*\*\s*(.*?)(?=\n\*\*[A-Za-z ]+:\*\*|\Z)', chunk, re.S)
        constraints_raw = clean_section(m_const.group(1)) if m_const else ""
        constraints = [c.strip("- *").strip() for c in constraints_raw.splitlines() if c.strip("- *").strip()]

        # Extract Notes / Rules / Examples if any
        m_rules = re.search(r'\*\*(?:Rules|Note|Example):\*\*\s*(.*?)(?=\n\*\*[A-Za-z ]+:\*\*|\Z)', chunk, re.S)
        extra_note = clean_section(m_rules.group(1)) if m_rules else ""

        # Extract Sample Input
        m_sin = re.search(r'\*\*Sample Input:\*\*[\s\r\n]*```[a-zA-Z]*\n?(.*?)```', chunk, re.S)
        sample_input = m_sin.group(1).rstrip("\r\n") if m_sin else ""

        # Extract Sample Output
        m_sout = re.search(r'\*\*Sample Output:\*\*[\s\r\n]*```[a-zA-Z]*\n?(.*?)```', chunk, re.S)
        sample_output = m_sout.group(1).rstrip("\r\n") if m_sout else ""

        # Extract Description (between **Difficulty:** and the first major section)
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

if __name__ == "__main__":
    all_probs = []
    for fname, start_n, end_n in files:
        fpath = os.path.join(demo_dir, fname)
        parsed = parse_file(fpath)
        print(f"{fname}: parsed {len(parsed)} problems (Expected {end_n - start_n + 1})")
        all_probs.extend(parsed)

    print(f"Total problems collected: {len(all_probs)}")
    
    # Check completeness
    for p in all_probs:
        if not p["title"] or not p["description"] or not p["sample_input"] or not p["sample_output"]:
            print(f"Incomplete Problem #{p['number']}: {p['title']}")
            print(f"  desc: {bool(p['description'])}, in: {repr(p['sample_input'])}, out: {repr(p['sample_output'])}")
