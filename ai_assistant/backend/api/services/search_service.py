# backend/api/services/search_service.py

from ...core.vector_db import VectorDB
import aiohttp

class SearchService:
    def __init__(self):
        self.vector_db = VectorDB()

    async def web_search(self, query: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.duckduckgo.com/?q={query}&format=json") as response:
                data = await response.json()
                return data.get("RelatedTopics", [])

    def knowledge_base_search(self, query: str, user_id: str):
        return self.vector_db.search(query, filter={"user_id": user_id})