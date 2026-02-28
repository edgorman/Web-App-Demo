/**
 * API service for backend communication
 */
import { config } from '../config/app'
import { ApiResponse } from '../types/models'

/**
 * Fetches data from the backend API
 * @param endpoint - The API endpoint to call (e.g., '/api/v1/hello')
 * @returns The API response
 */
export async function fetchFromBackend<T>(
  endpoint: string
): Promise<ApiResponse<T>> {
  const url = `${config.apiUrl}${endpoint}`

  const response = await fetch(url)

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`)
  }

  return response.json()
}
