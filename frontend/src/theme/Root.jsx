import React from 'react';
import { AuthProvider } from '@site/src/components/Auth/AuthContext';

// Root component that wraps the entire app
const Root = ({ children }) => {
  return (
    <AuthProvider>
      {children}
    </AuthProvider>
  );
};

export default Root;