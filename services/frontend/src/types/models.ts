/**
 * Type definitions for backend API responses
 */

export interface Message {
  message: string
}

export interface ApiResponse<T> {
  data: T
  timestamp: string
  success: boolean
  message?: string | null
}
