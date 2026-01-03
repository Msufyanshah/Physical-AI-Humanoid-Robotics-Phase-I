import React from 'react';
import { useAuth } from '@site/src/components/Auth/AuthContext';
import Link from '@docusaurus/Link';

const ProfilePage = () => {
  const { user, isAuthenticated, logout } = useAuth();

  if (!isAuthenticated) {
    return (
      <div style={{ padding: '2rem' }}>
        <h1>Profile</h1>
        <p>Please <Link to="/auth">log in</Link> to view your profile.</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem' }}>
      <h1>User Profile</h1>
      <div style={{ backgroundColor: '#f8f9fa', padding: '1.5rem', borderRadius: '8px' }}>
        <p><strong>Email:</strong> {user?.email}</p>
        <p><strong>Username:</strong> {user?.username || 'Not set'}</p>
        <p><strong>User ID:</strong> {user?.id}</p>
      </div>
      <div style={{ marginTop: '1.5rem' }}>
        <button 
          onClick={logout}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Logout
        </button>
      </div>
    </div>
  );
};

export default ProfilePage;