# Lesson 5: Web Searching and External Data Integration

## Introduction

In this lesson, we'll focus on implementing web search functionality and integrating external data into our AI-assisted CLI tool. We'll use the DuckDuckGo search API for web searches and implement image handling for both local and URL-based images. These features will enhance the AI's ability to provide context-aware assistance and handle a wider range of inputs.

## Project Structure

Before we dive into the implementation, let's review our updated project structure:

```
ai_cli_tool/
│
├── main.py
├── cli.py
├── ai_integration.py
├── file_handler.py
├── context_manager.py
├── web_search.py  # New file for this lesson
├── image_handler.py  # New file for this lesson
├── utils.py
├── .env
├── requirements.txt
└── README.md
```

## 1. Implementing Web Search Functionality

First, let's create a `WebSearch` class in `web_search.py` to handle web searches using the DuckDuckGo API:

```python
# web_search.py

import asyncio
from typing import List, Dict
from duckduckgo_search import AsyncDDGS

class WebSearch:
    def __init__(self):
        self.ddgs = AsyncDDGS()

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        try:
            results = await self.ddgs.text(query, max_results=max_results)
            return [
                {
                    "title": result["title"],
                    "body": result["body"],
                    "href": result["href"]
                }
                for result in results
            ]
        except Exception as e:
            print(f"Error performing web search: {e}")
            return []

    async def close(self):
        await self.ddgs.close()
```

This `WebSearch` class uses the `AsyncDDGS` client from the `duckduckgo_search` library to perform asynchronous web searches. It returns a list of dictionaries containing the title, body, and URL of each search result.

Now, let's update our `cli.py` to include a web search command:

```python
# cli.py

import asyncio
import click
from web_search import WebSearch
from context_manager import ContextManager

web_search = WebSearch()
context_manager = ContextManager()

@click.group()
def cli():
    """AI-Assisted Developer CLI Tool"""
    pass

@cli.command()
@click.argument('query')
@click.option('--max-results', default=5, help='Maximum number of search results')
def search(query: str, max_results: int):
    """Perform a web search and add results to AI context"""
    results = asyncio.run(web_search.search(query, max_results))
    if results:
        context_manager.add_search_results(query, results)
        click.echo(f"Added {len(results)} search results for query: {query}")
        for idx, result in enumerate(results, 1):
            click.echo(f"{idx}. {result['title']}")
    else:
        click.echo("No search results found.")

# ... (other CLI commands)

if __name__ == '__main__':
    cli()
```

We also need to update our `ContextManager` class to handle search results:

```python
# context_manager.py

from typing import Dict, List

class ContextManager:
    def __init__(self):
        self.files: Dict[str, str] = {}
        self.search_results: Dict[str, List[Dict[str, str]]] = {}
        self.history: List[Dict[str, str]] = []

    # ... (existing methods)

    def add_search_results(self, query: str, results: List[Dict[str, str]]):
        self.search_results[query] = results
        self.history.append({"action": "search", "query": query})

    def get_context(self) -> str:
        context = "Current files in context:\n\n"
        for filepath, content in self.files.items():
            context += f"File: {filepath}\n```\n{content}\n```\n\n"
        
        context += "Search results:\n\n"
        for query, results in self.search_results.items():
            context += f"Query: {query}\n"
            for result in results:
                context += f"- {result['title']}: {result['body'][:100]}...\n"
            context += "\n"
        
        return context
```

## 2. Handling Image Inputs (Local and URL-based)

Now, let's create an `ImageHandler` class in `image_handler.py` to handle both local and URL-based images:

```python
# image_handler.py

import base64
from typing import Optional
from PIL import Image
import requests
from io import BytesIO

class ImageHandler:
    @staticmethod
    def encode_image(image_path: str) -> Optional[str]:
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            print(f"Error: Image file not found: {image_path}")
            return None
        except IOError as e:
            print(f"Error reading image file: {e}")
            return None

    @staticmethod
    def get_image_from_url(url: str) -> Optional[str]:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            buffered = BytesIO()
            image.save(buffered, format=image.format)
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching image from URL: {e}")
            return None
        except IOError as e:
            print(f"Error processing image from URL: {e}")
            return None

    @staticmethod
    def is_url(string: str) -> bool:
        return string.startswith(('http://', 'https://'))
```

This `ImageHandler` class provides methods for encoding local images and fetching images from URLs. Both methods return base64-encoded strings that can be easily integrated into our AI context.

Let's update our `cli.py` to include an image command:

```python
# cli.py

# ... (previous imports)
from image_handler import ImageHandler

image_handler = ImageHandler()

@cli.command()
@click.argument('image_path')
def add_image(image_path: str):
    """Add an image (local file or URL) to the AI context"""
    if image_handler.is_url(image_path):
        image_data = image_handler.get_image_from_url(image_path)
        source = "URL"
    else:
        image_data = image_handler.encode_image(image_path)
        source = "local file"

    if image_data:
        context_manager.add_image(image_path, image_data, source)
        click.echo(f"Added image from {source}: {image_path}")
    else:
        click.echo(f"Failed to add image from {source}: {image_path}")

# ... (other CLI commands)
```

We also need to update our `ContextManager` class to handle images:

```python
# context_manager.py

from typing import Dict, List

class ContextManager:
    def __init__(self):
        self.files: Dict[str, str] = {}
        self.search_results: Dict[str, List[Dict[str, str]]] = {}
        self.images: Dict[str, Dict[str, str]] = {}
        self.history: List[Dict[str, str]] = []

    # ... (existing methods)

    def add_image(self, image_path: str, image_data: str, source: str):
        self.images[image_path] = {"data": image_data, "source": source}
        self.history.append({"action": "add_image", "path": image_path, "source": source})

    def get_context(self) -> str:
        context = "Current files in context:\n\n"
        for filepath, content in self.files.items():
            context += f"File: {filepath}\n```\n{content}\n```\n\n"
        
        context += "Search results:\n\n"
        for query, results in self.search_results.items():
            context += f"Query: {query}\n"
            for result in results:
                context += f"- {result['title']}: {result['body'][:100]}...\n"
            context += "\n"
        
        context += "Images in context:\n\n"
        for image_path, image_info in self.images.items():
            context += f"- {image_path} (from {image_info['source']})\n"
        
        return context
```

## 3. Integrating Web Search and Image Data with AI

Now that we have implemented web searching and image handling, we need to integrate this data with our AI component. Let's update the `ai_integration.py` file to handle these new types of context:

```python
# ai_integration.py

from typing import List, Dict
import openai
from context_manager import ContextManager

class AIAssistant:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        openai.api_key = api_key
        self.model = model
        self.context_manager = ContextManager()

    def generate_response(self, prompt: str) -> str:
        context = self.context_manager.get_context()
        messages = [
            {"role": "system", "content": "You are an AI assistant for developers. Use the following context to assist with coding tasks and questions."},
            {"role": "user", "content": context},
            {"role": "user", "content": prompt}
        ]

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message['content']
        except Exception as e:
            return f"Error generating AI response: {e}"

    def add_file_to_context(self, filepath: str, content: str):
        self.context_manager.add_file(filepath, content)

    def add_search_results_to_context(self, query: str, results: List[Dict[str, str]]):
        self.context_manager.add_search_results(query, results)

    def add_image_to_context(self, image_path: str, image_data: str, source: str):
        self.context_manager.add_image(image_path, image_data, source)
```

This updated `AIAssistant` class now includes methods for adding search results and images to the context. The `generate_response` method uses the entire context (including files, search results, and images) when generating a response.

## Conclusion

In this lesson, we've implemented web searching and external data integration for our AI-assisted CLI tool. We've created classes for web searching and image handling, and updated our context management to include this new data. These features allow developers to:

1. Perform web searches and add results to the AI context
2. Add local and URL-based images to the AI context
3. Integrate web search results and image data with the AI assistant

This implementation provides a more comprehensive context for the AI assistant, allowing it to provide more informed and relevant responses to user queries.

## Exercises

1. Implement a command to display the search history and allow users to remove specific search results from the context.
2. Add a feature to extract text from images using OCR (Optical Character Recognition) and include it in the AI context.
3. Implement a command to perform image searches and add the results to the AI context.
4. Create a method to summarize long search results or file contents before adding them to the context, to manage the context size more effectively.

By completing these exercises, you'll gain a deeper understanding of integrating external data sources and managing complex contexts in an AI-assisted CLI tool.
