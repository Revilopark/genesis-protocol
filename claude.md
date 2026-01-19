# The Genesis Protocol: Phased Rollout Documentation

## Project Overview

**Platform Name**: The Genesis Protocol  
**Mission**: Daily personalized comic book and video content generation within a centralized fictional universe  
**Target Demographic**: Youth >13 years old  
**Core Architecture**: Multi-agent AI system ("The Rooms") + Trinity Graph (Neo4j) + Hardware-anchored social verification

### Key Differentiators
- **Living Narrative Ecosystem**: 6-10 page comics + 60-second videos generated daily per user
- **Centralized Universe**: MCU-style shared world with canonical events affecting all users
- **Trusted Social Fabric**: Tin Can-inspired verification (no algorithmic feeds, physical-proximity connections only)
- **Industrial-Scale Creative Pipeline**: Writer's Room → Art Department → Studio (all AI-powered)

---

## Technical Stack Foundation

### Core Infrastructure
- **Orchestration**: Amazon EKS (Kubernetes)
- **Database**: Neo4j AuraDB (hierarchical graph for Canon/Variant topology)
- **Generative AI**: 
  - Google Gemini 1.5 Pro (2M token context, narrative generation)
  - Gemini 2.5 Flash Image (character consistency)
  - Veo 3.1 (generative video highlights)
- **Agent Framework**: Vertex AI Agent Builder + LangGraph
- **DevOps**: Claude Code (agentic infrastructure management)
- **CDN**: Cloudflare (content delivery)
- **CI/CD**: GitHub Actions → ArgoCD → EKS

### Identity & Verification
- **School Authentication**: Clever SSO (70% of U.S. K-12 schools)
- **Adult Verification**: ID.me API (guardian-anchored root)
- **Connection Protocol**: Double-Handshake (NFC bumping + dynamic QR codes)

### Content Pipeline
- **Comic Generation**: Imagen 3 (~$0.04/image, 40 images/day)
- **Video Hybrid Model**:
  - 45s: 2.5D parallax motion comics (low compute)
  - 15s: Veo 3.1 generative highlights ($0.15/sec fast tier)
- **Audio**: Gemini Live API (voice synthesis + foley)

---

## Phase 1: Foundation (Months 1-4)

### Month 1-2: Core Infrastructure

#### Objectives
Deploy production-ready cluster and data layer to support 500 concurrent users with <200ms p95 latency for content delivery.

#### Technical Deliverables

**1. EKS Cluster Deployment**
```yaml
Cluster Spec:
  - Region: us-east-1 (primary), us-west-2 (DR)
  - Node Groups: 
      - System: t3.large (3 nodes, auto-scaling 2-5)
      - Compute: c6i.2xlarge (5 nodes, auto-scaling 3-10)
      - GPU: g5.xlarge (2 nodes, for batch image gen)
  - Networking: VPC with private subnets, NAT Gateway
  - Modular Monolith Architecture:
      - Single deployment (avoid microservice complexity)
      - Clear module boundaries (Writers Room, Art Dept, Studio, Social Graph)
      - Shared Neo4j connection pool
```

**2. Neo4j AuraDB Setup**
```cypher
Schema Implementation:
  - Canon Layer (Global State):
      Nodes: Event, Location, NPC, Law, GlobalArc
      Relationships: AFFECTS, OCCURS_IN, PARTICIPATES, CONSTRAINS
  
  - Variant Layer (User State):
      Nodes: Hero, Episode, LocalEvent, Achievement
      Relationships: INHERITS_FROM (Canon), DEFEATS, BEFRIENDS, DISCOVERS
  
  - Social Graph:
      Nodes: HeroNode, SponsorNode
      Relationships: SPONSORED_BY, CONNECTED_TO (w/ approval_status)

Indexes:
  - Hero(user_id) - unique
  - Event(timestamp, significance_score)
  - Episode(hero_id, episode_number) - composite
```

**3. CI/CD Pipeline**
```bash
GitHub Actions Workflow:
  1. Lint & Test (pytest, mypy)
  2. Build Docker images (multi-stage)
  3. Push to Amazon ECR
  4. ArgoCD auto-sync to EKS (GitOps)
  
ArgoCD Applications:
  - genesis-api (FastAPI backend)
  - genesis-agents (Vertex AI wrappers)
  - neo4j-backup-cronjob
  - monitoring-stack (Prometheus + Grafana)
```

**4. Clever SSO Integration**
```python
Authentication Flow:
  1. User clicks "Sign in with School"
  2. Redirect to Clever OAuth 2.0 endpoint
  3. Clever returns: student_id, school_id, grade_level, birthdate
  4. Backend creates HeroNode (if new) or retrieves existing
  5. Age verification: birthdate > 13 years (hard requirement)
  6. School becomes "Trusted Zone" for same-school connections
  
Rate Limiting Lesson (from Tin Can failure):
  - Decouple auth from content generation
  - Use Clever's distributed infra (don't proxy)
  - Implement exponential backoff on Clever API calls
  - Cache school metadata (refresh daily, not per-login)
```

#### Acceptance Criteria
- [ ] EKS cluster passes load test: 500 simultaneous auth requests
- [ ] Neo4j query latency <50ms for single-hop reads (Hero→Episode)
- [ ] CI/CD pipeline completes full deploy in <10 minutes
- [ ] Clever SSO integration tested with 3 pilot schools
- [ ] Infrastructure as Code (Terraform) fully documented

#### Dependencies
- Google Cloud account with Vertex AI API enabled
- AWS account with EKS, ECR, CloudFront provisioned
- Clever partnership agreement (sandbox access for development)
- Neo4j Aura Professional tier subscription

---

### Month 3-4: Content Pipeline MVP

#### Objectives
Launch "Tier B" comic generation (asset-based, non-AI art) with RunwayML video synthesis for 100-500 pilot users.

#### Technical Deliverables

**1. Tier B Comic Generation (Asset Library Approach)**
```
Strategy: Reduce AI generation costs during pilot by using pre-rendered asset library

Asset Library Structure:
  - 500 base character poses (front, side, action, idle)
  - 200 background scenes (city, lab, forest, space)
  - 100 effect overlays (explosions, energy blasts, weather)

Generation Pipeline:
  1. Writers Room generates script (Gemini 1.5 Pro)
  2. Layout Agent selects assets matching scene description
  3. Composition Engine layers: Background + Character + Effects
  4. Text rendering (speech bubbles, captions)
  5. Export as 10-page PDF (Cloudflare CDN)

Cost Optimization:
  - Tier B: ~$1.50/day/user (mostly Gemini text generation)
  - Tier A (Phase 2): ~$1.60/day/user (full Imagen 3 generation)
```

**2. Video Synthesis Pipeline**
```yaml
RunwayML Gen-4 Turbo Integration:
  Input: 10 static comic panels (Tier B assets)
  Process:
    - Panels 1-8: 2.5D parallax (5s each, 40s total)
        - Separate foreground/background layers
        - Apply camera moves (Ken Burns effect)
        - Add subtle animation (floating debris, flickering lights)
    - Panels 9-10: RunwayML Gen-4 Turbo (10s each, 20s total)
        - "Money shot" full motion generation
        - Prompt includes static panel as seed
        - Character consistency via style reference
  
  Audio Layer:
    - Gemini Live API: Character voice acting
    - Sound library: Pre-licensed foley effects
    - Background music: Procedural generation (udio.com integration)

  Output: 60-second MP4 @ 1080p, H.264 codec
  
Cost: ~$2.50/episode (RunwayML + audio synthesis)
```

**3. Content Delivery via Cloudflare CDN**
```
CDN Configuration:
  - Origin: AWS S3 bucket (us-east-1)
  - Edge locations: Global (prioritize US, UK, Canada)
  - Caching rules:
      - Comics (PDF): 7-day TTL (episodes are immutable)
      - Videos (MP4): 7-day TTL
      - Character sheets: 30-day TTL (rarely change)
  
  Access Control:
    - Signed URLs with 24-hour expiration
    - User authentication token embedded in URL
    - Rate limit: 10 downloads/hour per user (prevent scraping)

Performance Targets:
  - TTFB (Time to First Byte): <100ms (p95)
  - Video start time: <2s on 10 Mbps connection
  - PDF load time: <1s
```

**4. Parental Consent & Age Verification**
```
Guardian Dashboard (Web App):
  - Tech Stack: Next.js + Tailwind CSS
  - Features:
      1. ID.me adult verification on first login
      2. Link child's Clever account via OAuth
      3. Approve/reject incoming friend requests (Digital Playdate)
      4. View child's recent episodes (read-only)
      5. Content settings: Violence level, language filter
      6. Export data (COPPA compliance: parent data access)

Age Verification Flow:
  1. Child creates account via Clever SSO (school verifies DOB)
  2. System checks DOB > 13 years (hard block if younger)
  3. Guardian receives email: "Approve [Child] to join Genesis Protocol"
  4. Guardian completes ID.me verification + COPPA consent checkboxes
  5. HeroNode status: PENDING → ACTIVE (only then can generate content)

Privacy Compliance:
  - No PII in Neo4j (only anonymized tokens: Hero_12345)
  - Real names stored in encrypted Guardian table (AWS KMS)
  - Retention: Delete all data within 30 days of account closure
```

#### Pilot Launch Strategy

**School Selection Criteria**:
1. Existing Clever integration (reduce auth friction)
2. Student body 500-2000 (manageable cohort)
3. Geographic diversity (US East, West, South)
4. Partnership agreement (co-marketing, feedback sessions)

**Pilot Schools (Target 2-3)**:
- Metro Nashville Public Schools (local to Vanderbilt, existing relationship)
- Bay Area Charter Network (tech-forward, diverse demographics)
- Florida Public School District (test compliance with FL social media ban)

**User Onboarding Flow**:
1. Week 1: Guardian-only access (setup, consent, character creation)
2. Week 2: Student access unlocked, first 7 episodes generated
3. Week 3: Enable social features (friend connections via NFC)
4. Week 4: First "Global Event" (test Canon Layer propagation)

**Success Metrics**:
- DAU/MAU ratio >0.6 (daily engagement)
- Episode completion rate >80% (users finish reading/watching)
- Friend connection rate: avg 5 connections per user within 30 days
- Guardian satisfaction: >4.0/5.0 on safety survey
- System uptime: >99.5% (exclude planned maintenance)

#### Acceptance Criteria
- [ ] 100 users generating daily comics with <5% failure rate
- [ ] Video synthesis completes within 2 minutes of comic generation
- [ ] Guardian dashboard tested with 50 parents (UAT)
- [ ] Parental consent flow complies with COPPA (legal review completed)
- [ ] Pilot schools signed MOUs with data processing agreements

#### Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|-----------|
| RunwayML API rate limits | High | Pre-purchase reserved capacity; fallback to motion-only |
| School onboarding delays | Medium | Begin outreach Month 1; have 5 schools in pipeline |
| Parental adoption friction | High | Simplify consent to 3 clicks; provide explainer video |
| Content quality concerns | Medium | Human QA review of first 100 episodes per pilot school |

---

## Phase 2: Scale (Months 5-10)

### Month 5-6: Tier A and Social Features

#### Objectives
Transition to full AI generation pipeline (Tier A) and enable cross-world character interactions for 500-5000 users.

#### Technical Deliverables

**1. Tier A: Full AI Generation Pipeline**
```python
Writers Room (Gemini 1.5 Pro):
  - Context window utilization: Inject last 30 days of Hero history + Canon state
  - Output format: JSON with per-panel prompts
  - Quality gates:
      1. Continuity Agent checks for contradictions
      2. Safety Agent filters violence/language per Guardian settings
      3. JSON Schema validator ensures downstream compatibility

Art Department (Imagen 3 / Gemini 2.5 Flash):
  Character Locker System:
    - On signup: Generate canonical character sheet (8 angles + turnaround)
    - Store in GCS bucket with immutable ID
    - Each panel generation includes Character Locker as reference image
  
  Panel Generation:
    - Input: visual_prompt (from Writers Room) + Character Locker
    - Imagen 3 API call with style consistency parameters
    - QA Agent (vision model) scores output (0.0-1.0)
    - If score <0.75: Regenerate with adjusted prompt
    - Max 3 retries before escalating to human review queue

Studio (Veo 3.1 Hybrid):
  - 45 seconds: 2.5D parallax from Imagen 3 panels
  - 15 seconds: Veo 3.1 generative video (climax scene only)
  - Cost per episode: $67.50/month (see economic analysis)

Premium Tier Pricing:
  - Free Tier: Comics only (Tier B assets, no video)
  - Standard Tier: $12.99/month (comics + motion video)
  - Pro Tier: $29.99/month (Tier A comics + Veo highlights)
```

**2. Cross-World Character Sharing**
```cypher
# Neo4j Schema Extension

# New relationship: TEAM_UP
CREATE (h1:Hero)-[:TEAM_UP {episode_id: e1, contribution: "saved_civilian"}]->(h2:Hero)

# Crossover Episode Generation
MATCH (h1:Hero {id: UserA})-[:CONNECTED_TO]->(h2:Hero {id: UserB})
WHERE h1.last_episode_number = h2.last_episode_number
CALL writers_room.generate_crossover(h1, h2, "bank_robbery_thwarted")
RETURN crossover_episode

# Propagation Rule:
# If UserA and UserB are friends AND both request episodes on same day,
# 20% chance system generates shared storyline affecting both Variant subgraphs
```

**Social Features Implementation**:
- **Shared Episodes**: Users can view friends' comics (with friend's permission setting)
- **Team Roster Dashboard**: See friends' hero names, power sets, last active timestamp
- **Crossover Requests**: User can "invite" friend to next episode (triggers Writers Room to merge storylines)
- **Leaderboard** (Optional): "Significance Score" based on Canon Layer contributions (gamification)

**3. Real-Time Presence & Activity Feeds**
```
Tech Stack:
  - WebSocket server: FastAPI + Socket.IO
  - State management: Redis pub/sub
  - UI: React with real-time updates

Features:
  - Live indicator: Green dot when friend is reading today's episode
  - Activity feed (feed-less design exception):
      "Hero_Blaze just completed Episode 47"
      "Hero_Storm discovered the Crystal Caves" (Canon contribution)
  - Push notifications (opt-in):
      "Your crossover episode with [Friend] is ready!"
      "A Global Event has been triggered in Sector 7"

Privacy Controls:
  - Users can hide online status (default: visible to friends only)
  - Activity feed limited to friends (no public broadcasting)
  - No algorithmic recommendations (feed shows only connected users)
```

**4. Content Moderation Pipeline**
```yaml
Moderation Layers:

Layer 1: Gemini Safety Filters (Pre-Generation)
  - Configured to "Strict" mode
  - Blocks prompts containing: violence against minors, sexual content, 
    self-harm references, hate speech, personal attacks
  - If blocked: Writers Room regenerates with constraint injection

Layer 2: Amazon Rekognition (Post-Generation, Images)
  - Scan all generated panels for:
      - Explicit nudity (threshold: 90% confidence)
      - Graphic violence (threshold: 85% confidence)
      - Text in image (OCR to detect profanity bypass)
  - If flagged: Panel regenerated OR escalated to human review

Layer 3: Amazon Augmented AI (A2I) - Human Review
  - Review queue for edge cases (5-10% of generations)
  - Reviewers see: Comic context, flagged panel, safety report
  - Actions: Approve, Regenerate with notes, Escalate to legal
  - SLA: 4-hour review turnaround (episode delivery may delay)

Layer 4: User Reporting
  - "Report Content" button on every episode
  - Reasons: Inappropriate, Bullying, Bug, Other
  - Auto-escalates to A2I if report matches safety pattern

Compliance:
  - Audit logs: Store all moderation decisions (7-year retention)
  - Quarterly review: Human auditors sample 1000 episodes
  - Transparency report: Publish monthly stats (% flagged, common reasons)
```

#### Acceptance Criteria
- [ ] Tier A pipeline generates 1000 episodes/day with <2% human review rate
- [ ] Crossover episodes tested with 50 friend pairs
- [ ] Real-time presence works with 500 concurrent WebSocket connections
- [ ] Content moderation achieves <0.1% false positive rate (user complaints)
- [ ] Premium tier conversion: >15% of free users upgrade within 60 days

---

### Month 7-8: Narrative Governance

#### Objectives
Establish editorial control over the centralized universe through curated events, emergent behavior detection, and modular storytelling (storylets).

#### Technical Deliverables

**1. Curated Event System with Editorial Workflow**
```
Event Types:
  1. Global Arcs (4-6 weeks): "The Invasion," "The Civil War"
  2. Regional Events (1-2 weeks): "Sector 7 Blackout" (affects only users in that city)
  3. Social Events (1 day): "Team-Up Tuesday" (encourages crossovers)

Editorial Dashboard (Human Showrunners):
  - Role: Narrative Directors (2-3 staff)
  - Tools: 
      - Canon Editor: WYSIWYG interface to Neo4j (add/modify Events, NPCs, Laws)
      - Event Scheduler: Calendar view to plan upcoming arcs
      - Impact Simulator: Preview how Canon change propagates to Variants
  
  Workflow:
    1. Director creates Event: "Alien fleet arrives in orbit"
    2. System generates Propagation Plan: Which Heroes see this first? (based on location, power level)
    3. Writers Room receives directive: All episodes this week include "sky turning red"
    4. Director monitors: Dashboard shows % of users who interacted with event
    5. Director adjusts: Escalate or de-escalate based on engagement

Agentic Assistance (Claude Code):
  - Auto-generate Event descriptions from high-level beats
  - Check for Canon contradictions (e.g., can't have two simultaneous "sun blocked" events)
  - Suggest NPC dialogue updates based on Event timeline
```

**2. Emergent Behavior Detection Pipeline**
```python
# Detect unexpected user patterns that become Canon

Significance Scoring (runs nightly):
  1. Scan all Episodes generated in last 24 hours
  2. Extract events tagged by Writers Room: SAVE_CITY, DISCOVER_TECH, DEFEAT_NPC
  3. Calculate significance:
      base_score = event_magnitude (1-10, from AI)
      social_multiplier = 1 + (num_friends_who_reference_event * 0.1)
      novelty_bonus = 1.5 if event_type never seen before
      final_score = base_score * social_multiplier * novelty_bonus
  
  4. Events with final_score > 50: Flag for Canon Auditor review

Canon Auditor (Gemini Agent):
  - Receives flagged events
  - Queries GraphRAG: "Does this contradict existing Canon?"
  - Generates proposal: "User Hero_Storm discovered 'Dark Matter Crystals'. 
      This could become global resource. Recommend adding to Canon Layer."
  - Human Director approves/rejects

Emergent NPC Protocol:
  - If 10+ users independently create similar villain archetype (via character customization),
      system proposes: "Many users fighting 'Shadow Cultists'. Promote to Canon NPC?"
  - Approved NPCs get canonical character sheets and appear in future episodes

Example (Historical):
  - Week 3 Pilot: 30% of users had episodes involving "stolen prototype device"
  - System detected pattern: "Tech theft is common plot"
  - Editorial decision: Introduce Canon NPC "The Collector" who steals tech (creates overarching threat)
  - Result: Engagement +15% (users felt their stories mattered)
```

**3. Storylet Engine for Modular Content**
```
Storylet Architecture (inspired by Fallen London / Sunless Sea):

Definition:
  - Storylet = Self-contained narrative module (3-5 pages of comic)
  - Can be inserted into any Hero's episode if preconditions met
  - Ensures narrative variety while maintaining Canon consistency

Structure:
  - Title: "The Abandoned Laboratory"
  - Preconditions: 
      Hero.power_type = "Tech" OR Hero.location = "Industrial Sector"
  - Outcomes:
      Success: Discover upgrade (add "EMP Blast" ability)
      Failure: NPC rivalry (introduce recurring villain)
  - Canon Hooks: References current Global Arc if active

Library (Month 7-8 Goal: 50 storylets):
  - 20 Combat encounters (scale to Hero power level)
  - 15 Investigation mysteries (clue-gathering)
  - 10 Social dilemmas (moral choices affect Hero reputation)
  - 5 Crossover templates (plug in any two friends)

Generation Logic:
  1. Writers Room requests storylet: "Need 6-page episode for Hero_X"
  2. Storylet Engine queries available storylets matching Hero_X preconditions
  3. Select storylet not used in last 30 days for Hero_X (avoid repetition)
  4. Inject Hero_X details into template
  5. Scriptwriter Agent fills dialogue/visuals
  6. Output structured JSON for Art Department

Benefits:
  - Consistency: Storylets are human-authored, ensuring quality baselines
  - Scalability: AI adapts templates to infinite Hero variations
  - Editorial control: Directors curate storylet library
```

**4. Seasonal Arc Launch**
```
First Seasonal Arc: "The Fractured Sky" (8 weeks)

Narrative Structure:
  - Week 1-2: Setup (mysterious cracks appear in sky, NPCs panic)
  - Week 3-4: Investigation (Heroes discover alien dimension bleeding through)
  - Week 5-6: Escalation (rift widens, monsters cross over)
  - Week 7: Climax (Global Event: All Heroes must choose side in battle)
  - Week 8: Resolution (User choices determine Canon outcome: Seal rift OR allow merge)

Technical Implementation:
  1. Canon Layer updated weekly with Arc state (Sky_Status: CRACKING → TORN → MERGED)
  2. Writers Room receives weekly beats: "This week focus: Heroes see first monster"
  3. Emergent Behavior Detection tracks: Which Heroes engaged with Arc content?
  4. Finale: Count user votes (via episode choices) → 60% vote "Seal" → Canon updates to sealed sky
  5. Post-Arc: Persistent consequences (new NPC faction formed from rift survivors)

Marketing Integration:
  - Arc trailer (Veo-generated): Sent to all users Week 1
  - Leaderboard: "Top 10 Heroes who saved the most civilians during Arc"
  - Merchandise: Physical comic book of Arc (for Pro subscribers)
```

#### Acceptance Criteria
- [ ] Editorial dashboard deployed with 3 Narrative Directors trained
- [ ] Curated event system triggers 1 Global Arc (8-week test)
- [ ] Emergent behavior pipeline promotes 5 user-created elements to Canon
- [ ] Storylet library reaches 50 modules with 95% positive user feedback
- [ ] Seasonal Arc achieves >70% user participation (engaged with Arc content)

---

## Success Metrics & KPIs

### Phase 1 (Pilot)
| Metric | Target | Measurement |
|--------|--------|-------------|
| Active Users | 100-500 | Daily logins |
| Episode Generation Success Rate | >95% | % episodes delivered on time |
| Average Session Duration | >8 min | Time spent reading/watching |
| Friend Connections per User | >5 | Avg connected Heroes |
| Guardian Approval Rating | >4.0/5.0 | Post-pilot survey |
| System Uptime | >99.5% | Monthly availability |

### Phase 2 (Scale)
| Metric | Target | Measurement |
|--------|--------|-------------|
| Active Users | 5,000 | Daily logins |
| Premium Conversion Rate | >15% | % users on paid tiers |
| Crossover Episodes Generated | >100/day | System logs |
| Content Moderation Accuracy | <0.1% false positive | User complaints |
| DAU/MAU Ratio | >0.6 | Engagement consistency |
| Seasonal Arc Participation | >70% | % users engaging with Arc content |

---

## Risk Register

### Technical Risks

**1. API Cost Overruns**
- **Impact**: Bankruptcy if Veo costs exceed projections
- **Probability**: Medium
- **Mitigation**: 
  - Tiered access (Free users get no video)
  - Reserved capacity contracts with Google
  - Real-time cost monitoring dashboard with kill-switch at $X/day

**2. Neo4j Performance Degradation**
- **Impact**: Slow episode generation → user churn
- **Probability**: Medium (at 5K+ users)
- **Mitigation**:
  - Index optimization (quarterly review)
  - Read replicas for Canon Layer queries
  - Caching layer (Redis) for frequently accessed Variant subgraphs

**3. Clever/ID.me Service Interruption**
- **Impact**: Users cannot authenticate → loss of new signups
- **Probability**: Low
- **Mitigation**:
  - Fallback to email-based verification (manual review queue)
  - Pre-authenticate during off-peak hours
  - Status page monitoring with auto-alerts

### Regulatory Risks

**4. COPPA Compliance Violation**
- **Impact**: FTC fines ($43K per violation), platform shutdown
- **Probability**: Low (if design followed)
- **Mitigation**:
  - Quarterly legal audits
  - Age-gating at multiple checkpoints (Clever DOB + Guardian verification)
  - Data minimization (no PII in AI prompts)

**5. State-Level Social Media Bans**
- **Impact**: Cannot operate in FL, TX, etc.
- **Probability**: Medium
- **Mitigation**:
  - Position as "creative utility," not social media (no feeds, no viral content)
  - Guardian dashboard emphasizes parental control
  - Legal memo prepared for each state's specific requirements

### Business Risks

**6. Low User Retention**
- **Impact**: High CAC, unsustainable growth
- **Probability**: Medium (novelty wears off)
- **Mitigation**:
  - Seasonal Arcs (create "appointment viewing")
  - Social features (friend crossovers increase stickiness)
  - Personalization depth (the longer you play, the richer your history)

**7. Content Quality Perception**
- **Impact**: "AI slop" reputation, viral negative reviews
- **Probability**: Medium (public is skeptical of AI-generated content)
- **Mitigation**:
  - Human QA review (spot-check 5% of episodes)
  - User feedback loop ("Rate this episode" after each view)
  - Storylet curation (blend AI generation with human-authored templates)

---

## Technical Debt & Future Work

### Post-Phase 2 (Months 9-12)

**1. Multi-Language Support**
- Expand beyond English (Spanish, Mandarin priority)
- Gemini 1.5 Pro supports 100+ languages
- Challenge: Cultural localization of storylets (not just translation)

**2. User-Generated Content (UGC)**
- Allow users to submit custom storylets for peer review
- Moderation: A2I pipeline + community voting
- Risk: Quality control, IP rights management

**3. Blockchain Integration (Optional)**
- NFT character sheets (ownership verification)
- Smart contracts for Canon contributions (users earn tokens for emergent additions)
- Caution: Regulatory uncertainty, environmental concerns

**4. Expanded Media Formats**
- Audio drama (podcast-style episode narration)
- Interactive VR episodes (Quest 3 integration)
- Physical merchandise (print-on-demand comics)

**5. B2B Licensing**
- License "Rooms" architecture to other studios (WhiteLabel SaaS)
- Provide Canon management tools for existing IP holders (e.g., "MCU Daily Adventures")

---

## Agentic DevOps: Claude Code Integration

### Infrastructure Management

**Daily Operations (Automated)**:
```bash
# Claude Code monitors and executes:

# 1. Cost anomaly detection
$ gcloud billing accounts list --format="json" | jq '.[] | select(.amount > threshold)'
# If exceeded: Alert Slack channel + suggest optimization

# 2. Neo4j backup verification
$ curl -X GET https://neo4j.aura.api/backups/latest | jq '.status'
# If failed: Trigger manual backup + file incident

# 3. Vertex AI quota monitoring
$ gcloud compute project-info describe --project=genesis-protocol | grep 'QUOTA'
# If near limit: Request increase + notify engineers

# 4. Security patching
$ kubectl get pods --all-namespaces -o json | jq '.items[] | select(.spec.containers[].image | contains("CRITICAL"))'
# Auto-update images if CVE detected
```

**Deployment Workflows (Human-Initiated)**:
```
Scenario: Update Scriptwriter Agent prompt to increase dialogue humor

1. Engineer: "Claude, update the Scriptwriter to add 20% more humor"
2. Claude Code:
   - Fetches current prompt from Vertex AI Agent Builder
   - Modifies prompt: Adds instruction "Include 1 witty one-liner per 3 pages"
   - Generates 50 test episodes in staging environment
   - Runs regression tests: JSON schema valid? Safety filters passed?
   - Compares humor score (sentiment analysis) before/after
3. Claude Code: "Humor increased by 18%. 2 test episodes flagged for sarcasm misinterpretation. Recommend human review."
4. Engineer: "Proceed with deployment"
5. Claude Code: Deploys to production via ArgoCD sync
```

### NPC Awareness Updates (Nightly Job)
```python
# Claude Code automates "World Bible" updates

def update_npc_knowledge():
    # 1. Canon Auditor summarizes today's global events
    summary = gemini.generate(
        prompt="Summarize today's canonical events in 500 words",
        context=neo4j.query("MATCH (e:Event {date: today}) RETURN e")
    )
    
    # 2. Embed summary into vector database
    embedding = vertex_ai.embed(summary)
    pinecone.upsert(vector=embedding, metadata={"date": today, "type": "canon_update"})
    
    # 3. Update NPC memory files (JSON stored in GCS)
    for npc in neo4j.query("MATCH (n:NPC) RETURN n"):
        npc_memory = load_json(f"gs://genesis-npcs/{npc.id}/memory.json")
        npc_memory["world_state"].append(summary)
        save_json(f"gs://genesis-npcs/{npc.id}/memory.json", npc_memory)
    
    # 4. Verify propagation
    test_query = "What happened in the world yesterday?"
    response = gemini.generate(prompt=test_query, context=npc_memory["world_state"][-1])
    assert "alien fleet" in response.lower()  # Check if NPC knows about today's event

# Scheduled: Runs at 2 AM UTC daily (off-peak)
```

---

## Appendix: Economic Model Deep Dive

### Unit Economics (Per User/Month)

**Tier B (Pilot Phase)**:
```
Costs:
  - Gemini 1.5 Pro (text generation): $5.00
  - Asset compositing (CPU): $1.50
  - RunwayML Gen-4 Turbo (20s video): $6.00
  - Cloudflare CDN: $2.00
  - Neo4j + EKS (allocated): $3.50
  Total: $18.00/user/month

Revenue:
  - Tier: Free (pilot, no monetization)
  - Subsidy required: $18.00/user
```

**Tier A (Pro Tier, Phase 2)**:
```
Costs:
  - Gemini 1.5 Pro: $5.00
  - Imagen 3 (40 images/day): $48.00
  - Veo 3.1 (15s generative): $67.50
  - Audio synthesis: $10.00
  - Infrastructure: $5.00
  Total: $135.50/user/month

Revenue:
  - Subscription: $29.99/user/month
  - Gap: -$105.51 (unsustainable)

Solution:
  - Native advertising (product placement in panels): +$20/user/month
  - Merchandising (physical comics): +$15/user/month (30% take rate)
  - Licensing (user-generated IP to studios): +$5/user/month (speculative)
  - Adjusted revenue: $69.99/user/month
  - Margin: -$65.52 (still unprofitable for Pro tier)

Conclusion: Pro tier is a loss leader. Profitability depends on scale (10K+ users) and B2B licensing.
```

**Standard Tier (Sustainable Target)**:
```
Costs:
  - Gemini: $5.00
  - Imagen 3: $48.00
  - Motion video only (no Veo): $2.00
  - Infrastructure: $3.50
  Total: $58.50/user/month

Revenue:
  - Subscription: $12.99/user/month
  - Advertising: +$8/user/month
  - Merchandising: +$5/user/month
  - Total: $25.99/user/month
  - Margin: -$32.51 (still unprofitable)

Reality Check: At current AI pricing, this model is subsidized by venture capital until:
  1. Veo pricing drops 80% (likely by 2027)
  2. User base reaches 100K+ (economies of scale)
  3. Advertising rates increase (proven engagement data)
```

---

## Glossary

**Canon Layer**: Global state in Neo4j containing immutable world laws and events affecting all users.

**Variant Layer**: User-specific subgraph inheriting from Canon but allowing personal divergence.

**The Rooms**: Multi-agent AI system (Writers Room, Art Department, Studio) that generates daily content.

**Double-Handshake Protocol**: Two-stage verification (identity + connection) ensuring trusted social fabric.

**GraphRAG**: Retrieval-Augmented Generation using graph relationships instead of vector similarity.

**Storylet**: Self-contained narrative module with preconditions and outcomes, ensuring modular content.

**Significance Score**: Metric determining if user-generated event becomes Canon (based on magnitude, novelty, social reach).

**HeroNode**: User account in social graph, anchored to SponsorNode (guardian).

**Tin Can Philosophy**: Anti-algorithmic social design prioritizing physical proximity and intentional connection over viral discovery.

---

## Contact & Escalation

**Project Lead**: [Name]  
**Technical Architect**: Claude Code (Agentic)  
**Narrative Director**: [Name]  
**Legal Counsel**: [Name]  

**Escalation Path**:
1. Technical issues → Claude Code (auto-resolve or escalate to engineer Slack)
2. Content moderation → A2I human review queue
3. Legal/compliance → Immediate email to Legal Counsel
4. User safety concerns → Guardian dashboard alert + 24-hour response SLA

---

## Version History

- **v1.0** (2026-01-18): Initial phased rollout plan
- **v1.1** (TBD): Post-pilot retrospective with adjusted timelines
- **v2.0** (TBD): Phase 3 expansion (international markets)

---

## References

1. The Genesis Protocol: Architecting the Decentralized Creative Universe (source document)
2. Tin Can Device Research (anti-smartphone ethos, Double-Handshake inspiration)
3. Google Vertex AI Documentation (Gemini 1.5 Pro, Veo 3.1 API specs)
4. Neo4j Graph Database Best Practices (Canon/Variant topology design)
5. COPPA Compliance Guidelines (FTC, 2024 update)
6. Clever API Integration Documentation (school-based SSO)
7. ID.me Identity Verification Specifications (adult verification flows)

---

**End of Document**

*This Claude.md file is a living document. Update monthly based on pilot learnings and Phase 2 execution.*
