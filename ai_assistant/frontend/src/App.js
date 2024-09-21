// frontend/src/App.js

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Navbar from './components/Navbar';
import Chat from './components/Chat';
import FileManager from './components/FileManager';
import CodeEditor from './components/CodeEditor';
import GitManager from './components/GitManager';
import ProjectAnalyzer from './components/ProjectAnalyzer';
import Login from './components/Login';
import { AuthProvider } from './context/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Navbar />
          <Switch>
            <Route exact path="/login" component={Login} />
            <PrivateRoute exact path="/" component={Chat} />
            <PrivateRoute path="/files" component={FileManager} />
            <PrivateRoute path="/editor" component={CodeEditor} />
            <PrivateRoute path="/git" component={GitManager} />
            <PrivateRoute path="/analyze" component={ProjectAnalyzer} />
          </Switch>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;