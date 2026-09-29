"""Competitor data service."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from backend.models.competitor import (
    CompetitorEvent, Competitor, StrategyProfile, EventType, EventImportance
)


class CompetitorService:
    """Manages competitor data and events."""
    
    def __init__(self):
        self.competitors: Dict[str, Competitor] = {}
        self.events: Dict[str, CompetitorEvent] = {}
        self.event_index: Dict[str, List[str]] = {}  # competitor -> event_ids
    
    def load_synthetic_data(self, events: List[Dict[str, Any]], competitors: List[Dict[str, Any]]):
        """Load synthetic dataset."""
        # Load competitors
        for comp_data in competitors:
            comp = Competitor(**comp_data)
            self.competitors[comp.id] = comp
            self.event_index[comp.name] = []
        
        # Load events
        for event_data in events:
            event = CompetitorEvent(**event_data)
            self.events[event.id] = event
            
            # Index by competitor
            if event.competitor not in self.event_index:
                self.event_index[event.competitor] = []
            self.event_index[event.competitor].append(event.id)
    
    def get_competitor(self, name: str) -> Optional[Competitor]:
        """Get competitor by name."""
        for comp in self.competitors.values():
            if comp.name == name:
                return comp
        return None
    
    def get_all_competitors(self) -> List[Competitor]:
        """Get all competitors."""
        return list(self.competitors.values())
    
    def get_competitor_events(
        self,
        competitor: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_types: Optional[List[str]] = None
    ) -> List[CompetitorEvent]:
        """Get events for a competitor, optionally filtered."""
        event_ids = self.event_index.get(competitor, [])
        events = [self.events[eid] for eid in event_ids if eid in self.events]
        
        # Filter by date
        if start_date:
            events = [e for e in events if e.date >= start_date]
        if end_date:
            events = [e for e in events if e.date <= end_date]
        
        # Filter by type
        if event_types:
            events = [e for e in events if e.event_type in event_types]
        
        # Sort by date
        return sorted(events, key=lambda e: e.date)
    
    def get_event(self, event_id: str) -> Optional[CompetitorEvent]:
        """Get event by ID."""
        return self.events.get(event_id)
    
    def get_events_at_date(
        self,
        competitor: str,
        target_date: datetime,
        before: bool = True
    ) -> List[CompetitorEvent]:
        """
        Get all events for a competitor up to a specific date.
        Useful for "time machine" feature.
        """
        events = self.get_competitor_events(competitor)
        
        if before:
            return [e for e in events if e.date <= target_date]
        else:
            return [e for e in events if e.date >= target_date]
    
    def get_event_timeline(self, competitor: str) -> List[CompetitorEvent]:
        """Get chronological timeline of events."""
        return sorted(
            self.get_competitor_events(competitor),
            key=lambda e: e.date
        )
    
    def find_similar_events(
        self,
        event_id: str,
        limit: int = 5
    ) -> List[CompetitorEvent]:
        """Find events similar to a given event."""
        if event_id not in self.events:
            return []
        
        reference_event = self.events[event_id]
        similar = []
        
        for event in self.events.values():
            if event.id == event_id:
                continue
            
            # Calculate similarity score
            score = 0
            
            # Same event type
            if event.event_type == reference_event.event_type:
                score += 2
            
            # Common topics
            common_topics = set(event.topics) & set(reference_event.topics)
            score += len(common_topics)
            
            # Common entities
            common_entities = set(event.entities) & set(reference_event.entities)
            score += len(common_entities) * 0.5
            
            if score > 0:
                similar.append((event, score))
        
        # Sort by similarity and return top N
        similar.sort(key=lambda x: x[1], reverse=True)
        return [e[0] for e in similar[:limit]]
    
    def get_high_importance_events(
        self,
        competitor: Optional[str] = None,
        limit: int = 20
    ) -> List[CompetitorEvent]:
        """Get most important events."""
        events_list = []
        
        if competitor:
            events_list = self.get_competitor_events(competitor)
        else:
            events_list = list(self.events.values())
        
        # Filter to high importance
        important = [
            e for e in events_list
            if e.importance in [EventImportance.CRITICAL, EventImportance.HIGH]
        ]
        
        # Sort by date, newest first
        important.sort(key=lambda e: e.date, reverse=True)
        
        return important[:limit]
    
    def get_events_by_type(
        self,
        event_type: str,
        competitor: Optional[str] = None
    ) -> List[CompetitorEvent]:
        """Get events of specific type."""
        if competitor:
            events = self.get_competitor_events(competitor)
        else:
            events = list(self.events.values())
        
        return [e for e in events if e.event_type == event_type]
    
    def get_recent_events(
        self,
        competitor: Optional[str] = None,
        days: int = 30
    ) -> List[CompetitorEvent]:
        """Get events from last N days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        if competitor:
            events = self.get_competitor_events(competitor, start_date=cutoff)
        else:
            events = [e for e in self.events.values() if e.date >= cutoff]
        
        return sorted(events, key=lambda e: e.date, reverse=True)
    
    def get_all_events(self) -> List[CompetitorEvent]:
        """Get all events."""
        return list(self.events.values())
    
    def add_event(self, event: CompetitorEvent) -> str:
        """Add a new event to the dataset."""
        self.events[event.id] = event
        
        if event.competitor not in self.event_index:
            self.event_index[event.competitor] = []
        self.event_index[event.competitor].append(event.id)
        
        return event.id


# Global instance
_competitor_service: Optional[CompetitorService] = None

def get_competitor_service() -> CompetitorService:
    """Get or create competitor service."""
    global _competitor_service
    if _competitor_service is None:
        _competitor_service = CompetitorService()
    return _competitor_service
