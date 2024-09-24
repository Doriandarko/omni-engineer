# Lesson 11: Frontend Development for Web-Based AI Assistant

In this lesson, we'll create a React-based frontend for our AI assistant web application. We'll implement components for file management, a chat interface, and a code editor. We'll also handle real-time updates and streaming responses from our backend API.

## Project Structure

Let's start by looking at our updated project structure, including the new frontend:

```
ai_assistant/
│
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── models/
│   │   ├── services/
│   │   └── middleware/
│   ├── core/
│   ├── utils/
│   ├── .env
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat.js
│   │   │   ├── FileManager.js
│   │   │   └── CodeEditor.js
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

## Step 1: Setting Up the React Project

First, let's create a new React project using Create React App:

```bash
npx create-react-app frontend
cd frontend
npm install axios react-ace socket.io-client
```

## Step 2: Implementing the Chat Component

Let's create a chat interface that communicates with our AI assistant:

```javascript
// src/components/Chat.js

import React, { useState, useEffect, useRef } from 'react';
import { sendMessage, startStreaming } from '../services/api';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      if (input.startsWith('/stream')) {
        setIsStreaming(true);
        const stream = await startStreaming(input.slice(8));
        let assistantMessage = { role: 'assistant', content: '' };
        setMessages(prev => [...prev, assistantMessage]);

        for await (const chunk of stream) {
          assistantMessage.content += chunk;
          setMessages(prev => [...prev.slice(0, -1), { ...assistantMessage }]);
        }
        setIsStreaming(false);
      } else {
        const response = await sendMessage(input);
        setMessages(prev => [...prev, { role: 'assistant', content: response }]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  return (
    <div className="chat">
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>
      <div className="chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          disabled={isStreaming}
        />
        <button onClick={handleSend} disabled={isStreaming}>Send</button>
      </div>
    </div>
  );
};

export default Chat;
```

## Step 3: Implementing the File Manager Component

Now, let's create a component to manage files:

```javascript
// src/components/FileManager.js

import React, { useState, useEffect } from 'react';
import { listFiles, uploadFile, deleteFile } from '../services/api';

const FileManager = () => {
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      const fileList = await listFiles();
      setFiles(fileList);
    } catch (error) {
      console.error('Error fetching files:', error);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      await uploadFile(file);
      fetchFiles();
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  const handleFileDelete = async (fileName) => {
    try {
      await deleteFile(fileName);
      fetchFiles();
    } catch (error) {
      console.error('Error deleting file:', error);
    }
  };

  return (
    <div className="file-manager">
      <h2>File Manager</h2>
      <input type="file" onChange={handleFileUpload} />
      <ul>
        {files.map((file, index) => (
          <li key={index}>
            {file.name}
            <button onClick={() => setSelectedFile(file)}>View</button>
            <button onClick={() => handleFileDelete(file.name)}>Delete</button>
          </li>
        ))}
      </ul>
      {selectedFile && (
        <div className="file-preview">
          <h3>{selectedFile.name}</h3>
          <pre>{selectedFile.content}</pre>
        </div>
      )}
    </div>
  );
};

export default FileManager;
```

## Step 4: Implementing the Code Editor Component

Let's create a code editor component using react-ace:

```javascript
// src/components/CodeEditor.js

import React, { useState } from 'react';
import AceEditor from 'react-ace';

import 'ace-builds/src-noconflict/mode-javascript';
import 'ace-builds/src-noconflict/theme-monokai';

const CodeEditor = ({ initialCode, onCodeChange }) => {
  const [code, setCode] = useState(initialCode || '');

  const handleChange = (newCode) => {
    setCode(newCode);
    onCodeChange(newCode);
  };

  return (
    <AceEditor
      mode="javascript"
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
  );
};

export default CodeEditor;
```

## Step 5: Implementing API Services

Let's create a service to handle API calls:

```javascript
// src/services/api.js

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
  },
});

export const sendMessage = async (message) => {
  const response = await api.post('/ai/ask', { prompt: message });
  return response.data.response;
};

export const startStreaming = async (message) => {
  const response = await api.post('/ai/stream', { prompt: message }, { responseType: 'stream' });
  return response.data;
};

export const listFiles = async () => {
  const response = await api.get('/files');
  return response.data;
};

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const deleteFile = async (fileName) => {
  const response = await api.delete(`/files/${fileName}`);
  return response.data;
};
```

## Step 6: Implementing WebSocket Service

To handle real-time updates, let's create a WebSocket service:

```javascript
// src/services/websocket.js

import io from 'socket.io-client';

const SOCKET_URL = 'http://localhost:8000';

class WebSocketService {
  socket = null;

  connect() {
    this.socket = io(SOCKET_URL, {
      auth: {
        token: localStorage.getItem('token'),
      },
    });

    this.socket.on('connect', () => {
      console.log('Connected to WebSocket');
    });

    this.socket.on('disconnect', () => {
      console.log('Disconnected from WebSocket');
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
    }
  }

  on(event, callback) {
    if (this.socket) {
      this.socket.on(event, callback);
    }
  }

  emit(event, data) {
    if (this.socket) {
      this.socket.emit(event, data);
    }
  }
}

export default new WebSocketService();
```

## Step 7: Putting It All Together in App.js

Now, let's combine all our components in the main App component:

```javascript
// src/App.js

import React, { useEffect } from 'react';
import Chat from './components/Chat';
import FileManager from './components/FileManager';
import CodeEditor from './components/CodeEditor';
import WebSocketService from './services/websocket';
import './App.css';

function App() {
  useEffect(() => {
    WebSocketService.connect();
    return () => {
      WebSocketService.disconnect();
    };
  }, []);

  const handleCodeChange = (newCode) => {
    // Here you can implement logic to send the updated code to the backend
    console.log('Code updated:', newCode);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Assistant</h1>
      </header>
      <div className="App-content">
        <div className="left-panel">
          <FileManager />
          <CodeEditor initialCode="" onCodeChange={handleCodeChange} />
        </div>
        <div className="right-panel">
          <Chat />
        </div>
      </div>
    </div>
  );
}

export default App;
```

## Step 8: Styling the Application

Let's add some basic styling to our application:

```css
/* src/App.css */

.App {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
}

.App-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.left-panel {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.right-panel {
  flex: 1;
  padding: 20px;
  border-left: 1px solid #ccc;
  display: flex;
  flex-direction: column;
}

.chat {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.chat-input {
  display: flex;
  padding: 10px;
}

.chat-input input {
  flex: 1;
  padding: 5px;
  font-size: 16px;
}

.chat-input button {
  padding: 5px 10px;
  font-size: 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
}

.file-manager ul {
  list-style-type: none;
  padding: 0;
}

.file-manager li {
  margin-bottom: 10px;
}

.file-preview {
  margin-top: 20px;
  border: 1px solid #ccc;
  padding: 10px;
}

.message {
  margin-bottom: 10px;
  padding: 10px;
  border-radius: 5px;
}

.message.user {
  background-color: #e6f3ff;
  align-self: flex-end;
}

.message.assistant {
  background-color: #f0f0f0;
  align-self: flex-start;
}
```

## Conclusion

In this lesson, we've created a React-based frontend for our AI assistant web application. We've implemented key components such as a chat interface, file manager, and code editor. We've also set up services to handle API calls and WebSocket connections for real-time updates.

Key takeaways:
1. React provides a powerful framework for building interactive user interfaces.
2. Components help organize and modularize our code, making it easier to manage and maintain.
3. Services abstract away the complexity of API calls and WebSocket connections.
4. Real-time updates can be achieved using WebSockets, enhancing the user experience.
5. The combination of a chat interface, file manager, and code editor creates a comprehensive environment for interacting with our AI assistant.

In the next lesson, we'll focus on advanced AI tasks and coding assistance, further enhancing the capabilities of our AI assistant.
