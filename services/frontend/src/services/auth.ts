/**
 * Google Sign-In authentication service
 */
import { fetchFromBackend } from './api'
import { ApiResponse, User } from '../types/models'

/**
 * Exchanges a Google Identity Services credential for the authenticated user
 * @param credential - The ID token credential returned by Google Identity Services
 * @returns The verified user's profile
 */
export function loginWithGoogle(credential: string): Promise<ApiResponse<User>> {
  return fetchFromBackend<User>('/api/v1/auth/google', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data: { credential } }),
  })
}
