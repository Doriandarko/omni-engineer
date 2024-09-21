# Lesson 8: Local Vector DB and Knowledge Management

In this lesson, we'll implement a local vector database for efficient knowledge management and retrieval in our AI-assisted CLI tool. We'll use Chroma as our vector database and integrate it with our existing system to enhance our tool's capabilities.

## Project Structure

Let's update our project structure to include the new components:

```
ai_cli_tool/
│
├── main.py
├── cli.py
├── ai_integration.py
├── file_handler.py
├── utils.py
├── models/
│   ├── __init__.py
│   ├── base_model.py
│   ├── gpt3_model.py
│   ├── gpt4_model.py
│   └── codex_model.py
├── services/
│   ├── __init__.py
│   ├── code_completion.py
│   ├── suggestion_service.py
│   └── vector_db_service.py
├── knowledge_base/
│   ├── __init__.py
│   ├── document.py
│   └── kb_manager.py
├── .env
├── requirements.txt
└── README.md
```

## 1. Setting up Chroma Vector Database

First, let's add Chroma to our requirements:

```
# requirements.txt
chromadb==0.3.21
sentence-transformers==2.2.2
```

Now, let's create a service to interact with our vector database:

```python
# services/vector_db_service.py

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

class VectorDBService:
    def __init__(self, collection_name: str = "code_knowledge"):
        self.client = chromadb.Client(Settings(persist_directory="./data"))
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

    def add_document(self, document_id: str, content: str, metadata: dict = None):
        embeddings = self.encoder.encode([content])[0].tolist()
        self.collection.add(
            embeddings=[embeddings],
            documents=[content],
            metadatas=[metadata] if metadata else None,
            ids=[document_id]
        )

    def search(self, query: str, n_results: int = 5):
        query_embedding = self.encoder.encode([query])[0].tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results
```

## 2. Implementing Document Management

Let's create a Document class to represent our knowledge base items:

```python
# knowledge_base/document.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class Document:
    id: str
    content: str
    metadata: Optional[dict] = None
```

Now, let's implement a KnowledgeBaseManager to handle document operations:

```python
# knowledge_base/kb_manager.py

from .document import Document
from services.vector_db_service import VectorDBService

class KnowledgeBaseManager:
    def __init__(self):
        self.vector_db = VectorDBService()

    def add_document(self, document: Document):
        self.vector_db.add_document(document.id, document.content, document.metadata)

    def search(self, query: str, n_results: int = 5):
        return self.vector_db.search(query, n_results)

    def get_relevant_context(self, query: str, n_results: int = 3) -> str:
        results = self.search(query, n_results)
        context = "\n\n".join(results['documents'][0])
        return context
```

## 3. Integrating Knowledge Base with AI Responses

Let's update our AIIntegration class to use the knowledge base:

```python
# ai_integration.py

from utils import context_manager
from knowledge_base.kb_manager import KnowledgeBaseManager

class AIIntegration:
    def __init__(self, model_name: str = "gpt3"):
        self.model = ModelFactory.get_model(model_name)
        self.kb_manager = KnowledgeBaseManager()

    def generate_response(self, prompt: str) -> str:
        coding_context = "You are an expert programmer assisting with coding tasks. "
        relevant_context = self.kb_manager.get_relevant_context(prompt)
        full_prompt = f"{coding_context}\n\nRelevant context:\n{relevant_context}\n\nConversation context:\n{context_manager.get_context()}\n\nUser: {prompt}\nAI:"
        response = self.model.generate_response(full_prompt)
        context_manager.add_to_context(f"User: {prompt}")
        context_manager.add_to_context(f"AI: {response}")
        return response
```

## 4. Adding CLI Commands for Knowledge Base Management

Let's add new commands to our CLI for managing the knowledge base:

```python
# cli.py

from knowledge_base.document import Document
from knowledge_base.kb_manager import KnowledgeBaseManager

kb_manager = KnowledgeBaseManager()

@cli.command()
@click.argument('file_path')
@click.option('--metadata', '-m', multiple=True, help='Metadata in the format key=value')
def add_to_kb(file_path: str, metadata):
    """Add a file to the knowledge base"""
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        
        metadata_dict = dict(item.split('=') for item in metadata)
        document = Document(id=file_path, content=content, metadata=metadata_dict)
        kb_manager.add_document(document)
        click.echo(f"Added {file_path} to the knowledge base")
    except Exception as e:
        click.echo(f"Error adding file to knowledge base: {str(e)}")

@cli.command()
@click.argument('query')
@click.option('--n_results', default=3, help='Number of results to return')
def search_kb(query: str, n_results: int):
    """Search the knowledge base"""
    results = kb_manager.search(query, n_results)
    for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
        click.echo(f"Result {i}:")
        click.echo(f"Content: {doc[:100]}...")
        click.echo(f"Metadata: {metadata}")
        click.echo("---")
```

## 5. Implementing a Question-Answering System

Let's create a question-answering system that uses our knowledge base:

```python
# services/qa_service.py

from knowledge_base.kb_manager import KnowledgeBaseManager
from models import ModelFactory

class QuestionAnsweringService:
    def __init__(self, model_name: str = "gpt4"):
        self.model = ModelFactory.get_model(model_name)
        self.kb_manager = KnowledgeBaseManager()

    def answer_question(self, question: str) -> str:
        context = self.kb_manager.get_relevant_context(question)
        prompt = f"""Answer the following question based on the given context. If the context doesn't contain enough information to answer the question, say "I don't have enough information to answer that question."

Context:
{context}

Question: {question}

Answer:"""
        return self.model.generate_response(prompt)
```

Now, let's add a CLI command for the QA system:

```python
# cli.py

from services.qa_service import QuestionAnsweringService

qa_service = QuestionAnsweringService()

@cli.command()
@click.argument('question')
def ask(question: str):
    """Ask a question using the knowledge base"""
    answer = qa_service.answer_question(question)
    click.echo(f"Q: {question}")
    click.echo(f"A: {answer}")
```

## Conclusion

In this lesson, we've implemented a local vector database using Chroma and integrated it into our AI-assisted CLI tool. We've created a knowledge base management system that allows us to:

1. Add documents to the vector database
2. Search for relevant information in the knowledge base
3. Use the knowledge base to provide context for AI-generated responses
4. Implement a question-answering system based on the knowledge base

These enhancements significantly improve our tool's ability to provide relevant and accurate information to users. The vector database allows for efficient storage and retrieval of knowledge, while the integration with our AI models enables more context-aware responses.

To further improve the system, consider the following:

1. Implement automatic knowledge base updates from external sources
2. Add support for different document types (e.g., PDF, Markdown)
3. Implement versioning for knowledge base entries
4. Create a web interface for easier knowledge base management
5. Optimize vector search performance for larger datasets

In the next lesson, we'll explore Git integration and version control features to enhance our tool's capabilities in managing code repositories.
