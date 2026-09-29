# 🧠 Omni Engineer: An AI-Powered Developer Console

An intelligent assistant designed to enhance your development workflow with advanced AI capabilities.

## ✨ NEW
O1 support. Simply use 
openai/o1-preview or openai/o1-mini as models.

## 🔍 Overview

Omni Engineer is a console-based tool that integrates AI capabilities into your development process. It offers smart responses to coding queries, file management, web searching, and image processing functionalities, now with enhanced features for a more robust development experience.

Omni Engineer is a spiritual successor to [Claude Engineer](https://github.com/Doriandarko/claude-engineer), built from extensive usage of hand-made AI tools, trial and error, and user feedback. This new script allows for more control via simplicity while introducing powerful new features like multi-file editing and chat session management.

## 🌟 Features

- AI-Powered Responses with Streaming Output
- Advanced File Management (Add, Edit, Create, Show Content)
- Multi-File Editing Support
- Web Searching with DuckDuckGo Integration
- Image Processing (Local Files and URLs)
- Undo Functionality for File Edits
- Conversation Save & Load
- Syntax Highlighting for Code
- Diff Display for File Changes
- AI Model Selection and Switching

## 🖥️ Commands

- `/add <filepath>`: Add files to AI context
- `/edit <filepath>`: Edit existing files
- `/new <filepath>`: Create new files
- `/search`: Perform web searches
- `/image <filepath/url>`: Add images to context
- `/clear`: Clear AI memory
- `/reset`: Reset the session
- `/diff`: Toggle diff display
- `/history`: View chat history
- `/save`: Save current chat
- `/load`: Load a previous chat
- `/undo <filepath>`: Undo last file edit
- `/help`: Display available commands
- `/model`: Show current AI model
- `/change_model`: Change the AI model
- `/show <filepath>`: Display content of a file

## 🚀 Installation

1. Clone the repository:
   ```
   git clone https://github.com/doriandarko/omni-engineer.git
   cd omni-engineer
   ```
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Rename the .env.example to .env and add your API Key:
   ```
   OPENROUTER_API_KEY="Your key"
   ```

   To use Ollama or another OpenAI-compatible endpoint instead of OpenRouter:
   ```
   OPENAI_BASE_URL="http://localhost:11434/v1"
   OPENAI_API_KEY="ollama"
   DEFAULT_MODEL="llama3.2:3b"
   EDITOR_MODEL="starcoder2:3b"
   ```
   `OPENAI_API_KEY` can be any non-empty value for local servers that do not require authentication. Keep the `/v1` suffix for Ollama's OpenAI-compatible API.
4. Run the main script:
   ```
   python omni-eng.py
   ```

## 📚 Usage

After launching the console, enter commands or questions as needed. The AI will respond accordingly, assisting with various development tasks. Use the `/help` command to see a list of available commands and their descriptions.

## 🤖 AI Models

Omni Engineer uses OpenRouter by default, but it can also connect to any OpenAI-compatible endpoint through `OPENAI_BASE_URL`. The default and editor models can be overridden with `DEFAULT_MODEL` and `EDITOR_MODEL`. You can view the current model with `/model` and change it using `/change_model`. For OpenRouter model names, refer to [OpenRouter's documentation](https://openrouter.ai/models).

## 🔧 Advanced Features

- **Multi-File Editing**: Edit multiple files in a single session.
- **Real-time Diff Display**: See changes as they're made with the diff feature.
- **Syntax Highlighting**: Improved code readability with syntax highlighting.
- **Image Context**: Add both local and URL-based images to your AI context.
- **Flexible Model Selection**: Switch between different AI models for various tasks.

## 🐛 Issue Reporting

Please use the issue tracker only for reporting actual bugs in the code. This helps keep the issue tracker focused on improving the project's stability and functionality.

## 🤝 Contributing

Contributions to Omni Engineer are welcome! Please feel free to submit pull requests, create issues for bugs, or suggest new features.

omni-engineer Copyright (c) 2024, Pietro Schirano

## ⭐️ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Doriandarko/omni-engineer&type=Date)](https://star-history.com/#Doriandarko/omni-engineer&Date)
