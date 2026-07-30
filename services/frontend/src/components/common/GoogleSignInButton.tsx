import { useEffect, useRef } from 'react'

interface GoogleSignInButtonProps {
  ready: boolean
  onRender: (element: HTMLElement) => void
}

function GoogleSignInButton({ ready, onRender }: GoogleSignInButtonProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (ready && containerRef.current) {
      onRender(containerRef.current)
    }
  }, [ready, onRender])

  return <div ref={containerRef} />
}

export default GoogleSignInButton
