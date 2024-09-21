// frontend/src/components/CodeEditor.js

import React, { useState, useEffect } from 'react';
import AceEditor from 'react-ace';
import 'ace-builds/src-noconflict/mode-python';
import 'ace-builds/src-noconflict/theme-monokai';
import { getRefactoringSuggestions, getCodeCompletion } from '../services/api';
import RefactorSuggestions from './RefactorSuggestions';
import DebugAssistant from './DebugAssistant';

const CodeEditor = () => {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [suggestions, setSuggestions] = useState([]);

  useEffect(() => {
    const debouncedGetSuggestions = debounce(async () => {
      try {
        const response = await getRefactoringSuggestions(code, language);
        setSuggestions(response.suggestions);
      } catch (error) {
        console.error('Error getting refactoring suggestions:', error);
      }
    }, 1000);

    debouncedGetSuggestions();

    return () => debouncedGetSuggestions.cancel();
  }, [code, language]);

  const handleChange = (newCode) => {
    setCode(newCode);
  };

  const handleLanguageChange = (event) => {
    setLanguage(event.target.value);
  };

  const handleCompletion = async () => {
    try {
      const completion = await getCodeCompletion(code, language);
      setCode(code + completion);
    } catch (error) {
      console.error('Error getting code completion:', error);
    }
  };

  return (
    <div className="code-editor">
      <select value={language} onChange={handleLanguageChange}>
        <option value="python">Python</option>
        <option value="javascript">JavaScript</option>
        {/* Add more language options as needed */}
      </select>
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
      <button onClick={handleCompletion}>Get Completion</button>
      <RefactorSuggestions suggestions={suggestions} />
      <DebugAssistant code={code} language={language} />
    </div>
  );
};

export default CodeEditor;