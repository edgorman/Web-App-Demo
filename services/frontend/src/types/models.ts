/**
 * Type definitions for backend API responses
 */

export interface Message {
  message: string
}

export interface User {
  id: string
  email: string
  name: string
}

export interface ApiResponse<T> {
  data: T
  timestamp: string
  success: boolean
  message?: string | null
}
