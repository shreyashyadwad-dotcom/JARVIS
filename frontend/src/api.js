const BASE_URL = 'http://localhost:8000'

export async function sendMessage(message, sessionId) {
  const res = await fetch(`${BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId }),
  })
  if (!res.ok) throw new Error('Jarvis backend returned an error')
  return res.json()
}

export async function getSessions() {
  const res = await fetch(`${BASE_URL}/api/sessions`)
  if (!res.ok) throw new Error('Could not load sessions')
  return res.json()
}

export async function getHistory(sessionId) {
  const res = await fetch(`${BASE_URL}/api/history/${sessionId}`)
  if (!res.ok) throw new Error('Could not load history')
  return res.json()
}

export async function clearHistory(sessionId) {
  const res = await fetch(`${BASE_URL}/api/history/${sessionId}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Could not clear history')
  return res.json()
}

export async function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${BASE_URL}/api/upload`, {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) throw new Error('Upload failed')
  return res.json()
}

export async function checkHealth() {
  const res = await fetch(`${BASE_URL}/api/health`)
  if (!res.ok) throw new Error('Backend unreachable')
  return res.json()
}
