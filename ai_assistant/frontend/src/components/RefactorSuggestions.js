import React from 'react';

const RefactorSuggestions = ({ suggestions }) => {
  return (
    <div className="refactor-suggestions">
      <h3>Refactoring Suggestions</h3>
      {suggestions.length > 0 ? (
        <ul>
          {suggestions.map((suggestion, index) => (
            <li key={index}>
              <strong>Line {suggestion.line}:</strong> {suggestion.message}
              <pre>{suggestion.suggestion}</pre>
            </li>
          ))}
        </ul>
      ) : (
        <p>No refactoring suggestions available.</p>
      )}
    </div>
  );
};

export default RefactorSuggestions;