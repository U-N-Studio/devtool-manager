import { useEffect, useState } from 'react'

export default function App() {
  const [status, setStatus] = useState('connecting...')

  useEffect(() => {
    window.api
      .rpc('ping')
      .then((r: any) => setStatus(JSON.stringify(r)))
      .catch((e: Error) => setStatus(`error: ${e.message}`))
  }, [])

  return (
    <div className="flex h-screen w-screen flex-col items-center justify-center">
      <h1 className="text-2xl font-bold">DevTool Manager</h1>
      <p className="mt-4 text-muted-foreground">{status}</p>
    </div>
  )
}
