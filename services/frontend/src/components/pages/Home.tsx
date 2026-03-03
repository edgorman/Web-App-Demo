import { useEffect, useState } from 'react'
import { fetchFromBackend } from '../../services/api'
import { ApiResponse, Message } from '../../types/models'

function Home() {
  const [data, setData] = useState<ApiResponse<Message> | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const response = await fetchFromBackend<Message>('/')
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
