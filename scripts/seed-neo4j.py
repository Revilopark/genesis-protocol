#!/usr/bin/env python3
"""Seed Neo4j database with initial schema and data."""

import asyncio
import os
from neo4j import AsyncGraphDatabase


async def create_schema(driver):
    """Create constraints and indexes."""
    schema_statements = [
        # Canon Layer constraints
        "CREATE CONSTRAINT canon_event_id IF NOT EXISTS FOR (e:CanonEvent) REQUIRE e.id IS UNIQUE",
        "CREATE CONSTRAINT location_id IF NOT EXISTS FOR (l:Location) REQUIRE l.id IS UNIQUE",
        "CREATE CONSTRAINT npc_id IF NOT EXISTS FOR (n:NPC) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT law_id IF NOT EXISTS FOR (l:Law) REQUIRE l.id IS UNIQUE",
        "CREATE CONSTRAINT global_arc_id IF NOT EXISTS FOR (a:GlobalArc) REQUIRE a.id IS UNIQUE",

        # Variant Layer constraints
        "CREATE CONSTRAINT hero_id IF NOT EXISTS FOR (h:Hero) REQUIRE h.id IS UNIQUE",
        "CREATE CONSTRAINT episode_id IF NOT EXISTS FOR (e:Episode) REQUIRE e.id IS UNIQUE",
        "CREATE CONSTRAINT local_event_id IF NOT EXISTS FOR (e:LocalEvent) REQUIRE e.id IS UNIQUE",
        "CREATE CONSTRAINT achievement_id IF NOT EXISTS FOR (a:Achievement) REQUIRE a.id IS UNIQUE",

        # Social Graph constraints
        "CREATE CONSTRAINT sponsor_id IF NOT EXISTS FOR (s:SponsorNode) REQUIRE s.id IS UNIQUE",
        "CREATE CONSTRAINT school_id IF NOT EXISTS FOR (s:School) REQUIRE s.id IS UNIQUE",

        # Content Pipeline constraints
        "CREATE CONSTRAINT storylet_id IF NOT EXISTS FOR (s:Storylet) REQUIRE s.id IS UNIQUE",
        "CREATE CONSTRAINT moderation_log_id IF NOT EXISTS FOR (m:ModerationLog) REQUIRE m.id IS UNIQUE",

        # Indexes
        "CREATE INDEX hero_user_id IF NOT EXISTS FOR (h:Hero) ON (h.user_id)",
        "CREATE INDEX episode_hero_number IF NOT EXISTS FOR (e:Episode) ON (e.hero_id, e.episode_number)",
        "CREATE INDEX event_timestamp IF NOT EXISTS FOR (e:CanonEvent) ON (e.start_date)",
        "CREATE INDEX event_significance IF NOT EXISTS FOR (e:CanonEvent) ON (e.significance_score)",
        "CREATE INDEX episode_status IF NOT EXISTS FOR (e:Episode) ON (e.generation_status)",
        "CREATE INDEX episode_date IF NOT EXISTS FOR (e:Episode) ON (e.generated_at)",
        "CREATE INDEX hero_status IF NOT EXISTS FOR (h:Hero) ON (h.status)",
        "CREATE INDEX npc_type IF NOT EXISTS FOR (n:NPC) ON (n.npc_type)",
    ]

    async with driver.session() as session:
        for statement in schema_statements:
            try:
                await session.run(statement)
                print(f"✓ {statement[:60]}...")
            except Exception as e:
                print(f"✗ Error: {e}")


async def seed_initial_data(driver):
    """Seed initial canon data."""
    async with driver.session() as session:
        # Create initial locations
        await session.run("""
            MERGE (l:Location {id: 'loc_metropolis'})
            SET l.name = 'Metropolis Prime',
                l.location_type = 'city',
                l.description = 'The central hub of hero activity, a gleaming metropolis of tomorrow.',
                l.is_canonical = true
        """)

        await session.run("""
            MERGE (l:Location {id: 'loc_shadow_district'})
            SET l.name = 'Shadow District',
                l.location_type = 'region',
                l.description = 'The underbelly of Metropolis Prime, where villains lurk.',
                l.is_canonical = true
        """)

        await session.run("""
            MERGE (l:Location {id: 'loc_tech_spire'})
            SET l.name = 'Tech Spire Academy',
                l.location_type = 'landmark',
                l.description = 'Training grounds for tech-powered heroes.',
                l.is_canonical = true
        """)

        # Create initial NPCs
        await session.run("""
            MERGE (n:NPC {id: 'npc_mentor_prime'})
            SET n.name = 'Mentor Prime',
                n.npc_type = 'hero',
                n.description = 'The legendary hero who guides new champions.',
                n.power_level = 10,
                n.is_canonical = true,
                n.origin = 'editorial'
        """)

        await session.run("""
            MERGE (n:NPC {id: 'npc_shadow_king'})
            SET n.name = 'The Shadow King',
                n.npc_type = 'villain',
                n.description = 'A mysterious figure controlling the criminal underworld.',
                n.power_level = 9,
                n.is_canonical = true,
                n.origin = 'editorial'
        """)

        # Create initial global arc
        await session.run("""
            MERGE (a:GlobalArc {id: 'arc_awakening'})
            SET a.title = 'The Awakening',
                a.description = 'New heroes are emerging across the world as an ancient power stirs.',
                a.status = 'active',
                a.current_phase = 1,
                a.total_phases = 4,
                a.start_week = 1
        """)

        # Create some storylets
        storylets = [
            {
                "id": "storylet_first_patrol",
                "title": "First Patrol",
                "category": "combat",
                "page_count": 6,
                "preconditions": {"power_types": [], "locations": [], "min_level": 1},
            },
            {
                "id": "storylet_mystery_signal",
                "title": "The Mystery Signal",
                "category": "investigation",
                "page_count": 5,
                "preconditions": {"power_types": ["tech"], "locations": [], "min_level": 1},
            },
            {
                "id": "storylet_ally_or_enemy",
                "title": "Ally or Enemy?",
                "category": "social",
                "page_count": 4,
                "preconditions": {"power_types": [], "locations": [], "min_level": 2},
            },
        ]

        for storylet in storylets:
            await session.run("""
                MERGE (s:Storylet {id: $id})
                SET s.title = $title,
                    s.category = $category,
                    s.page_count = $page_count,
                    s.preconditions = $preconditions,
                    s.is_active = true,
                    s.usage_count = 0
            """, **storylet)

        print("✓ Seeded initial canon data")


async def main():
    """Main entry point."""
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "local_password")

    print(f"Connecting to Neo4j at {uri}...")
    driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    try:
        await create_schema(driver)
        await seed_initial_data(driver)
        print("\n✓ Database seeding complete!")
    finally:
        await driver.close()


if __name__ == "__main__":
    asyncio.run(main())
