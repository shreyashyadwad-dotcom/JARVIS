import { useEffect, useRef, useState } from 'react'
import CoreOrb from './components/CoreOrb.jsx'
import ChatMessage from './components/ChatMessage.jsx'
import Sidebar from './components/Sidebar.jsx'
import { sendMessage, getSessions, getHistory, uploadDocument, checkHealth } from './api.js'

function formatTime(iso) {
  try {
    return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch {
    return ''
  }
}

export default function App() {
  const [sessions, setSessions] = useState([])
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [orbState, setOrbState] = useState('idle')
  const [backendStatus, setBackendStatus] = useState('checking')
  const [uploadStatus, setUploadStatus] = useState('')
  const scrollRef = useRef(null)

  useEffect(() => {
    checkHealth()
      .then((h) => setBackendStatus(h.mode))
      .catch(() => setBackendStatus('offline'))
    refreshSessions()
  }, [])

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, orbState])

  async function refreshSessions() {
    try {
      const s = await getSessions()
      setSessions(s)
    } catch {
      /* backend not running yet -- fine on first load */
    }
  }

  async function handleSelectSession(id) {
    setSessionId(id)
    const hist = await getHistory(id)
    setMessages(hist.map((h) => ({ ...h, timestamp: formatTime(h.created_at) })))
  }

  function handleNewChat() {
    setSessionId(null)
    setMessages([])
  }

  async function handleSend() {
    const text = input.trim()
    if (!text) return
    setInput('')

    const userMsg = { role: 'user', content: text, timestamp: formatTime(new Date().toISOString()) }
    setMessages((prev) => [...prev, userMsg])
    setOrbState('thinking')

    try {
      const res = await sendMessage(text, sessionId)
      setSessionId(res.session_id)
      setOrbState('speaking')
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.reply,
          sources: res.sources,
          timestamp: formatTime(new Date().toISOString()),
        },
      ])
      refreshSessions()
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `Connection error: ${err.message}. Is the backend running on port 8000?` },
      ])
    } finally {
      setTimeout(() => setOrbState('idle'), 600)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  async function handleUpload(file) {
    setUploadStatus(`Indexing ${file.name}...`)
    try {
      const res = await uploadDocument(file)
      setUploadStatus(`Indexed (${res.total_chunks_in_index} chunks total)`)
    } catch (err) {
      setUploadStatus(`Failed: ${err.message}`)
    }
  }

  return (
    <div className="app">
      <Sidebar
        sessions={sessions}
        activeSessionId={sessionId}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        onUpload={handleUpload}
        uploadStatus={uploadStatus}
      />

      <main className="main">
        <header className="topbar">
          <div className="topbar__title">Personal Assistant Console</div>
          <div className={`topbar__status topbar__status--${backendStatus === 'offline' ? 'off' : 'on'}`}>
            <span className="topbar__status-dot" />
            {backendStatus === 'checking' && 'Connecting...'}
            {backendStatus === 'offline' && 'Backend offline'}
            {backendStatus !== 'checking' && backendStatus !== 'offline' && `Online -- ${backendStatus}`}
          </div>
        </header>

        <div className="chat-area" ref={scrollRef}>
          {messages.length === 0 && (
            <div className="empty-state">
              <CoreOrb state="idle" />
              <p>Systems online. How can I help, sir/ma'am?</p>
            </div>
          )}

          {messages.map((m, i) => (
            <ChatMessage
              key={i}
              role={m.role}
              content={m.content}
              sources={m.sources}
              timestamp={m.timestamp}
            />
          ))}

          {orbState === 'thinking' && (
            <div className="msg-row msg-row--jarvis">
              <div className="msg-bubble msg-bubble--thinking">
                <CoreOrb state="thinking" />
                <span>Processing...</span>
              </div>
            </div>
          )}
        </div>

        <div className="composer">
          <textarea
            className="composer__input"
            placeholder="Ask Jarvis anything..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
          />
          <button className="btn btn--primary composer__send" onClick={handleSend}>
            Send
          </button>
        </div>
      </main>
    </div>
  )
}
