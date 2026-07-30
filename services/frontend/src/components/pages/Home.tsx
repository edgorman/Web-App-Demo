import { useEffect, useState } from 'react'
import { fetchFromBackend } from '../../services/api'
import { ApiResponse, Message } from '../../types/models'
import { useGoogleAuth } from '../../hooks/useGoogleAuth'
import GoogleSignInButton from '../common/GoogleSignInButton'

function Home() {
  const [data, setData] = useState<ApiResponse<Message> | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { user, error: authError, ready, renderButton, signOut } = useGoogleAuth()

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const response = await fetchFromBackend<Message>('/api/v1/hello')
        setData(response)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred')
        setData(null)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  return (
    <div className="home-container">
      <h1>Hello World</h1>
      <p>Welcome to the Web App Demo frontend service!</p>

      <div style={{ marginTop: '2rem' }}>
        <h2>Sign in</h2>
        {user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {user.picture && (
              <img
                src={user.picture}
                alt={user.name}
                style={{ width: 40, height: 40, borderRadius: '50%' }}
              />
            )}
            <div>
              <p style={{ margin: 0 }}>
                Signed in as <strong>{user.name}</strong> ({user.email})
              </p>
              <button onClick={signOut}>Sign out</button>
            </div>
          </div>
        ) : (
          <>
            <GoogleSignInButton ready={ready} onRender={renderButton} />
            {authError && <p style={{ color: 'red' }}>{authError}</p>}
          </>
        )}
      </div>

      <div style={{ marginTop: '2rem' }}>
        <h2>Backend API Response</h2>
        {loading && <p>Loading...</p>}
        {error && (
          <div
            style={{
              color: 'red',
              backgroundColor: '#ffebee',
              padding: '1rem',
              borderRadius: '4px',
              border: '1px solid #ef5350',
            }}
          >
            <h3 style={{ marginTop: 0 }}>Error Details:</h3>
            <pre
              style={{
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
                margin: 0,
                fontFamily: 'monospace',
                fontSize: '0.9rem',
              }}
            >
              {error}
            </pre>
          </div>
        )}
        {data && (
          <pre
            style={{
              backgroundColor: '#f5f5f5',
              padding: '1rem',
              borderRadius: '4px',
              textAlign: 'left',
              overflow: 'auto',
            }}
          >
            {JSON.stringify(data, null, 2)}
          </pre>
        )}
      </div>
    </div>
  )
}

export default Home
