// frontend/src/components/FileManager.js

import React, { useState, useEffect } from 'react';
import { listFiles, uploadFile, deleteFile, getFileContent } from '../services/api';

const FileManager = () => {
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('');

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
      if (selectedFile === fileName) {
        setSelectedFile(null);
        setFileContent('');
      }
    } catch (error) {
      console.error('Error deleting file:', error);
    }
  };

  const handleFileSelect = async (fileName) => {
    try {
      const content = await getFileContent(fileName);
      setSelectedFile(fileName);
      setFileContent(content);
    } catch (error) {
      console.error('Error fetching file content:', error);
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
            <button onClick={() => handleFileSelect(file.name)}>View</button>
            <button onClick={() => handleFileDelete(file.name)}>Delete</button>
          </li>
        ))}
      </ul>
      {selectedFile && (
        <div className="file-preview">
          <h3>{selectedFile}</h3>
          <pre>{fileContent}</pre>
        </div>
      )}
    </div>
  );
};

export default FileManager;