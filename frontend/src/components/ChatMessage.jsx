export default function ChatMessage({ role, content, sources, timestamp }) {
  const isUser = role === 'user'
  return (
    <div className={`msg-row ${isUser ? 'msg-row--user' : 'msg-row--jarvis'}`}>
      <div className="msg-bubble">
        <div className="msg-bubble__label">
          {isUser ? 'YOU' : 'JARVIS'}
          {timestamp && <span className="msg-bubble__time">{timestamp}</span>}
        </div>
        <div className="msg-bubble__text">{content}</div>
        {sources && sources.length > 0 && (
          <div className="msg-bubble__sources">
            <span>Referenced:</span>
            {sources.map((s) => (
              <span className="source-chip" key={s}>{s}</span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
