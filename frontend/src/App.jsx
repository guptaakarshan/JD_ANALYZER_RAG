import React from 'react';
import Dashboard from './pages/Dashboard';
import { Toaster } from 'react-hot-toast';

function App() {
  return (
    <>
      <Dashboard />
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            fontFamily: 'Inter, sans-serif',
            fontSize: '13px',
            background: '#1a1a1f',
            color: '#fafafa',
            border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: '10px',
            boxShadow: '0 8px 24px rgba(0,0,0,0.4)',
          },
          success: { iconTheme: { primary: '#22c55e', secondary: '#1a1a1f' } },
          error:   { iconTheme: { primary: '#ef4444', secondary: '#1a1a1f' } },
        }}
      />
    </>
  );
}

export default App;
