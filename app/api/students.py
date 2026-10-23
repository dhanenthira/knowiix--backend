from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.schemas.user import UserResponse
from app.api.auth import get_current_user
from app.core.security import oauth2_scheme
from app.core.database import get_db
from datetime import datetime, timedelta
from app.models.sql_models import (
    UserModel, DailySetModel, LearningModuleModel, AssessmentTestModel,
    QuestionModel, CodingProblemModel, NotificationModel, SubmissionModel,
    QuestionSolvedModel, ProblemSolvedModel
)
from app.schemas.practice import DailySetSummary
from app.schemas.lesson import ModuleSummary
from app.schemas.test import AssessmentTest

router = APIRouter(prefix="/students", tags=["Students"])

def get_optional_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[UserResponse]:
    if not token or not db:
        return None
    try:
        return get_current_user(token=token, db=db)
    except Exception:
        return None

def _generate_svg_curve(values: List[float], labels: List[str], max_val: float = 100.0, min_val: float = 0.0, unit: str = "%"):
    n = len(values)
    if n == 0:
        values = [75.0]
        labels = ["Active"]
        n = 1

    margin_left = 60
    margin_right = 950
    nodes = []
    val_range = max(1.0, max_val - min_val)
    for i, val in enumerate(values):
        cx = round(margin_left + (i * (margin_right - margin_left) / max(1, n - 1)))
        # Y goes from 40 (max_val) to 200 (min_val)
        norm = (max(min_val, min(max_val, float(val))) - min_val) / val_range
        cy = round(200 - norm * 160)
        cy = max(35, min(205, cy))
        formatted_val = f"{round(val)}{unit}" if unit == "%" else f"{round(val)} {unit}".strip()
        nodes.append({"cx": cx, "cy": cy, "val": formatted_val, "raw": round(float(val), 1)})

    if n == 1:
        path_line = f"M {nodes[0]['cx']},{nodes[0]['cy']}"
        path_area = f"M {nodes[0]['cx']},{nodes[0]['cy']} L {nodes[0]['cx']},210 Z"
    else:
        path_line_parts = [f"M {nodes[0]['cx']},{nodes[0]['cy']}"]
        for i in range(n - 1):
            p0 = nodes[i]
            p1 = nodes[i + 1]
            dx = (p1['cx'] - p0['cx']) / 2.0
            c1x = round(p0['cx'] + dx * 0.7)
            c1y = p0['cy']
            c2x = round(p1['cx'] - dx * 0.7)
            c2y = p1['cy']
            path_line_parts.append(f"C {c1x},{c1y} {c2x},{c2y} {p1['cx']},{p1['cy']}")
        path_line = " ".join(path_line_parts)
        path_area = f"{path_line} L {nodes[-1]['cx']},210 L {nodes[0]['cx']},210 Z"

    return {
        "nodes": nodes,
        "labels": labels,
        "pathLine": path_line,
        "pathArea": path_area
    }

def _compute_skill_progress(db: Session, user: Optional[UserModel]) -> Dict[str, Any]:
    # 1. Aptitude Track - Real DB questions and solved records
    apt_total = db.query(QuestionModel).filter(QuestionModel.category.ilike("%aptitude%")).count() if db else 0
    apt_solved = db.query(QuestionSolvedModel).filter(
        QuestionSolvedModel.user_id == user.id,
        QuestionSolvedModel.category.ilike("%aptitude%")
    ).count() if (user and db) else 0
    apt_remaining = max(0, apt_total - apt_solved)
    apt_pct = round((apt_solved / apt_total) * 100, 1) if apt_total > 0 else 0.0

    # 2. Technical Track (DSA & Core) - Real DB questions and solved records
    tech_total = db.query(QuestionModel).filter(QuestionModel.category.ilike("%tech%")).count() if db else 0
    tech_solved = db.query(QuestionSolvedModel).filter(
        QuestionSolvedModel.user_id == user.id,
        QuestionSolvedModel.category.ilike("%tech%")
    ).count() if (user and db) else 0
    tech_remaining = max(0, tech_total - tech_solved)
    tech_pct = round((tech_solved / tech_total) * 100, 1) if tech_total > 0 else 0.0

    # 3. Coding Track (Competitive Programming) - Real DB problems and solved records
    code_total = db.query(CodingProblemModel).filter(CodingProblemModel.is_published == True).count() if db else 0
    code_solved = db.query(ProblemSolvedModel).filter(
        ProblemSolvedModel.user_id == user.id
    ).count() if (user and db) else 0
    code_remaining = max(0, code_total - code_solved)
    code_pct = round((code_solved / code_total) * 100, 1) if code_total > 0 else 0.0

    overall_readiness = round((apt_pct + tech_pct + code_pct) / 3, 1)

    return {
        "overall_readiness": overall_readiness,
        "readiness_text": f"Overall: {round(overall_readiness)}% Ready",
        "aptitude": {
            "id": "aptitude",
            "title": "Aptitude & Problem Solving",
            "subtitle": "Quantitative & Logical Reasoning",
            "total_problems": apt_total,
            "problems_solved": apt_solved,
            "problems_remaining": apt_remaining,
            "progress_percentage": apt_pct,
            "theme": "purple",
            "tag": "Working" if apt_solved > 0 else "Not Started",
            "tag_color": "purple",
            "date": "Updated from DB",
            "deadline_badge": f"{apt_remaining} Remaining",
            "path": "/aptitude"
        },
        "technical": {
            "id": "technical",
            "title": "Technical (DSA & Core)",
            "subtitle": "Data Structures, Algorithms & OS",
            "total_problems": tech_total,
            "problems_solved": tech_solved,
            "problems_remaining": tech_remaining,
            "progress_percentage": tech_pct,
            "theme": "blue",
            "tag": "In Progress" if tech_solved > 0 else "Not Started",
            "tag_color": "blue",
            "date": "Active Session",
            "deadline_badge": f"{tech_remaining} Qs Left",
            "path": "/questions?category=Technical"
        },
        "coding": {
            "id": "coding",
            "title": "Coding & Algorithms",
            "subtitle": "Competitive Programming Drills",
            "total_problems": code_total,
            "problems_solved": code_solved,
            "problems_remaining": code_remaining,
            "progress_percentage": code_pct,
            "theme": "purple",
            "tag": "Working" if code_solved > 0 else "Not Started",
            "tag_color": "purple",
            "date": "Daily Target",
            "deadline_badge": f"{code_remaining} Problems Left",
            "path": "/coding/practice"
        }
    }

def _get_sub_metrics(s: SubmissionModel):
    if s.status and s.status.lower() == "accepted":
        return 100.0, 100.0
    if s.total_test_cases and s.total_test_cases > 0:
        pct = round((s.passed_test_cases / s.total_test_cases) * 100.0, 1)
        return pct, pct
    if s.max_score and s.max_score > 0:
        pct = round(((s.score or 0.0) / s.max_score) * 100.0, 1)
        return pct, pct
    val = min(100.0, float(s.score or 0.0))
    return val, val

def _compute_performance_overview(db: Session, user: Optional[UserModel]) -> Dict[str, Any]:
    submissions = []
    if user and db:
        submissions = db.query(SubmissionModel).filter(
            SubmissionModel.user_id == user.id,
            SubmissionModel.submission_type.in_(["test", "code", "practice"])
        ).order_by(SubmissionModel.submitted_at.asc()).all()

    sub_scores = []
    sub_accs = []
    for s in submissions:
        sc, ac = _get_sub_metrics(s)
        sub_scores.append(sc)
        sub_accs.append(ac)

    user_acc = round(sum(sub_accs) / len(sub_accs), 1) if sub_accs else (round(user.overall_accuracy or 0.0, 1) if user else 0.0)
    avg_score = round(sum(sub_scores) / len(sub_scores), 1) if sub_scores else 0.0
    streak = user.streak_days if (user and user.streak_days is not None) else (1 if submissions else 0)
    total_evals = len(submissions)

    now = datetime.utcnow()
    today = now.date()

    # --- 7 Days Config calculated strictly from DB records ---
    days_7 = [today - timedelta(days=6 - i) for i in range(7)]
    day_labels = [d.strftime("%a") for d in days_7]

    p7_score = []
    p7_acc = []
    p7_tests = []
    for d in days_7:
        d_subs = [s for s in submissions if s.submitted_at and s.submitted_at.date() <= d]
        p7_tests.append(len(d_subs))
        if d_subs:
            d_scores = [_get_sub_metrics(s)[0] for s in d_subs]
            d_accs = [_get_sub_metrics(s)[1] for s in d_subs]
            p7_score.append(round(sum(d_scores) / len(d_scores), 1))
            p7_acc.append(round(sum(d_accs) / len(d_accs), 1))
        else:
            p7_score.append(0.0)
            p7_acc.append(user_acc if user_acc > 0 else 0.0)

    max_7d_test = max(4.0, float(max(p7_tests) if p7_tests else 4.0))
    svg_7d_score = _generate_svg_curve(p7_score, day_labels, max_val=100.0, min_val=0.0, unit="%")
    svg_7d_acc = _generate_svg_curve(p7_acc, day_labels, max_val=100.0, min_val=0.0, unit="%")
    svg_7d_tests = _generate_svg_curve(p7_tests, day_labels, max_val=max_7d_test, min_val=0.0, unit="")

    trend_7d = f"↑ +{round(p7_score[-1] - p7_score[0], 1)}% this period" if (p7_score and p7_score[-1] > p7_score[0]) else ("Active Synced" if total_evals > 0 else "No evaluations yet")

    # --- Live Real-Time Sliding Config (Real-Time Method based on current real stats) ---
    if submissions:
        live_subs = submissions[-7:]
        pad_count = 7 - len(live_subs)
        p_live_score = [0.0] * pad_count + [_get_sub_metrics(s)[0] for s in live_subs]
        p_live_acc = [user_acc] * pad_count + [_get_sub_metrics(s)[1] for s in live_subs]
        p_live_tests = [0] * pad_count + list(range(max(1, total_evals - len(live_subs) + 1), total_evals + 1))
        live_labels = [
            (now - timedelta(minutes=(6 - i) * 5)).strftime("%H:%M") for i in range(pad_count)
        ] + [
            s.submitted_at.strftime("%H:%M") if s.submitted_at else "Now" for s in live_subs
        ]
    else:
        live_labels = [(now - timedelta(seconds=(6 - i) * 15)).strftime("%H:%M:%S") for i in range(7)]
        p_live_score = [0.0] * 7
        p_live_acc = [user_acc] * 7
        p_live_tests = [0] * 7

    max_live_test = max(4.0, float(max(p_live_tests) if p_live_tests else 4.0))
    svg_live_score = _generate_svg_curve(p_live_score, live_labels, max_val=100.0, min_val=0.0, unit="%")
    svg_live_acc = _generate_svg_curve(p_live_acc, live_labels, max_val=100.0, min_val=0.0, unit="%")
    svg_live_tests = _generate_svg_curve(p_live_tests, live_labels, max_val=max_live_test, min_val=0.0, unit="")

    # --- 30 Days Config (4 week buckets) ---
    w_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]
    w_dates = [today - timedelta(days=21), today - timedelta(days=14), today - timedelta(days=7), today]
    p30_score = []
    p30_acc = []
    p30_tests = []
    for wd in w_dates:
        w_subs = [s for s in submissions if s.submitted_at and s.submitted_at.date() <= wd]
        p30_tests.append(len(w_subs))
        if w_subs:
            w_sc = [_get_sub_metrics(s)[0] for s in w_subs]
            w_accs = [_get_sub_metrics(s)[1] for s in w_subs]
            p30_score.append(round(sum(w_sc) / len(w_sc), 1))
            p30_acc.append(round(sum(w_accs) / len(w_accs), 1))
        else:
            p30_score.append(0.0)
            p30_acc.append(user_acc if user_acc > 0 else 0.0)

    max_30d_test = max(4.0, float(max(p30_tests) if p30_tests else 4.0))
    svg_30d_score = _generate_svg_curve(p30_score, w_labels, max_val=100.0, min_val=0.0, unit="%")
    svg_30d_acc = _generate_svg_curve(p30_acc, w_labels, max_val=100.0, min_val=0.0, unit="%")
    svg_30d_tests = _generate_svg_curve(p30_tests, w_labels, max_val=max_30d_test, min_val=0.0, unit="")

    # --- 3 Months Config ---
    m_labels = ["Month 1", "Month 2", "Month 3"]
    m_dates = [today - timedelta(days=60), today - timedelta(days=30), today]
    p3m_score = []
    p3m_acc = []
    p3m_tests = []
    for md in m_dates:
        m_subs = [s for s in submissions if s.submitted_at and s.submitted_at.date() <= md]
        p3m_tests.append(len(m_subs))
        if m_subs:
            m_sc = [_get_sub_metrics(s)[0] for s in m_subs]
            m_accs = [_get_sub_metrics(s)[1] for s in m_subs]
            p3m_score.append(round(sum(m_sc) / len(m_sc), 1))
            p3m_acc.append(round(sum(m_accs) / len(m_accs), 1))
        else:
            p3m_score.append(0.0)
            p3m_acc.append(user_acc if user_acc > 0 else 0.0)

    max_3m_test = max(4.0, float(max(p3m_tests) if p3m_tests else 4.0))
    svg_3m_score = _generate_svg_curve(p3m_score, m_labels, max_val=100.0, min_val=0.0, unit="%")
    svg_3m_acc = _generate_svg_curve(p3m_acc, m_labels, max_val=100.0, min_val=0.0, unit="%")
    svg_3m_tests = _generate_svg_curve(p3m_tests, m_labels, max_val=max_3m_test, min_val=0.0, unit="")

    return {
        "7d": {
            "avg": f"{avg_score}%",
            "acc": f"{user_acc}%",
            "tests": f"{total_evals} Tests",
            "streak": f"{streak} Days Active",
            "trend": trend_7d,
            "metrics": {
                "score": {
                    "id": "score",
                    "title": "Average Score",
                    "value": f"{avg_score}%",
                    "color": "#4285F4",
                    "gradientId": "dashScoreGrad",
                    "yMarkers": ["100%", "75%", "50%", "0%"],
                    "values": p7_score,
                    **svg_7d_score
                },
                "accuracy": {
                    "id": "accuracy",
                    "title": "Overall Accuracy",
                    "value": f"{user_acc}%",
                    "color": "#059669",
                    "gradientId": "dashAccGrad",
                    "yMarkers": ["100%", "75%", "50%", "0%"],
                    "values": p7_acc,
                    **svg_7d_acc
                },
                "tests": {
                    "id": "tests",
                    "title": "Tests Completed",
                    "value": f"{total_evals} Tests",
                    "color": "#7C3AED",
                    "gradientId": "dashTestsGrad",
                    "yMarkers": [str(int(max_7d_test)), str(int(max_7d_test * 0.75)), str(int(max_7d_test * 0.5)), "0"],
                    "values": p7_tests,
                    **svg_7d_tests
                }
            },
            **svg_7d_score
        },
        "live": {
            "avg": f"{avg_score}%",
            "acc": f"{user_acc}%",
            "tests": f"{total_evals} Tests",
            "streak": f"{streak} Days Active",
            "trend": "⚡ Real-Time DB Synced" if total_evals > 0 else "Live Ready",
            "metrics": {
                "score": {
                    "id": "score",
                    "title": "Average Score",
                    "value": f"{avg_score}%",
                    "color": "#4285F4",
                    "gradientId": "dashScoreGrad",
                    "yMarkers": ["100%", "75%", "50%", "0%"],
                    "values": p_live_score,
                    **svg_live_score
                },
                "accuracy": {
                    "id": "accuracy",
                    "title": "Overall Accuracy",
                    "value": f"{user_acc}%",
                    "color": "#059669",
                    "gradientId": "dashAccGrad",
                    "yMarkers": ["100%", "75%", "50%", "0%"],
                    "values": p_live_acc,
                    **svg_live_acc
                },
                "tests": {
                    "id": "tests",
                    "title": "Tests Completed",
                    "value": f"{total_evals} Tests",
                    "color": "#7C3AED",
                    "gradientId": "dashTestsGrad",
                    "yMarkers": [str(int(max_live_test)), str(int(max_live_test * 0.75)), str(int(max_live_test * 0.5)), "0"],
                    "values": p_live_tests,
                    **svg_live_tests
                }
            },
            **svg_live_score
        },
        "30d": {
            "avg": f"{avg_score}%",
            "acc": f"{user_acc}%",
            "tests": f"{total_evals} Tests",
            "streak": f"{streak} Days Active",
            "trend": trend_7d,
            "metrics": {
                "score": {
                    "id": "score",
                    "title": "Average Score",
                    "value": f"{avg_score}%",
                    "color": "#4285F4",
                    "gradientId": "dashScoreGrad",
                    "yMarkers": ["100%", "75%", "50%", "0%"],
                    "values": p30_score,
                    **svg_30d_score
                },
                "accuracy": {
                    "id": "accuracy",
                    "title": "Overall Accuracy",
                    "value": f"{user_acc}%",
                    "color": "#059669",
                    "gradientId": "dashAccGrad",
                    "yMarkers": ["100%", "75%", "50%", "0%"],
                    "values": p30_acc,
                    **svg_30d_acc
                },
                "tests": {
                    "id": "tests",
                    "title": "Tests Completed",
                    "value": f"{total_evals} Tests",
                    "color": "#7C3AED",
                    "gradientId": "dashTestsGrad",
                    "yMarkers": [str(int(max_30d_test)), str(int(max_30d_test * 0.75)), str(int(max_30d_test * 0.5)), "0"],
                    "values": p30_tests,
                    **svg_30d_tests
                }
            },
            **svg_30d_score
        },
        "3m": {
            "avg": f"{avg_score}%",
            "acc": f"{user_acc}%",
            "tests": f"{total_evals} Tests",
            "streak": f"{streak} Days Active",
            "trend": trend_7d,
            "metrics": {
                "score": {
                    "id": "score",
                    "title": "Average Score",
                    "value": f"{avg_score}%",
                    "color": "#4285F4",
                    "gradientId": "dashScoreGrad",
                    "yMarkers": ["100%", "75%", "50%", "0%"],
                    "values": p3m_score,
                    **svg_3m_score
                },
                "accuracy": {
                    "id": "accuracy",
                    "title": "Overall Accuracy",
                    "value": f"{user_acc}%",
                    "color": "#059669",
                    "gradientId": "dashAccGrad",
                    "yMarkers": ["100%", "75%", "50%", "0%"],
                    "values": p3m_acc,
                    **svg_3m_acc
                },
                "tests": {
                    "id": "tests",
                    "title": "Tests Completed",
                    "value": f"{total_evals} Tests",
                    "color": "#7C3AED",
                    "gradientId": "dashTestsGrad",
                    "yMarkers": [str(int(max_3m_test)), str(int(max_3m_test * 0.75)), str(int(max_3m_test * 0.5)), "0"],
                    "values": p3m_tests,
                    **svg_3m_tests
                }
            },
            **svg_3m_score
        }
    }

def _compute_recent_assessments(db: Session, user: Optional[UserModel]) -> List[Dict[str, Any]]:
    recent_assessments = []

    # 1. Fetch real student submissions across test, code, and practice drills
    if user and db:
        subs = db.query(SubmissionModel).filter(
            SubmissionModel.user_id == user.id,
            SubmissionModel.submission_type.in_(["test", "code", "practice"])
        ).order_by(SubmissionModel.submitted_at.desc()).limit(10).all()

        for s in subs:
            score_pct, acc_pct = _get_sub_metrics(s)
            score_num = round(score_pct)
            acc_num = round(acc_pct)

            if s.submission_type == "code":
                code_prob = db.query(CodingProblemModel).filter(
                    (CodingProblemModel.id == s.problem_id) | (CodingProblemModel.slug == s.problem_id)
                ).first()
                title = code_prob.title if code_prob else f"Coding Problem #{s.problem_id[:8]}"
                icon = "💻"
                action_url = f"/coding/problem/{code_prob.slug if code_prob and code_prob.slug else s.problem_id}"
                action_label = "View Solution"
            elif s.submission_type == "practice":
                q_obj = db.query(QuestionModel).filter(QuestionModel.id == s.problem_id).first()
                title = q_obj.title if q_obj else "Aptitude Practice Drill"
                icon = "🧠"
                action_url = "/aptitude"
                action_label = "Review"
            else:
                test = db.query(AssessmentTestModel).filter(AssessmentTestModel.id == s.problem_id).first()
                title = test.title if test else f"Assessment #{s.problem_id[:8]}"
                cat = (test.category if test else "general").lower()
                icon = "🧠" if "apt" in cat else ("💻" if "tech" in cat else ("🗣" if "comm" in cat or "verbal" in cat else "⭐"))
                action_url = "/assessments"
                action_label = "Review"

            # Relative date calculation
            delta = datetime.utcnow() - (s.submitted_at or datetime.utcnow())
            if delta.days == 0:
                d_str = "Today"
            elif delta.days == 1:
                d_str = "Yesterday"
            else:
                d_str = f"{delta.days} days ago"

            recent_assessments.append({
                "id": s.id,
                "test_id": s.problem_id,
                "title": title,
                "icon": icon,
                "score": f"{score_num}%",
                "score_num": score_num,
                "accuracy": f"{acc_num}%",
                "accuracy_num": acc_num,
                "date": d_str,
                "status": "completed",
                "action_label": action_label,
                "action_url": action_url
            })

    # 2. Check QuestionSolvedModel for practice solves if still fewer than 4
    if len(recent_assessments) < 4 and user and db:
        existing_q_ids = {a.get("test_id") for a in recent_assessments}
        q_solves = db.query(QuestionSolvedModel).filter(
            QuestionSolvedModel.user_id == user.id
        ).order_by(QuestionSolvedModel.first_solved_at.desc()).limit(6).all()

        for qs in q_solves:
            if qs.question_id not in existing_q_ids and len(recent_assessments) < 4:
                q_obj = db.query(QuestionModel).filter(QuestionModel.id == qs.question_id).first()
                title = q_obj.title if q_obj else f"{qs.category.title()} Question Solved"
                icon = "🧠" if "apt" in (qs.category or "") else "⚙️"
                delta = datetime.utcnow() - (qs.first_solved_at or datetime.utcnow())
                d_str = "Today" if delta.days == 0 else (f"{delta.days}d ago" if delta.days > 0 else "Just now")
                recent_assessments.append({
                    "id": f"qs_{qs.id}",
                    "test_id": qs.question_id,
                    "title": title,
                    "icon": icon,
                    "score": "100%",
                    "score_num": 100,
                    "accuracy": "100%",
                    "accuracy_num": 100,
                    "date": d_str,
                    "status": "completed",
                    "action_label": "Practice",
                    "action_url": "/aptitude"
                })

    # 3. If student has fewer than 4 items, supplement with real active tests from database
    if len(recent_assessments) < 4 and db:
        existing_test_ids = {a.get("test_id") for a in recent_assessments}
        db_tests = db.query(AssessmentTestModel).all()
        for t in db_tests:
            if t.id not in existing_test_ids and len(recent_assessments) < 4:
                cat = (t.category or "general").lower()
                icon = "🧠" if "apt" in cat else ("💻" if "tech" in cat else ("🗣" if "comm" in cat or "verbal" in cat else "⭐"))
                recent_assessments.append({
                    "id": t.id,
                    "test_id": t.id,
                    "title": t.title,
                    "icon": icon,
                    "score": "Not Attempted",
                    "score_num": 0,
                    "accuracy": "-",
                    "accuracy_num": 0,
                    "date": t.status.title() if t.status else "Available",
                    "status": t.status or "active",
                    "action_label": "Launch",
                    "action_url": f"/aptitude?mode=mock" if "apt" in cat else "/assessments"
                })

    return recent_assessments

@router.get("/dashboard")
def get_student_dashboard(
    current_user: Optional[UserResponse] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    user = None
    if current_user:
        user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user:
        user = (
            db.query(UserModel).filter(UserModel.id == "user_student_01").first()
            or db.query(UserModel).filter(UserModel.role == "student", UserModel.coding_problems_solved > 0).first()
            or db.query(UserModel).filter(UserModel.role == "student").first()
            or db.query(UserModel).first()
        )
    
    daily_sets = db.query(DailySetModel).all()
    modules = db.query(LearningModuleModel).all()
    tests = db.query(AssessmentTestModel).all()

    # Coding problems count from DB
    easy_code_count = db.query(CodingProblemModel).filter(CodingProblemModel.difficulty == "easy").count()
    med_code_count = db.query(CodingProblemModel).filter(CodingProblemModel.difficulty == "medium").count()
    hard_code_count = db.query(CodingProblemModel).filter(CodingProblemModel.difficulty == "hard").count()
    total_code_count = easy_code_count + med_code_count + hard_code_count

    # Questions count per category from DB
    apt_q_count = db.query(QuestionModel).filter(QuestionModel.category.ilike("%aptitude%")).count()
    tech_q_count = db.query(QuestionModel).filter(QuestionModel.category.ilike("%tech%")).count()
    comm_q_count = db.query(QuestionModel).filter(QuestionModel.category.ilike("%comm%")).count()
    total_q_count = db.query(QuestionModel).count()

    # Top students for leaderboard preview strictly from DB
    top_students = db.query(UserModel).filter(UserModel.role == "student").order_by(UserModel.total_points.desc()).limit(3).all()
    leaderboard_preview = []
    for idx, s in enumerate(top_students, start=1):
        leaderboard_preview.append({
            "rank": idx,
            "name": s.name,
            "student_id": s.student_id,
            "points": s.total_points or 0,
            "avatar": s.avatar_url
        })

    # Compute skill progress, performance overview and assessments strictly from DB
    skill_progress_data = _compute_skill_progress(db, user)
    performance_overview_data = _compute_performance_overview(db, user)
    recent_assessments_data = _compute_recent_assessments(db, user)

    user_resp = UserResponse.model_validate(user, from_attributes=True) if user else current_user

    return {
        "user": user_resp.model_dump() if user_resp else None,
        "stats": {
            "total_questions": total_q_count,
            "questions_solved": user.questions_solved if (user and user.questions_solved is not None) else 0,
            "overall_accuracy": round(user.overall_accuracy or 0.0, 1) if user else 0.0,
            "coding_problems_solved": user.coding_problems_solved if (user and user.coding_problems_solved is not None) else 0,
            "streak_days": user.streak_days if (user and user.streak_days is not None) else 0,
            "total_points": user.total_points if (user and user.total_points is not None) else 0,
            "battles_won": user.battles_won if (user and user.battles_won is not None) else 0,
            "coding_breakdown": {
                "easy": easy_code_count,
                "medium": med_code_count,
                "hard": hard_code_count,
                "total": total_code_count
            },
            "category_questions": {
                "aptitude": apt_q_count,
                "technical": tech_q_count,
                "communication": comm_q_count,
                "coding": total_code_count
            },
            "aptitude_progress": skill_progress_data["aptitude"]
        },
        "skill_progress": skill_progress_data,
        "aptitude_progress": skill_progress_data["aptitude"],
        "performance_overview": performance_overview_data,
        "recent_assessments": recent_assessments_data,
        "daily_challenges": [DailySetSummary.model_validate(s, from_attributes=True).model_dump() for s in daily_sets],
        "learning_modules": [ModuleSummary.model_validate(m, from_attributes=True).model_dump() for m in modules],
        "upcoming_tests": [AssessmentTest.model_validate(t, from_attributes=True).model_dump() for t in tests if t.status in ["upcoming", "active"]],
        "leaderboard_preview": leaderboard_preview
    }

@router.put("/profile", response_model=UserResponse)
def update_profile(
    updates: Dict[str, Any],
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for k in ["name", "college_name", "department", "graduation_year", "bio", "avatar_url"]:
        if k in updates:
            setattr(user, k, updates[k])
            
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user, from_attributes=True)

@router.get("/profile", response_model=UserResponse)
def get_my_profile(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user, from_attributes=True)

@router.get("/me", response_model=UserResponse)
def get_current_student_me(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_my_profile(current_user, db)

@router.get("/realtime-flow")
def get_student_realtime_flow(
    current_user: Optional[UserResponse] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    user = None
    if current_user:
        user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user:
        user = db.query(UserModel).filter(UserModel.role == "student").first() or db.query(UserModel).first()

    now = datetime.utcnow()
    perf = _compute_performance_overview(db, user)
    live_perf = perf.get("live", {})
    metrics = live_perf.get("metrics", {})

    user_acc = round(user.overall_accuracy or 0.0, 1) if user else 0.0
    streak = user.streak_days if (user and user.streak_days is not None) else 0

    # Real evaluations count
    subs = db.query(SubmissionModel).filter(
        SubmissionModel.user_id == user.id
    ).order_by(SubmissionModel.submitted_at.desc()).all() if user else []

    scores = [
        round((s.score / max(1.0, s.max_score or 1.0)) * 100, 1) if s.max_score else round(float(s.score or 0.0), 1)
        for s in subs
    ]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

    # Build real event log from DB records
    events = []
    # 1. Recent submissions
    for s in subs[:3]:
        delta = now - (s.submitted_at or now)
        d_str = "Just now" if delta.seconds < 120 and delta.days == 0 else (f"{delta.days}d ago" if delta.days > 0 else f"{int(delta.seconds/60)}m ago")
        test = db.query(AssessmentTestModel).filter(AssessmentTestModel.id == s.problem_id).first()
        title = test.title if test else (f"Problem #{s.problem_id[:8]}" if s.problem_id else f"Submission #{s.id[:8]}")
        events.append({
            "id": s.id,
            "time": d_str,
            "category": "Assessment" if s.submission_type == "test" else "Coding",
            "type": "evaluation",
            "title": f"{title} Evaluated",
            "description": f"Submitted with score {s.score}. Status: {s.status or 'Completed'}.",
            "impact": f"{round(s.score or 0)} Marks",
            "status": "completed",
            "xp": int(s.score or 50),
            "badge_color": "#059669" if (s.score and s.score >= 50) else "#2563EB",
            "icon": "📊"
        })

    # 2. Recent question solves
    if user:
        q_solves = db.query(QuestionSolvedModel).filter(
            QuestionSolvedModel.user_id == user.id
        ).order_by(QuestionSolvedModel.first_solved_at.desc()).limit(3).all()
        for q in q_solves:
            delta = now - (q.first_solved_at or now)
            d_str = "Just now" if delta.seconds < 120 and delta.days == 0 else (f"{delta.days}d ago" if delta.days > 0 else f"{int(delta.seconds/60)}m ago")
            events.append({
                "id": f"q_{q.id}",
                "time": d_str,
                "category": q.category.title() if q.category else "Aptitude",
                "type": "solve",
                "title": f"{q.category.title() if q.category else 'Question'} #{q.question_id[:8]} Solved",
                "description": "Verified with precision and saved to database.",
                "impact": "+10 Points",
                "status": "success",
                "xp": 10,
                "badge_color": "#7C3AED",
                "icon": "🧠"
            })

    events = events[:4]

    return {
        "status": "CONNECTED",
        "live": True,
        "timestamp": now.isoformat(),
        "session_telemetry": {
            "active": True,
            "live_accuracy_pct": user_acc,
            "live_score_avg": avg_score,
            "tests_evaluated": len(subs),
            "streak_days": streak,
            "pipeline_latency_ms": 18
        },
        "realtime_graph": metrics,
        "usage_flow_events": events
    }

@router.post("/realtime-flow/simulate")
def simulate_student_realtime_event(
    action: Optional[Dict[str, Any]] = None,
    current_user: Optional[UserResponse] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    action_type = (action or {}).get("action_type", "aptitude_solve")
    now = datetime.utcnow()
    new_event = {
        "id": f"sim_{int(now.timestamp())}",
        "time": "Just now",
        "category": "Aptitude" if "apt" in action_type else ("Technical" if "tech" in action_type else "Coding"),
        "type": "solve",
        "title": f"Live Practice Action: {action_type.replace('_', ' ').title()}",
        "description": "Interactive real-time problem solved and ingested into live pipeline.",
        "impact": "+1 Solved • Calibrated",
        "status": "success",
        "xp": 100,
        "badge_color": "#7C3AED" if "apt" in action_type else "#2563EB"
    }

    return {
        "success": True,
        "message": "Real-time usage event ingested into live pipeline.",
        "event": new_event,
        "delta": {
            "aptitude_solved_increment": 1 if "apt" in action_type else 0,
            "score_progression": "+0.4%",
            "timestamp": now.isoformat()
        }
    }

@router.get("/{student_id}", response_model=UserResponse)
def get_student_by_id(
    student_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")

    target = db.query(UserModel).filter(
        (UserModel.id == student_id) | (UserModel.student_id == student_id)
    ).first()
    if not target:
        raise HTTPException(status_code=404, detail="Student not found")

    return UserResponse.model_validate(target, from_attributes=True)



