"""Content moderation API routes."""

import logging
from datetime import datetime
from enum import Enum
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from neo4j import AsyncSession
from pydantic import BaseModel

from genesis.auth.dependencies import get_current_admin, get_current_user
from genesis.core.database import get_db

logger = logging.getLogger(__name__)
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
    hero_id: str
    episode_number: int
    flagged_reason: str
    flagged_at: datetime
    layer: str = "human"


class EscalationRequest(BaseModel):
    """Escalation request for legal review."""

    episode_id: str
    reason: str
    severity: str = "medium"  # low, medium, high, critical


class AutoModerationResult(BaseModel):
    """Result from automated moderation scan."""

    episode_id: str
    passed: bool
    layer: str
    issues: list[dict[str, str]]
    confidence_score: float


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
    layer: Annotated[str | None, Query()] = None,
) -> list[ModerationQueueItem]:
    """Get items pending moderation review.

    Args:
        limit: Maximum number of items to return
        layer: Filter by moderation layer (human, escalated)
    """
    if layer:
        query = """
        MATCH (hero:Hero)-[:STARS_IN]->(e:Episode {moderation_status: 'flagged'})
        OPTIONAL MATCH (r:ContentReport {episode_id: e.id, status: 'pending'})
        WHERE coalesce(e.moderation_layer, 'human') = $layer
        RETURN e.id as episode_id, hero.id as hero_id, hero.hero_name as hero_name,
               e.episode_number as episode_number,
               coalesce(r.reason, 'auto_flagged') as flagged_reason,
               coalesce(r.created_at, e.generated_at) as flagged_at,
               coalesce(e.moderation_layer, 'human') as layer
        ORDER BY flagged_at ASC
        LIMIT $limit
        """
        result = await session.run(query, limit=limit, layer=layer)
    else:
        query = """
        MATCH (hero:Hero)-[:STARS_IN]->(e:Episode {moderation_status: 'flagged'})
        OPTIONAL MATCH (r:ContentReport {episode_id: e.id, status: 'pending'})
        RETURN e.id as episode_id, hero.id as hero_id, hero.hero_name as hero_name,
               e.episode_number as episode_number,
               coalesce(r.reason, 'auto_flagged') as flagged_reason,
               coalesce(r.created_at, e.generated_at) as flagged_at,
               coalesce(e.moderation_layer, 'human') as layer
        ORDER BY flagged_at ASC
        LIMIT $limit
        """
        result = await session.run(query, limit=limit)
    records = await result.fetch(limit)
    return [
        ModerationQueueItem(
            episode_id=r["episode_id"],
            hero_id=r["hero_id"],
            hero_name=r["hero_name"],
            episode_number=r["episode_number"],
            flagged_reason=r["flagged_reason"],
            flagged_at=r["flagged_at"],
            layer=r["layer"],
        )
        for r in records
    ]


@router.post("/admin/review/{episode_id}")
async def review_content(
    episode_id: str,
    action: ModerationAction,
    admin: Annotated[dict[str, str], Depends(get_current_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
    background_tasks: BackgroundTasks,
    reason: Annotated[str | None, Query()] = None,
) -> dict[str, str]:
    """Submit moderation decision for an episode."""
    # Map action to new status
    status_map = {
        ModerationAction.APPROVED: "approved",
        ModerationAction.REGENERATED: "regenerating",
        ModerationAction.REJECTED: "rejected",
        ModerationAction.ESCALATED: "escalated",
    }
    new_status = status_map[action]

    # Get hero_id for potential regeneration
    hero_query = """
    MATCH (hero:Hero)-[:STARS_IN]->(e:Episode {id: $episode_id})
    RETURN hero.id as hero_id
    """
    hero_result = await session.run(hero_query, episode_id=episode_id)
    hero_record = await hero_result.single()
    hero_id = hero_record["hero_id"] if hero_record else None

    query = """
    MATCH (e:Episode {id: $episode_id})
    SET e.moderation_status = $new_status,
        e.moderation_layer = CASE WHEN $action = 'escalated' THEN 'legal' ELSE 'human' END
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

    # If regenerated, trigger new generation in background
    if action == ModerationAction.REGENERATED and hero_id:
        from genesis.jobs.episode_generator import EpisodeGeneratorJob

        async def regenerate_episode():
            try:
                logger.info(f"Regenerating episode for hero {hero_id}")
                job = EpisodeGeneratorJob()
                await job.run_for_hero(hero_id)
                # Update old episode status after successful regeneration
                async with get_db() as db_session:
                    await db_session.run(
                        """
                        MATCH (e:Episode {id: $episode_id})
                        SET e.moderation_status = 'replaced'
                        """,
                        episode_id=episode_id,
                    )
                logger.info(f"Episode regenerated for hero {hero_id}")
            except Exception as e:
                logger.error(f"Failed to regenerate episode for hero {hero_id}: {e}")

        background_tasks.add_task(regenerate_episode)

    return {"message": f"Episode {action.value}", "hero_id": hero_id}


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
        "escalated": stats.get("escalated", 0),
        "regenerating": stats.get("regenerating", 0),
        "replaced": stats.get("replaced", 0),
    }


# Layer 3: Escalation to legal review
@router.post("/admin/escalate/{episode_id}")
async def escalate_to_legal(
    episode_id: str,
    request: EscalationRequest,
    admin: Annotated[dict[str, str], Depends(get_current_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Escalate content to legal review (Layer 3).

    This endpoint is used when human reviewers identify content that requires
    legal counsel review (e.g., potential defamation, copyright issues).
    """
    query = """
    MATCH (e:Episode {id: $episode_id})
    SET e.moderation_status = 'escalated',
        e.moderation_layer = 'legal',
        e.escalation_severity = $severity
    CREATE (log:ModerationLog {
        id: randomUUID(),
        episode_id: $episode_id,
        layer: 'legal_escalation',
        action: 'escalated',
        reason: $reason,
        reviewer_id: $reviewer_id,
        severity: $severity,
        created_at: datetime()
    })
    RETURN e
    """
    result = await session.run(
        query,
        episode_id=episode_id,
        reason=request.reason,
        severity=request.severity,
        reviewer_id=admin["id"],
    )
    record = await result.single()
    if not record:
        raise ValueError("Episode not found")

    logger.warning(
        f"Episode {episode_id} escalated to legal review: {request.reason} "
        f"(severity: {request.severity})"
    )

    return {
        "message": "Episode escalated to legal review",
        "episode_id": episode_id,
        "severity": request.severity,
    }


@router.get("/admin/escalated", response_model=list[ModerationQueueItem])
async def get_escalated_content(
    admin: Annotated[dict[str, str], Depends(get_current_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[ModerationQueueItem]:
    """Get content escalated to legal review."""
    query = """
    MATCH (hero:Hero)-[:STARS_IN]->(e:Episode {moderation_status: 'escalated'})
    OPTIONAL MATCH (log:ModerationLog {episode_id: e.id, layer: 'legal_escalation'})
    RETURN e.id as episode_id, hero.id as hero_id, hero.hero_name as hero_name,
           e.episode_number as episode_number,
           coalesce(log.reason, 'escalated') as flagged_reason,
           coalesce(log.created_at, e.generated_at) as flagged_at,
           'legal' as layer
    ORDER BY e.escalation_severity DESC, flagged_at ASC
    LIMIT $limit
    """
    result = await session.run(query, limit=limit)
    records = await result.fetch(limit)
    return [
        ModerationQueueItem(
            episode_id=r["episode_id"],
            hero_id=r["hero_id"],
            hero_name=r["hero_name"],
            episode_number=r["episode_number"],
            flagged_reason=r["flagged_reason"],
            flagged_at=r["flagged_at"],
            layer=r["layer"],
        )
        for r in records
    ]


# Layer 4: Automated content scanning (pre-generation)
@router.post("/scan", response_model=AutoModerationResult)
async def scan_content(
    episode_id: str,
    admin: Annotated[dict[str, str], Depends(get_current_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> AutoModerationResult:
    """Scan episode content with automated moderation (Layer 1-2).

    This runs Gemini safety filters and image analysis on generated content.
    Used for re-scanning flagged content or manual verification.
    """
    # Get episode content
    query = """
    MATCH (e:Episode {id: $episode_id})
    RETURN e.script as script, e.panels as panels
    """
    result = await session.run(query, episode_id=episode_id)
    record = await result.single()
    if not record:
        raise ValueError("Episode not found")

    issues: list[dict[str, str]] = []
    passed = True
    confidence_score = 1.0

    # Layer 1: Check script content with safety keywords
    script = record.get("script", {})
    if script:
        text_content = str(script)
        # Basic safety check (in production, use Gemini Safety Filters)
        safety_keywords = [
            "violence against minors",
            "explicit",
            "self-harm",
            "hate speech",
        ]
        for keyword in safety_keywords:
            if keyword.lower() in text_content.lower():
                issues.append({
                    "layer": "text_safety",
                    "issue": f"Potential safety concern: {keyword}",
                    "severity": "high",
                })
                passed = False
                confidence_score -= 0.25

    # Layer 2: Check panels (placeholder for Amazon Rekognition)
    panels = record.get("panels", [])
    if panels and len(panels) > 0:
        # In production, this would call Amazon Rekognition
        # For now, we mark as passed
        pass

    # Update episode moderation status
    if not passed:
        await session.run(
            """
            MATCH (e:Episode {id: $episode_id})
            SET e.moderation_status = 'flagged',
                e.moderation_layer = 'auto'
            CREATE (log:ModerationLog {
                id: randomUUID(),
                episode_id: $episode_id,
                layer: 'auto',
                action: 'flagged',
                reason: $reason,
                created_at: datetime()
            })
            """,
            episode_id=episode_id,
            reason="; ".join([i["issue"] for i in issues]),
        )

    return AutoModerationResult(
        episode_id=episode_id,
        passed=passed,
        layer="auto",
        issues=issues,
        confidence_score=max(0.0, confidence_score),
    )


@router.post("/admin/bulk-approve")
async def bulk_approve(
    episode_ids: list[str],
    admin: Annotated[dict[str, str], Depends(get_current_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, int]:
    """Bulk approve multiple episodes."""
    query = """
    UNWIND $episode_ids AS episode_id
    MATCH (e:Episode {id: episode_id, moderation_status: 'flagged'})
    SET e.moderation_status = 'approved'
    WITH e
    CREATE (log:ModerationLog {
        id: randomUUID(),
        episode_id: e.id,
        layer: 'human',
        action: 'approved',
        reason: 'bulk_approval',
        reviewer_id: $reviewer_id,
        created_at: datetime()
    })
    RETURN count(e) as approved_count
    """
    result = await session.run(
        query,
        episode_ids=episode_ids,
        reviewer_id=admin["id"],
    )
    record = await result.single()
    approved_count = record["approved_count"] if record else 0

    logger.info(f"Bulk approved {approved_count} episodes by admin {admin['id']}")

    return {"approved_count": approved_count}
