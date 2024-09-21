# backend/core/vector_db.py

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

class VectorDB:
    def __init__(self, collection_name: str = "code_knowledge"):
        self.client = chromadb.Client(Settings(persist_directory="./data"))
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

    def add_document(self, document_id: str, content: str, metadata: Dict[str, Any] = None):
        embeddings = self.encoder.encode([content])[0].tolist()
        self.collection.add(
            embeddings=[embeddings],
            documents=[content],
            metadatas=[metadata] if metadata else None,
            ids=[document_id]
        )

    def search(self, query: str, n_results: int = 5, filter: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        query_embedding = self.encoder.encode([query])[0].tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter
        )
        return [
            {
                "id": id,
                "content": document,
                "metadata": metadata,
                "distance": distance
            }
            for id, document, metadata, distance in zip(
                results['ids'][0],
                results['documents'][0],
                results['metadatas'][0] if results['metadatas'] else [None] * len(results['ids'][0]),
                results['distances'][0]
            )
        ]

    def update_document(self, document_id: str, content: str, metadata: Dict[str, Any] = None):
        embeddings = self.encoder.encode([content])[0].tolist()
        self.collection.update(
            embeddings=[embeddings],
            documents=[content],
            metadatas=[metadata] if metadata else None,
            ids=[document_id]
        )

    def delete_document(self, document_id: str):
        self.collection.delete(ids=[document_id])

    def get_document(self, document_id: str) -> Dict[str, Any]:
        result = self.collection.get(ids=[document_id])
        if result['ids']:
            return {
                "id": result['ids'][0],
                "content": result['documents'][0],
                "metadata": result['metadatas'][0] if result['metadatas'] else None
            }
        return None

    def list_documents(self) -> List[str]:
        return self.collection.get()['ids']