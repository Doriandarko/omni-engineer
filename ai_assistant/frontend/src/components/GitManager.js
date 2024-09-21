// frontend/src/components/GitManager.js

import React, { useState, useEffect } from 'react';
import { commitChanges, createBranch, getCurrentBranch, listBranches, reviewChanges } from '../services/api';

const GitManager = () => {
  const [branches, setBranches] = useState([]);
  const [currentBranch, setCurrentBranch] = useState('');
  const [commitMessage, setCommitMessage] = useState('');
  const [newBranchName, setNewBranchName] = useState('');
  const [review, setReview] = useState('');

  useEffect(() => {
    fetchBranches();
    fetchCurrentBranch();
  }, []);

  const fetchBranches = async () => {
    try {
      const branchList = await listBranches();
      setBranches(branchList);
    } catch (error) {
      console.error('Error fetching branches:', error);
    }
  };

  const fetchCurrentBranch = async () => {
    try {
      const branch = await getCurrentBranch();
      setCurrentBranch(branch);
    } catch (error) {
      console.error('Error fetching current branch:', error);
    }
  };

  const handleCommit = async () => {
    try {
      await commitChanges(commitMessage);
      setCommitMessage('');
      alert('Changes committed successfully');
    } catch (error) {
      console.error('Error committing changes:', error);
    }
  };

  const handleCreateBranch = async () => {
    try {
      await createBranch(newBranchName);
      setNewBranchName('');
      fetchBranches();
      fetchCurrentBranch();
    } catch (error) {
      console.error('Error creating branch:', error);
    }
  };

  const handleReview = async () => {
    try {
      const reviewResult = await reviewChanges();
      setReview(reviewResult);
    } catch (error) {
      console.error('Error reviewing changes:', error);
    }
  };

  return (
    <div className="git-manager">
      <h2>Git Manager</h2>
      <div>
        <h3>Current Branch: {currentBranch}</h3>
        <h3>Branches:</h3>
        <ul>
          {branches.map((branch, index) => (
            <li key={index}>{branch}</li>
          ))}
        </ul>
      </div>
      <div>
        <h3>Commit Changes</h3>
        <input
          type="text"
          value={commitMessage}
          onChange={(e) => setCommitMessage(e.target.value)}
          placeholder="Enter commit message"
        />
        <button onClick={handleCommit}>Commit</button>
      </div>
      <div>
        <h3>Create New Branch</h3>
        <input
          type="text"
          value={newBranchName}
          onChange={(e) => setNewBranchName(e.target.value)}
          placeholder="Enter new branch name"
        />
        <button onClick={handleCreateBranch}>Create Branch</button>
      </div>
      <div>
        <h3>Review Changes</h3>
        <button onClick={handleReview}>Review</button>
        {review && (
          <div className="review-result">
            <h4>AI Review:</h4>
            <pre>{review}</pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default GitManager;