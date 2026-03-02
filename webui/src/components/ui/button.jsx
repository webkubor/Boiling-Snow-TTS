export function Button({ children, className = '', ...props }) {
  return (
    <button
      className={`rounded-xl bg-amber-700 px-4 py-2 text-sm font-semibold text-amber-50 transition hover:bg-amber-800 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
