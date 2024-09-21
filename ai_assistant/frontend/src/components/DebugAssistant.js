import React, { useState } from 'react';
import { getDebugAssistance } from '../services/api';

const DebugAssistant = ({ code, language }) => {
  const [error, setError] = useState('');
  const [assistance, setAssistance] = useState('');

  const handleDebugRequest = async () => {
    try {
      const response = await getDebugAssistance(code, error, language);
      setAssistance(response.assistance);
    } catch (error) {
      console.error('Error getting debug assistance:', error);
      setAssistance('An error occurred while fetching debug assistance.');
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