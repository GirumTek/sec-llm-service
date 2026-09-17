import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import outputs from "../amplify_outputs.json";
import "@aws-amplify/ui-react/styles.css";
import { Amplify } from "aws-amplify";
import { ThemeProvider } from "@aws-amplify/ui-react";

Amplify.configure(outputs);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
  <ThemeProvider>
    <App />
  </ThemeProvider>
</StrictMode>,
)
