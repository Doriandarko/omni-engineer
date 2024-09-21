// frontend/src/services/api.js

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include the auth token in all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export const login = async (username, password) => {
  const response = await api.post('/auth/token', { username, password });
  return response.data;
};

export const sendMessage = async (message) => {
  const response = await api.post('/ai/ask', { prompt: message });
  return response.data.response;
};

export const startStreaming = async (message) => {
  const response = await api.post('/ai/stream', { prompt: message }, { responseType: 'stream' });
  return response.data;
};

export const listFiles = async () => {
  const response = await api.get('/files/list');
  return response.data.files;
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

export const getFileContent = async (fileName) => {
  const response = await api.get(`/files/${fileName}`);
  return response.data.content;
};

export const getRefactoringSuggestions = async (code, language) => {
  const response = await api.post('/code/refactor', { code, language });
  return response.data;
};

export const getCodeCompletion = async (code, language) => {
  const response = await api.post('/code/complete', { code, language });
  return response.data.completion;
};

export const commitChanges = async (message) => {
  const response = await api.post('/git/commit', { message });
  return response.data;
};

export const createBranch = async (name) => {
  const response = await api.post('/git/create-branch', { name });
  return response.data;
};

export const getCurrentBranch = async () => {
  const response = await api.get('/git/current-branch');
  return response.data.branch;
};

export const listBranches = async () => {
  const response = await api.get('/git/branches');
  return response.data.branches;
};

export const reviewChanges = async () => {
  const response = await api.post('/git/review');
  return response.data.review;
};

export const analyzeProject = async (projectPath) => {
  const response = await api.post('/project/analyze', { project_path: projectPath });
  return response.data;
};

export default api;