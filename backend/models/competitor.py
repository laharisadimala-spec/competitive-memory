"""Competitor and event data models."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Types of competitor events."""
    PRODUCT_LAUNCH = "product_launch"
    FEATURE_RELEASE = "feature_release"
    PRICING_CHANGE = "pricing_change"
    HIRING = "hiring"
    LEADERSHIP_CHANGE = "leadership_change"
    PARTNERSHIP = "partnership"
    ACQUISITION = "acquisition"
    FUNDING = "funding"
    MARKETING_CAMPAIGN = "marketing_campaign"
    WEBSITE_CHANGE = "website_change"
    MESSAGING_SHIFT = "messaging_shift"
    MARKET_EVENT = "market_event"
    STRATEGY_SHIFT = "strategy_shift"


class EventImportance(str, Enum):
    """Importance levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINOR = "minor"


class CompetitorEvent(BaseModel):
    """A single competitor event."""
    id: str = Field(..., description="Unique event ID")
    competitor: str = Field(..., description="Competitor name")
    date: datetime = Field(..., description="When event occurred")
    event_type: EventType = Field(..., description="Type of event")
    title: str = Field(..., description="Short title")
    description: str = Field(..., description="Full description")
    source: str = Field(default="", description="Where information came from")
    importance: EventImportance = Field(default=EventImportance.MEDIUM)
    entities: List[str] = Field(default_factory=list, description="Key entities mentioned")
    topics: List[str] = Field(default_factory=list, description="Topics/categories")
    related_events: List[str] = Field(default_factory=list, description="IDs of related events")
    outcome: Optional[str] = Field(default=None, description="What happened as result")
    metrics: Optional[Dict[str, Any]] = Field(default=None, description="Associated metrics")
    
    class Config:
        use_enum_values = True


class Competitor(BaseModel):
    """Competitor profile."""
    id: str
    name: str
    description: str = ""
    founded: Optional[str] = None
    headquarters: Optional[str] = None
    website: Optional[str] = None
    employees_estimate: Optional[int] = None
    
    # Dynamic strategic profile
    ai_investment_score: float = 0.0  # 0-1
    enterprise_focus_score: float = 0.0  # 0-1
    pricing_aggression_score: float = 0.0  # 0-1
    product_velocity_score: float = 0.0  # 0-1
    hiring_activity_score: float = 0.0  # 0-1
    marketing_intensity_score: float = 0.0  # 0-1
    
    # Metadata
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    event_count: int = 0
    
    class Config:
        use_enum_values = True


class StrategyProfile(BaseModel):
    """Competitor's current strategy profile."""
    competitor: str
    primary_strategy: str  # e.g., "SMB-focused", "Enterprise-first", "AI-first"
    secondary_strategies: List[str] = []
    pricing_model: str  # e.g., "freemium", "premium", "enterprise"
    target_customer: str  # e.g., "SMB", "Enterprise", "Mid-market"
    product_focus: str  # e.g., "General", "AI-first", "Developer-focused"
    go_to_market: str  # e.g., "Self-serve", "Sales-led"
    confidence: float = Field(default=0.0, ge=0, le=1)  # How confident in this profile
    evidence_count: int = 0  # Number of events supporting this profile


class StrategyShift(BaseModel):
    """Detected strategy change."""
    competitor: str
    from_strategy: str
    to_strategy: str
    start_date: datetime
    end_date: Optional[datetime] = None
    signals: List[str] = []  # Event types that signaled this shift
    confidence: float = Field(default=0.0, ge=0, le=1)
    explanation: str = ""


class Pattern(BaseModel):
    """Recurring pattern in competitor behavior."""
    id: str
    name: str
    description: str
    sequence: List[str]  # Event types in order
    frequency: int  # How many times observed
    competitors: List[str]  # Which competitors showed this
    typical_duration_days: Optional[int] = None
    outcomes: List[str] = []  # Common outcomes
    confidence: float = Field(default=0.0, ge=0, le=1)


class Investigation(BaseModel):
    """User investigation/question about competitors."""
    id: str
    title: str
    question: str
    competitor: Optional[str] = None
    status: str = "open"  # open, in_progress, resolved
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    supporting_evidence: List[str] = []  # Event IDs
    contradicting_evidence: List[str] = []  # Event IDs
    unknowns: List[str] = []  # Unresolved questions
    conclusion: Optional[str] = None


class Evidence(BaseModel):
    """Supporting evidence for an insight."""
    id: str
    event_id: str
    event_title: str
    competitor: str
    date: datetime
    event_type: str
    supports: str  # What hypothesis/insight this supports
    strength: str  # "strong", "moderate", "weak"
    explanation: str = ""
