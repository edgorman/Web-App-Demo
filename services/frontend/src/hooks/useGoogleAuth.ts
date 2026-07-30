/**
 * Hook wrapping the Google Identity Services sign-in flow
 */
import { useCallback, useEffect, useRef, useState } from 'react'
import { config } from '../config/app'
import { loginWithGoogle } from '../services/auth'
import { User } from '../types/models'
import { GoogleCredentialResponse } from '../types/google'

const STORAGE_KEY = 'google_user'
const SCRIPT_ELEMENT_ID = 'google-identity-services'

function readStoredUser(): User | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as User) : null
  } catch {
    return null
  }
}

interface UseGoogleAuthResult {
  user: User | null
  error: string | null
  ready: boolean
  renderButton: (element: HTMLElement) => void
  signOut: () => void
}

export function useGoogleAuth(): UseGoogleAuthResult {
  const [user, setUser] = useState<User | null>(readStoredUser)
  const [error, setError] = useState<string | null>(null)
  const [ready, setReady] = useState(false)
  const initialized = useRef(false)

  const handleCredentialResponse = useCallback(async (response: GoogleCredentialResponse) => {
    try {
      const apiResponse = await loginWithGoogle(response.credential)
      setUser(apiResponse.data)
      setError(null)
      localStorage.setItem(STORAGE_KEY, JSON.stringify(apiResponse.data))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Google sign-in failed')
    }
  }, [])

  useEffect(() => {
    if (!config.googleClientId) {
      setError('Google sign-in is not configured (missing VITE_GOOGLE_CLIENT_ID)')
      return
    }

    const initialize = () => {
      if (initialized.current || !window.google) {
        return
      }
      window.google.accounts.id.initialize({
        client_id: config.googleClientId,
        callback: handleCredentialResponse,
      })
      initialized.current = true
      setReady(true)
    }

    if (window.google) {
      initialize()
      return
    }

    const script = document.getElementById(SCRIPT_ELEMENT_ID)
    script?.addEventListener('load', initialize)
    return () => script?.removeEventListener('load', initialize)
  }, [handleCredentialResponse])

  const renderButton = useCallback((element: HTMLElement) => {
    if (!window.google || !initialized.current) {
      return
    }
    window.google.accounts.id.renderButton(element, {
      type: 'standard',
      theme: 'outline',
      size: 'large',
    })
  }, [])

  const signOut = useCallback(() => {
    window.google?.accounts.id.disableAutoSelect()
    setUser(null)
    localStorage.removeItem(STORAGE_KEY)
  }, [])

  return { user, error, ready, renderButton, signOut }
}
