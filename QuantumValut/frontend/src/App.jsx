import React, { useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import AppRouter from './routes/AppRouter';
import { useAuth } from './hooks/useAuth';

function App() {
  useAuth(); // Initialize auth hook and session restoration

  return (
    <>
      <Toaster position="top-right" />
      <AppRouter />
    </>
  );
}

export default App;
