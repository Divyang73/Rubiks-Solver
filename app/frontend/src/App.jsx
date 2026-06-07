import { Link, Route, Routes } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Home from './pages/Home'
import NotFound from './pages/NotFound'

export default function App() {
  return (
    <div className="app-shell">
      <Toaster position="bottom-right" />
      <header className="site-header">
        <Link to="/" className="brand">Korf Rubik&apos;s Solver</Link>
        <nav>
          <Link to="/">Solver</Link>
        </nav>
      </header>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="*" element={<NotFound />} />
      </Routes>

      <footer className="site-footer">
        Korf Rubik&apos;s Solver
      </footer>
    </div>
  )
}
