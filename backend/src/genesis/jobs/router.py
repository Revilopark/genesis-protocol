"""Jobs router for Cloud Scheduler triggers."""

import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Header

from genesis.config import settings
from genesis.jobs.episode_generator import EpisodeGeneratorJob
from genesis.jobs.canon_updater import CanonUpdaterJob

logger = logging.getLogger(__name__)
router = APIRouter()


def verify_scheduler_token(x_cloudscheduler: str | None = Header(None)) -> None:
    """Verify the request comes from Cloud Scheduler.

    In production, this would verify a service account token or OIDC token.
    For development, we allow requests without the header.
    """
    if settings.environment == "production":
        if not x_cloudscheduler:
            raise HTTPException(status_code=403, detail="Forbidden")
        # Additional token verification would go here


@router.post("/generate-episodes")
async def trigger_episode_generation(
    background_tasks: BackgroundTasks,
    batch_size: int = 50,
    x_cloudscheduler: str | None = Header(None),
) -> dict[str, Any]:
    """Trigger daily episode generation for all active heroes.

    This endpoint is called by Cloud Scheduler daily (e.g., 2 AM UTC).

    Args:
        background_tasks: FastAPI background tasks
        batch_size: Number of heroes to process in parallel

    Returns:
        Job status and ID
    """
    verify_scheduler_token(x_cloudscheduler)

    logger.info("Episode generation job triggered")

    # Run in background for long-running job
    job = EpisodeGeneratorJob()

    async def run_job():
        result = await job.run(batch_size=batch_size)
        logger.info(f"Episode generation completed: {result}")

    background_tasks.add_task(run_job)

    return {
        "status": "started",
        "message": "Episode generation job started in background",
        "batch_size": batch_size,
    }


@router.post("/generate-episode/{hero_id}")
async def trigger_single_episode(
    hero_id: str,
    x_cloudscheduler: str | None = Header(None),
) -> dict[str, Any]:
    """Generate an episode for a specific hero.

    This endpoint can be used for:
    - Manual episode generation
    - Retry failed episode generation
    - New user first episode

    Args:
        hero_id: The hero's ID

    Returns:
        Generated episode data
    """
    verify_scheduler_token(x_cloudscheduler)

    logger.info(f"Single episode generation triggered for hero {hero_id}")

    job = EpisodeGeneratorJob()

    try:
        result = await job.run_for_hero(hero_id)
        return {
            "status": "completed",
            "hero_id": hero_id,
            "episode": result,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Episode generation failed for {hero_id}: {e}")
        raise HTTPException(status_code=500, detail="Episode generation failed")


@router.post("/update-canon")
async def trigger_canon_update(
    background_tasks: BackgroundTasks,
    x_cloudscheduler: str | None = Header(None),
) -> dict[str, Any]:
    """Trigger nightly canon update job.

    This endpoint is called by Cloud Scheduler nightly (e.g., 2 AM UTC).

    Args:
        background_tasks: FastAPI background tasks

    Returns:
        Job status
    """
    verify_scheduler_token(x_cloudscheduler)

    logger.info("Canon update job triggered")

    job = CanonUpdaterJob()

    async def run_job():
        result = await job.run()
        logger.info(f"Canon update completed: {result}")

    background_tasks.add_task(run_job)

    return {
        "status": "started",
        "message": "Canon update job started in background",
    }


@router.get("/status")
async def get_jobs_status() -> dict[str, Any]:
    """Get status of scheduled jobs.

    Returns:
        Job configuration and last run information
    """
    return {
        "jobs": [
            {
                "name": "episode_generation",
                "schedule": "0 2 * * *",  # Daily at 2 AM
                "description": "Generate daily episodes for all active heroes",
                "endpoint": "/api/v1/jobs/generate-episodes",
            },
            {
                "name": "canon_update",
                "schedule": "0 3 * * *",  # Daily at 3 AM
                "description": "Update Canon Layer with emergent events",
                "endpoint": "/api/v1/jobs/update-canon",
            },
        ],
        "environment": settings.environment,
    }
