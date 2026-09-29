"""
Main FastAPI backend for Competitive Memory.

Endpoints:
- Timeline and events
- Strategy analysis
- Pattern detection
- Historical analysis
- Investigation
- Memory management
- Demo mode
"""

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import Optional, List
import os
import json

from backend.services.hindsight_service import get_hindsight_service
from backend.services.competitor_service import get_competitor_service
from backend.services.pattern_service import get_pattern_service
from backend.services.strategy_service import get_strategy_service
from backend.services.investigation_service import get_investigation_service
from backend.models.competitor import (
    CompetitorEvent, Competitor, StrategyProfile, Pattern, StrategyShift
)
from data.synthetic_dataset import generate_synthetic_dataset

app = FastAPI(
    title="Competitive Memory API",
    description="AI-powered competitive intelligence with persistent memory",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services
hindsight_service = None
competitor_service = None
pattern_service = None
strategy_service = None
investigation_service = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global hindsight_service, competitor_service, pattern_service, strategy_service, investigation_service
    
    hindsight_service = await get_hindsight_service()
    competitor_service = get_competitor_service()
    pattern_service = get_pattern_service()
    strategy_service = get_strategy_service()
    investigation_service = get_investigation_service()
    
    # Load synthetic data
    events, competitors = generate_synthetic_dataset()
    
    # Convert to models and load
    event_models = []
    for e in events:
        e['date'] = datetime.fromisoformat(e['date']) if isinstance(e['date'], str) else e['date']
        event_models.append(CompetitorEvent(**e))
    
    competitor_models = []
    for c in competitors:
        c['last_updated'] = datetime.utcnow()
        c['event_count'] = len([e for e in event_models if e.competitor == c['name']])
        competitor_models.append(Competitor(**c))
    
    competitor_service.load_synthetic_data(
        [e.dict() for e in event_models],
        [c.dict() for c in competitor_models]
    )
    
    # Retain events in Hindsight
    for event in event_models:
        await hindsight_service.retain_event(event.dict())
    
    print("[OK] Competitive Memory initialized")
    print(f"[OK] Loaded {len(event_models)} events across {len(competitor_models)} competitors")
    print(f"[OK] Memory service: {'Hindsight' if hindsight_service.connected else 'Demo Mode'}")


# ============================================================
# HEALTH & STATUS
# ============================================================

@app.get("/health")
async def health_check():
    """System health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "memory_service": hindsight_service.get_memory_status() if hindsight_service else None
    }


# ============================================================
# COMPETITORS
# ============================================================

@app.get("/api/competitors")
async def get_competitors():
    """Get all competitors."""
    competitors = competitor_service.get_all_competitors()
    return {
        "competitors": [c.dict() for c in competitors],
        "count": len(competitors)
    }


@app.get("/api/competitors/{competitor_name}")
async def get_competitor_detail(competitor_name: str):
    """Get detailed competitor profile."""
    competitor = competitor_service.get_competitor(competitor_name)
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    # Get recent events
    events = competitor_service.get_competitor_events(competitor_name)
    recent = competitor_service.get_recent_events(competitor_name, days=60)
    
    # Get strategy profile
    profile = strategy_service.detect_strategy_profile(events)
    
    return {
        "competitor": competitor.dict(),
        "strategy_profile": profile.dict(),
        "total_events": len(events),
        "recent_events": [e.dict() for e in recent[:10]],
        "event_types": list(set(e.event_type for e in events))
    }


# ============================================================
# TIMELINE & EVENTS
# ============================================================

@app.get("/api/timeline")
async def get_timeline(
    competitor: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    days: Optional[int] = Query(180)
):
    """Get competitive timeline."""
    if competitor:
        events = competitor_service.get_competitor_events(competitor)
    else:
        events = competitor_service.get_all_events()
    
    # Filter by date
    cutoff = datetime.utcnow() - timedelta(days=days)
    events = [e for e in events if e.date >= cutoff]
    
    # Filter by type
    if event_type:
        events = [e for e in events if e.event_type == event_type]
    
    # Sort chronologically
    events = sorted(events, key=lambda e: e.date)
    
    return {
        "events": [e.dict() for e in events],
        "count": len(events),
        "time_range": {
            "start": min(e.date for e in events).isoformat() if events else None,
            "end": max(e.date for e in events).isoformat() if events else None
        }
    }


@app.get("/api/events/{event_id}")
async def get_event(event_id: str):
    """Get single event details."""
    event = competitor_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Find related events
    similar = competitor_service.find_similar_events(event_id, limit=5)
    
    return {
        "event": event.dict(),
        "similar_events": [e.dict() for e in similar]
    }


# ============================================================
# TIME MACHINE
# ============================================================

@app.get("/api/time-machine")
async def time_machine(
    competitor: str,
    date: str,
    include_future: bool = False
):
    """
    Travel to a specific historical date.
    Shows what was known at that time.
    """
    try:
        target_date = datetime.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    
    # Get events up to that date
    events_at_time = competitor_service.get_events_at_date(
        competitor,
        target_date,
        before=True
    )
    
    # Get events after that date (what happened next)
    future_cutoff = target_date + timedelta(days=90)
    later_events = [
        e for e in competitor_service.get_events_at_date(
            competitor,
            future_cutoff,
            before=True
        )
        if e.date > target_date
    ]
    
    return {
        "target_date": target_date.isoformat(),
        "known_at_time": {
            "events": [e.dict() for e in events_at_time],
            "count": len(events_at_time)
        },
        "happened_later": {
            "events": [e.dict() for e in later_events[:10]] if include_future else [],
            "count": len(later_events)
        }
    }


# ============================================================
# STRATEGY ANALYSIS
# ============================================================

@app.get("/api/strategy/{competitor_name}")
async def get_strategy(competitor_name: str):
    """Get current strategy profile."""
    events = competitor_service.get_competitor_events(competitor_name)
    if not events:
        raise HTTPException(status_code=404, detail="No events found for competitor")
    
    profile = strategy_service.detect_strategy_profile(events)
    shifts = strategy_service.detect_strategy_shifts(events)
    
    return {
        "competitor": competitor_name,
        "current_profile": profile.dict(),
        "strategy_shifts": [s.dict() for s in shifts],
        "shift_count": len(shifts)
    }


@app.get("/api/strategy/{competitor_name}/first-signal")
async def get_first_signal(
    competitor_name: str,
    strategy: str = Query("enterprise")
):
    """Find first signal of a strategy direction."""
    events = competitor_service.get_competitor_events(competitor_name)
    if not events:
        raise HTTPException(status_code=404, detail="No events found")
    
    first_event = strategy_service.find_first_signal(events, strategy)
    
    if not first_event:
        return {
            "competitor": competitor_name,
            "strategy": strategy,
            "first_signal": None,
            "message": f"No clear signals found for {strategy} strategy"
        }
    
    # Get timeline from first signal to now
    timeline = [
        e for e in events
        if e.date >= first_event.date
    ]
    
    return {
        "competitor": competitor_name,
        "strategy": strategy,
        "first_signal": first_event.dict(),
        "days_since_first_signal": (datetime.utcnow() - first_event.date).days,
        "timeline_since_signal": [e.dict() for e in timeline[:10]]
    }


# ============================================================
# PATTERNS
# ============================================================

@app.get("/api/patterns")
async def get_patterns(competitor: Optional[str] = Query(None)):
    """Detect recurring patterns."""
    if competitor:
        events = competitor_service.get_competitor_events(competitor)
    else:
        events = competitor_service.get_all_events()
    
    if not events:
        return {"patterns": [], "count": 0}
    
    patterns = pattern_service.detect_patterns(events, sequence_length=2, min_frequency=1)
    
    return {
        "patterns": [p.dict() for p in patterns],
        "count": len(patterns)
    }


@app.get("/api/patterns/{pattern_id}/history")
async def get_pattern_history(
    pattern_id: str,
    competitor: Optional[str] = Query(None)
):
    """Get historical occurrences of a pattern."""
    events = competitor_service.get_competitor_events(competitor) if competitor else competitor_service.get_all_events()
    
    patterns = pattern_service.detect_patterns(events)
    pattern = next((p for p in patterns if p.id == pattern_id), None)
    
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")
    
    occurrences = pattern_service.find_sequence_occurrences(events, pattern.sequence)
    
    return {
        "pattern": pattern.dict(),
        "occurrences": [
            {
                "events": [e.dict() for e in occurrence],
                "start_date": occurrence[0].date.isoformat(),
                "end_date": occurrence[-1].date.isoformat()
            }
            for occurrence in occurrences
        ],
        "occurrence_count": len(occurrences)
    }


# ============================================================
# WE'VE SEEN THIS BEFORE
# ============================================================

@app.post("/api/similarity-search")
async def find_similar_situations(payload: dict = Body(...)):
    competitor = payload.get("competitor")
    event_id = payload.get("event_id")
    if not competitor or not event_id:
        raise HTTPException(status_code=400, detail="competitor and event_id are required")
    """Find historical situations similar to current event."""
    event = competitor_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Find similar events
    similar = competitor_service.find_similar_events(event_id, limit=5)
    
    # For each similar event, get its timeline context
    similar_with_context = []
    for sim_event in similar:
        all_events = competitor_service.get_competitor_events(sim_event.competitor)
        sim_index = next(
            (i for i, e in enumerate(sorted(all_events, key=lambda x: x.date)) if e.id == sim_event.id),
            -1
        )
        
        events_sorted = sorted(all_events, key=lambda x: x.date)
        
        context = {
            "before": events_sorted[max(0, sim_index-2):sim_index],
            "event": sim_event,
            "after": events_sorted[sim_index+1:sim_index+3]
        }
        similar_with_context.append({
            "similarity": "historical match",
            "event": sim_event.dict(),
            "context": {
                "before": [e.dict() for e in context["before"]],
                "after": [e.dict() for e in context["after"]]
            }
        })
    
    return {
        "current_event": event.dict(),
        "similar_historical_events": similar_with_context,
        "match_count": len(similar_with_context)
    }


# ============================================================
# INVESTIGATION & EVIDENCE
# ============================================================

@app.post("/api/investigate")
async def investigate(hypothesis: str, competitor: Optional[str] = Query(None)):
    """Investigate a hypothesis."""
    if competitor:
        events = competitor_service.get_competitor_events(competitor)
    else:
        events = competitor_service.get_all_events()
    
    analysis = investigation_service.analyze_hypothesis(
        hypothesis,
        events,
        competitor
    )
    
    return {
        "hypothesis": hypothesis,
        "supporting_evidence": [e.dict() for e in analysis["supporting_evidence"]],
        "contradicting_evidence": [e.dict() for e in analysis["contradicting_evidence"]],
        "unknowns": analysis["unknowns"],
        "confidence": analysis["confidence"],
        "strength": analysis["strength"]
    }


@app.post("/api/investigate/prove")
async def prove_hypothesis(hypothesis: str, competitor: Optional[str] = Query(None)):
    """Find evidence supporting a hypothesis."""
    if competitor:
        events = competitor_service.get_competitor_events(competitor)
    else:
        events = competitor_service.get_all_events()
    
    evidence = investigation_service.prove_hypothesis(hypothesis, events, competitor)
    
    return {
        "hypothesis": hypothesis,
        "evidence": [e.dict() for e in evidence],
        "evidence_count": len(evidence)
    }


@app.post("/api/investigate/disprove")
async def disprove_hypothesis(hypothesis: str, competitor: Optional[str] = Query(None)):
    """Find evidence contradicting a hypothesis."""
    if competitor:
        events = competitor_service.get_competitor_events(competitor)
    else:
        events = competitor_service.get_all_events()
    
    evidence = investigation_service.disprove_hypothesis(hypothesis, events, competitor)
    
    return {
        "hypothesis": hypothesis,
        "contradicting_evidence": [e.dict() for e in evidence],
        "contradiction_count": len(evidence)
    }


@app.get("/api/investigate/gaps")
async def identify_gaps(competitor: Optional[str] = Query(None)):
    """Identify what we don't know."""
    if competitor:
        events = competitor_service.get_competitor_events(competitor)
    else:
        events = competitor_service.get_all_events()
    
    gaps = investigation_service.identify_gaps(events, competitor)
    
    return {
        "competitor": competitor,
        "gaps": gaps,
        "research_questions": [g.replace("Unknown: ", "") for g in gaps]
    }


# ============================================================
# MEMORY
# ============================================================

@app.get("/api/memory/status")
async def memory_status():
    """Get memory service status."""
    return hindsight_service.get_memory_status()


@app.get("/api/memory/all")
async def get_all_memories(competitor: Optional[str] = Query(None)):
    """Get all stored memories."""
    memories = await hindsight_service.get_all_memories(competitor)
    
    return {
        "memories": memories,
        "count": len(memories),
        "competitor": competitor
    }


@app.post("/api/memory/recall")
async def recall_memory(query: str, competitor: Optional[str] = Query(None)):
    """Recall relevant memories from Hindsight or the transparent demo memory."""
    memories = await hindsight_service.recall_similar(query, competitor=competitor, limit=12)
    return {"query": query, "memories": memories, "count": len(memories), "source": hindsight_service.get_memory_status()["mode"]}


@app.post("/api/memory/retain")
async def retain_event(event: dict):
    """Store an event in Hindsight memory."""
    result = await hindsight_service.retain_event(event)
    
    return {
        "success": result["success"],
        "memory_id": result["memory_id"],
        "source": result.get("source", "hindsight")
    }


# ============================================================
# DEMO MODE
# ============================================================

@app.get("/api/demo/story")
async def get_demo_story():
    """Get curated demo story flow."""
    # ApexAI's transformation story (best story for demo)
    apexai_events = sorted(
        [e for e in competitor_service.get_all_events() if e.competitor == "ApexAI"],
        key=lambda e: e.date
    )
    
    return {
        "title": "ApexAI: From SMB to Enterprise",
        "description": "Watch how ApexAI strategically shifted from SMB-focused to enterprise-first over 6 months",
        "competitor": "ApexAI",
        "events": [e.dict() for e in apexai_events],
        "demo_duration_minutes": 3,
        "key_moments": [
            {"month": "January", "event": "First AI hiring", "event_id": apexai_events[0].id if apexai_events else None},
            {"month": "March", "event": "AI feature launch", "event_id": None},
            {"month": "April", "event": "Enterprise sales hire", "event_id": None},
            {"month": "June", "event": "Enterprise suite launch", "event_id": None}
        ]
    }


@app.post("/api/demo/query")
async def demo_query(question: str):
    """Query the system with a demo question."""
    question_lower = question.lower()
    apexai_events = sorted(
        [e for e in competitor_service.get_all_events() if e.competitor == "ApexAI"],
        key=lambda e: e.date
    )
    
    if "what changed" in question_lower or "changed about" in question_lower:
        profile = strategy_service.detect_strategy_profile(apexai_events)
        shifts = strategy_service.detect_strategy_shifts(apexai_events)
        return {
            "question": question,
            "answer": f"ApexAI shifted from general market to {profile.primary_strategy}",
            "strategy_shifts": [s.dict() for s in shifts],
            "events_supporting": [e.dict() for e in apexai_events[-3:]]
        }
    
    elif "seen this before" in question_lower or "similar" in question_lower:
        current = apexai_events[-1] if apexai_events else None
        recalled = await hindsight_service.recall_similar(
            query=f"{current.title if current else question} {current.description if current else question}",
            competitor="ApexAI",
            limit=5
        )
        similar = competitor_service.find_similar_events(current.id, limit=3) if current else []
        matches = recalled or [e.dict() for e in similar]
        return {
            "question": question,
            "answer": "Yes, similar historical context was found in competitive memory.",
            "historical_matches": matches,
            "match_count": len(matches),
            "memory_source": hindsight_service.get_memory_status()["mode"]
        }

    elif "happened last time" in question_lower or "last time" in question_lower:
        current = apexai_events[-1] if apexai_events else None
        similar = competitor_service.find_similar_events(current.id, limit=1) if current else []
        historical = similar[0] if similar else None
        return {
            "question": question,
            "answer": historical.outcome if historical and historical.outcome else (historical.description if historical else "No earlier matching event was found."),
            "historical_matches": [historical.dict()] if historical else []
        }

    elif "first signal" in question_lower or "started" in question_lower:
        first = strategy_service.find_first_signal(apexai_events, "enterprise")
        return {
            "question": question,
            "answer": "The earliest visible enterprise signal was identified from the retained event history.",
            "first_signal": first.dict() if first else None
        }

    elif "missing" in question_lower or "don't know" in question_lower:
        gaps = investigation_service.identify_gaps(apexai_events, "ApexAI")
        return {
            "question": question,
            "answer": "Several unexplained signals remain",
            "unknowns": gaps
        }

    else:
        return {
            "question": question,
            "answer": "Query processed",
            "data": apexai_events[-5:]
        }


# ============================================================
# COMPARISON
# ============================================================

@app.get("/api/comparison/war-room")
async def get_war_room():
    """Get multi-competitor comparison for war room."""
    competitors = competitor_service.get_all_competitors()
    
    comparison_data = []
    for comp in competitors:
        events = competitor_service.get_competitor_events(comp.name)
        recent = competitor_service.get_recent_events(comp.name, days=60)
        profile = strategy_service.detect_strategy_profile(events)
        
        comparison_data.append({
            "competitor": comp.name,
            "strategy": profile.primary_strategy,
            "recent_activity": len(recent),
            "recent_events": [e.dict() for e in recent[:3]],
            "profile": profile.dict()
        })
    
    return {
        "competitors": comparison_data,
        "count": len(comparison_data)
    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Competitive Memory",
        "tagline": "Your company's competitive memory",
        "version": "1.0.0",
        "status": "running",
        "memory_mode": hindsight_service.get_memory_status()["mode"] if hindsight_service else "unknown"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
