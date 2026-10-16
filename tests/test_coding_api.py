import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)

@pytest.fixture
def auth_headers():
    token = create_access_token(subject="user_student_01", role="student")
    return {"Authorization": f"Bearer {token}"}

def test_get_categories():
    response = client.get("/api/v1/coding/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 10
    names = [c["name"] for c in data]
    assert "Basic Programming" in names
    assert "Python" in names
    assert "Algorithms" in names

def test_get_problems_list():
    response = client.get("/api/v1/coding/problems?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 10
    assert len(data["items"]) <= 10

def test_problem_detail_hides_hidden_cases():
    response = client.get("/api/v1/coding/problems/hello-world")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Hello World"
    assert "sample_test_cases" in data
    # Ensure hidden_test_cases field is NEVER exposed
    assert "hidden_test_cases" not in data

def test_run_code():
    run_payload = {
        "problem_id": "hello-world",
        "language": "python",
        "code": "print('Hello, World!')"
    }
    response = client.post("/api/v1/coding/run", json=run_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert data["passed_test_cases"] >= 1

def test_submit_code_and_progress(auth_headers):
    # Submit solution for Hello World
    submit_payload = {
        "problem_id": "hello-world",
        "language": "python",
        "code": "print('Hello, World!')"
    }
    sub_resp = client.post("/api/v1/coding/submit", json=submit_payload, headers=auth_headers)
    assert sub_resp.status_code == 200
    sub_data = sub_resp.json()
    assert sub_data["status"] == "Accepted"

    # Verify problem status
    status_resp = client.get("/api/v1/coding/problems/hello-world/status", headers=auth_headers)
    assert status_resp.status_code == 200
    assert status_resp.json()["is_solved"] is True

    # Verify user progress
    prog_resp = client.get("/api/v1/coding/progress/me", headers=auth_headers)
    assert prog_resp.status_code == 200
    prog_data = prog_resp.json()
    assert prog_data["problems_solved"] >= 1

    # Verify private submissions
    my_subs_resp = client.get("/api/v1/coding/submissions/me", headers=auth_headers)
    assert my_subs_resp.status_code == 200
    my_subs = my_subs_resp.json()
    assert len(my_subs) >= 1
    assert any(s["problem_id"] == "cp_example_01" or "Hello World" in s.get("problem_title", "") for s in my_subs)
