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


@router.post("/seed-test-data")
async def seed_test_data(
    x_admin_token: str | None = Header(None),
) -> dict[str, Any]:
    """Seed test data for development and pilot testing.

    Creates sample heroes, guardians, and canon events.
    Requires admin token in production.
    """
    # Allow in non-production or with admin token
    admin_token = "genesis-admin-seed-2026"
    if settings.environment == "production" and x_admin_token != admin_token:
        raise HTTPException(status_code=403, detail="Admin token required in production")

    from genesis.core.database import get_session

    created = {"heroes": [], "guardians": [], "events": []}

    try:
        async with get_session() as session:
            # Create test guardian
            result = await session.run(
                """
                MERGE (g:Guardian {id: 'guardian-test-001'})
                ON CREATE SET
                    g.email = 'test.guardian@example.com',
                    g.name = 'Test Guardian',
                    g.verified = true,
                    g.created_at = datetime()
                RETURN g.id as id
                """
            )
            record = await result.single()
            if record:
                created["guardians"].append(record["id"])

            # Create test heroes
            heroes = [
                {
                    "id": "hero-test-001",
                    "user_id": "user-test-001",
                    "hero_name": "Nova Storm",
                    "power_type": "Cosmic Energy Manipulation",
                    "origin_story": "During a meteor shower that opened a rift to another dimension, discovered the ability to channel cosmic energy.",
                },
                {
                    "id": "hero-test-002",
                    "user_id": "user-test-002",
                    "hero_name": "Shadow Strike",
                    "power_type": "Darkness Control",
                    "origin_story": "Born with the ability to manipulate shadows, trained in stealth and precision.",
                },
                {
                    "id": "hero-test-003",
                    "user_id": "user-test-003",
                    "hero_name": "Crystal Guardian",
                    "power_type": "Earth/Crystal",
                    "origin_story": "Discovered an ancient crystal that bonded with their body, granting control over minerals.",
                },
            ]

            for hero in heroes:
                result = await session.run(
                    """
                    MERGE (h:Hero {id: $id})
                    ON CREATE SET
                        h.user_id = $user_id,
                        h.hero_name = $hero_name,
                        h.power_type = $power_type,
                        h.origin_story = $origin_story,
                        h.current_location = 'Metropolis Prime',
                        h.status = 'active',
                        h.episode_count = 0,
                        h.significance_score = 0,
                        h.created_at = datetime(),
                        h.content_settings = {violence_level: 1, language_filter: true}
                    WITH h
                    MATCH (g:Guardian {id: 'guardian-test-001'})
                    MERGE (h)-[:SPONSORED_BY]->(g)
                    RETURN h.id as id
                    """,
                    **hero,
                )
                record = await result.single()
                if record:
                    created["heroes"].append(record["id"])

            # Create a global event
            result = await session.run(
                """
                MERGE (e:Event {id: 'event-fractured-sky'})
                ON CREATE SET
                    e.title = 'The Fractured Sky',
                    e.description = 'Mysterious cracks have appeared in the sky above major cities. Strange energy emanates from these rifts, and unknown creatures have begun emerging.',
                    e.layer = 'canon',
                    e.status = 'active',
                    e.significance_score = 100,
                    e.start_date = date(),
                    e.created_at = datetime()
                RETURN e.id as id
                """
            )
            record = await result.single()
            if record:
                created["events"].append(record["id"])

        logger.info(f"Seeded test data: {created}")
        return {"status": "success", "created": created}

    except Exception as e:
        logger.error(f"Failed to seed test data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to seed data: {str(e)}")
