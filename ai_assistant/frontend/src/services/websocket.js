// frontend/src/services/websocket.js

import io from 'socket.io-client';

const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || 'http://localhost:8000';

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

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error);
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

  // Example method for AI streaming
  streamAIResponse(prompt, callback) {
    this.emit('stream_ai_response', { prompt });
    this.on('ai_stream_chunk', callback);
  }

  // Example method for real-time file updates
  subscribeToFileUpdates(callback) {
    this.on('file_updated', callback);
  }

  // Example method for real-time Git updates
  subscribeToGitUpdates(callback) {
    this.on('git_update', callback);
  }
}

export default new WebSocketService();