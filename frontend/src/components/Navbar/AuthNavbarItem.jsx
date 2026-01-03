import React from 'react';
import Link from '@docusaurus/Link';
import { useAuth } from '@site/src/components/Auth/AuthContext';

const AuthNavbarItem = () => {
  const { isAuthenticated, user, logout } = useAuth();

  if (isAuthenticated) {
    return (
      <div className="navbar__item navbar__item--right">
        <div className="dropdown dropdown--hoverable dropdown--right">
          <span className="navbar__link">
            {user?.username || user?.email}
          </span>
          <ul className="dropdown__menu">
            <li>
              <Link className="dropdown__link" to="/profile">
                Profile
              </Link>
            </li>
            <li>
              <button 
                className="dropdown__link"
                onClick={logout}
                style={{ width: '100%', textAlign: 'left', background: 'none', border: 'none', cursor: 'pointer' }}
              >
                Logout
              </button>
            </li>
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className="navbar__item navbar__item--right">
      <Link className="navbar__link" to="/auth">
        Login/Register
      </Link>
    </div>
  );
};

export default AuthNavbarItem;