import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <main className="page">
      <section className="panel">
        <h1>Page not found</h1>
        <p>This route does not exist.</p>
        <Link className="inline-link" to="/">Return to solver</Link>
      </section>
    </main>
  )
}
