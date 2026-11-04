import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import { AppProviders } from './providers/AppProviders.jsx';

// Import global styles ONLY
import './styles/global.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AppProviders>
      <App />
    </AppProviders>
  </React.StrictMode>,
);
