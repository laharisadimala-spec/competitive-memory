"""Generate realistic synthetic competitive intelligence dataset."""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import os


def generate_synthetic_dataset() -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Generate a 6-month realistic competitive intelligence dataset.
    
    Competitors:
    - ApexAI: Aggressive AI investment (SMB → Enterprise shift)
    - CloudForge: Stable infrastructure play, incremental improvements
    - DataPulse: Pricing-focused, moving upmarket
    - OrbitWorks: Crisis mode (funding issues) then pivot
    
    Returns:
        (events, competitors)
    """
    
    base_date = datetime.utcnow() - timedelta(days=180)
    
    competitors = [
        {
            "id": "comp_apexai",
            "name": "ApexAI",
            "description": "AI-first analytics platform, formerly SMB-focused",
            "website": "apexai.com",
            "employees_estimate": 150,
            "ai_investment_score": 0.85,
            "enterprise_focus_score": 0.7,
            "pricing_aggression_score": 0.8,
            "product_velocity_score": 0.9,
            "hiring_activity_score": 0.85,
            "marketing_intensity_score": 0.75
        },
        {
            "id": "comp_cloudforge",
            "name": "CloudForge",
            "description": "Cloud infrastructure and DevOps platform",
            "website": "cloudforge.io",
            "employees_estimate": 200,
            "ai_investment_score": 0.4,
            "enterprise_focus_score": 0.6,
            "pricing_aggression_score": 0.3,
            "product_velocity_score": 0.5,
            "hiring_activity_score": 0.4,
            "marketing_intensity_score": 0.3
        },
        {
            "id": "comp_datapulse",
            "name": "DataPulse",
            "description": "Data analytics for growing businesses",
            "website": "datapulse.co",
            "employees_estimate": 120,
            "ai_investment_score": 0.6,
            "enterprise_focus_score": 0.5,
            "pricing_aggression_score": 0.7,
            "product_velocity_score": 0.6,
            "hiring_activity_score": 0.5,
            "marketing_intensity_score": 0.6
        },
        {
            "id": "comp_orbitworks",
            "name": "OrbitWorks",
            "description": "Satellite data and geospatial analytics",
            "website": "orbitworks.space",
            "employees_estimate": 80,
            "ai_investment_score": 0.3,
            "enterprise_focus_score": 0.8,
            "pricing_aggression_score": 0.2,
            "product_velocity_score": 0.2,
            "hiring_activity_score": 0.1,
            "marketing_intensity_score": 0.2
        }
    ]
    
    events = []
    event_id = 0
    
    # ===== APEXAI: AI-first transformation story =====
    # January: Early hiring signals
    events.extend([
        {
            "id": f"event_{event_id}",
            "competitor": "ApexAI",
            "date": base_date + timedelta(days=5),
            "event_type": "hiring",
            "title": "ApexAI hires 3 ML engineers",
            "description": "ApexAI posted openings for 3 machine learning engineers. This is their first significant ML hiring push.",
            "source": "LinkedIn",
            "importance": "medium",
            "entities": ["ApexAI", "machine learning"],
            "topics": ["hiring", "ai"],
            "related_events": [],
            "outcome": None,
            "metrics": {"positions": 3, "level": "mid-senior"}
        }
    ])
    event_id += 1
    
    # February: Website messaging shift
    events.extend([
        {
            "id": f"event_{event_id}",
            "competitor": "ApexAI",
            "date": base_date + timedelta(days=40),
            "event_type": "messaging_shift",
            "title": "ApexAI website emphasizes AI capabilities",
            "description": "Homepage redesign with prominent AI/ML messaging. 'Powered by AI' now in tagline.",
            "source": "Website",
            "importance": "medium",
            "entities": ["ApexAI", "marketing"],
            "topics": ["messaging", "ai"],
            "related_events": [],
            "outcome": None
        }
    ])
    event_id += 1
    
    # March: New AI product feature launch
    events.extend([
        {
            "id": f"event_{event_id}",
            "competitor": "ApexAI",
            "date": base_date + timedelta(days=70),
            "event_type": "feature_release",
            "title": "ApexAI launches AI-powered anomaly detection",
            "description": "New feature uses LLMs for intelligent anomaly detection in datasets. Requires enterprise plan.",
            "source": "Product announcement",
            "importance": "high",
            "entities": ["ApexAI", "LLM", "anomaly detection"],
            "topics": ["product", "ai", "enterprise"],
            "related_events": [],
            "outcome": "Major feature adoption"
        }
    ])
    event_id += 1
    
    # April: Enterprise sales hiring
    events.extend([
        {
            "id": f"event_{event_id}",
            "competitor": "ApexAI",
            "date": base_date + timedelta(days=95),
            "event_type": "hiring",
            "title": "ApexAI hires VP Enterprise Sales",
            "description": "Hired Sarah Chen as VP Enterprise Sales. Previously at Salesforce.",
            "source": "LinkedIn",
            "importance": "high",
            "entities": ["ApexAI", "sales"],
            "topics": ["hiring", "enterprise"],
            "related_events": [],
            "outcome": "Enterprise motion begins"
        }
    ])
    event_id += 1
    
    # April: Pricing change
    events.extend([
        {
            "id": f"event_{event_id}",
            "competitor": "ApexAI",
            "date": base_date + timedelta(days=100),
            "event_type": "pricing_change",
            "title": "ApexAI introduces premium enterprise tier",
            "description": "New 'Enterprise AI' pricing tier at $5k/month. Includes dedicated support and advanced features.",
            "source": "Pricing page",
            "importance": "high",
            "entities": ["ApexAI", "pricing"],
            "topics": ["pricing", "enterprise"],
            "related_events": [],
            "outcome": "Revenue acceleration"
        }
    ])
    event_id += 1
    
    # May: More hiring
    events.extend([
        {
            "id": f"event_{event_id}",
            "competitor": "ApexAI",
            "date": base_date + timedelta(days=125),
            "event_type": "hiring",
            "title": "ApexAI hiring 5 more AI/ML specialists",
            "description": "Posting for 5 roles: prompt engineers, AI research, and MLOps. AI investment accelerating.",
            "source": "LinkedIn",
            "importance": "high",
            "entities": ["ApexAI", "ai research"],
            "topics": ["hiring", "ai"],
            "related_events": [],
            "outcome": None
        }
    ])
    event_id += 1
    
    # May: Partnership
    events.extend([
        {
            "id": f"event_{event_id}",
            "competitor": "ApexAI",
            "date": base_date + timedelta(days=135),
            "event_type": "partnership",
            "title": "ApexAI partners with OpenAI",
            "description": "Integration with OpenAI APIs for enterprise customers. Strategic partnership announced.",
            "source": "Press release",
            "importance": "critical",
            "entities": ["ApexAI", "OpenAI"],
            "topics": ["partnership", "ai"],
            "related_events": [],
            "outcome": "Competitive advantage"
        }
    ])
    event_id += 1
    
    # June: Enterprise product launch
    events.extend([
        {
            "id": f"event_{event_id}",
            "competitor": "ApexAI",
            "date": base_date + timedelta(days=160),
            "event_type": "product_launch",
            "title": "ApexAI Enterprise Suite launched",
            "description": "Full enterprise offering with AI automation, compliance, and advanced analytics. Focus on Fortune 500.",
            "source": "Product launch event",
            "importance": "critical",
            "entities": ["ApexAI", "enterprise"],
            "topics": ["product", "enterprise", "ai"],
            "related_events": [],
            "outcome": "Major market expansion"
        }
    ])
    event_id += 1
    
    # June: Funding
    events.extend([
        {
            "id": f"event_{event_id}",
            "competitor": "ApexAI",
            "date": base_date + timedelta(days=175),
            "event_type": "funding",
            "title": "ApexAI raises $25M Series B",
            "description": "Series B funding round led by Sequoia Capital. Valuation: $250M. Focus on enterprise expansion.",
            "source": "TechCrunch",
            "importance": "critical",
            "entities": ["ApexAI", "funding"],
            "topics": ["funding", "enterprise"],
            "related_events": [],
            "outcome": "Accelerated growth"
        }
    ])
    event_id += 1
    
    # ===== CLOUDFORGE: Steady state story =====
    events.extend([
        {
            "id": f"event_{event_id}",
            "competitor": "CloudForge",
            "date": base_date + timedelta(days=30),
            "event_type": "feature_release",
            "title": "CloudForge releases Kubernetes v2 support",
            "description": "Enhanced support for Kubernetes workloads. Incremental product improvement.",
            "source": "Product blog",
            "importance": "medium",
            "entities": ["CloudForge", "Kubernetes"],
            "topics": ["product", "infrastructure"],
            "related_events": [],
            "outcome": None
        }
    ])
    event_id += 1
    
    events.extend([
        {
            "id": f"event_{event_id}",
            "competitor": "CloudForge",
            "date": base_date + timedelta(days=80),
            "event_type": "hiring",
            "title": "CloudForge hires 2 DevOps engineers",
            "description": "Steady hiring to maintain product support.",
            "source": "LinkedIn",
            "importance": "low",
            "entities": ["CloudForge"],
            "topics": ["hiring"],
            "related_events": [],
            "outcome": None
        }
    ])
    event_id += 1
    
    events.extend([
        {
            "id": f"event_{event_id}",
            "competitor": "CloudForge",
            "date": base_date + timedelta(days=150),
            "event_type": "feature_release",
            "title": "CloudForge adds cost optimization tools",
            "description": "New dashboard showing cost reduction opportunities. Helps with ROI messaging.",
            "source": "Website",
            "importance": "medium",
            "entities": ["CloudForge"],
            "topics": ["product"],
            "related_events": [],
            "outcome": None
        }
    ])
    event_id += 1
    
    # ===== DATAPULSE: Pricing war story =====
    events.extend([
        {
            "id": f"event_{event_id}",
            "competitor": "DataPulse",
            "date": base_date + timedelta(days=15),
            "event_type": "pricing_change",
            "title": "DataPulse slashes SMB pricing by 30%",
            "description": "Aggressive pricing move targeting growing companies. Freemium tier expanded.",
            "source": "Pricing page",
            "importance": "high",
            "entities": ["DataPulse", "pricing"],
            "topics": ["pricing"],
            "related_events": [],
            "outcome": "Market share grab"
        }
    ])
    event_id += 1
    
    events.extend([
        {
            "id": f"event_{event_id}",
            "competitor": "DataPulse",
            "date": base_date + timedelta(days=55),
            "event_type": "marketing_campaign",
            "title": "DataPulse 'Built for Growth' campaign",
            "description": "Major marketing push targeting Series A/B companies.",
            "source": "LinkedIn ads",
            "importance": "medium",
            "entities": ["DataPulse"],
            "topics": ["marketing"],
            "related_events": [],
            "outcome": None
        }
    ])
    event_id += 1
    
    events.extend([
        {
            "id": f"event_{event_id}",
            "competitor": "DataPulse",
            "date": base_date + timedelta(days=110),
            "event_type": "hiring",
            "title": "DataPulse hires 3 salespeople",
            "description": "Building out sales team for upmarket push.",
            "source": "LinkedIn",
            "importance": "medium",
            "entities": ["DataPulse"],
            "topics": ["hiring"],
            "related_events": [],
            "outcome": None
        }
    ])
    event_id += 1
    
    events.extend([
        {
            "id": f"event_{event_id}",
            "competitor": "DataPulse",
            "date": base_date + timedelta(days=140),
            "event_type": "messaging_shift",
            "title": "DataPulse emphasizes 'Enterprise-ready' in messaging",
            "description": "Homepage redesign. New messaging: 'Analytics for enterprises that grew fast'.",
            "source": "Website",
            "importance": "medium",
            "entities": ["DataPulse"],
            "topics": ["messaging"],
            "related_events": [],
            "outcome": None
        }
    ])
    event_id += 1
    
    # ===== ORBITWORKS: Crisis and pivot story =====
    events.extend([
        {
            "id": f"event_{event_id}",
            "competitor": "OrbitWorks",
            "date": base_date + timedelta(days=20),
            "event_type": "funding",
            "title": "OrbitWorks Series A stalled (rumor)",
            "description": "Unconfirmed reports suggest funding round delays. Market conditions cited.",
            "source": "Industry rumors",
            "importance": "high",
            "entities": ["OrbitWorks", "funding"],
            "topics": ["funding"],
            "related_events": [],
            "outcome": "Cash constraints likely"
        }
    ])
    event_id += 1
    
    events.extend([
        {
            "id": f"event_{event_id}",
            "competitor": "OrbitWorks",
            "date": base_date + timedelta(days=65),
            "event_type": "leadership_change",
            "title": "OrbitWorks CEO announces 'strategic pivot'",
            "description": "New direction: moving from consumer-focused to enterprise contracts. Restructuring hinted.",
            "source": "Company blog",
            "importance": "critical",
            "entities": ["OrbitWorks", "ceo"],
            "topics": ["leadership", "strategy"],
            "related_events": [],
            "outcome": "Major pivot"
        }
    ])
    event_id += 1
    
    events.extend([
        {
            "id": f"event_{event_id}",
            "competitor": "OrbitWorks",
            "date": base_date + timedelta(days=90),
            "event_type": "messaging_shift",
            "title": "OrbitWorks emphasizes government/defense contracts",
            "description": "Website reposition. New tagline: 'Mission-critical geospatial for defense and intelligence'.",
            "source": "Website",
            "importance": "high",
            "entities": ["OrbitWorks"],
            "topics": ["messaging"],
            "related_events": [],
            "outcome": None
        }
    ])
    event_id += 1
    
    events.extend([
        {
            "id": f"event_{event_id}",
            "competitor": "OrbitWorks",
            "date": base_date + timedelta(days=130),
            "event_type": "partnership",
            "title": "OrbitWorks partners with Palantir",
            "description": "Integration partnership with Palantir for government sector.",
            "source": "Press release",
            "importance": "high",
            "entities": ["OrbitWorks", "Palantir"],
            "topics": ["partnership"],
            "related_events": [],
            "outcome": "Access to government market"
        }
    ])
    event_id += 1
    
    # ===== Cross-competitor event: Market shift =====
    events.extend([
        {
            "id": f"event_{event_id}",
            "competitor": "General Market",
            "date": base_date + timedelta(days=170),
            "event_type": "market_event",
            "title": "Enterprise buyers shift focus to AI-powered analytics",
            "description": "Gartner research shows 78% of enterprises prioritizing AI in analytics selection.",
            "source": "Gartner report",
            "importance": "critical",
            "entities": ["market", "AI"],
            "topics": ["market", "ai"],
            "related_events": [],
            "outcome": None
        }
    ])
    event_id += 1
    
    return events, competitors


def save_synthetic_data():
    """Save synthetic dataset to JSON files."""
    events, competitors = generate_synthetic_dataset()
    
    data_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(data_dir, "events.json"), "w") as f:
        json.dump(events, f, indent=2, default=str)
    
    with open(os.path.join(data_dir, "competitors.json"), "w") as f:
        json.dump(competitors, f, indent=2)
    
    print(f"Generated {len(events)} events across {len(set(e['competitor'] for e in events))} competitors")


if __name__ == "__main__":
    save_synthetic_data()
