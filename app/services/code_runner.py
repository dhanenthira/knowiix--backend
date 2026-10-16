import os
import sys
import time
import shutil
import tempfile
import subprocess
import requests
from typing import List, Dict, Any, Optional
from app.schemas.coding import CodeExecutionResult, TestCaseEvaluation

# Max limits for security
MAX_CODE_LENGTH = 50000        # 50 KB max source code
MAX_INPUT_LENGTH = 100000      # 100 KB max input
MAX_OUTPUT_LENGTH = 65536      # 64 KB output buffer truncation
DEFAULT_TIMEOUT_SECONDS = 2.0  # 2.0s execution time limit per testcase

def normalize_output(text: Optional[str]) -> str:
    """Standardizes string output for whitespace and newline differences."""
    if not text:
        return ""
    # Strip line-by-line and remove trailing empty lines
    lines = [line.rstrip() for line in text.strip().splitlines()]
    return "\n".join(lines).strip()

class CodeRunnerService:
    def __init__(self):
        self.judge0_url = os.getenv("JUDGE0_API_URL", "").rstrip("/")
        self.judge0_key = os.getenv("JUDGE0_API_KEY", "")
        self.execution_provider = os.getenv("EXECUTION_PROVIDER", "sandbox").lower()

    def _get_clean_env(self, temp_dir: str) -> Dict[str, str]:
        """
        Creates an isolated, stripped environment dictionary.
        Strictly excludes all application secrets, database credentials, and API keys.
        """
        clean_env = {
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", "C:\\Windows"),
            "WINDIR": os.environ.get("WINDIR", "C:\\Windows"),
            "PATH": os.environ.get("PATH", ""),
            "TEMP": temp_dir,
            "TMP": temp_dir,
            "PYTHONUTF8": "1",
            "PYTHONUNBUFFERED": "1",
        }
        return clean_env

    def _execute_in_sandbox(
        self,
        language: str,
        code: str,
        stdin_data: str,
        timeout_seconds: float,
        temp_dir: str
    ) -> Dict[str, Any]:
        """
        Executes code inside an isolated sandbox subprocess.
        Returns dict with keys: stdout, stderr, returncode, timed_out, exec_time_ms, compilation_error
        """
        lang = language.lower().strip()
        env = self._get_clean_env(temp_dir)
        start_t = time.perf_counter()

        # 1. PYTHON
        if lang in ["python", "py", "python3"]:
            script_path = os.path.join(temp_dir, "solution.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code)

            # -I isolates Python: ignores PYTHONPATH, user site packages, etc.
            cmd = [sys.executable, "-I", "-B", script_path]
            try:
                proc = subprocess.run(
                    cmd,
                    input=stdin_data,
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                    cwd=temp_dir,
                    env=env
                )
                exec_time_ms = (time.perf_counter() - start_t) * 1000
                return {
                    "stdout": proc.stdout[:MAX_OUTPUT_LENGTH],
                    "stderr": proc.stderr[:MAX_OUTPUT_LENGTH],
                    "returncode": proc.returncode,
                    "timed_out": False,
                    "exec_time_ms": exec_time_ms,
                    "compilation_error": None,
                }
            except subprocess.TimeoutExpired:
                exec_time_ms = (time.perf_counter() - start_t) * 1000
                return {
                    "stdout": "",
                    "stderr": f"Execution timed out after {timeout_seconds} seconds.",
                    "returncode": -1,
                    "timed_out": True,
                    "exec_time_ms": exec_time_ms,
                    "compilation_error": None,
                }

        # 2. JAVASCRIPT / NODE.JS
        elif lang in ["javascript", "js", "node", "nodejs"]:
            node_exe = shutil.which("node")
            if not node_exe:
                return {
                    "stdout": "",
                    "stderr": "Node.js runtime is not installed or configured on the execution host.",
                    "returncode": 1,
                    "timed_out": False,
                    "exec_time_ms": 0.0,
                    "compilation_error": "Node.js runtime not found.",
                }

            script_path = os.path.join(temp_dir, "solution.js")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code)

            cmd = [node_exe, script_path]
            try:
                proc = subprocess.run(
                    cmd,
                    input=stdin_data,
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                    cwd=temp_dir,
                    env=env
                )
                exec_time_ms = (time.perf_counter() - start_t) * 1000
                return {
                    "stdout": proc.stdout[:MAX_OUTPUT_LENGTH],
                    "stderr": proc.stderr[:MAX_OUTPUT_LENGTH],
                    "returncode": proc.returncode,
                    "timed_out": False,
                    "exec_time_ms": exec_time_ms,
                    "compilation_error": None,
                }
            except subprocess.TimeoutExpired:
                exec_time_ms = (time.perf_counter() - start_t) * 1000
                return {
                    "stdout": "",
                    "stderr": f"Execution timed out after {timeout_seconds} seconds.",
                    "returncode": -1,
                    "timed_out": True,
                    "exec_time_ms": exec_time_ms,
                    "compilation_error": None,
                }

        # 3. JAVA
        elif lang in ["java"]:
            javac_exe = shutil.which("javac")
            java_exe = shutil.which("java")
            if not javac_exe or not java_exe:
                return {
                    "stdout": "",
                    "stderr": "Java JDK (javac/java) is not installed or configured on the execution host.",
                    "returncode": 1,
                    "timed_out": False,
                    "exec_time_ms": 0.0,
                    "compilation_error": "Java JDK compiler not found.",
                }

            source_path = os.path.join(temp_dir, "Solution.java")
            with open(source_path, "w", encoding="utf-8") as f:
                f.write(code)

            # Compile step
            compile_proc = subprocess.run(
                [javac_exe, "-encoding", "UTF-8", "Solution.java"],
                capture_output=True,
                text=True,
                timeout=10.0,
                cwd=temp_dir,
                env=env
            )
            if compile_proc.returncode != 0:
                return {
                    "stdout": "",
                    "stderr": compile_proc.stderr[:MAX_OUTPUT_LENGTH],
                    "returncode": compile_proc.returncode,
                    "timed_out": False,
                    "exec_time_ms": 0.0,
                    "compilation_error": compile_proc.stderr[:MAX_OUTPUT_LENGTH],
                }

            # Run step
            cmd = [java_exe, "-Xmx128m", "-Dfile.encoding=UTF-8", "Solution"]
            try:
                proc = subprocess.run(
                    cmd,
                    input=stdin_data,
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                    cwd=temp_dir,
                    env=env
                )
                exec_time_ms = (time.perf_counter() - start_t) * 1000
                return {
                    "stdout": proc.stdout[:MAX_OUTPUT_LENGTH],
                    "stderr": proc.stderr[:MAX_OUTPUT_LENGTH],
                    "returncode": proc.returncode,
                    "timed_out": False,
                    "exec_time_ms": exec_time_ms,
                    "compilation_error": None,
                }
            except subprocess.TimeoutExpired:
                exec_time_ms = (time.perf_counter() - start_t) * 1000
                return {
                    "stdout": "",
                    "stderr": f"Execution timed out after {timeout_seconds} seconds.",
                    "returncode": -1,
                    "timed_out": True,
                    "exec_time_ms": exec_time_ms,
                    "compilation_error": None,
                }

        # 4. C / C++
        elif lang in ["c", "cpp", "c++"]:
            compiler = shutil.which("gcc") if lang == "c" else (shutil.which("g++") or shutil.which("gcc"))
            if not compiler:
                return {
                    "stdout": "",
                    "stderr": f"C/C++ compiler ({lang}) is not installed or configured on the execution host.",
                    "returncode": 1,
                    "timed_out": False,
                    "exec_time_ms": 0.0,
                    "compilation_error": f"{lang.upper()} compiler not found.",
                }

            ext = ".c" if lang == "c" else ".cpp"
            source_path = os.path.join(temp_dir, f"solution{ext}")
            bin_path = os.path.join(temp_dir, "solution.exe" if os.name == "nt" else "solution")

            with open(source_path, "w", encoding="utf-8") as f:
                f.write(code)

            compile_cmd = [compiler, "-O2", source_path, "-o", bin_path]
            compile_proc = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                timeout=10.0,
                cwd=temp_dir,
                env=env
            )
            if compile_proc.returncode != 0:
                return {
                    "stdout": "",
                    "stderr": compile_proc.stderr[:MAX_OUTPUT_LENGTH],
                    "returncode": compile_proc.returncode,
                    "timed_out": False,
                    "exec_time_ms": 0.0,
                    "compilation_error": compile_proc.stderr[:MAX_OUTPUT_LENGTH],
                }

            try:
                proc = subprocess.run(
                    [bin_path],
                    input=stdin_data,
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                    cwd=temp_dir,
                    env=env
                )
                exec_time_ms = (time.perf_counter() - start_t) * 1000
                return {
                    "stdout": proc.stdout[:MAX_OUTPUT_LENGTH],
                    "stderr": proc.stderr[:MAX_OUTPUT_LENGTH],
                    "returncode": proc.returncode,
                    "timed_out": False,
                    "exec_time_ms": exec_time_ms,
                    "compilation_error": None,
                }
            except subprocess.TimeoutExpired:
                exec_time_ms = (time.perf_counter() - start_t) * 1000
                return {
                    "stdout": "",
                    "stderr": f"Execution timed out after {timeout_seconds} seconds.",
                    "returncode": -1,
                    "timed_out": True,
                    "exec_time_ms": exec_time_ms,
                    "compilation_error": None,
                }

        # 5. Unsupported
        else:
            return {
                "stdout": "",
                "stderr": f"Unsupported programming language: {language}",
                "returncode": 1,
                "timed_out": False,
                "exec_time_ms": 0.0,
                "compilation_error": f"Language '{language}' not supported by execution service.",
            }

    def _execute_judge0(
        self,
        language: str,
        code: str,
        test_cases: List[Dict[str, Any]],
        timeout_seconds: float
    ) -> Optional[CodeExecutionResult]:
        """Executes code via Judge0 API when JUDGE0_API_URL is configured."""
        if not self.judge0_url:
            return None

        # Language ID mapping for Judge0
        lang_map = {
            "python": 71,    # Python (3.8.1)
            "python3": 71,
            "py": 71,
            "javascript": 63, # Node.js (12.14.0)
            "js": 63,
            "java": 62,      # Java (OpenJDK 13.0.1)
            "c": 50,         # C (GCC 9.2.0)
            "cpp": 54,       # C++ (GCC 9.2.0)
            "c++": 54
        }
        lang_id = lang_map.get(language.lower().strip())
        if not lang_id:
            return None

        evaluations: List[TestCaseEvaluation] = []
        passed_count = 0
        total_time_ms = 0.0
        overall_status = "Accepted"
        first_stdout = ""
        first_stderr = ""

        headers = {"Content-Type": "application/json"}
        if self.judge0_key:
            headers["X-Auth-Token"] = self.judge0_key

        for idx, tc in enumerate(test_cases, start=1):
            input_data = tc.get("input", "") or ""
            expected = tc.get("expected_output", "") or ""
            is_hidden = tc.get("is_hidden", False)

            payload = {
                "source_code": code,
                "language_id": lang_id,
                "stdin": input_data,
                "expected_output": expected,
                "cpu_time_limit": min(timeout_seconds, 5.0),
                "memory_limit": 128000
            }

            try:
                resp = requests.post(
                    f"{self.judge0_url}/submissions?wait=true",
                    json=payload,
                    headers=headers,
                    timeout=timeout_seconds + 3.0
                )
                if resp.status_code in [200, 201]:
                    data = resp.json()
                    status_desc = data.get("status", {}).get("description", "Error")
                    actual_out = data.get("stdout", "") or ""
                    err_out = (data.get("compile_output", "") or "") + (data.get("stderr", "") or "")
                    tc_time = float(data.get("time", 0.0) or 0.0) * 1000

                    if not first_stdout:
                        first_stdout = actual_out
                    if not first_stderr:
                        first_stderr = err_out

                    if status_desc == "Accepted":
                        status_str = "Passed"
                        passed_count += 1
                    elif "Time Limit" in status_desc:
                        status_str = "Time Limit Exceeded"
                        if overall_status == "Accepted":
                            overall_status = "Time Limit Exceeded"
                    elif "Compilation" in status_desc:
                        status_str = "Compilation Error"
                        overall_status = "Compilation Error"
                    elif "Runtime" in status_desc:
                        status_str = "Runtime Error"
                        if overall_status in ["Accepted", "Wrong Answer"]:
                            overall_status = "Runtime Error"
                    else:
                        status_str = "Wrong Answer"
                        if overall_status == "Accepted":
                            overall_status = "Wrong Answer"

                    total_time_ms += tc_time
                    evaluations.append(TestCaseEvaluation(
                        test_case_number=idx,
                        is_hidden=is_hidden,
                        status=status_str,
                        input=None if is_hidden else input_data,
                        expected_output=None if is_hidden else expected,
                        actual_output=None if is_hidden else actual_out,
                        error_message=None if is_hidden else (err_out or None),
                        execution_time_ms=round(tc_time, 2)
                    ))
                else:
                    return None
            except Exception:
                return None

        points = 25 if overall_status == "Accepted" else int((passed_count / max(1, len(test_cases))) * 25)
        return CodeExecutionResult(
            status=overall_status,
            total_test_cases=len(test_cases),
            passed_test_cases=passed_count,
            execution_time_ms=round(total_time_ms, 2),
            memory_used_kb=1536.0,
            evaluations=evaluations,
            stdout=first_stdout,
            stderr=first_stderr,
            points_awarded=points
        )

    def run_code(
        self,
        language: str,
        code: str,
        test_cases: List[Dict[str, Any]],
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    ) -> CodeExecutionResult:
        """
        Executes code against given test cases securely in an isolated sandbox.
        Hides all hidden test case inputs and expected/actual outputs from the result.
        """
        # Validate inputs
        if len(code) > MAX_CODE_LENGTH:
            return CodeExecutionResult(
                status="Compilation Error",
                total_test_cases=len(test_cases),
                passed_test_cases=0,
                execution_time_ms=0.0,
                memory_used_kb=0.0,
                evaluations=[],
                stdout="",
                stderr=f"Source code exceeds maximum size limit ({MAX_CODE_LENGTH} characters).",
                points_awarded=0
            )

        # Try external Judge0 if configured
        if self.judge0_url:
            judge_res = self._execute_judge0(language, code, test_cases, timeout_seconds)
            if judge_res:
                return judge_res

        # Isolated Sandbox Execution
        evaluations: List[TestCaseEvaluation] = []
        passed_count = 0
        total_time_ms = 0.0
        overall_status = "Accepted"
        first_stdout = ""
        first_stderr = ""

        # Run in a dedicated temporary sandbox directory
        with tempfile.TemporaryDirectory(prefix="code_sandbox_") as temp_dir:
            for idx, tc in enumerate(test_cases, start=1):
                input_data = tc.get("input", "") or ""
                expected = tc.get("expected_output", "") or ""
                is_hidden = tc.get("is_hidden", False)

                res = self._execute_in_sandbox(
                    language=language,
                    code=code,
                    stdin_data=input_data,
                    timeout_seconds=timeout_seconds,
                    temp_dir=temp_dir
                )

                exec_time = res["exec_time_ms"]
                total_time_ms += exec_time

                if res["compilation_error"]:
                    overall_status = "Compilation Error"
                    first_stderr = res["compilation_error"]
                    evaluations.append(TestCaseEvaluation(
                        test_case_number=idx,
                        is_hidden=is_hidden,
                        status="Compilation Error",
                        input=None if is_hidden else input_data,
                        expected_output=None if is_hidden else expected,
                        actual_output=None,
                        error_message=None if is_hidden else res["compilation_error"],
                        execution_time_ms=0.0
                    ))
                    break

                if res["timed_out"]:
                    status_str = "Time Limit Exceeded"
                    if overall_status == "Accepted":
                        overall_status = "Time Limit Exceeded"
                elif res["returncode"] != 0:
                    status_str = "Runtime Error"
                    if overall_status in ["Accepted", "Wrong Answer"]:
                        overall_status = "Runtime Error"
                    if not first_stderr:
                        first_stderr = res["stderr"]
                else:
                    norm_actual = normalize_output(res["stdout"])
                    norm_expected = normalize_output(expected)
                    if norm_actual == norm_expected:
                        status_str = "Passed"
                        passed_count += 1
                    else:
                        status_str = "Wrong Answer"
                        if overall_status == "Accepted":
                            overall_status = "Wrong Answer"

                if not first_stdout and res["stdout"]:
                    first_stdout = res["stdout"]
                if not first_stderr and res["stderr"]:
                    first_stderr = res["stderr"]

                evaluations.append(TestCaseEvaluation(
                    test_case_number=idx,
                    is_hidden=is_hidden,
                    status=status_str,
                    input=None if is_hidden else input_data,
                    expected_output=None if is_hidden else expected,
                    actual_output=None if is_hidden else res["stdout"].strip(),
                    error_message=None if is_hidden else (res["stderr"].strip() if res["stderr"] else None),
                    execution_time_ms=round(exec_time, 2)
                ))

        if overall_status == "Accepted" and passed_count < len(test_cases):
            overall_status = "Wrong Answer"

        points = 25 if overall_status == "Accepted" else int((passed_count / max(1, len(test_cases))) * 25)

        return CodeExecutionResult(
            status=overall_status,
            total_test_cases=len(test_cases),
            passed_test_cases=passed_count,
            execution_time_ms=round(total_time_ms, 2),
            memory_used_kb=1536.0,
            evaluations=evaluations,
            stdout=first_stdout.strip(),
            stderr=first_stderr.strip(),
            points_awarded=points
        )

code_runner = CodeRunnerService()
