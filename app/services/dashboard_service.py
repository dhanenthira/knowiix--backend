from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, desc
from fastapi import HTTPException, status

from app.models.category import CategoryModel
from app.models.tutorial import TutorialModel
from app.models.topic import TopicModel
from app.models.progress import UserProgressModel
from app.models.bookmark import BookmarkModel
from app.models.activity import LearningActivityModel
from app.models.sql_models import UserModel
from app.schemas.dashboard import DashboardSummaryResponse
from app.schemas.category import CategoryResponse
from app.schemas.tutorial import TutorialResponse, TopicResponse, ContinueLearningItem
from app.schemas.bookmark import BookmarkResponse
from app.schemas.progress import TopicProgressResponse, UserProgressSummary, LearningActivityResponse


class DashboardService:
    @staticmethod
    def get_dashboard_summary(user_id: str, db: Session) -> DashboardSummaryResponse:
        """
        Calculates all dashboard metrics strictly from database records:
        - Available Courses (count of published tutorials)
        - Courses Started (distinct tutorials with at least one user progress record)
        - Completed Lessons (distinct topics completed by this user)
        - Saved Tutorials (distinct bookmarks for this user)
        - Overall Progress (completed lessons / total available topics * 100)
        """
        # 1. Total published tutorials
        available_courses = db.query(func.count(TutorialModel.id)).filter(
            TutorialModel.is_published == True
        ).scalar() or 0

        # 2. Total published topics
        total_available_topics = db.query(func.count(TopicModel.id)).join(
            TutorialModel, TopicModel.tutorial_id == TutorialModel.id
        ).filter(TutorialModel.is_published == True).scalar() or 0

        # 3. Courses started by user (distinct tutorials with any progress)
        courses_started = db.query(func.count(distinct(TopicModel.tutorial_id))).join(
            UserProgressModel, TopicModel.id == UserProgressModel.topic_id
        ).filter(
            UserProgressModel.user_id == user_id
        ).scalar() or 0

        # 4. Completed lessons for user
        completed_lessons = db.query(func.count(distinct(UserProgressModel.topic_id))).filter(
            UserProgressModel.user_id == user_id,
            UserProgressModel.is_completed == True
        ).scalar() or 0

        # 5. Saved tutorials (bookmarks)
        saved_tutorials = db.query(func.count(BookmarkModel.id)).filter(
            BookmarkModel.user_id == user_id
        ).scalar() or 0

        # 6. Overall progress formula
        if total_available_topics > 0:
            overall_progress = round((completed_lessons / total_available_topics) * 100.0, 1)
        else:
            overall_progress = 0.0

        return DashboardSummaryResponse(
            available_courses=available_courses,
            courses_started=courses_started,
            completed_lessons=completed_lessons,
            saved_tutorials=saved_tutorials,
            overall_progress_percentage=overall_progress,
            total_available_topics=total_available_topics
        )

    @staticmethod
    def get_categories(db: Session) -> List[CategoryResponse]:
        """
        Retrieves active categories with their published tutorial count, ordered by display_order.
        """
        categories = db.query(CategoryModel).filter(
            CategoryModel.is_active == True
        ).order_by(CategoryModel.display_order.asc(), CategoryModel.name.asc()).all()

        results = []
        for cat in categories:
            t_count = db.query(func.count(TutorialModel.id)).filter(
                TutorialModel.category_id == cat.id,
                TutorialModel.is_published == True
            ).scalar() or 0

            results.append(CategoryResponse(
                id=cat.id,
                name=cat.name,
                slug=cat.slug,
                description=cat.description or "",
                icon=cat.icon or "code",
                display_order=cat.display_order,
                is_active=cat.is_active,
                tutorial_count=t_count
            ))
        return results

    @staticmethod
    def get_continue_learning(user_id: str, db: Session, limit: int = 5) -> List[ContinueLearningItem]:
        """
        Retrieves recently accessed tutorials for the user, calculating exact progress
        and identifying the resume topic and link.
        """
        # Find tutorials that have progress records for this user, ordered by most recent access
        subquery = db.query(
            TopicModel.tutorial_id,
            func.max(UserProgressModel.last_read_at).label("latest_read")
        ).join(
            UserProgressModel, TopicModel.id == UserProgressModel.topic_id
        ).filter(
            UserProgressModel.user_id == user_id
        ).group_by(TopicModel.tutorial_id).subquery()

        recent_tutorials = db.query(TutorialModel, subquery.c.latest_read).join(
            subquery, TutorialModel.id == subquery.c.tutorial_id
        ).filter(
            TutorialModel.is_published == True
        ).order_by(desc(subquery.c.latest_read)).limit(limit).all()

        items = []
        for tut, latest_read in recent_tutorials:
            category = tut.category
            cat_name = category.name if category else "General"
            cat_slug = category.slug if category else "general"
            cat_icon = category.icon if category else "code"

            # Count total topics
            total_topics = db.query(func.count(TopicModel.id)).filter(
                TopicModel.tutorial_id == tut.id
            ).scalar() or 0

            # Count completed topics
            completed_topics = db.query(func.count(TopicModel.id)).join(
                UserProgressModel, TopicModel.id == UserProgressModel.topic_id
            ).filter(
                TopicModel.tutorial_id == tut.id,
                UserProgressModel.user_id == user_id,
                UserProgressModel.is_completed == True
            ).scalar() or 0

            progress_pct = round((completed_topics / total_topics * 100.0), 1) if total_topics > 0 else 0.0

            # Find the most recently accessed topic or first incomplete topic
            recent_progress = db.query(UserProgressModel).join(
                TopicModel, UserProgressModel.topic_id == TopicModel.id
            ).filter(
                TopicModel.tutorial_id == tut.id,
                UserProgressModel.user_id == user_id
            ).order_by(UserProgressModel.last_read_at.desc()).first()

            resume_topic = None
            if recent_progress:
                resume_topic = db.query(TopicModel).filter(TopicModel.id == recent_progress.topic_id).first()

            # If recent topic is completed, find next incomplete topic
            if resume_topic and recent_progress.is_completed:
                next_incomplete = db.query(TopicModel).outerjoin(
                    UserProgressModel,
                    (TopicModel.id == UserProgressModel.topic_id) & (UserProgressModel.user_id == user_id)
                ).filter(
                    TopicModel.tutorial_id == tut.id,
                    (UserProgressModel.is_completed == False) | (UserProgressModel.is_completed == None)
                ).order_by(TopicModel.display_order.asc()).first()
                if next_incomplete:
                    resume_topic = next_incomplete

            if not resume_topic:
                resume_topic = db.query(TopicModel).filter(
                    TopicModel.tutorial_id == tut.id
                ).order_by(TopicModel.display_order.asc()).first()

            resume_route = f"/learning?tutorial={tut.slug}&topic={resume_topic.id if resume_topic else ''}"

            items.append(ContinueLearningItem(
                tutorial_id=tut.id,
                tutorial_title=tut.title,
                tutorial_slug=tut.slug,
                category_name=cat_name,
                category_slug=cat_slug,
                category_icon=cat_icon,
                total_topics=total_topics,
                completed_topics=completed_topics,
                progress_percentage=progress_pct,
                last_accessed_at=latest_read or datetime.utcnow(),
                last_topic_id=resume_topic.id if resume_topic else None,
                last_topic_title=resume_topic.title if resume_topic else None,
                resume_route=resume_route
            ))

        return items

    @staticmethod
    def get_recommended_tutorials(user_id: str, db: Session, limit: int = 6) -> List[TutorialResponse]:
        """
        Recommends tutorials matching the user's active categories, falling back to beginner tutorials.
        Excludes completely finished tutorials when other tutorials are available.
        """
        # Find categories the user has interacted with
        active_cat_ids = [
            row[0] for row in db.query(distinct(TutorialModel.category_id)).join(
                TopicModel, TutorialModel.id == TopicModel.tutorial_id
            ).join(
                UserProgressModel, TopicModel.id == UserProgressModel.topic_id
            ).filter(UserProgressModel.user_id == user_id).all()
        ]

        query = db.query(TutorialModel).filter(TutorialModel.is_published == True)
        all_tutorials = query.all()

        recommended = []
        for tut in all_tutorials:
            # Calculate user's progress on this tutorial
            total_topics = db.query(func.count(TopicModel.id)).filter(
                TopicModel.tutorial_id == tut.id
            ).scalar() or 0

            completed_topics = db.query(func.count(TopicModel.id)).join(
                UserProgressModel, TopicModel.id == UserProgressModel.topic_id
            ).filter(
                TopicModel.tutorial_id == tut.id,
                UserProgressModel.user_id == user_id,
                UserProgressModel.is_completed == True
            ).scalar() or 0

            progress_pct = round((completed_topics / total_topics * 100.0), 1) if total_topics > 0 else 0.0

            # If user has completed 100% of this tutorial and other uncompleted tutorials exist, de-prioritize
            is_completed = total_topics > 0 and completed_topics >= total_topics

            # Check bookmark status
            is_bm = db.query(BookmarkModel).filter(
                BookmarkModel.user_id == user_id,
                BookmarkModel.tutorial_id == tut.id
            ).first() is not None

            category = tut.category
            cat_name = category.name if category else "General"
            cat_slug = category.slug if category else "general"
            cat_icon = category.icon if category else "code"

            score = 0
            if tut.category_id in active_cat_ids:
                score += 50
            if tut.difficulty.lower() == "beginner":
                score += 30
            elif tut.difficulty.lower() == "intermediate":
                score += 20
            if is_completed:
                score -= 100 # Put already completed tutorials at the end

            resp = TutorialResponse(
                id=tut.id,
                category_id=tut.category_id,
                title=tut.title,
                slug=tut.slug,
                description=tut.description or "",
                difficulty=tut.difficulty,
                estimated_minutes=tut.estimated_minutes,
                is_published=tut.is_published,
                created_at=tut.created_at,
                category_name=cat_name,
                category_slug=cat_slug,
                category_icon=cat_icon,
                total_topics=total_topics,
                completed_topics=completed_topics,
                progress_percentage=progress_pct,
                is_bookmarked=is_bm
            )
            recommended.append((score, resp))

        # Sort by recommendation score descending
        recommended.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in recommended[:limit]]

    @staticmethod
    def get_bookmarks(user_id: str, db: Session) -> List[BookmarkResponse]:
        """
        Retrieves all bookmarked tutorials belonging exclusively to the current user.
        """
        bms = db.query(BookmarkModel).filter(
            BookmarkModel.user_id == user_id
        ).order_by(BookmarkModel.created_at.desc()).all()

        results = []
        for bm in bms:
            tut = bm.tutorial
            if not tut or not tut.is_published:
                continue

            total_topics = db.query(func.count(TopicModel.id)).filter(
                TopicModel.tutorial_id == tut.id
            ).scalar() or 0

            completed_topics = db.query(func.count(TopicModel.id)).join(
                UserProgressModel, TopicModel.id == UserProgressModel.topic_id
            ).filter(
                TopicModel.tutorial_id == tut.id,
                UserProgressModel.user_id == user_id,
                UserProgressModel.is_completed == True
            ).scalar() or 0

            progress_pct = round((completed_topics / total_topics * 100.0), 1) if total_topics > 0 else 0.0
            category = tut.category

            tut_resp = TutorialResponse(
                id=tut.id,
                category_id=tut.category_id,
                title=tut.title,
                slug=tut.slug,
                description=tut.description or "",
                difficulty=tut.difficulty,
                estimated_minutes=tut.estimated_minutes,
                is_published=tut.is_published,
                created_at=tut.created_at,
                category_name=category.name if category else "General",
                category_slug=category.slug if category else "general",
                category_icon=category.icon if category else "code",
                total_topics=total_topics,
                completed_topics=completed_topics,
                progress_percentage=progress_pct,
                is_bookmarked=True
            )

            results.append(BookmarkResponse(
                id=bm.id,
                user_id=bm.user_id,
                tutorial_id=bm.tutorial_id,
                created_at=bm.created_at,
                tutorial=tut_resp
            ))
        return results

    @staticmethod
    def add_bookmark(user_id: str, tutorial_id: str, db: Session) -> Dict[str, Any]:
        """
        Bookmarks a tutorial for the current user and logs activity.
        """
        tutorial = db.query(TutorialModel).filter(
            TutorialModel.id == tutorial_id,
            TutorialModel.is_published == True
        ).first()

        if not tutorial:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tutorial not found or not published")

        existing = db.query(BookmarkModel).filter(
            BookmarkModel.user_id == user_id,
            BookmarkModel.tutorial_id == tutorial_id
        ).first()

        if existing:
            return {"status": "success", "message": "Already bookmarked", "bookmark_id": existing.id}

        new_bm = BookmarkModel(user_id=user_id, tutorial_id=tutorial_id)
        db.add(new_bm)

        # Log activity
        activity = LearningActivityModel(
            user_id=user_id,
            tutorial_id=tutorial_id,
            activity_type="bookmarked"
        )
        db.add(activity)

        db.commit()
        db.refresh(new_bm)
        return {"status": "success", "message": "Tutorial saved to bookmarks", "bookmark_id": new_bm.id}

    @staticmethod
    def remove_bookmark(user_id: str, tutorial_id: str, db: Session) -> Dict[str, Any]:
        """
        Removes a bookmark for the current user and logs activity.
        """
        existing = db.query(BookmarkModel).filter(
            BookmarkModel.user_id == user_id,
            BookmarkModel.tutorial_id == tutorial_id
        ).first()

        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")

        db.delete(existing)

        # Log activity
        activity = LearningActivityModel(
            user_id=user_id,
            tutorial_id=tutorial_id,
            activity_type="removed_bookmark"
        )
        db.add(activity)

        db.commit()
        return {"status": "success", "message": "Bookmark removed"}

    @staticmethod
    def complete_topic(user_id: str, topic_id: str, db: Session) -> Dict[str, Any]:
        """
        Marks a topic completed for the user, preventing duplicates, saving timestamp,
        recording learning activity and awarding points.
        """
        topic = db.query(TopicModel).filter(TopicModel.id == topic_id).first()
        if not topic:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

        progress = db.query(UserProgressModel).filter(
            UserProgressModel.user_id == user_id,
            UserProgressModel.topic_id == topic_id
        ).first()

        is_first_completion = False
        if not progress:
            progress = UserProgressModel(
                user_id=user_id,
                topic_id=topic_id,
                is_completed=True,
                last_read_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            )
            db.add(progress)
            is_first_completion = True
        else:
            if not progress.is_completed:
                is_first_completion = True
            progress.is_completed = True
            progress.completed_at = datetime.utcnow()
            progress.last_read_at = datetime.utcnow()

        # Record activity
        activity = LearningActivityModel(
            user_id=user_id,
            tutorial_id=topic.tutorial_id,
            topic_id=topic_id,
            activity_type="completed_topic"
        )
        db.add(activity)

        # Award points to student if newly completed
        if is_first_completion:
            user = db.query(UserModel).filter(UserModel.id == user_id).first()
            if user:
                user.total_points = (user.total_points or 0) + 20

        db.commit()
        db.refresh(progress)
        return {
            "status": "success",
            "message": "Topic completed successfully",
            "topic_id": topic_id,
            "is_completed": True,
            "completed_at": progress.completed_at.isoformat() if progress.completed_at else None
        }

    @staticmethod
    def record_topic_access(user_id: str, topic_id: str, db: Session) -> None:
        """
        Updates last_read_at and logs viewed_topic activity when a user accesses a topic.
        """
        topic = db.query(TopicModel).filter(TopicModel.id == topic_id).first()
        if not topic:
            return

        progress = db.query(UserProgressModel).filter(
            UserProgressModel.user_id == user_id,
            UserProgressModel.topic_id == topic_id
        ).first()

        if not progress:
            progress = UserProgressModel(
                user_id=user_id,
                topic_id=topic_id,
                is_completed=False,
                last_read_at=datetime.utcnow()
            )
            db.add(progress)
        else:
            progress.last_read_at = datetime.utcnow()

        # Record activity
        activity = LearningActivityModel(
            user_id=user_id,
            tutorial_id=topic.tutorial_id,
            topic_id=topic_id,
            activity_type="viewed_topic"
        )
        db.add(activity)
        db.commit()

    @staticmethod
    def get_user_progress(user_id: str, db: Session) -> UserProgressSummary:
        """
        Retrieves user's completed and in-progress topics with progress statistics.
        """
        total_available = db.query(func.count(TopicModel.id)).join(
            TutorialModel, TopicModel.tutorial_id == TutorialModel.id
        ).filter(TutorialModel.is_published == True).scalar() or 0

        progress_records = db.query(UserProgressModel, TopicModel, TutorialModel).join(
            TopicModel, UserProgressModel.topic_id == TopicModel.id
        ).join(
            TutorialModel, TopicModel.tutorial_id == TutorialModel.id
        ).filter(
            UserProgressModel.user_id == user_id
        ).order_by(UserProgressModel.last_read_at.desc()).all()

        completed_list = []
        in_progress_list = []

        for prog, top, tut in progress_records:
            item = TopicProgressResponse(
                id=prog.id,
                user_id=prog.user_id,
                topic_id=prog.topic_id,
                is_completed=prog.is_completed,
                last_read_at=prog.last_read_at,
                completed_at=prog.completed_at,
                reading_position=prog.reading_position,
                topic_title=top.title,
                tutorial_id=tut.id,
                tutorial_title=tut.title
            )
            if prog.is_completed:
                completed_list.append(item)
            else:
                in_progress_list.append(item)

        completed_count = len(completed_list)
        pct = round((completed_count / total_available * 100.0), 1) if total_available > 0 else 0.0

        return UserProgressSummary(
            total_available_topics=total_available,
            completed_topics_count=completed_count,
            overall_progress_percentage=pct,
            completed_topics=completed_list,
            in_progress_topics=in_progress_list
        )

    @staticmethod
    def get_recent_activity(user_id: str, db: Session, limit: int = 15) -> List[LearningActivityResponse]:
        """
        Retrieves learning activity for authenticated user, newest first.
        """
        activities = db.query(
            LearningActivityModel,
            TutorialModel.title.label("tutorial_title"),
            TopicModel.title.label("topic_title")
        ).outerjoin(
            TutorialModel, LearningActivityModel.tutorial_id == TutorialModel.id
        ).outerjoin(
            TopicModel, LearningActivityModel.topic_id == TopicModel.id
        ).filter(
            LearningActivityModel.user_id == user_id
        ).order_by(LearningActivityModel.created_at.desc()).limit(limit).all()

        results = []
        for act, tut_title, top_title in activities:
            results.append(LearningActivityResponse(
                id=str(act.id),
                user_id=act.user_id,
                tutorial_id=act.tutorial_id,
                topic_id=act.topic_id,
                activity_type=act.activity_type,
                created_at=act.created_at,
                tutorial_title=tut_title,
                topic_title=top_title
            ))
        return results
