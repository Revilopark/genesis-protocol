"""Content moderation API routes."""

from datetime import datetime
from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from neo4j import AsyncSession
from pydantic import BaseModel

from genesis.auth.dependencies import get_current_admin, get_current_user
from genesis.core.database import get_db

router = APIRouter()


class ReportReason(str, Enum):
    """Reason for reporting content."""

    INAPPROPRIATE = "inappropriate"
    BULLYING = "bullying"
    BUG = "bug"
    OTHER = "other"


class ModerationAction(str, Enum):
    """Moderation action taken."""

    APPROVED = "approved"
    REGENERATED = "regenerated"
    REJECTED = "rejected"
    ESCALATED = "escalated"


class ContentReport(BaseModel):
    """Content report model."""

    episode_id: str
    reason: ReportReason
    details: str | None = None


class ModerationLog(BaseModel):
    """Moderation log entry."""

    id: str
    episode_id: str
    layer: str
    action: ModerationAction
    reason: str | None
    reviewer_id: str | None
    created_at: datetime


class ModerationQueueItem(BaseModel):
    """Item in moderation review queue."""

    episode_id: str
    hero_name: str
    episode_number: int
    flagged_reason: str
    flagged_at: datetime


@router.post("/report", status_code=status.HTTP_201_CREATED)
async def report_content(
    report: ContentReport,
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Report inappropriate content."""
    query = """
    MATCH (e:Episode {id: $episode_id})
    CREATE (r:ContentReport {
        id: randomUUID(),
        episode_id: $episode_id,
        reported_by: $user_id,
        reason: $reason,
        details: $details,
        status: 'pending',
        created_at: datetime()
    })
    SET e.moderation_status = 'flagged'
    RETURN r
    """
    result = await session.run(
        query,
        episode_id=report.episode_id,
        user_id=current_user["id"],
        reason=report.reason.value,
        details=report.details,
    )
    record = await result.single()
    if not record:
        raise ValueError("Failed to create report")
    return {"message": "Report submitted", "report_id": record["r"]["id"]}


# Admin endpoints
@router.get("/admin/queue", response_model=list[ModerationQueueItem])
async def get_moderation_queue(
    admin: Annotated[dict[str, str], Depends(get_current_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[ModerationQueueItem]:
    """Get items pending moderation review."""
    query = """
    MATCH (hero:Hero)-[:STARS_IN]->(e:Episode {moderation_status: 'flagged'})
    OPTIONAL MATCH (r:ContentReport {episode_id: e.id, status: 'pending'})
    RETURN e.id as episode_id, hero.hero_name as hero_name,
           e.episode_number as episode_number,
           coalesce(r.reason, 'auto_flagged') as flagged_reason,
           coalesce(r.created_at, e.generated_at) as flagged_at
    ORDER BY flagged_at ASC
    LIMIT $limit
    """
    result = await session.run(query, limit=limit)
    records = await result.fetch(limit)
    return [
        ModerationQueueItem(
            episode_id=r["episode_id"],
            hero_name=r["hero_name"],
            episode_number=r["episode_number"],
            flagged_reason=r["flagged_reason"],
            flagged_at=r["flagged_at"],
        )
        for r in records
    ]


@router.post("/admin/review/{episode_id}")
async def review_content(
    episode_id: str,
    action: ModerationAction,
    admin: Annotated[dict[str, str], Depends(get_current_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
    reason: Annotated[str | None, Query()] = None,
) -> dict[str, str]:
    """Submit moderation decision for an episode."""
    # Map action to new status
    status_map = {
        ModerationAction.APPROVED: "approved",
        ModerationAction.REGENERATED: "pending",
        ModerationAction.REJECTED: "rejected",
        ModerationAction.ESCALATED: "flagged",
    }
    new_status = status_map[action]

    query = """
    MATCH (e:Episode {id: $episode_id})
    SET e.moderation_status = $new_status
    CREATE (log:ModerationLog {
        id: randomUUID(),
        episode_id: $episode_id,
        layer: 'human',
        action: $action,
        reason: $reason,
        reviewer_id: $reviewer_id,
        created_at: datetime()
    })
    WITH e
    OPTIONAL MATCH (r:ContentReport {episode_id: e.id, status: 'pending'})
    SET r.status = 'reviewed'
    RETURN e
    """
    result = await session.run(
        query,
        episode_id=episode_id,
        new_status=new_status,
        action=action.value,
        reason=reason,
        reviewer_id=admin["id"],
    )
    record = await result.single()
    if not record:
        raise ValueError("Episode not found")

    # If regenerated, trigger new generation
    if action == ModerationAction.REGENERATED:
        # TODO: Trigger content pipeline to regenerate
        pass

    return {"message": f"Episode {action.value}"}


@router.get("/admin/logs/{episode_id}", response_model=list[ModerationLog])
async def get_moderation_logs(
    episode_id: str,
    admin: Annotated[dict[str, str], Depends(get_current_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> list[ModerationLog]:
    """Get moderation history for an episode."""
    query = """
    MATCH (log:ModerationLog {episode_id: $episode_id})
    RETURN log
    ORDER BY log.created_at DESC
    """
    result = await session.run(query, episode_id=episode_id)
    records = await result.fetch(100)
    return [
        ModerationLog(
            id=r["log"]["id"],
            episode_id=r["log"]["episode_id"],
            layer=r["log"]["layer"],
            action=ModerationAction(r["log"]["action"]),
            reason=r["log"].get("reason"),
            reviewer_id=r["log"].get("reviewer_id"),
            created_at=r["log"]["created_at"],
        )
        for r in records
    ]


@router.get("/admin/stats")
async def get_moderation_stats(
    admin: Annotated[dict[str, str], Depends(get_current_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, int]:
    """Get moderation statistics."""
    query = """
    MATCH (e:Episode)
    RETURN e.moderation_status as status, count(e) as count
    """
    result = await session.run(query)
    records = await result.fetch(10)
    stats = {r["status"]: r["count"] for r in records}
    return {
        "pending": stats.get("pending", 0),
        "approved": stats.get("approved", 0),
        "flagged": stats.get("flagged", 0),
        "rejected": stats.get("rejected", 0),
    }
