export default function Sidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  onUpload,
  uploadStatus,
}) {
  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <span className="sidebar__brand-dot" />
        JARVIS
      </div>

      <button className="btn btn--primary sidebar__new-chat" onClick={onNewChat}>
        + New session
      </button>

      <div className="sidebar__section-label">History log</div>
      <div className="sidebar__sessions">
        {sessions.length === 0 && (
          <div className="sidebar__empty">No sessions yet. Say hello.</div>
        )}
        {sessions.map((s) => (
          <button
            key={s.id}
            className={`sidebar__session ${s.id === activeSessionId ? 'sidebar__session--active' : ''}`}
            onClick={() => onSelectSession(s.id)}
          >
            {s.title || 'Untitled session'}
          </button>
        ))}
      </div>

      <div className="sidebar__section-label">Knowledge base</div>
      <label className="btn btn--ghost sidebar__upload">
        Upload document (.txt/.md/.pdf)
        <input
          type="file"
          accept=".txt,.md,.pdf"
          style={{ display: 'none' }}
          onChange={(e) => e.target.files[0] && onUpload(e.target.files[0])}
        />
      </label>
      {uploadStatus && <div className="sidebar__upload-status">{uploadStatus}</div>}
    </aside>
  )
}
