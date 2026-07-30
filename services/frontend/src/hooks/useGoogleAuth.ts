/**
 * Hook wrapping the Google Identity Services sign-in flow.
 *
 * There is no backend login call: the ID token from Google is decoded
 * client-side for display, and reused as a bearer credential on backend
 * requests, which verify it via the auth middleware.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { config } from '../config/app'
import { User } from '../types/models'
import { GoogleCredentialResponse } from '../types/google'

const SCRIPT_ELEMENT_ID = 'google-identity-services'
const AUTH_PROVIDER = 'google'

function decodeCredential(credential: string): User {
  // JWT payloads are base64url-encoded (`-`/`_`, no padding); atob() only
  // understands standard base64 (`+`/`/`), so translate before decoding.
  const base64 = credential.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
  const payload = JSON.parse(atob(base64))
  return {
    id: payload.sub,
    email: payload.email,
    name: payload.name ?? payload.email,
  }
}

interface UseGoogleAuthResult {
  user: User | null
  authHeaders: Record<string, string>
  error: string | null
  ready: boolean
  renderButton: (element: HTMLElement) => void
  signOut: () => void
}

export function useGoogleAuth(): UseGoogleAuthResult {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [ready, setReady] = useState(false)
  const initialized = useRef(false)

  const handleCredentialResponse = useCallback((response: GoogleCredentialResponse) => {
    try {
      setUser(decodeCredential(response.credential))
      setToken(response.credential)
      setError(null)
    } catch {
      setError('Failed to read the Google sign-in response')
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
    setToken(null)
  }, [])

  const authHeaders = useMemo<Record<string, string>>(() => {
    const headers: Record<string, string> = {}
    if (token) {
      headers.Authorization = `Bearer ${token}`
      headers['Authorization-Provider'] = AUTH_PROVIDER
    }
    return headers
  }, [token])

  return { user, authHeaders, error, ready, renderButton, signOut }
}
