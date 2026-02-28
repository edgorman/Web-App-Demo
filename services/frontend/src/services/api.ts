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
  const url = `${config.backendUrl}${endpoint}`

  try {
    const response = await fetch(url)

    if (!response.ok) {
      const errorBody = await response.text().catch(() => 'No error details')
      throw new Error(
        `API request failed: ${response.status} ${response.statusText} - URL: ${url} - ${errorBody}`
      )
    }

    try {
      return await response.json()
    } catch (jsonError) {
      throw new Error(
        `Failed to parse JSON response from ${url}: ${jsonError instanceof Error ? jsonError.message : String(jsonError)}`
      )
    }
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error(`Failed to fetch from ${url}: ${String(error)}`)
  }
}
