# Architecture

Competitive Memory is built on a decoupled full-stack architecture where persistent memory is the foundational primitive.

```
┌─────────────────────────────────────────────────────────────┐
│                    React 18 + Vite UI                       │
│  (Timeline, Strategy, Investigate, War Room, Time Machine)  │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / REST API
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI Backend Engine                   │
├─────────────────────────────────────────────────────────────┤
│  • CompetitorService     • StrategyService                  │
│  • PatternService        • InvestigationService             │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                  Hindsight Memory Layer                     │
│  (Hindsight Persistent API / Transparent Demo Fallback)     │
└─────────────────────────────────────────────────────────────┘
```

## The Memory Loop

1. **Competitive Event Ingestion**: Signals (hiring, product launches, pricing shifts, partnerships, funding) are normalized into `CompetitorEvent` objects.
2. **Retain Memory**: Events are embedded and stored in Hindsight memory banks (`/v1/default/banks/{bank_id}/memories`) with rich metadata.
3. **Historical Recall**: Queries retrieve semantically similar historical events and precedents.
4. **Pattern & Strategy Detection**: Sequential algorithms analyze recurring event sequences and strategic pivots over time.
5. **Evidence-Based Reasoning**: The investigation engine weighs supporting vs. contradicting evidence from memory to validate or disprove market hypotheses.
6. **Continuous Insight Generation**: Analysis conclusions are retained back into memory for future competitive queries.

## Service Breakdown

### 1. `HindsightMemoryService` (`backend/services/hindsight_service.py`)
- Manages connection to Hindsight Cloud API (`https://api.hindsight.vectorize.io`).
- Implements `retain_event`, `recall_similar`, `recall_pattern`, `store_analysis`, and `get_memory_status`.
- Provides transparent fallback to Demo Memory Mode when API credentials are not provided.

### 2. `CompetitorService` (`backend/services/competitor_service.py`)
- Maintains competitor state, historical event records, and filtering across dimensions (importance, event type, time range).
- Implements similarity calculation across competitor actions.

### 3. `StrategyService` (`backend/services/strategy_service.py`)
- Analyzes event distribution to determine primary and secondary strategic focus (AI-first, Enterprise, SMB, Infrastructure).
- Detects strategic shifts and traces back to the exact "First Signal" that preceded a pivot.

### 4. `PatternService` (`backend/services/pattern_service.py`)
- Scans event sequences across competitors to find multi-step behavioral patterns (e.g., Hiring → Feature Launch → Pricing Tier → Enterprise Product).

### 5. `InvestigationService` (`backend/services/investigation_service.py`)
- Evaluates user-submitted hypotheses against the evidence repository.
- Partitions evidence into supporting, contradicting, and knowledge gap unknowns.
