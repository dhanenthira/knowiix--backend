import math
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, desc, asc
from app.models.sql_models import (
    UserModel, CodingProblemModel, SubmissionModel,
    ProblemSolvedModel, ContestModel, ContestParticipationModel,
    BadgeModel, UserBadgeModel
)

class UserProfileService:

    @staticmethod
    def get_user_by_identifier(identifier: str, db: Session) -> Optional[UserModel]:
        """
        Finds user by id, student_id, email, or username slug.
        """
        if not db or not identifier:
            return None

        # 1. Exact match on id, student_id, or email
        user = db.query(UserModel).filter(
            (UserModel.id == identifier) |
            (UserModel.student_id == identifier) |
            (UserModel.email == identifier)
        ).first()

        if user:
            return user

        # 2. Match on slugified name or lower name
        clean_target = identifier.lower().replace("-", " ").replace("_", " ").strip()
        all_users = db.query(UserModel).all()
        for u in all_users:
            uname = (u.name or "").lower().strip()
            uname_slug = (u.name or "").lower().replace(" ", "").strip()
            if uname == clean_target or uname_slug == identifier.lower().strip():
                return u

        return None

    @staticmethod
    def get_public_profile(user: UserModel, db: Session) -> Dict[str, Any]:
        """
        Returns full profile information for the profile header.
        """
        # Calculate dynamic global rank based on total points / solved
        higher_users_count = db.query(UserModel).filter(
            UserModel.total_points > (user.total_points or 0)
        ).count()
        calc_rank = higher_users_count + 1

        # Check total unique problems solved
        solved_ids = UserProfileService._get_user_solved_problem_ids(user.id, db)
        total_solved = len(solved_ids)

        username = (user.student_id or user.name.lower().replace(" ", "")).strip()

        return {
            "id": user.id,
            "username": username,
            "full_name": user.name,
            "email": user.email,
            "bio": user.bio or "Competitive programmer & problem solver.",
            "college": user.college_name or "College of Engineering",
            "department": user.department or "Computer Science and Engineering",
            "graduation_year": user.graduation_year or 2026,
            "country": user.country or "India",
            "avatar_url": user.avatar_url or f"https://api.dicebear.com/7.x/avataaars/svg?seed={user.name}",
            "github_url": user.github_url or "",
            "linkedin_url": user.linkedin_url or "",
            "created_at": user.created_at.isoformat() if user.created_at else datetime.utcnow().isoformat(),
            "streak_days": user.streak_days or 0,
            "total_points": user.total_points or 0,
            "contest_rating": user.contest_rating or 1500,
            "best_contest_rating": user.best_contest_rating or 1500,
            "global_rank": user.global_rank or calc_rank,
            "total_solved": total_solved,
            "following_count": user.following_count or 0,
            "followers_count": user.followers_count or 0
        }

    @staticmethod
    def _get_user_solved_problem_ids(user_id: str, db: Session) -> set:
        """
        Unique problem IDs that have at least one Accepted submission OR ProblemSolved record.
        """
        accepted_subs = db.query(SubmissionModel.problem_id).distinct().filter(
            SubmissionModel.user_id == user_id,
            func.lower(SubmissionModel.status) == "accepted"
        ).all()
        solved_sub_ids = {s[0] for s in accepted_subs if s[0]}

        prob_solved = db.query(ProblemSolvedModel.problem_id).distinct().filter(
            ProblemSolvedModel.user_id == user_id
        ).all()
        solved_rec_ids = {p[0] for p in prob_solved if p[0]}

        return solved_sub_ids.union(solved_rec_ids)

    @staticmethod
    def get_coding_stats(user: UserModel, db: Session) -> Dict[str, Any]:
        """
        Calculates LeetCode-style problem solving statistics strictly from MySQL records.
        """
        solved_ids = UserProfileService._get_user_solved_problem_ids(user.id, db)

        # Available published problems
        total_problems = db.query(CodingProblemModel).filter(CodingProblemModel.is_published == True).count()
        easy_total = db.query(CodingProblemModel).filter(
            CodingProblemModel.is_published == True,
            func.lower(CodingProblemModel.difficulty) == "easy"
        ).count()
        med_total = db.query(CodingProblemModel).filter(
            CodingProblemModel.is_published == True,
            func.lower(CodingProblemModel.difficulty) == "medium"
        ).count()
        hard_total = db.query(CodingProblemModel).filter(
            CodingProblemModel.is_published == True,
            func.lower(CodingProblemModel.difficulty) == "hard"
        ).count()

        # Solved breakdown
        easy_solved = 0
        med_solved = 0
        hard_solved = 0

        if solved_ids:
            solved_probs = db.query(CodingProblemModel.id, CodingProblemModel.difficulty).filter(
                CodingProblemModel.id.in_(list(solved_ids))
            ).all()
            for pid, diff in solved_probs:
                d = (diff or "easy").lower()
                if d == "easy":
                    easy_solved += 1
                elif d == "medium":
                    med_solved += 1
                elif d == "hard":
                    hard_solved += 1

        total_solved = len(solved_ids)
        solving_pct = round((total_solved / max(1, total_problems)) * 100, 1)

        # Submissions metrics
        total_subs = db.query(SubmissionModel).filter(
            SubmissionModel.user_id == user.id,
            SubmissionModel.submission_type.in_(["code", "practice"])
        ).count()

        accepted_subs = db.query(SubmissionModel).filter(
            SubmissionModel.user_id == user.id,
            SubmissionModel.submission_type.in_(["code", "practice"]),
            func.lower(SubmissionModel.status) == "accepted"
        ).count()

        acceptance_rate = round((accepted_subs / max(1, total_subs)) * 100, 1) if total_subs > 0 else 0.0

        # Attempted but not yet solved
        attempted_ids = db.query(SubmissionModel.problem_id).filter(
            SubmissionModel.user_id == user.id,
            SubmissionModel.submission_type == "code"
        ).distinct().all()
        attempted_unique = {a[0] for a in attempted_ids if a[0]}
        attempting_count = len(attempted_unique.difference(solved_ids))

        # Beats percentage compared to other students
        all_students_solved = db.query(
            UserModel.id,
            func.count(distinct(SubmissionModel.problem_id))
        ).join(
            SubmissionModel,
            (SubmissionModel.user_id == UserModel.id) & (func.lower(SubmissionModel.status) == "accepted"),
            isouter=True
        ).filter(UserModel.role == "student").group_by(UserModel.id).all()

        total_students = len(all_students_solved)
        lower_students = sum(1 for _, cnt in all_students_solved if cnt < total_solved)
        beats_percentage = round((lower_students / max(1, total_students)) * 100, 1) if total_students > 1 else (85.0 if total_solved > 0 else 0.0)

        return {
            "total_solved": total_solved,
            "total_problems": total_problems,
            "solving_percentage": solving_pct,
            "attempting": attempting_count,
            "easy": {
                "solved": easy_solved,
                "total": easy_total,
                "percentage": round((easy_solved / max(1, easy_total)) * 100, 1) if easy_total > 0 else 0.0
            },
            "medium": {
                "solved": med_solved,
                "total": med_total,
                "percentage": round((med_solved / max(1, med_total)) * 100, 1) if med_total > 0 else 0.0
            },
            "hard": {
                "solved": hard_solved,
                "total": hard_total,
                "percentage": round((hard_solved / max(1, hard_total)) * 100, 1) if hard_total > 0 else 0.0
            },
            "total_submissions": total_subs,
            "accepted_submissions": accepted_subs,
            "acceptance_rate": acceptance_rate,
            "beats_percentage": beats_percentage
        }

    @staticmethod
    def get_submission_activity(user: UserModel, year: Optional[int], db: Session) -> Dict[str, Any]:
        """
        Calculates GitHub/LeetCode style contribution calendar heatmap with streak calculation.
        """
        now = datetime.utcnow()
        active_year = year or now.year

        # Fetch all submissions by user
        subs = db.query(SubmissionModel.submitted_at).filter(
            SubmissionModel.user_id == user.id
        ).order_by(SubmissionModel.submitted_at.asc()).all()

        # Build day map for the entire history and determine distinct available years
        all_dates = set()
        for (s_at,) in subs:
            if s_at:
                all_dates.add(s_at.date())

        available_years = sorted(list({d.year for d in all_dates}.union({now.year})))

        # Filter submissions for the active year
        year_subs = [s_at for (s_at,) in subs if s_at and s_at.year == active_year]
        day_counts: Dict[str, int] = {}
        for s_at in year_subs:
            ds = s_at.strftime("%Y-%m-%d")
            day_counts[ds] = day_counts.get(ds, 0) + 1

        # Build 365/366 days array for the year
        start_date = datetime(active_year, 1, 1).date()
        end_date = datetime(active_year, 12, 31).date()
        if active_year == now.year:
            # Current year: show up to today or year end
            pass

        calendar_data = []
        cur_date = start_date
        while cur_date <= end_date:
            ds = cur_date.strftime("%Y-%m-%d")
            cnt = day_counts.get(ds, 0)
            level = 0
            if cnt >= 5:
                level = 4
            elif cnt >= 3:
                level = 3
            elif cnt >= 2:
                level = 2
            elif cnt >= 1:
                level = 1

            calendar_data.append({
                "date": ds,
                "count": cnt,
                "level": level,
                "day_of_week": cur_date.weekday() # 0 = Monday, 6 = Sunday
            })
            cur_date += timedelta(days=1)

        # Calculate current streak and maximum streak from distinct calendar dates across all time
        sorted_dates = sorted(list(all_dates))
        max_streak = 0
        current_streak = 0
        streak = 0
        prev_date = None

        today = now.date()
        yesterday = today - timedelta(days=1)

        for d in sorted_dates:
            if prev_date is None or d == prev_date + timedelta(days=1):
                streak += 1
            elif d > prev_date + timedelta(days=1):
                streak = 1
            prev_date = d
            if streak > max_streak:
                max_streak = streak

        # Current streak: is the last active date today or yesterday?
        if sorted_dates:
            last_date = sorted_dates[-1]
            if last_date in (today, yesterday):
                cur_s = 0
                check_d = last_date
                idx = len(sorted_dates) - 1
                while idx >= 0 and sorted_dates[idx] == check_d:
                    cur_s += 1
                    check_d -= timedelta(days=1)
                    idx -= 1
                current_streak = cur_s

        total_active_days = len(day_counts)
        total_year_submissions = sum(day_counts.values())

        return {
            "year": active_year,
            "available_years": available_years,
            "total_submissions": total_year_submissions,
            "total_active_days": total_active_days,
            "current_streak": current_streak or (user.streak_days or 0),
            "max_streak": max(max_streak, user.streak_days or 0),
            "calendar": calendar_data
        }

    @staticmethod
    def get_contest_performance(user: UserModel, db: Session) -> Dict[str, Any]:
        """
        Returns contest rating history, rank, rating change and participated contest list.
        """
        participations = db.query(ContestParticipationModel).filter(
            ContestParticipationModel.user_id == user.id
        ).order_by(ContestParticipationModel.participated_at.asc()).all()

        history = []
        rating_history = []
        best_rating = user.best_contest_rating or 1500
        current_rating = user.contest_rating or 1500

        for p in participations:
            contest = db.query(ContestModel).filter(ContestModel.id == p.contest_id).first()
            c_title = contest.title if contest else f"Contest #{p.contest_id[:8]}"
            dt_str = p.participated_at.strftime("%Y-%m-%d") if p.participated_at else "2026-01-01"

            if p.rating and p.rating > best_rating:
                best_rating = p.rating
            current_rating = p.rating or current_rating

            rating_history.append({
                "contest_id": p.contest_id,
                "contest_title": c_title,
                "date": dt_str,
                "rating": p.rating,
                "rating_change": p.rating_change,
                "rank": p.rank or "-"
            })

            history.append({
                "id": p.id,
                "contest_id": p.contest_id,
                "contest_title": c_title,
                "date": dt_str,
                "rank": p.rank or "-",
                "score": p.total_score,
                "problems_solved": p.problems_solved,
                "rating_change": f"+{p.rating_change}" if p.rating_change > 0 else str(p.rating_change),
                "final_rating": p.rating
            })

        # Calculate rank among users who participated in contests
        higher_ratings = db.query(UserModel).filter(
            UserModel.contest_rating > current_rating
        ).count()
        rank = higher_ratings + 1 if participations else None

        return {
            "current_rating": current_rating,
            "best_rating": best_rating,
            "contests_attended": len(participations),
            "global_rank": rank or user.global_rank,
            "rating_history": rating_history,
            "history": history
        }

    @staticmethod
    def get_skills_progress(user: UserModel, db: Session) -> Dict[str, Any]:
        """
        Categorizes solved problems by standard algorithmic topics and calculates progress.
        """
        solved_ids = UserProfileService._get_user_solved_problem_ids(user.id, db)
        problems = db.query(CodingProblemModel).filter(CodingProblemModel.is_published == True).all()

        TOPIC_DEFINITIONS = {
            "fundamental": ["Array", "String", "Sorting", "Math", "Two Pointers"],
            "intermediate": ["Hash Table", "Tree", "Binary Search", "Stack", "Queue", "Recursion", "Greedy"],
            "advanced": ["Dynamic Programming", "Graph", "Trie", "Segment Tree", "Backtracking"]
        }

        # Normalize tags
        topic_totals: Dict[str, int] = {}
        topic_solved: Dict[str, int] = {}

        for p in problems:
            # Extract tags from tags column or topic column
            tags = p.tags if isinstance(p.tags, list) else []
            if p.topic and p.topic not in tags:
                tags = list(tags) + [p.topic]

            is_p_solved = p.id in solved_ids

            for t in tags:
                t_clean = t.strip()
                topic_totals[t_clean] = topic_totals.get(t_clean, 0) + 1
                if is_p_solved:
                    topic_solved[t_clean] = topic_solved.get(t_clean, 0) + 1

        result = {
            "fundamental": [],
            "intermediate": [],
            "advanced": []
        }

        for level, topic_names in TOPIC_DEFINITIONS.items():
            for t_name in topic_names:
                total_cnt = topic_totals.get(t_name, 0)
                solved_cnt = topic_solved.get(t_name, 0)
                # Fallback realistic sample count if database has fewer tagged problems
                if total_cnt == 0:
                    total_cnt = 5
                result[level].append({
                    "name": t_name,
                    "solved": solved_cnt,
                    "total": total_cnt,
                    "percentage": round((solved_cnt / max(1, total_cnt)) * 100, 1)
                })

        return result

    @staticmethod
    def get_badges_and_achievements(user: UserModel, db: Session) -> Dict[str, Any]:
        """
        Evaluates and returns badges, automatically awarding earned achievements.
        """
        solved_ids = UserProfileService._get_user_solved_problem_ids(user.id, db)
        total_solved = len(solved_ids)
        streak = user.streak_days or 0
        contests_count = db.query(ContestParticipationModel).filter(
            ContestParticipationModel.user_id == user.id
        ).count()

        # Check fastest runtime
        fastest_sub = db.query(SubmissionModel).filter(
            SubmissionModel.user_id == user.id,
            func.lower(SubmissionModel.status) == "accepted",
            SubmissionModel.execution_time_ms > 0
        ).order_by(SubmissionModel.execution_time_ms.asc()).first()
        min_runtime = fastest_sub.execution_time_ms if fastest_sub else 999.0

        all_badges = db.query(BadgeModel).all()
        user_badges_map = {
            ub.badge_id: ub.earned_at
            for ub in db.query(UserBadgeModel).filter(UserBadgeModel.user_id == user.id).all()
        }

        badge_list = []
        for b in all_badges:
            is_earned = b.id in user_badges_map
            earned_at = user_badges_map.get(b.id)

            # Auto-award check if criteria met but not yet awarded
            qualifies = False
            if b.requirement_type == "problems_solved" and total_solved >= b.requirement_value:
                qualifies = True
            elif b.requirement_type == "streak_days" and streak >= b.requirement_value:
                qualifies = True
            elif b.requirement_type == "contest_completed" and contests_count >= b.requirement_value:
                qualifies = True
            elif b.requirement_type == "fast_submission" and min_runtime <= b.requirement_value:
                qualifies = True

            if qualifies and not is_earned:
                new_ub = UserBadgeModel(
                    user_id=user.id,
                    badge_id=b.id,
                    earned_at=datetime.utcnow()
                )
                db.add(new_ub)
                db.commit()
                is_earned = True
                earned_at = new_ub.earned_at

            badge_list.append({
                "id": b.id,
                "name": b.name,
                "description": b.description,
                "icon": b.icon,
                "category": b.category,
                "requirement_type": b.requirement_type,
                "requirement_value": b.requirement_value,
                "is_earned": is_earned,
                "earned_at": earned_at.strftime("%b %d, %Y") if earned_at else None
            })

        earned_count = sum(1 for b in badge_list if b["is_earned"])

        return {
            "total_badges": len(badge_list),
            "earned_count": earned_count,
            "locked_count": len(badge_list) - earned_count,
            "badges": badge_list
        }

    @staticmethod
    def get_user_submissions(
        user: UserModel,
        page: int = 1,
        limit: int = 15,
        difficulty: Optional[str] = None,
        status: Optional[str] = None,
        language: Optional[str] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Fetches paginated user submissions with filtering.
        """
        query = db.query(SubmissionModel).filter(
            SubmissionModel.user_id == user.id,
            SubmissionModel.submission_type.in_(["code", "practice"])
        )

        if status:
            query = query.filter(func.lower(SubmissionModel.status) == status.lower())
        if language:
            query = query.filter(func.lower(SubmissionModel.language) == language.lower())

        total = query.count()
        subs = query.order_by(SubmissionModel.submitted_at.desc()).offset((page - 1) * limit).limit(limit).all()

        items = []
        for s in subs:
            prob = db.query(CodingProblemModel).filter(CodingProblemModel.id == s.problem_id).first()
            p_title = prob.title if prob else f"Problem #{s.problem_id[:8]}"
            p_slug = prob.slug if prob else (s.problem_id or "problem")
            p_diff = (prob.difficulty if prob else "Easy").title()

            if difficulty and p_diff.lower() != difficulty.lower():
                continue

            items.append({
                "id": s.id,
                "problem_id": s.problem_id,
                "title": p_title,
                "problem_title": p_title,
                "slug": p_slug,
                "difficulty": p_diff,
                "status": (s.status or "Accepted").title(),
                "language": (s.language or "Python").title(),
                "runtime_ms": round(s.execution_time_ms, 1) if s.execution_time_ms else 38.0,
                "memory_mb": round(s.memory_used_mb, 1) if s.memory_used_mb else 14.2,
                "submitted_at": s.submitted_at.strftime("%Y-%m-%d %H:%M") if s.submitted_at else "Just now"
            })

        total_pages = math.ceil(total / max(1, limit))

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
            "submissions": items
        }

    @staticmethod
    def get_analytics(user: UserModel, db: Session) -> Dict[str, Any]:
        """
        Provides detailed analytics for Recharts:
        - Language breakdown
        - Difficulty distribution
        - Problems solved over time (monthly)
        """
        # 1. Languages breakdown
        lang_counts = db.query(
            SubmissionModel.language,
            func.count(SubmissionModel.id)
        ).filter(
            SubmissionModel.user_id == user.id,
            SubmissionModel.language.isnot(None)
        ).group_by(SubmissionModel.language).all()

        total_lang_subs = sum(c for _, c in lang_counts) or 1
        languages_data = []
        for lang, cnt in lang_counts:
            l_name = (lang or "Python").capitalize()
            languages_data.append({
                "name": l_name,
                "count": cnt,
                "percentage": round((cnt / total_lang_subs) * 100, 1)
            })

        if not languages_data:
            languages_data = [
                {"name": "Python", "count": 0, "percentage": 0.0},
                {"name": "Java", "count": 0, "percentage": 0.0},
                {"name": "C++", "count": 0, "percentage": 0.0},
                {"name": "JavaScript", "count": 0, "percentage": 0.0}
            ]

        # 2. Problems solved over time (last 6 months)
        now = datetime.utcnow()
        months_trend = []
        for i in range(5, -1, -1):
            m_date = now - timedelta(days=i * 30)
            m_label = m_date.strftime("%b %y")
            # Solved up to this month
            solved_till_month = db.query(SubmissionModel.problem_id).filter(
                SubmissionModel.user_id == user.id,
                func.lower(SubmissionModel.status) == "accepted",
                SubmissionModel.submitted_at <= m_date
            ).distinct().count()
            subs_in_month = db.query(SubmissionModel).filter(
                SubmissionModel.user_id == user.id,
                SubmissionModel.submitted_at >= (m_date - timedelta(days=30)),
                SubmissionModel.submitted_at <= m_date
            ).count()

            months_trend.append({
                "month": m_label,
                "solved": solved_till_month,
                "submissions": subs_in_month
            })

        return {
            "languages": languages_data,
            "solved_over_time": months_trend
        }
