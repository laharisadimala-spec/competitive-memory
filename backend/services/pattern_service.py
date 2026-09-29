"""Pattern detection in competitor behavior."""

from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from backend.models.competitor import CompetitorEvent, Pattern, EventType


class PatternDetectionService:
    """Detects recurring patterns in competitor events."""
    
    def __init__(self):
        self.detected_patterns: Dict[str, Pattern] = {}
    
    def detect_patterns(
        self,
        events: List[CompetitorEvent],
        sequence_length: int = 3,
        min_frequency: int = 2
    ) -> List[Pattern]:
        """
        Detect recurring sequences in events.
        
        Args:
            events: List of events (should be chronologically sorted)
            sequence_length: Length of sequences to look for
            min_frequency: Minimum occurrences to count as pattern
        
        Returns:
            List of detected patterns
        """
        if len(events) < sequence_length * min_frequency:
            return []
        
        # Extract event type sequences
        sequences = []
        events_by_date = sorted(events, key=lambda e: e.date)
        
        for i in range(len(events_by_date) - sequence_length + 1):
            sequence = [events_by_date[i + j].event_type for j in range(sequence_length)]
            sequences.append(tuple(sequence))
        
        # Find recurring sequences
        sequence_counts = Counter(sequences)
        patterns = []
        
        for sequence, count in sequence_counts.items():
            if count >= min_frequency:
                pattern = Pattern(
                    id=f"pat_{len(self.detected_patterns)}",
                    name=self._describe_sequence(sequence),
                    description=f"Pattern repeated {count} times",
                    sequence=list(sequence),
                    frequency=count,
                    competitors=self._find_competitors_with_sequence(events, sequence),
                    confidence=min(count / 10.0, 1.0),  # Higher frequency = higher confidence
                )
                patterns.append(pattern)
        
        return sorted(patterns, key=lambda p: p.frequency, reverse=True)
    
    def detect_strategy_shifts(
        self,
        events: List[CompetitorEvent],
        window_days: int = 60
    ) -> List[Tuple[CompetitorEvent, float]]:
        """
        Detect sudden changes in event patterns (potential strategy shifts).
        
        Args:
            events: Chronologically sorted events
            window_days: Window to analyze for rate change
        
        Returns:
            List of events with shift scores
        """
        if len(events) < 2:
            return []
        
        shifts = []
        events_by_date = sorted(events, key=lambda e: e.date)
        
        for i, event in enumerate(events_by_date):
            # Count events of this type before and after
            before_start = event.date - timedelta(days=window_days)
            after_end = event.date + timedelta(days=window_days)
            
            before_count = sum(
                1 for e in events_by_date
                if before_start <= e.date < event.date and e.event_type == event.event_type
            )
            after_count = sum(
                1 for e in events_by_date
                if event.date <= e.date <= after_end and e.event_type == event.event_type
            )
            
            # Calculate shift magnitude
            if before_count > 0:
                shift_score = abs(after_count - before_count) / (before_count + 1)
                if shift_score > 0.5:  # Significant change
                    shifts.append((event, shift_score))
        
        return sorted(shifts, key=lambda x: x[1], reverse=True)
    
    def find_sequence_occurrences(
        self,
        events: List[CompetitorEvent],
        sequence: List[str],
        max_days_between: int = 90
    ) -> List[List[CompetitorEvent]]:
        """
        Find all occurrences of a specific sequence in events.
        
        Args:
            events: Events to search
            sequence: Sequence of event types to find
            max_days_between: Max days allowed between sequence events
        
        Returns:
            List of event sequences matching the pattern
        """
        if len(sequence) < 2 or len(events) < len(sequence):
            return []
        
        events_by_date = sorted(events, key=lambda e: e.date)
        occurrences = []
        
        for i in range(len(events_by_date) - len(sequence) + 1):
            # Check if this is a match
            potential_match = events_by_date[i:i + len(sequence)]
            
            # Verify sequence types match
            if all(potential_match[j].event_type == sequence[j] for j in range(len(sequence))):
                # Check time constraint
                time_span = (potential_match[-1].date - potential_match[0].date).days
                if time_span <= max_days_between:
                    occurrences.append(potential_match)
        
        return occurrences
    
    def compare_patterns(
        self,
        events1: List[CompetitorEvent],
        events2: List[CompetitorEvent],
        sequence_length: int = 3
    ) -> float:
        """
        Compare similarity between two event sequences.
        
        Returns:
            Similarity score (0-1)
        """
        def get_sequence_types(events, length):
            sorted_events = sorted(events, key=lambda e: e.date)
            sequences = []
            for i in range(max(0, len(sorted_events) - length + 1)):
                seq = tuple(sorted_events[i:i + length].event_type for _ in range(length))
                sequences.append(seq)
            return sequences
        
        seq1 = get_sequence_types(events1, sequence_length)
        seq2 = get_sequence_types(events2, sequence_length)
        
        if not seq1 or not seq2:
            return 0.0
        
        # Find common sequences
        common = len(set(seq1) & set(seq2))
        total = len(set(seq1) | set(seq2))
        
        return common / total if total > 0 else 0.0
    
    def get_sequence_outcomes(
        self,
        events: List[CompetitorEvent],
        sequence: List[str]
    ) -> List[str]:
        """Get outcomes that typically follow a sequence."""
        occurrences = self.find_sequence_occurrences(events, sequence)
        
        if not occurrences:
            return []
        
        outcomes = []
        for occurrence in occurrences:
            # Get next event after sequence
            last_event_date = occurrence[-1].date
            following = [
                e for e in events
                if e.date > last_event_date and
                (e.date - last_event_date).days <= 90
            ]
            if following:
                next_event = min(following, key=lambda e: e.date)
                outcomes.append(next_event.title)
        
        return outcomes
    
    def calculate_event_importance_from_patterns(
        self,
        event: CompetitorEvent,
        all_events: List[CompetitorEvent]
    ) -> float:
        """
        Calculate importance based on whether event appears in patterns.
        
        Returns:
            Importance score (0-1)
        """
        score = 0.0
        
        # Check if this event type appears in detected patterns
        patterns = self.detect_patterns(all_events)
        for pattern in patterns:
            if event.event_type in pattern.sequence:
                score += pattern.frequency * 0.1
        
        # Check if this event precedes strategy shifts
        shifts = self.detect_strategy_shifts(all_events)
        for shift_event, shift_score in shifts:
            if shift_event.id == event.id:
                score += shift_score
        
        return min(score, 1.0)
    
    def _describe_sequence(self, sequence: Tuple[str, ...]) -> str:
        """Generate a human-readable description of a sequence."""
        return " → ".join([
            s.replace("_", " ").title()
            for s in sequence
        ])
    
    def _find_competitors_with_sequence(
        self,
        events: List[CompetitorEvent],
        sequence: Tuple[str, ...]
    ) -> List[str]:
        """Find which competitors exhibited this sequence."""
        by_competitor = defaultdict(list)
        for event in events:
            by_competitor[event.competitor].append(event)
        
        competitors = []
        for competitor, comp_events in by_competitor.items():
            occurrences = self.find_sequence_occurrences(
                comp_events,
                list(sequence)
            )
            if occurrences:
                competitors.append(competitor)
        
        return competitors


# Global instance
_pattern_service: Optional[PatternDetectionService] = None

def get_pattern_service() -> PatternDetectionService:
    """Get or create pattern service."""
    global _pattern_service
    if _pattern_service is None:
        _pattern_service = PatternDetectionService()
    return _pattern_service
