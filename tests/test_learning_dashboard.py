import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.sql_models import UserModel
from app.models.category import CategoryModel
from app.models.tutorial import TutorialModel
from app.models.topic import TopicModel
from app.models.progress import UserProgressModel
from app.models.bookmark import BookmarkModel
from app.core.security import get_password_hash

client = TestClient(app)

import uuid

@pytest.fixture(scope="module")
def auth_tokens():
    # Login user 1 (Alex Mercer)
    res1 = client.post("/api/auth/login", json={
        "email": "student@codearena.com",
        "password": "password123"
    })
    assert res1.status_code == 200
    token1 = res1.json()["access_token"]
    user1 = res1.json()["user"]

    # Provision and login a brand new unique test user (Zero activity)
    uid = uuid.uuid4().hex[:8]
    new_user_email = f"student_{uid}@codearena.com"
    db = SessionLocal()
    new_u = UserModel(
        id=f"user_{uid}",
        student_id=f"STU-{uid[:6].upper()}",
        email=new_user_email,
        password=get_password_hash("password123"),
        name="Brand New Student",
        role="student",
        college_name="Test Engineering College",
        avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=Zero"
    )
    db.add(new_u)
    db.commit()
    db.close()

    res2 = client.post("/api/auth/login", json={
        "email": new_user_email,
        "password": "password123"
    })
    assert res2.status_code == 200
    token2 = res2.json()["access_token"]
    user2 = res2.json()["user"]

    return {
        "user1": {"token": token1, "user": user1, "headers": {"Authorization": f"Bearer {token1}"}},
        "user2": {"token": token2, "user": user2, "headers": {"Authorization": f"Bearer {token2}"}},
        "user2_email": new_user_email
    }

def test_1_login_and_auth_me(auth_tokens):
    """1 & 2. Verify current user profile name, email and DP."""
    headers = auth_tokens["user1"]["headers"]
    res = client.get("/api/auth/me", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "student@codearena.com"
    assert data["name"] == "Alex Mercer"
    assert "avatar_url" in data or "profile_image_url" in data

def test_2_categories_endpoint():
    """3. Verify category counts and all 13 categories returned."""
    res = client.get("/api/categories")
    assert res.status_code == 200
    categories = res.json()
    assert len(categories) >= 13
    slugs = [c["slug"] for c in categories]
    for expected_slug in ["html", "css", "javascript", "react", "python", "java", "c", "cpp", "sql", "mysql", "fastapi", "nodejs", "git"]:
        assert expected_slug in slugs
    # Verify tutorial counts are populated from database
    for c in categories:
        assert c["tutorial_count"] >= 0

def test_3_new_user_zero_state(auth_tokens):
    """11. Test a new user with no activity returns zeros, not 500."""
    headers = auth_tokens["user2"]["headers"]
    res = client.get("/api/dashboard/summary", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["courses_started"] == 0
    assert data["completed_lessons"] == 0
    assert data["saved_tutorials"] == 0
    assert data["overall_progress_percentage"] == 0.0

    cont_res = client.get("/api/dashboard/continue-learning", headers=headers)
    assert cont_res.status_code == 200
    assert cont_res.json() == []

    bm_res = client.get("/api/bookmarks", headers=headers)
    assert bm_res.status_code == 200
    assert bm_res.json() == []

def test_4_start_and_continue_learning(auth_tokens):
    """4. Access a topic and confirm it appears in Continue Learning."""
    headers = auth_tokens["user2"]["headers"]
    
    # Access topic in HTML tutorial
    res = client.get("/api/topics/top_html_intro", headers=headers)
    assert res.status_code == 200
    topic = res.json()
    assert topic["id"] == "top_html_intro"

    # Confirm it now appears in Continue Learning
    cont_res = client.get("/api/dashboard/continue-learning", headers=headers)
    assert cont_res.status_code == 200
    items = cont_res.json()
    assert len(items) >= 1
    assert items[0]["tutorial_id"] == "tut_html_fundamentals"
    assert items[0]["last_topic_id"] == "top_html_intro"

def test_5_complete_topic_and_stats_update(auth_tokens):
    """5 & 6. Complete a topic and verify completed count & progress % changes."""
    headers = auth_tokens["user2"]["headers"]

    # Check initial summary
    sum_before = client.get("/api/dashboard/summary", headers=headers).json()
    completed_before = sum_before["completed_lessons"]

    # Mark top_html_intro completed
    comp_res = client.post("/api/topics/top_html_intro/complete", headers=headers)
    assert comp_res.status_code == 200
    assert comp_res.json()["is_completed"] == True

    # Re-fetch summary
    sum_after = client.get("/api/dashboard/summary", headers=headers).json()
    assert sum_after["completed_lessons"] == completed_before + 1
    assert sum_after["overall_progress_percentage"] > 0.0

def test_6_bookmark_add_and_remove(auth_tokens):
    """7 & 8. Save a tutorial and verify bookmark count, then remove and verify."""
    headers = auth_tokens["user2"]["headers"]

    # Bookmark CSS tutorial
    bm_res = client.post("/api/bookmarks/tut_css_layout", headers=headers)
    assert bm_res.status_code == 200

    # Verify bookmark count in summary
    sum_bm = client.get("/api/dashboard/summary", headers=headers).json()
    assert sum_bm["saved_tutorials"] >= 1

    # Verify in /api/bookmarks
    bms = client.get("/api/bookmarks", headers=headers).json()
    tut_ids = [b["tutorial_id"] for b in bms]
    assert "tut_css_layout" in tut_ids

    # Remove bookmark
    del_res = client.delete("/api/bookmarks/tut_css_layout", headers=headers)
    assert del_res.status_code == 200

    # Verify removed
    bms_after = client.get("/api/bookmarks", headers=headers).json()
    assert "tut_css_layout" not in [b["tutorial_id"] for b in bms_after]

def test_7_progress_persistence_and_relogin(auth_tokens):
    """9 & 10. Confirm progress persists across re-login."""
    # Login again as user 2
    login_res = client.post("/api/auth/login", json={
        "email": auth_tokens["user2_email"],
        "password": "password123"
    })
    assert login_res.status_code == 200
    fresh_token = login_res.json()["access_token"]
    fresh_headers = {"Authorization": f"Bearer {fresh_token}"}

    # Verify completed topic is still recorded
    prog_res = client.get("/api/progress/me", headers=fresh_headers)
    assert prog_res.status_code == 200
    prog_data = prog_res.json()
    completed_ids = [t["topic_id"] for t in prog_data["completed_topics"]]
    assert "top_html_intro" in completed_ids

def test_8_user_privacy_isolation(auth_tokens):
    """12. Verify user 2 cannot see or delete user 1's bookmarks."""
    h1 = auth_tokens["user1"]["headers"]
    h2 = auth_tokens["user2"]["headers"]

    # Ensure user 1 has tut_python_core bookmarked
    client.post("/api/bookmarks/tut_python_core", headers=h1)

    # User 2 bookmarks list must NOT contain user 1's bookmark
    user2_bms = client.get("/api/bookmarks", headers=h2).json()
    for bm in user2_bms:
        assert bm["user_id"] != auth_tokens["user1"]["user"]["id"]

    # User 2 trying to delete user 1's bookmark tutorial if user 2 hasn't bookmarked it
    del_resp = client.delete("/api/bookmarks/tut_python_core", headers=h2)
    assert del_resp.status_code == 404

def test_9_missing_and_invalid_records(auth_tokens):
    """13. Test missing records and invalid IDs."""
    headers = auth_tokens["user1"]["headers"]

    # Invalid topic complete
    res = client.post("/api/topics/non_existent_topic_xyz/complete", headers=headers)
    assert res.status_code == 404

    # Invalid bookmark add
    res_bm = client.post("/api/bookmarks/non_existent_tutorial_xyz", headers=headers)
    assert res_bm.status_code == 404

    # Invalid tutorial get
    res_tut = client.get("/api/tutorials/non_existent_tutorial_xyz", headers=headers)
    assert res_tut.status_code == 404
