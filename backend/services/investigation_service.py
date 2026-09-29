"""Investigation and evidence analysis service."""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from backend.models.competitor import (
    CompetitorEvent, Investigation, Evidence, EventType
)


class InvestigationService:
    """Manages investigations and evidence analysis."""
    
    def __init__(self):
        self.investigations: Dict[str, Investigation] = {}
    
    def create_investigation(
        self,
        title: str,
        question: str,
        competitor: Optional[str] = None
    ) -> Investigation:
        """Create a new investigation."""
        investigation = Investigation(
            id=f"inv_{len(self.investigations)}",
            title=title,
            question=question,
            competitor=competitor,
            status="open"
        )
        self.investigations[investigation.id] = investigation
        return investigation
    
    def analyze_hypothesis(
        self,
        hypothesis: str,
        events: List[CompetitorEvent],
        competitor: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Analyze a hypothesis against available evidence.
        
        Returns:
            {
                "hypothesis": str,
                "supporting_evidence": List[Evidence],
                "contradicting_evidence": List[Evidence],
                "unknowns": List[str],
                "confidence": float
            }
        """
        supporting = self._find_supporting_evidence(hypothesis, events, competitor)
        contradicting = self._find_contradicting_evidence(hypothesis, events, competitor)
        unknowns = self._identify_unknowns(hypothesis, events, competitor)
        
        # Calculate confidence
        if not supporting and contradicting:
            confidence = 0.0
        elif supporting and not contradicting:
            confidence = 0.8
        elif supporting and contradicting:
            ratio = len(supporting) / (len(supporting) + len(contradicting))
            confidence = 0.5 + (ratio * 0.5)  # 0.5-1.0 range
        else:
            confidence = 0.3
        
        return {
            "hypothesis": hypothesis,
            "supporting_evidence": supporting,
            "contradicting_evidence": contradicting,
            "unknowns": unknowns,
            "confidence": confidence,
            "strength": self._describe_strength(confidence)
        }
    
    def prove_hypothesis(
        self,
        hypothesis: str,
        events: List[CompetitorEvent],
        competitor: Optional[str] = None
    ) -> List[Evidence]:
        """Find all evidence supporting a hypothesis."""
        return self._find_supporting_evidence(hypothesis, events, competitor)
    
    def disprove_hypothesis(
        self,
        hypothesis: str,
        events: List[CompetitorEvent],
        competitor: Optional[str] = None
    ) -> List[Evidence]:
        """Find evidence contradicting a hypothesis."""
        return self._find_contradicting_evidence(hypothesis, events, competitor)
    
    def identify_gaps(
        self,
        events: List[CompetitorEvent],
        competitor: Optional[str] = None
    ) -> List[str]:
        """Identify what we don't know."""
        gaps = []
        
        # Check for unexplained hiring spikes
        hiring_events = [e for e in events if e.event_type == EventType.HIRING]
        if hiring_events:
            high_impact_hiring = []
            for e in hiring_events:
                description = e.description.lower()
                first_token = e.description.split()[0] if e.description.split() else ""
                numeric_spike = first_token.isdigit() and int(first_token) > 2
                if "multiple" in description or numeric_spike:
                    high_impact_hiring.append(e)
            if high_impact_hiring and not any("ai" in e.description.lower() for e in high_impact_hiring):
                gaps.append("Unknown: What is the purpose of recent hiring surge?")
        
        # Check for unexplained pricing changes
        pricing_events = [e for e in events if e.event_type == EventType.PRICING_CHANGE]
        if pricing_events:
            gaps.append("Unknown: Whether pricing changes are market-wide or company-specific strategy")
        
        # Check for isolated features
        feature_events = [e for e in events if e.event_type == EventType.FEATURE_RELEASE]
        if feature_events:
            isolated = [
                e for e in feature_events
                if not any(
                    e.date - timedelta(days=60) <= other.date <= e.date + timedelta(days=60) and other.event_type != EventType.FEATURE_RELEASE
                    for other in events if other.id != e.id
                )
            ]
            if isolated:
                gaps.append("Unknown: Strategic direction behind recent feature releases")
        
        # Check for geographic scope
        messaging_events = [e for e in events if e.event_type == EventType.MESSAGING_SHIFT]
        if messaging_events:
            gaps.append("Unknown: Whether strategy changes apply globally or are region-specific")
        
        return gaps[:3]  # Return top 3 gaps
    
    def find_evidence_chain(
        self,
        insight: str,
        events: List[CompetitorEvent]
    ) -> List[Evidence]:
        """Build a chain of evidence supporting an insight."""
        evidence_list = []
        
        # Map insights to event types
        insight_lower = insight.lower()
        
        if "enterprise" in insight_lower:
            relevant_types = [
                EventType.HIRING, EventType.PRICING_CHANGE,
                EventType.PRODUCT_LAUNCH, EventType.MESSAGING_SHIFT,
                EventType.FEATURE_RELEASE
            ]
        elif "ai" in insight_lower:
            relevant_types = [
                EventType.HIRING, EventType.PARTNERSHIP,
                EventType.FEATURE_RELEASE, EventType.PRODUCT_LAUNCH,
                EventType.MESSAGING_SHIFT
            ]
        elif "product" in insight_lower:
            relevant_types = [
                EventType.PRODUCT_LAUNCH, EventType.FEATURE_RELEASE,
                EventType.HIRING, EventType.PARTNERSHIP
            ]
        else:
            relevant_types = list(EventType)
        
        for i, event in enumerate(sorted(events, key=lambda e: e.date)):
            if event.event_type in relevant_types and any(
                word in (event.title + " " + event.description).lower()
                for word in insight_lower.split()
            ):
                evidence = Evidence(
                    id=f"ev_{i}",
                    event_id=event.id,
                    event_title=event.title,
                    competitor=event.competitor,
                    date=event.date,
                    event_type=event.event_type,
                    supports=insight,
                    strength="strong" if event.importance in ["critical", "high"] else "moderate",
                    explanation=event.description
                )
                evidence_list.append(evidence)
        
        return evidence_list[:5]  # Return top 5 pieces of evidence
    
    def _find_supporting_evidence(
        self,
        hypothesis: str,
        events: List[CompetitorEvent],
        competitor: Optional[str] = None
    ) -> List[Evidence]:
        """Find events that support a hypothesis."""
        hypothesis_lower = hypothesis.lower()
        keywords = set(hypothesis_lower.split())
        
        supporting = []
        
        for event in events:
            if competitor and event.competitor != competitor:
                continue
            
            event_text = (event.title + " " + event.description).lower()
            
            # Check keyword overlap
            keyword_matches = len(keywords & set(event_text.split()))
            
            # Check for relevant event types
            if hypothesis.lower().__contains__("enterprise"):
                if event.event_type in [
                    EventType.PRICING_CHANGE, EventType.HIRING,
                    EventType.FEATURE_RELEASE, EventType.LEADERSHIP_CHANGE
                ]:
                    keyword_matches += 2
            
            if hypothesis.lower().__contains__("ai"):
                if event.event_type in [
                    EventType.HIRING, EventType.PARTNERSHIP,
                    EventType.FEATURE_RELEASE, EventType.PRODUCT_LAUNCH
                ] and "ai" in event_text:
                    keyword_matches += 3
            
            if keyword_matches >= 2:
                strength = "strong" if keyword_matches >= 4 else "moderate"
                supporting.append(Evidence(
                    id=f"sup_{len(supporting)}",
                    event_id=event.id,
                    event_title=event.title,
                    competitor=event.competitor,
                    date=event.date,
                    event_type=event.event_type,
                    supports=hypothesis,
                    strength=strength,
                    explanation=event.description
                ))
        
        return sorted(supporting, key=lambda e: e.date, reverse=True)[:5]
    
    def _find_contradicting_evidence(
        self,
        hypothesis: str,
        events: List[CompetitorEvent],
        competitor: Optional[str] = None
    ) -> List[Evidence]:
        """Find events that contradict a hypothesis."""
        hypothesis_lower = hypothesis.lower()
        contradicting = []
        
        # Simple contradiction logic
        if "smb" in hypothesis_lower:
            # Look for enterprise signals
            for event in events:
                if competitor and event.competitor != competitor:
                    continue
                if "enterprise" in event.description.lower():
                    contradicting.append(Evidence(
                        id=f"con_{len(contradicting)}",
                        event_id=event.id,
                        event_title=event.title,
                        competitor=event.competitor,
                        date=event.date,
                        event_type=event.event_type,
                        supports=hypothesis,
                        strength="strong",
                        explanation="Observed enterprise-focused activity contradicts SMB focus hypothesis"
                    ))
        
        if "stable" in hypothesis_lower or "no change" in hypothesis_lower:
            # Look for significant events
            significant_events = [
                e for e in events
                if e.importance in ["critical", "high"]
            ]
            for event in significant_events:
                if competitor and event.competitor != competitor:
                    continue
                contradicting.append(Evidence(
                    id=f"con_{len(contradicting)}",
                    event_id=event.id,
                    event_title=event.title,
                    competitor=event.competitor,
                    date=event.date,
                    event_type=event.event_type,
                    supports=hypothesis,
                    strength="strong",
                    explanation="Significant activity contradicts stability hypothesis"
                ))
        
        return contradicting[:5]
    
    def _identify_unknowns(
        self,
        hypothesis: str,
        events: List[CompetitorEvent],
        competitor: Optional[str] = None
    ) -> List[str]:
        """Identify gaps in knowledge about a hypothesis."""
        unknowns = []
        
        if "enterprise" in hypothesis.lower():
            unknowns.append("Unknown: Market size and TAM for enterprise segment")
            unknowns.append("Unknown: Pricing strategy details for enterprise tier")
            unknowns.append("Unknown: Timeline for enterprise product maturity")
        
        if "ai" in hypothesis.lower():
            unknowns.append("Unknown: Specific AI technologies being developed")
            unknowns.append("Unknown: Timeline for AI feature rollout")
            unknowns.append("Unknown: Integration strategy with existing products")
        
        return unknowns[:3]
    
    def _describe_strength(self, confidence: float) -> str:
        """Describe hypothesis strength based on confidence."""
        if confidence >= 0.8:
            return "Very Strong"
        elif confidence >= 0.6:
            return "Strong"
        elif confidence >= 0.4:
            return "Moderate"
        elif confidence >= 0.2:
            return "Weak"
        else:
            return "Very Weak"


# Global instance
_investigation_service: Optional[InvestigationService] = None

def get_investigation_service() -> InvestigationService:
    """Get or create investigation service."""
    global _investigation_service
    if _investigation_service is None:
        _investigation_service = InvestigationService()
    return _investigation_service
