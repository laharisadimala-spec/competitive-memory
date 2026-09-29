"""Hindsight persistent memory integration with a transparent local demo fallback."""
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx

class HindsightMemoryService:
    def __init__(self):
        self.api_key = os.getenv("HINDSIGHT_API_KEY")
        self.bank_id = os.getenv("HINDSIGHT_BANK_ID") or os.getenv("HINDSIGHT_WORKSPACE_ID")
        self.api_base = os.getenv("HINDSIGHT_API_BASE", "https://api.hindsight.vectorize.io").rstrip("/")
        self.demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
        self.connected = bool(self.api_key and self.bank_id and not self.demo_mode)
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        self.client = httpx.AsyncClient(headers=headers, timeout=30.0)
        self.demo_memories: Dict[str, Dict[str, Any]] = {}

    @property
    def bank_path(self) -> str:
        return f"{self.api_base}/v1/default/banks/{self.bank_id}"

    def get_memory_status(self) -> Dict[str, Any]:
        return {
            "connected": self.connected,
            "demo_mode": self.demo_mode or not self.connected,
            "mode": "Hindsight" if self.connected else "Demo Memory Mode",
            "bank_id": self.bank_id if self.connected else None,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _disable_remote(self, error: Exception) -> None:
        print(f"Hindsight unavailable: {error}. Using transparent demo memory fallback.")
        self.connected = False

    async def retain_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        content = (
            f"{event_data.get('competitor')} — {event_data.get('title')}. "
            f"{event_data.get('description')} Event type: {event_data.get('event_type')}. "
            f"Topics: {', '.join(event_data.get('topics') or [])}."
        )
        if self.connected:
            try:
                response = await self.client.post(
                    f"{self.bank_path}/memories",
                    json={"items": [{
                        "content": content,
                        "timestamp": event_data.get("date") or datetime.utcnow().isoformat(),
                        "context": "competitive intelligence event",
                        "metadata": {
                            "event_id": str(event_data.get("id", "")),
                            "competitor": str(event_data.get("competitor", "")),
                            "event_type": str(event_data.get("event_type", "")),
                        },
                    }]},
                )
                response.raise_for_status()
                payload = response.json()
                return {"success": True, "memory_id": payload.get("id") or event_data.get("id"), "source": "hindsight"}
            except (httpx.HTTPError, ValueError) as exc:
                self._disable_remote(exc)
        memory_id = event_data.get("id", f"mem_{len(self.demo_memories)}")
        self.demo_memories[memory_id] = {**event_data, "memory_id": memory_id, "memory_type": "experience", "source": "demo_memory"}
        return {"success": True, "memory_id": memory_id, "source": "demo_memory"}

    async def recall_similar(self, query: str, competitor: Optional[str] = None, event_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        if self.connected:
            try:
                response = await self.client.post(
                    f"{self.bank_path}/memories/recall",
                    json={"query": query, "types": ["world", "experience", "observation"]},
                )
                response.raise_for_status()
                results = response.json().get("results", [])
                output = []
                for item in results:
                    metadata = item.get("metadata") or {}
                    if competitor and metadata.get("competitor") != competitor:
                        continue
                    if event_type and metadata.get("event_type") != event_type:
                        continue
                    output.append(item)
                    if len(output) >= limit:
                        break
                return output
            except (httpx.HTTPError, ValueError) as exc:
                self._disable_remote(exc)
        query_terms = set(query.lower().split())
        scored = []
        for mem in self.demo_memories.values():
            if competitor and mem.get("competitor") != competitor:
                continue
            if event_type and mem.get("event_type") != event_type:
                continue
            text = f"{mem.get('title', '')} {mem.get('description', '')} {mem.get('event_type', '')}".lower()
            score = len(query_terms & set(text.split()))
            if score or not query_terms:
                scored.append((score, mem))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored[:limit]]

    async def recall_pattern(self, pattern_sequence: List[str], competitor: Optional[str] = None) -> List[Dict[str, Any]]:
        return await self.recall_similar(" ".join(pattern_sequence), competitor=competitor, limit=20)

    async def store_analysis(self, competitor: str, analysis_type: str, content: Dict[str, Any]) -> Dict[str, Any]:
        text = f"Competitive analysis for {competitor}. Type: {analysis_type}. Content: {content}"
        if self.connected:
            try:
                response = await self.client.post(f"{self.bank_path}/memories", json={"items": [{"content": text, "context": f"competitive {analysis_type} analysis"}]})
                response.raise_for_status()
                return {"success": True, "id": response.json().get("id"), "source": "hindsight"}
            except (httpx.HTTPError, ValueError) as exc:
                self._disable_remote(exc)
        memory_id = f"analysis_{len(self.demo_memories)}"
        self.demo_memories[memory_id] = {"competitor": competitor, "type": analysis_type, "content": content, "timestamp": datetime.utcnow().isoformat(), "memory_id": memory_id, "memory_type": "observation", "source": "demo_memory"}
        return {"success": True, "id": memory_id, "source": "demo_memory"}

    async def get_all_memories(self, competitor: Optional[str] = None) -> List[Dict[str, Any]]:
        if self.connected:
            try:
                return await self.recall_similar(f"competitive history {competitor or ''}", competitor=competitor, limit=50)
            except Exception as exc:
                self._disable_remote(exc)
        return [m for m in self.demo_memories.values() if not competitor or m.get("competitor") == competitor]

    async def close(self):
        await self.client.aclose()

    async def clear_demo_memory(self):
        self.demo_memories = {}

_hindsight_service: Optional[HindsightMemoryService] = None

async def get_hindsight_service() -> HindsightMemoryService:
    global _hindsight_service
    if _hindsight_service is None:
        _hindsight_service = HindsightMemoryService()
    return _hindsight_service
