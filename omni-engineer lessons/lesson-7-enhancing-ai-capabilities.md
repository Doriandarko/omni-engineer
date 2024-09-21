# Lesson 7: Enhancing AI Capabilities

In this lesson, we'll focus on enhancing the AI capabilities of our CLI tool. We'll cover implementing model switching, fine-tuning AI responses for coding tasks, and adding code completion and suggestion features. Let's dive in!

## Project Structure

Before we start, let's review our updated project structure:

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
│   └── suggestion_service.py
├── .env
├── requirements.txt
└── README.md
```

## 1. Implementing Model Switching

To implement model switching, we'll create a factory pattern for our AI models. This will allow us to easily switch between different models based on user preferences or task requirements.

First, let's create a base model class:

```python
# models/base_model.py

from abc import ABC, abstractmethod

class BaseModel(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        pass
```

Now, let's implement specific model classes:

```python
# models/gpt3_model.py

from .base_model import BaseModel
import openai

class GPT3Model(BaseModel):
    def __init__(self):
        self.model_name = "text-davinci-002"

    def generate_response(self, prompt: str) -> str:
        response = openai.Completion.create(
            engine=self.model_name,
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response.choices[0].text.strip()

    def get_model_name(self) -> str:
        return self.model_name
```

Implement similar classes for GPT-4 and Codex models.

Now, let's create a model factory:

```python
# models/__init__.py

from .gpt3_model import GPT3Model
from .gpt4_model import GPT4Model
from .codex_model import CodexModel

class ModelFactory:
    @staticmethod
    def get_model(model_name: str):
        if model_name == "gpt3":
            return GPT3Model()
        elif model_name == "gpt4":
            return GPT4Model()
        elif model_name == "codex":
            return CodexModel()
        else:
            raise ValueError(f"Unknown model: {model_name}")
```

Update the `ai_integration.py` file to use the model factory:

```python
# ai_integration.py

from models import ModelFactory

class AIIntegration:
    def __init__(self, model_name: str = "gpt3"):
        self.model = ModelFactory.get_model(model_name)

    def generate_response(self, prompt: str) -> str:
        return self.model.generate_response(prompt)

    def switch_model(self, model_name: str):
        self.model = ModelFactory.get_model(model_name)
```

Add a new command in `cli.py` to switch models:

```python
@cli.command()
@click.argument('model_name')
def switch_model(model_name):
    """Switch the AI model"""
    try:
        ai_integration.switch_model(model_name)
        click.echo(f"Switched to model: {model_name}")
    except ValueError as e:
        click.echo(f"Error: {str(e)}")
```

## 2. Fine-tuning AI Responses for Coding Tasks

To fine-tune AI responses for coding tasks, we'll create specialized prompts and implement a context management system. This will help the AI generate more relevant and accurate responses for coding-related queries.

First, let's create a context manager:

```python
# utils.py

class ContextManager:
    def __init__(self):
        self.context = []

    def add_to_context(self, message: str):
        self.context.append(message)
        if len(self.context) > 5:  # Keep only the last 5 messages
            self.context.pop(0)

    def get_context(self) -> str:
        return "\n".join(self.context)

context_manager = ContextManager()
```

Now, let's update the `generate_response` method in `ai_integration.py`:

```python
# ai_integration.py

from utils import context_manager

class AIIntegration:
    # ... (previous code)

    def generate_response(self, prompt: str) -> str:
        coding_context = "You are an expert programmer assisting with coding tasks. "
        full_prompt = f"{coding_context}\n\nContext:\n{context_manager.get_context()}\n\nUser: {prompt}\nAI:"
        response = self.model.generate_response(full_prompt)
        context_manager.add_to_context(f"User: {prompt}")
        context_manager.add_to_context(f"AI: {response}")
        return response
```

## 3. Adding Code Completion and Suggestion Features

To implement code completion and suggestion features, we'll create separate services that interact with our AI models. These services will use specialized prompts and parsing techniques to generate relevant code completions and suggestions.

First, let's create a code completion service:

```python
# services/code_completion.py

from models import ModelFactory

class CodeCompletionService:
    def __init__(self, model_name: str = "codex"):
        self.model = ModelFactory.get_model(model_name)

    def complete_code(self, code_snippet: str, max_tokens: int = 50) -> str:
        prompt = f"Complete the following code:\n\n{code_snippet}\n"
        completion = self.model.generate_response(prompt)
        return completion[:max_tokens]
```

Now, let's create a suggestion service:

```python
# services/suggestion_service.py

from models import ModelFactory

class SuggestionService:
    def __init__(self, model_name: str = "gpt4"):
        self.model = ModelFactory.get_model(model_name)

    def get_suggestions(self, code_snippet: str, num_suggestions: int = 3) -> list:
        prompt = f"Provide {num_suggestions} suggestions to improve the following code:\n\n{code_snippet}\n"
        response = self.model.generate_response(prompt)
        suggestions = response.split("\n")
        return suggestions[:num_suggestions]
```

Update the `cli.py` file to include new commands for code completion and suggestions:

```python
# cli.py

from services.code_completion import CodeCompletionService
from services.suggestion_service import SuggestionService

code_completion_service = CodeCompletionService()
suggestion_service = SuggestionService()

@cli.command()
@click.argument('code_snippet')
def complete_code(code_snippet):
    """Complete the given code snippet"""
    completion = code_completion_service.complete_code(code_snippet)
    click.echo(f"Completed code:\n{completion}")

@cli.command()
@click.argument('code_snippet')
@click.option('--num_suggestions', default=3, help='Number of suggestions to generate')
def get_suggestions(code_snippet, num_suggestions):
    """Get suggestions to improve the given code snippet"""
    suggestions = suggestion_service.get_suggestions(code_snippet, num_suggestions)
    click.echo("Suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        click.echo(f"{i}. {suggestion}")
```

## Conclusion

In this lesson, we've enhanced our AI-assisted CLI tool's capabilities by implementing model switching, fine-tuning AI responses for coding tasks, and adding code completion and suggestion features. These improvements make our tool more versatile and powerful for assisting developers with various coding tasks.

To further improve the tool, consider the following:

1. Implement caching for AI responses to improve performance.
2. Add support for language-specific code completion and suggestions.
3. Integrate with popular IDEs or text editors for seamless coding assistance.
4. Implement a feedback system to continuously improve AI responses based on user interactions.

In the next lesson, we'll explore implementing a local vector database for efficient knowledge management and retrieval.
