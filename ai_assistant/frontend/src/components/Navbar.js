// frontend/src/components/Navbar.js

import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();

  return (
    <nav className="navbar">
      <ul>
        <li><Link to="/">Home</Link></li>
        <li><Link to="/files">Files</Link></li>
        <li><Link to="/editor">Code Editor</Link></li>
        <li><Link to="/git">Git Manager</Link></li>
        <li><Link to="/analyze">Project Analyzer</Link></li>
      </ul>
      <div className="user-menu">
        {user ? (
          <>
            <span>Welcome, {user.username}!</span>
            <button onClick={logout}>Logout</button>
          </>
        ) : (
          <Link to="/login">Login</Link>
        )}
      </div>
    </nav>
  );
};

export default Navbar;