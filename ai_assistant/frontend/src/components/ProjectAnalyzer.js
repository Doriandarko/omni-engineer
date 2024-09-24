// frontend/src/components/ProjectAnalyzer.js

import React, { useState } from 'react';
import { analyzeProject } from '../services/api';

const ProjectAnalyzer = () => {
  const [projectPath, setProjectPath] = useState('');
  const [analysis, setAnalysis] = useState(null);

  const handleAnalyze = async () => {
    try {
      const result = await analyzeProject(projectPath);
      setAnalysis(result.project_analysis);
    } catch (error) {
      console.error('Error analyzing project:', error);
    }
  };

  return (
    <div className="project-analyzer">
      <h2>Project Analyzer</h2>
      <input
        type="text"
        value={projectPath}
        onChange={(e) => setProjectPath(e.target.value)}
        placeholder="Enter project path"
      />
      <button onClick={handleAnalyze}>Analyze</button>
      {analysis && (
        <div className="analysis-result">
          <h3>Analysis Result:</h3>
          {Object.entries(analysis).map(([file, fileAnalysis]) => (
            <div key={file}>
              <h4>{file}</h4>
              <ul>
                {fileAnalysis.map((item, index) => (
                  <li key={index}>
                    {item.type}: {item.message} (line {item.line})
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProjectAnalyzer;