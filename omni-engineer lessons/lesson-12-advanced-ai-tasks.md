# Lesson 12: Advanced AI Tasks and Coding Assistance

In this lesson, we'll enhance our AI assistant with advanced capabilities, including code refactoring suggestions, multi-language support, AI-powered debugging assistance, and project-wide code analysis. We'll integrate these features into both our backend API and frontend interface.

## Project Structure

Let's start by looking at our updated project structure:

```
ai_assistant/
│
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── ai_routes.py
│   │   │   ├── code_routes.py
│   │   │   └── project_routes.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── code_models.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── ai_service.py
│   │   │   ├── code_service.py
│   │   │   └── project_service.py
│   │   └── middleware/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── ai_integration.py
│   │   ├── code_analyzer.py
│   │   └── language_support.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py
│   ├── .env
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat.js
│   │   │   ├── FileManager.js
│   │   │   ├── CodeEditor.js
│   │   │   ├── RefactorSuggestions.js
│   │   │   └── DebugAssistant.js
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── websocket.js
│   │   ├── utils/
│   │   │   └── helpers.js
│   │   ├── App.js
│   │   ├── App.css
│   │   └── index.js
│   ├── package.json
│   └── README.md
│
└── README.md
```

## Step 1: Implementing Code Refactoring Suggestions

Let's start by adding code refactoring capabilities to our backend.

```python
# backend/core/code_analyzer.py

import ast
import astroid
from typing import List, Dict

def analyze_code(code: str) -> List[Dict]:
    tree = ast.parse(code)
    analyzer = CodeAnalyzer()
    analyzer.visit(tree)
    return analyzer.suggestions

class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.suggestions = []

    def visit_FunctionDef(self, node):
        if len(node.body) > 20:
            self.suggestions.append({
                "type": "refactor",
                "message": f"Function '{node.name}' is too long. Consider breaking it into smaller functions.",
                "line": node.lineno
            })
        self.generic_visit(node)

    def visit_For(self, node):
        if isinstance(node.body[0], ast.For):
            self.suggestions.append({
                "type": "refactor",
                "message": "Nested loop detected. Consider extracting inner loop to a separate function.",
                "line": node.lineno
            })
        self.generic_visit(node)

# Add more visit methods for other types of suggestions

def get_refactoring_suggestions(code: str) -> List[Dict]:
    return analyze_code(code)
```

Now, let's add a route to handle refactoring requests:

```python
# backend/api/routes/code_routes.py

from fastapi import APIRouter, Depends, HTTPException
from ..models.code_models import CodeSnippet
from ..services.code_service import get_refactoring_suggestions

router = APIRouter()

@router.post("/refactor")
async def refactor_code(code_snippet: CodeSnippet):
    suggestions = get_refactoring_suggestions(code_snippet.code)
    return {"suggestions": suggestions}
```

## Step 2: Implementing Multi-Language Support

To support multiple programming languages, we'll create a language detection and parsing system:

```python
# backend/core/language_support.py

from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound

SUPPORTED_LANGUAGES = {
    "python": "python",
    "javascript": "javascript",
    "java": "java",
    "cpp": "cpp",
    "csharp": "csharp",
    "ruby": "ruby",
    "go": "go",
    "rust": "rust",
    "php": "php",
    "swift": "swift"
}

def detect_language(code: str) -> str:
    try:
        lexer = guess_lexer(code)
        return SUPPORTED_LANGUAGES.get(lexer.name.lower(), "unknown")
    except ClassNotFound:
        return "unknown"

def parse_code(code: str, language: str):
    if language not in SUPPORTED_LANGUAGES.values():
        raise ValueError(f"Unsupported language: {language}")
    
    lexer = get_lexer_by_name(language)
    # Implement language-specific parsing logic here
    # This could involve using language-specific AST libraries
    # For simplicity, we'll just return tokenized code
    return list(lexer.get_tokens(code))
```

## Step 3: Implementing AI-Powered Debugging Assistance

Let's create a service for AI-powered debugging assistance:

```python
# backend/services/ai_service.py

from ..core.ai_integration import get_ai_completion
from ..core.language_support import detect_language, parse_code

async def get_debug_assistance(code: str, error_message: str) -> str:
    language = detect_language(code)
    parsed_code = parse_code(code, language)
    
    prompt = f"""
    Language: {language}
    Code:
    {code}
    
    Error message:
    {error_message}
    
    Provide a detailed explanation of the error and suggest possible fixes.
    """
    
    response = await get_ai_completion(prompt)
    return response

# backend/api/routes/ai_routes.py

from fastapi import APIRouter
from ..models.code_models import DebugRequest
from ..services.ai_service import get_debug_assistance

router = APIRouter()

@router.post("/debug")
async def debug_code(debug_request: DebugRequest):
    assistance = await get_debug_assistance(debug_request.code, debug_request.error)
    return {"assistance": assistance}
```

## Step 4: Implementing Project-Wide Code Analysis

For project-wide code analysis, we'll create a service that analyzes multiple files:

```python
# backend/services/project_service.py

import os
from typing import List, Dict
from ..core.code_analyzer import analyze_code
from ..core.language_support import detect_language

def analyze_project(project_path: str) -> Dict[str, List[Dict]]:
    project_analysis = {}
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(('.py', '.js', '.java', '.cpp', '.cs', '.rb', '.go', '.rs', '.php', '.swift')):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    code = f.read()
                language = detect_language(code)
                analysis = analyze_code(code)
                project_analysis[file_path] = {
                    'language': language,
                    'analysis': analysis
                }
    return project_analysis

# backend/api/routes/project_routes.py

from fastapi import APIRouter
from ..services.project_service import analyze_project

router = APIRouter()

@router.post("/analyze-project")
async def analyze_project_route(project_path: str):
    analysis = analyze_project(project_path)
    return {"project_analysis": analysis}
```

## Step 5: Updating Frontend Components

Now, let's update our frontend to incorporate these new features. We'll create new components for refactoring suggestions and debugging assistance.

```javascript
// frontend/src/components/RefactorSuggestions.js

import React from 'react';

const RefactorSuggestions = ({ suggestions }) => {
  return (
    <div className="refactor-suggestions">
      <h3>Refactoring Suggestions</h3>
      <ul>
        {suggestions.map((suggestion, index) => (
          <li key={index}>
            <strong>Line {suggestion.line}:</strong> {suggestion.message}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default RefactorSuggestions;

// frontend/src/components/DebugAssistant.js

import React, { useState } from 'react';
import { getDebugAssistance } from '../services/api';

const DebugAssistant = ({ code }) => {
  const [error, setError] = useState('');
  const [assistance, setAssistance] = useState('');

  const handleDebugRequest = async () => {
    try {
      const response = await getDebugAssistance(code, error);
      setAssistance(response.assistance);
    } catch (error) {
      console.error('Error getting debug assistance:', error);
    }
  };

  return (
    <div className="debug-assistant">
      <h3>Debug Assistant</h3>
      <textarea
        value={error}
        onChange={(e) => setError(e.target.value)}
        placeholder="Paste your error message here"
      />
      <button onClick={handleDebugRequest}>Get Debug Assistance</button>
      {assistance && (
        <div className="debug-assistance">
          <h4>AI Assistance:</h4>
          <pre>{assistance}</pre>
        </div>
      )}
    </div>
  );
};

export default DebugAssistant;
```

Update the CodeEditor component to include these new features:

```javascript
// frontend/src/components/CodeEditor.js

import React, { useState, useEffect } from 'react';
import AceEditor from 'react-ace';
import { getRefactoringSuggestions } from '../services/api';
import RefactorSuggestions from './RefactorSuggestions';
import DebugAssistant from './DebugAssistant';

import 'ace-builds/src-noconflict/mode-python';
import 'ace-builds/src-noconflict/mode-javascript';
import 'ace-builds/src-noconflict/theme-monokai';

const CodeEditor = ({ initialCode, language }) => {
  const [code, setCode] = useState(initialCode || '');
  const [suggestions, setSuggestions] = useState([]);

  useEffect(() => {
    const debouncedGetSuggestions = debounce(async () => {
      try {
        const response = await getRefactoringSuggestions(code);
        setSuggestions(response.suggestions);
      } catch (error) {
        console.error('Error getting refactoring suggestions:', error);
      }
    }, 1000);

    debouncedGetSuggestions();

    return () => debouncedGetSuggestions.cancel();
  }, [code]);

  const handleChange = (newCode) => {
    setCode(newCode);
  };

  return (
    <div className="code-editor-container">
      <AceEditor
        mode={language}
        theme="monokai"
        onChange={handleChange}
        value={code}
        name="code-editor"
        editorProps={{ $blockScrolling: true }}
        setOptions={{
          enableBasicAutocompletion: true,
          enableLiveAutocompletion: true,
          enableSnippets: true,
          showLineNumbers: true,
          tabSize: 2,
        }}
        style={{ width: '100%', height: '400px' }}
      />
      <RefactorSuggestions suggestions={suggestions} />
      <DebugAssistant code={code} />
    </div>
  );
};

export default CodeEditor;
```

Lastly, update the API service to include the new endpoints:

```javascript
// frontend/src/services/api.js

// ... existing code ...

export const getRefactoringSuggestions = async (code) => {
  const response = await api.post('/code/refactor', { code });
  return response.data;
};

export const getDebugAssistance = async (code, error) => {
  const response = await api.post('/ai/debug', { code, error });
  return response.data;
};

export const analyzeProject = async (projectPath) => {
  const response = await api.post('/project/analyze-project', { project_path: projectPath });
  return response.data;
};
```

## Conclusion

In this lesson, we've implemented advanced AI tasks and coding assistance features, including:

1. Code refactoring suggestions
2. Multi-language support
3. AI-powered debugging assistance
4. Project-wide code analysis

Key takeaways:
1. Leveraging AST (Abstract Syntax Tree) for code analysis enables powerful refactoring suggestions.
2. Multi-language support requires careful consideration of language-specific parsing and analysis techniques.
3. AI-powered debugging assistance can significantly speed up the debugging process by providing intelligent insights.
4. Project-wide code analysis offers a holistic view of code quality and potential improvements across an entire codebase.
5. Integrating these advanced features into the frontend requires thoughtful UI design to present complex information in an accessible manner.

These advanced features significantly enhance the capabilities of our AI assistant, making it a powerful tool for developers. In the next lesson, we'll focus on optimizing performance and improving the scalability of our application.
