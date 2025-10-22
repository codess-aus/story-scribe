/**
 * Application Configuration
 * 
 * Centralizes environment-specific configuration values.
 * Uses Vite's environment variable system.
 */

export const config = {
  // API base URL - defaults to relative path for development proxy
  apiUrl: import.meta.env.VITE_API_URL || '',
  
  // Environment
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
  
  // Version
  version: import.meta.env.VITE_APP_VERSION || '0.1.0'
};

export default config;
