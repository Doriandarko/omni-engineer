# backend/core/language_support.py

from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound
from pygments.token import Token
from typing import List, Tuple

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

def parse_code(code: str, language: str) -> List[Tuple[Token, str]]:
    if language not in SUPPORTED_LANGUAGES.values():
        raise ValueError(f"Unsupported language: {language}")
    
    lexer = get_lexer_by_name(language)
    return list(lexer.get_tokens(code))

def get_language_specific_rules(language: str) -> dict:
    """
    Return language-specific rules for code analysis.
    This is a placeholder function and should be expanded with actual rules.
    """
    rules = {
        "python": {
            "max_line_length": 79,
            "max_function_length": 50,
            "naming_convention": r"^[a-z_][a-z0-9_]*$"
        },
        "javascript": {
            "max_line_length": 80,
            "max_function_length": 30,
            "naming_convention": r"^[a-zA-Z_$][a-zA-Z0-9_$]*$"
        }
        # Add rules for other supported languages
    }
    return rules.get(language, {})

def format_code(code: str, language: str) -> str:
    """
    Format code according to language-specific standards.
    This is a placeholder function and should be implemented with actual formatting logic.
    """
    # In a real implementation, you might use language-specific formatters like:
    # - Black for Python
    # - Prettier for JavaScript
    # - clang-format for C/C++
    # etc.
    return code  # For now, just return the original code

def get_language_documentation(language: str) -> str:
    """
    Return links to official documentation for the specified language.
    """
    docs = {
        "python": "https://docs.python.org/3/",
        "javascript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
        "java": "https://docs.oracle.com/en/java/",
        "cpp": "https://en.cppreference.com/w/",
        "csharp": "https://docs.microsoft.com/en-us/dotnet/csharp/",
        "ruby": "https://ruby-doc.org/",
        "go": "https://golang.org/doc/",
        "rust": "https://doc.rust-lang.org/book/",
        "php": "https://www.php.net/docs.php",
        "swift": "https://swift.org/documentation/"
    }
    return docs.get(language, "Documentation not available for this language.")