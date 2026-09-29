import * as Types from '../types'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  })

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }

  return response.json()
}

export const api = {
  // Status & Health
  async getHealth() {
    return fetchAPI('/health')
  },

  async getMemoryStatus(): Promise<Types.MemoryStatus> {
    return fetchAPI('/api/memory/status')
  },

  // Competitors
  async getCompetitors(): Promise<{ competitors: Types.Competitor[]; count: number }> {
    return fetchAPI('/api/competitors')
  },

  async getCompetitorDetail(name: string) {
    return fetchAPI(`/api/competitors/${name}`)
  },

  // Timeline & Events
  async getTimeline(competitor?: string, days?: number) {
    const params = new URLSearchParams()
    if (competitor) params.append('competitor', competitor)
    if (days) params.append('days', days.toString())

    return fetchAPI(`/api/timeline?${params.toString()}`)
  },

  async getEvent(eventId: string) {
    return fetchAPI(`/api/events/${eventId}`)
  },

  // Time Machine
  async timeMachine(competitor: string, date: string, includeFuture?: boolean) {
    const params = new URLSearchParams({
      competitor,
      date,
      ...(includeFuture && { include_future: 'true' })
    })

    return fetchAPI(`/api/time-machine?${params.toString()}`)
  },

  // Strategy
  async getStrategy(competitorName: string) {
    return fetchAPI(`/api/strategy/${competitorName}`)
  },

  async getFirstSignal(competitorName: string, strategy: string = 'enterprise') {
    return fetchAPI(`/api/strategy/${competitorName}/first-signal?strategy=${strategy}`)
  },

  // Patterns
  async getPatterns(competitor?: string) {
    const params = new URLSearchParams()
    if (competitor) params.append('competitor', competitor)

    return fetchAPI(`/api/patterns?${params.toString()}`)
  },

  async getPatternHistory(patternId: string, competitor?: string) {
    const params = new URLSearchParams()
    if (competitor) params.append('competitor', competitor)

    return fetchAPI(`/api/patterns/${patternId}/history?${params.toString()}`)
  },

  // Similarity
  async findSimilarSituations(competitor: string, eventId: string) {
    return fetchAPI('/api/similarity-search', {
      method: 'POST',
      body: JSON.stringify({ competitor, event_id: eventId })
    })
  },

  // Investigation
  async investigate(hypothesis: string, competitor?: string) {
    const params = new URLSearchParams()
    if (competitor) params.append('competitor', competitor)

    return fetchAPI(`/api/investigate?hypothesis=${encodeURIComponent(hypothesis)}&${params.toString()}`, {
      method: 'POST'
    })
  },

  async proveHypothesis(hypothesis: string, competitor?: string) {
    const params = new URLSearchParams()
    if (competitor) params.append('competitor', competitor)

    return fetchAPI(`/api/investigate/prove?hypothesis=${encodeURIComponent(hypothesis)}&${params.toString()}`, {
      method: 'POST'
    })
  },

  async disproveHypothesis(hypothesis: string, competitor?: string) {
    const params = new URLSearchParams()
    if (competitor) params.append('competitor', competitor)

    return fetchAPI(`/api/investigate/disprove?hypothesis=${encodeURIComponent(hypothesis)}&${params.toString()}`, {
      method: 'POST'
    })
  },

  async identifyGaps(competitor?: string) {
    const params = new URLSearchParams()
    if (competitor) params.append('competitor', competitor)

    return fetchAPI(`/api/investigate/gaps?${params.toString()}`)
  },

  // Memory
  async recallMemory(query: string, competitor?: string) {
    const params = new URLSearchParams({ query })
    if (competitor) params.append('competitor', competitor)
    return fetchAPI(`/api/memory/recall?${params.toString()}`, { method: 'POST' })
  },

  async getAllMemories(competitor?: string) {
    const params = new URLSearchParams()
    if (competitor) params.append('competitor', competitor)

    return fetchAPI(`/api/memory/all?${params.toString()}`)
  },

  async retainEvent(event: any) {
    return fetchAPI('/api/memory/retain', {
      method: 'POST',
      body: JSON.stringify(event)
    })
  },

  // Demo
  async getDemoStory() {
    return fetchAPI('/api/demo/story')
  },

  async demoQuery(question: string) {
    return fetchAPI(`/api/demo/query?question=${encodeURIComponent(question)}`, {
      method: 'POST'
    })
  },

  // Comparison
  async getWarRoom() {
    return fetchAPI('/api/comparison/war-room')
  }
}
