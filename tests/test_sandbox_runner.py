import pytest
from app.services.code_runner import code_runner

def test_code_runner_accepted():
    res = code_runner.run_code(
        language="python",
        code="name = input()\nprint(f'Hello, {name}!')",
        test_cases=[
            {"input": "Alice", "expected_output": "Hello, Alice!", "is_hidden": False},
            {"input": "Bob", "expected_output": "Hello, Bob!", "is_hidden": True}
        ]
    )
    assert res.status == "Accepted"
    assert res.passed_test_cases == 2
    assert res.total_test_cases == 2
    # Hidden test case privacy check
    assert res.evaluations[1].is_hidden is True
    assert res.evaluations[1].input is None
    assert res.evaluations[1].expected_output is None
    assert res.evaluations[1].actual_output is None

def test_code_runner_wrong_answer():
    res = code_runner.run_code(
        language="python",
        code="print('Wrong')",
        test_cases=[{"input": "", "expected_output": "Right", "is_hidden": False}]
    )
    assert res.status == "Wrong Answer"
    assert res.passed_test_cases == 0

def test_code_runner_timeout():
    res = code_runner.run_code(
        language="python",
        code="import time\ntime.sleep(5)",
        test_cases=[{"input": "", "expected_output": "", "is_hidden": False}],
        timeout_seconds=0.5
    )
    assert res.status == "Time Limit Exceeded"

def test_code_runner_runtime_error():
    res = code_runner.run_code(
        language="python",
        code="print(1 / 0)",
        test_cases=[{"input": "", "expected_output": "0", "is_hidden": False}]
    )
    assert res.status == "Runtime Error"

def test_code_runner_compilation_error():
    res = code_runner.run_code(
        language="python",
        code="def bad_syntax(;",
        test_cases=[{"input": "", "expected_output": "", "is_hidden": False}]
    )
    assert res.status in ["Runtime Error", "Compilation Error"]
