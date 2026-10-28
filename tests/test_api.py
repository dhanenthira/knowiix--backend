from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Knowiix" in data["platform"]

def test_auth_login():
    response = client.post("/api/v1/auth/login", json={
        "email": "student@knowiix.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "student"

def test_admin_login():
    response = client.post("/api/v1/auth/admin/login", json={
        "email": "admin@knowiix.com",
        "password": "adminpassword123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "admin"

def test_student_dashboard():
    response = client.get("/api/v1/students/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "stats" in data
    assert "daily_challenges" in data

def test_coding_problems_and_run():
    response = client.get("/api/v1/coding/problems")
    assert response.status_code == 200
    data = response.json()
    items = data["items"] if isinstance(data, dict) and "items" in data else data
    assert len(items) > 0
    
    # Run code on hello-world
    run_resp = client.post("/api/v1/coding/run", json={
        "problem_id": "hello-world",
        "language": "python",
        "code": "print('Hello, World!')"
    })
    assert run_resp.status_code == 200
    res_data = run_resp.json()
    assert res_data["status"] == "Accepted"

def test_questions_endpoints():
    response = client.get("/api/v1/questions")
    assert response.status_code == 200
    assert len(response.json()) > 0

    cats_resp = client.get("/api/v1/questions/categories")
    assert cats_resp.status_code == 200
    assert len(cats_resp.json()) > 0

def test_lessons_endpoints():
    response = client.get("/api/v1/lessons/modules")
    assert response.status_code == 200
    modules = response.json()
    assert len(modules) > 0

    detail_resp = client.get("/api/v1/lessons/py_intro")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["id"] == "py_intro"

def test_practice_endpoints():
    response = client.get("/api/v1/practice/daily-sets")
    assert response.status_code == 200
    assert len(response.json()) > 0

    q_resp = client.get("/api/v1/practice/set/ds_apt_today/questions")
    assert q_resp.status_code == 200
    assert isinstance(q_resp.json(), list)

def test_leaderboard_endpoint():
    response = client.get("/api/v1/leaderboard")
    assert response.status_code == 200
    leaders = response.json()
    assert len(leaders) > 0
    assert leaders[0]["rank"] == 1

def test_admin_dashboard_and_students():
    # Using admin token header
    headers = {"Authorization": "Bearer admin_demo_jwt_token"}
    dash_resp = client.get("/api/v1/admin/dashboard", headers=headers)
    assert dash_resp.status_code == 200
    assert "analytics" in dash_resp.json()

    students_resp = client.get("/api/v1/admin/students", headers=headers)
    assert students_resp.status_code == 200
    assert len(students_resp.json()) > 0
