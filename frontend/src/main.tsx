import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './CSS/index.css'
import App from './App.tsx'
// import AppBackup from './App-backup.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
    {/* <AppBackup /> */}
  </StrictMode>,
)
