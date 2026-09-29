export interface CompetitorEvent {
  id: string
  competitor: string
  date: string
  event_type: string
  title: string
  description: string
  source: string
  importance: string
  entities: string[]
  topics: string[]
  outcome?: string
}

export interface Competitor {
  id: string
  name: string
  description: string
  ai_investment_score: number
  enterprise_focus_score: number
  pricing_aggression_score: number
  product_velocity_score: number
  hiring_activity_score: number
  marketing_intensity_score: number
}

export interface StrategyProfile {
  competitor: string
  primary_strategy: string
  pricing_model: string
  target_customer: string
  product_focus: string
  go_to_market: string
  confidence: number
}

export interface StrategyShift {
  competitor: string
  from_strategy: string
  to_strategy: string
  start_date: string
  signals: string[]
  confidence: number
}

export interface Pattern {
  id: string
  name: string
  description?: string
  sequence: string[]
  frequency: number
  competitors?: string[]
  typical_duration_days?: number
  outcomes?: string[]
  confidence: number
}

export interface Evidence {
  id: string
  event_id: string
  event_title: string
  competitor: string
  date: string
  event_type: string
  strength: string
  explanation: string
}

export interface Investigation {
  hypothesis: string
  supporting_evidence: Evidence[]
  contradicting_evidence: Evidence[]
  unknowns: string[]
  confidence: number
  strength: string
}

export interface MemoryStatus {
  connected: boolean
  demo_mode: boolean
  mode: string
  timestamp: string
}
