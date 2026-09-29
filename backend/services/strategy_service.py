"""Strategy detection and analysis service."""

from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from backend.models.competitor import (
    CompetitorEvent, StrategyProfile, StrategyShift, EventType
)


class StrategyDetectionService:
    """Detects strategy changes and builds strategic profiles."""
    
    def detect_strategy_profile(
        self,
        events: List[CompetitorEvent],
        window_days: int = 180
    ) -> StrategyProfile:
        """
        Analyze events to build a strategy profile.
        
        Args:
            events: Recent events (typically from sliding window)
            window_days: Days to consider as "recent"
        
        Returns:
            Current strategy profile
        """
        if not events:
            return StrategyProfile(
                competitor="Unknown",
                primary_strategy="No data",
                pricing_model="Unknown",
                target_customer="Unknown",
                product_focus="Unknown",
                go_to_market="Unknown"
            )
        
        competitor = events[0].competitor if events else "Unknown"
        
        # Analyze dimensions
        ai_investment = self._analyze_ai_investment(events)
        enterprise_focus = self._analyze_enterprise_focus(events)
        pricing_model = self._analyze_pricing_model(events)
        product_focus = self._analyze_product_focus(events)
        go_to_market = self._analyze_go_to_market(events)
        
        # Determine primary strategy
        primary = self._determine_primary_strategy(
            ai_investment,
            enterprise_focus,
            pricing_model,
            product_focus
        )
        
        # Calculate confidence based on evidence
        evidence_count = len(events)
        confidence = min(evidence_count / 10.0, 1.0)
        
        return StrategyProfile(
            competitor=competitor,
            primary_strategy=primary,
            pricing_model=pricing_model,
            target_customer="Enterprise" if enterprise_focus > 0.6 else "SMB",
            product_focus=product_focus,
            go_to_market=go_to_market,
            confidence=confidence,
            evidence_count=evidence_count
        )
    
    def detect_strategy_shifts(
        self,
        events: List[CompetitorEvent],
        min_shift_score: float = 0.6
    ) -> List[StrategyShift]:
        """
        Detect changes in strategy over time.
        
        Args:
            events: All events chronologically sorted
            min_shift_score: Minimum score to count as shift
        
        Returns:
            List of detected strategy shifts
        """
        if len(events) < 10:
            return []
        
        shifts = []
        events_sorted = sorted(events, key=lambda e: e.date)
        
        # Divide events into periods
        period_size = max(1, len(events_sorted) // 3)
        
        if period_size < 1:
            return []
        
        period1 = events_sorted[:period_size]
        period2 = events_sorted[period_size:2*period_size]
        period3 = events_sorted[2*period_size:]
        
        # Analyze shifts between periods
        for prev_period, curr_period, name in [
            (period1, period2, "Early-to-Mid"),
            (period2, period3, "Mid-to-Late")
        ]:
            if not prev_period or not curr_period:
                continue
            
            prev_profile = self.detect_strategy_profile(prev_period)
            curr_profile = self.detect_strategy_profile(curr_period)
            
            # Calculate shift score
            shift_score = self._calculate_strategy_distance(prev_profile, curr_profile)
            
            if shift_score >= min_shift_score:
                signals = self._identify_shift_signals(prev_period, curr_period)
                
                shift = StrategyShift(
                    competitor=events[0].competitor,
                    from_strategy=prev_profile.primary_strategy,
                    to_strategy=curr_profile.primary_strategy,
                    start_date=prev_period[-1].date,
                    end_date=curr_period[-1].date,
                    signals=signals,
                    confidence=shift_score,
                    explanation=f"Shift detected from {prev_profile.primary_strategy} to {curr_profile.primary_strategy}"
                )
                shifts.append(shift)
        
        return shifts
    
    def find_first_signal(
        self,
        events: List[CompetitorEvent],
        target_strategy: str
    ) -> Optional[CompetitorEvent]:
        """
        Find the earliest signal of a strategy direction.
        
        Args:
            events: Events chronologically sorted
            target_strategy: Strategy to find first signal for (e.g., "enterprise")
        
        Returns:
            Earliest event signaling this strategy
        """
        strategy_signals = {
            "enterprise": [
                EventType.PRICING_CHANGE,
                EventType.HIRING,
                EventType.LEADERSHIP_CHANGE,
                EventType.FEATURE_RELEASE,
                EventType.MESSAGING_SHIFT
            ],
            "ai": [
                EventType.HIRING,
                EventType.PARTNERSHIP,
                EventType.FEATURE_RELEASE,
                EventType.MESSAGING_SHIFT,
                EventType.PRODUCT_LAUNCH
            ],
            "acquisition": [
                EventType.ACQUISITION,
                EventType.FUNDING,
                EventType.PARTNERSHIP,
                EventType.HIRING
            ]
        }
        
        target_types = strategy_signals.get(target_strategy.lower(), [])
        
        sorted_events = sorted(events, key=lambda e: e.date)
        
        for event in sorted_events:
            if event.event_type in target_types:
                # Check if keywords in description support the strategy
                keywords = {
                    "enterprise": ["enterprise", "sales", "b2b"],
                    "ai": ["ai", "machine learning", "neural", "llm"],
                    "acquisition": ["acquire", "acquisition", "purchase"]
                }
                
                target_keywords = keywords.get(target_strategy.lower(), [])
                event_text = (event.title + " " + event.description).lower()
                
                if any(kw in event_text for kw in target_keywords):
                    return event
        
        # Fallback: return first event of relevant type
        for event in sorted_events:
            if event.event_type in target_types:
                return event
        
        return None
    
    def detect_contradictions(
        self,
        events: List[CompetitorEvent],
        statements: Optional[List[str]] = None
    ) -> List[Tuple[str, List[CompetitorEvent]]]:
        """
        Find contradictions between stated strategy and observed behavior.
        
        Args:
            events: Observed events
            statements: Previous public statements (optional)
        
        Returns:
            List of (contradiction description, supporting events)
        """
        contradictions = []
        
        # Analyze messaging vs behavior
        messaging_events = [e for e in events if e.event_type == EventType.MESSAGING_SHIFT]
        behavior_events = [e for e in events if e.event_type in [
            EventType.HIRING, EventType.PRODUCT_LAUNCH, EventType.PRICING_CHANGE
        ]]
        
        for msg_event in messaging_events:
            if "SMB" in msg_event.title.upper() or "small" in msg_event.description.lower():
                # Claims SMB focus - check if actions support it
                enterprise_signals = [
                    e for e in behavior_events
                    if e.date > msg_event.date and
                    ("enterprise" in e.description.lower() or "sales" in e.description.lower())
                ]
                if enterprise_signals:
                    contradictions.append((
                        "Messaging claims SMB focus but observed enterprise-focused activities",
                        [msg_event] + enterprise_signals[:2]
                    ))
        
        return contradictions
    
    def _analyze_ai_investment(self, events: List[CompetitorEvent]) -> float:
        """Score AI investment based on events."""
        ai_keywords = ["ai", "machine learning", "llm", "neural", "gpt"]
        ai_events = [
            e for e in events
            if any(kw in (e.title + " " + e.description).lower() for kw in ai_keywords)
        ]
        return min(len(ai_events) * 0.2, 1.0)
    
    def _analyze_enterprise_focus(self, events: List[CompetitorEvent]) -> float:
        """Score enterprise focus based on events."""
        enterprise_keywords = ["enterprise", "sales", "b2b", "pricing", "sales-led"]
        enterprise_events = [
            e for e in events
            if any(kw in (e.title + " " + e.description).lower() for kw in enterprise_keywords)
        ]
        return min(len(enterprise_events) * 0.2, 1.0)
    
    def _analyze_pricing_model(self, events: List[CompetitorEvent]) -> str:
        """Determine pricing model from events."""
        pricing_changes = [e for e in events if e.event_type == EventType.PRICING_CHANGE]
        
        if not pricing_changes:
            return "Unknown"
        
        latest_pricing = pricing_changes[-1].description.lower()
        
        if "enterprise" in latest_pricing or "premium" in latest_pricing:
            return "Enterprise/Premium"
        elif "freemium" in latest_pricing or "free" in latest_pricing:
            return "Freemium"
        else:
            return "Subscription"
    
    def _analyze_product_focus(self, events: List[CompetitorEvent]) -> str:
        """Determine product focus from events."""
        product_events = [
            e for e in events
            if e.event_type in [EventType.PRODUCT_LAUNCH, EventType.FEATURE_RELEASE]
        ]
        
        if not product_events:
            return "General"
        
        text = " ".join([e.title + " " + e.description for e in product_events]).lower()
        
        if "ai" in text or "llm" in text:
            return "AI-first"
        elif "developer" in text or "api" in text:
            return "Developer-focused"
        else:
            return "General"
    
    def _analyze_go_to_market(self, events: List[CompetitorEvent]) -> str:
        """Determine GTM model from events."""
        hiring_events = [e for e in events if e.event_type == EventType.HIRING]
        
        sales_hiring = [
            e for e in hiring_events
            if "sales" in e.description.lower()
        ]
        
        if len(sales_hiring) > len(hiring_events) * 0.5:
            return "Sales-led"
        else:
            return "Self-serve"
    
    def _determine_primary_strategy(
        self,
        ai_score: float,
        enterprise_score: float,
        pricing: str,
        product_focus: str
    ) -> str:
        """Determine primary strategy from component scores."""
        if ai_score > 0.6:
            return "AI-first"
        elif enterprise_score > 0.6:
            if "Premium" in pricing or "Enterprise" in pricing:
                return "Enterprise-Premium"
            return "Enterprise-focused"
        elif "Premium" in pricing:
            return "Premium positioning"
        else:
            return "General market"
    
    def _calculate_strategy_distance(
        self,
        profile1: StrategyProfile,
        profile2: StrategyProfile
    ) -> float:
        """Calculate how different two strategy profiles are."""
        score = 0.0
        
        if profile1.primary_strategy != profile2.primary_strategy:
            score += 0.4
        
        if profile1.pricing_model != profile2.pricing_model:
            score += 0.2
        
        if profile1.target_customer != profile2.target_customer:
            score += 0.2
        
        if profile1.go_to_market != profile2.go_to_market:
            score += 0.2
        
        return min(score, 1.0)
    
    def _identify_shift_signals(
        self,
        prev_events: List[CompetitorEvent],
        curr_events: List[CompetitorEvent]
    ) -> List[str]:
        """Identify what signaled the strategy shift."""
        signals = []
        
        prev_types = set(e.event_type for e in prev_events)
        curr_types = set(e.event_type for e in curr_events)
        
        new_types = curr_types - prev_types
        increased_types = [
            t for t in curr_types & prev_types
            if sum(1 for e in curr_events if e.event_type == t) >
               sum(1 for e in prev_events if e.event_type == t) * 1.5
        ]
        
        for event_type in new_types:
            signals.append(f"New activity: {event_type.replace('_', ' ').title()}")
        
        for event_type in increased_types:
            signals.append(f"Increased: {event_type.replace('_', ' ').title()}")
        
        return signals[:3]  # Return top 3 signals


# Global instance
_strategy_service: Optional[StrategyDetectionService] = None

def get_strategy_service() -> StrategyDetectionService:
    """Get or create strategy service."""
    global _strategy_service
    if _strategy_service is None:
        _strategy_service = StrategyDetectionService()
    return _strategy_service
