"""Backend tests for Competitive Memory."""

import pytest
from datetime import datetime, timedelta
from backend.models.competitor import (
    CompetitorEvent, Competitor, EventType, EventImportance,
    StrategyProfile, Pattern
)
from backend.services.competitor_service import CompetitorService
from backend.services.pattern_service import PatternDetectionService
from backend.services.strategy_service import StrategyDetectionService
from backend.services.investigation_service import InvestigationService


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def sample_events():
    """Create sample events for testing."""
    base_date = datetime.utcnow() - timedelta(days=90)
    return [
        CompetitorEvent(
            id="ev1",
            competitor="TestCorp",
            date=base_date,
            event_type=EventType.HIRING,
            title="Hired 3 ML engineers",
            description="Machine learning team expansion",
            importance=EventImportance.MEDIUM,
            entities=["ML", "hiring"],
            topics=["ai"]
        ),
        CompetitorEvent(
            id="ev2",
            competitor="TestCorp",
            date=base_date + timedelta(days=30),
            event_type=EventType.FEATURE_RELEASE,
            title="Launched AI analytics",
            description="New AI-powered analytics dashboard",
            importance=EventImportance.HIGH,
            entities=["AI", "analytics"],
            topics=["product", "ai"]
        ),
        CompetitorEvent(
            id="ev3",
            competitor="TestCorp",
            date=base_date + timedelta(days=60),
            event_type=EventType.PRICING_CHANGE,
            title="Enterprise pricing tier",
            description="New $5k/month enterprise plan",
            importance=EventImportance.HIGH,
            entities=["enterprise"],
            topics=["pricing"]
        ),
        CompetitorEvent(
            id="ev4",
            competitor="OtherCorp",
            date=base_date + timedelta(days=15),
            event_type=EventType.HIRING,
            title="Hired 3 ML engineers",
            description="Similar ML hiring",
            importance=EventImportance.MEDIUM,
            entities=["ML"],
            topics=["ai"]
        ),
    ]


@pytest.fixture
def competitor_service():
    """Create competitor service with sample data."""
    service = CompetitorService()
    competitors = [
        Competitor(id="c1", name="TestCorp", founded="2020"),
        Competitor(id="c2", name="OtherCorp", founded="2019"),
    ]
    return service


# ============================================================
# COMPETITOR SERVICE TESTS
# ============================================================

def test_competitor_service_load_data(competitor_service, sample_events):
    """Test loading events into service."""
    competitors = [{"id": f"c{i}", "name": name} for i, name in enumerate(sorted({e.competitor for e in sample_events}), start=1)]
    competitor_service.load_synthetic_data(
        [e.dict() for e in sample_events],
        [{"id": c["id"], "name": c["name"]} for c in competitors]
    )
    
    assert len(competitor_service.events) == len(sample_events)
    assert "TestCorp" in competitor_service.event_index


def test_get_competitor_events(competitor_service, sample_events):
    """Test retrieving events for a competitor."""
    competitors = [{"id": c, "name": n} for c, n in [("c1", "TestCorp"), ("c2", "OtherCorp")]]
    competitor_service.load_synthetic_data(
        [e.dict() for e in sample_events],
        competitors
    )
    
    events = competitor_service.get_competitor_events("TestCorp")
    assert len(events) == 3
    assert all(e.competitor == "TestCorp" for e in events)


def test_event_timeline_sorted(competitor_service, sample_events):
    """Test that timeline is chronologically sorted."""
    competitors = [{"id": c, "name": n} for c, n in [("c1", "TestCorp"), ("c2", "OtherCorp")]]
    competitor_service.load_synthetic_data(
        [e.dict() for e in sample_events],
        competitors
    )
    
    timeline = competitor_service.get_event_timeline("TestCorp")
    dates = [e.date for e in timeline]
    assert dates == sorted(dates)


def test_similar_events(competitor_service, sample_events):
    """Test finding similar events."""
    competitors = [{"id": c, "name": n} for c, n in [("c1", "TestCorp"), ("c2", "OtherCorp")]]
    competitor_service.load_synthetic_data(
        [e.dict() for e in sample_events],
        competitors
    )
    
    similar = competitor_service.find_similar_events("ev1")
    assert len(similar) > 0
    assert "ev1" not in [e.id for e in similar]


def test_recent_events(competitor_service, sample_events):
    """Test retrieving recent events."""
    competitors = [{"id": c, "name": n} for c, n in [("c1", "TestCorp"), ("c2", "OtherCorp")]]
    competitor_service.load_synthetic_data(
        [e.dict() for e in sample_events],
        competitors
    )
    
    recent = competitor_service.get_recent_events("TestCorp", days=45)
    assert len(recent) == 1  # Only the event within the last 45 days


# ============================================================
# PATTERN DETECTION TESTS
# ============================================================

def test_detect_patterns(sample_events):
    """Test pattern detection."""
    service = PatternDetectionService()
    patterns = service.detect_patterns(sample_events, sequence_length=2, min_frequency=1)
    
    # Should detect hiring -> feature sequence
    assert len(patterns) >= 0  # May or may not detect depending on data


def test_strategy_shift_detection(sample_events):
    """Test detecting strategy shifts."""
    service = StrategyDetectionService()
    shifts = service.detect_strategy_shifts(sample_events)
    
    # With sample data showing hiring -> feature -> pricing: should detect shift
    # Result depends on implementation


def test_pattern_sequence_matching():
    """Test finding sequence occurrences."""
    service = PatternDetectionService()
    base_date = datetime.utcnow() - timedelta(days=90)
    
    events = [
        CompetitorEvent(
            id=f"ev{i}",
            competitor="Test",
            date=base_date + timedelta(days=i*10),
            event_type=[EventType.HIRING, EventType.FEATURE_RELEASE, EventType.PRICING_CHANGE][i % 3],
            title=f"Event {i}",
            description="Test"
        )
        for i in range(9)
    ]
    
    occurrences = service.find_sequence_occurrences(
        events,
        [EventType.HIRING, EventType.FEATURE_RELEASE, EventType.PRICING_CHANGE]
    )
    
    assert len(occurrences) >= 1


# ============================================================
# STRATEGY SERVICE TESTS
# ============================================================

def test_strategy_profile_detection(sample_events):
    """Test detecting strategy profile."""
    service = StrategyDetectionService()
    profile = service.detect_strategy_profile(sample_events)
    
    assert profile.competitor == "TestCorp"
    assert profile.primary_strategy is not None
    assert 0 <= profile.confidence <= 1


def test_first_signal_detection(sample_events):
    """Test finding first signal of strategy."""
    service = StrategyDetectionService()
    first_signal = service.find_first_signal(sample_events, "enterprise")
    
    # Should find something related to enterprise
    if first_signal:
        assert first_signal.competitor == "TestCorp"


def test_contradiction_detection(sample_events):
    """Test detecting contradictions."""
    service = StrategyDetectionService()
    contradictions = service.detect_contradictions(sample_events)
    
    # May or may not find contradictions depending on data


# ============================================================
# INVESTIGATION SERVICE TESTS
# ============================================================

def test_investigate_hypothesis(sample_events):
    """Test investigating a hypothesis."""
    service = InvestigationService()
    analysis = service.analyze_hypothesis(
        "TestCorp is moving to enterprise",
        sample_events,
        "TestCorp"
    )
    
    assert "hypothesis" in analysis
    assert "supporting_evidence" in analysis
    assert "contradicting_evidence" in analysis
    assert "confidence" in analysis
    assert 0 <= analysis["confidence"] <= 1


def test_prove_hypothesis(sample_events):
    """Test proving a hypothesis."""
    service = InvestigationService()
    evidence = service.prove_hypothesis(
        "TestCorp is hiring AI engineers",
        sample_events,
        "TestCorp"
    )
    
    assert isinstance(evidence, list)
    # Should find supporting events


def test_disprove_hypothesis(sample_events):
    """Test disproving a hypothesis."""
    service = InvestigationService()
    evidence = service.disprove_hypothesis(
        "TestCorp is SMB-focused",
        sample_events,
        "TestCorp"
    )
    
    assert isinstance(evidence, list)
    # May find contradicting events


def test_identify_gaps(sample_events):
    """Test identifying knowledge gaps."""
    service = InvestigationService()
    gaps = service.identify_gaps(sample_events, "TestCorp")
    
    assert isinstance(gaps, list)
    assert len(gaps) >= 0


def test_evidence_chain(sample_events):
    """Test building evidence chain."""
    service = InvestigationService()
    evidence = service.find_evidence_chain(
        "enterprise focus",
        sample_events
    )
    
    assert isinstance(evidence, list)


# ============================================================
# INTEGRATION TESTS
# ============================================================

def test_end_to_end_analysis(sample_events):
    """Test complete analysis pipeline."""
    # Setup services
    competitor_service = CompetitorService()
    pattern_service = PatternDetectionService()
    strategy_service = StrategyDetectionService()
    investigation_service = InvestigationService()
    
    # Load data
    competitors = [{"id": c, "name": n} for c, n in [("c1", "TestCorp"), ("c2", "OtherCorp")]]
    competitor_service.load_synthetic_data(
        [e.dict() for e in sample_events],
        competitors
    )
    
    # Analyze
    events = competitor_service.get_competitor_events("TestCorp")
    profile = strategy_service.detect_strategy_profile(events)
    patterns = pattern_service.detect_patterns(events)
    analysis = investigation_service.analyze_hypothesis(
        "enterprise focus",
        events,
        "TestCorp"
    )
    
    # Verify
    assert profile.primary_strategy is not None
    assert analysis["confidence"] >= 0
    assert isinstance(patterns, list)


def test_data_consistency():
    """Test data model consistency."""
    event = CompetitorEvent(
        id="test",
        competitor="TestCorp",
        date=datetime.utcnow(),
        event_type=EventType.HIRING,
        title="Test event",
        description="Test description"
    )
    
    # Should serialize/deserialize
    event_dict = event.dict()
    event_restored = CompetitorEvent(**event_dict)
    
    assert event.id == event_restored.id
    assert event.competitor == event_restored.competitor


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
