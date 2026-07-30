/**
 * Application configuration
 */
export const config = {
  backendUrl: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8080',
  googleClientId: import.meta.env.VITE_GOOGLE_CLIENT_ID || '',
}
