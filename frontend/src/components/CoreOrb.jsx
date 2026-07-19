export default function CoreOrb({ state }) {
  // state: 'idle' | 'thinking' | 'speaking'
  return (
    <div className={`core-orb core-orb--${state}`}>
      <div className="core-orb__ring core-orb__ring--outer" />
      <div className="core-orb__ring core-orb__ring--mid" />
      <div className="core-orb__core" />
    </div>
  )
}
