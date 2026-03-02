export function Card({ title, subtitle, children, className = '' }) {
  return (
    <section className={`rounded-2xl border border-amber-100/40 bg-white/85 p-5 shadow-flame backdrop-blur ${className}`}>
      {(title || subtitle) && (
        <header className="mb-4 border-b border-amber-200/50 pb-3">
          {title && <h2 className="font-title text-2xl text-amber-900">{title}</h2>}
          {subtitle && <p className="mt-1 text-sm text-amber-800/70">{subtitle}</p>}
        </header>
      )}
      {children}
    </section>
  )
}
