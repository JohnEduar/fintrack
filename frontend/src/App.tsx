import { useState, type FormEvent } from 'react'
import { login } from './api/client'
import {
  getAccessToken,
  removeAccessToken,
  saveAccessToken,
} from './auth/token'
import Dashboard from './pages/Dashboard'

function App() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(
    () => getAccessToken() !== null,
  )

  function handleLogout(logoutMessage = '') {
    removeAccessToken()
    setIsAuthenticated(false)
    setEmail('')
    setPassword('')
    setMessage(logoutMessage)
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!email.trim() || !password.trim()) {
      setMessage('Completa tu correo y contraseña.')
      return
    }

    setIsSubmitting(true)
    setMessage('')

    try {
      const session = await login(email, password)

      saveAccessToken(session.access_token)
      setIsAuthenticated(true)
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : 'Ocurrió un error inesperado al iniciar sesión.'

      setMessage(errorMessage)
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isAuthenticated) {
    return <Dashboard onLogout={handleLogout} />
  }

  return (
    <main className="auth-page">
      <section className="auth-card" aria-labelledby="login-title">
        <div className="brand">
          <p className="eyebrow">Finanzas personales</p>
          <h1>FinTrack</h1>
        </div>

        <div>
          <h2 id="login-title">Bienvenido de nuevo</h2>
          <p className="description">
            Inicia sesión para consultar y organizar tus finanzas.
          </p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <label htmlFor="email">
            Correo electrónico
            <input
              id="email"
              name="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="nombre@ejemplo.com"
              autoComplete="email"
              required
              disabled={isSubmitting}
            />
          </label>

          <label htmlFor="password">
            Contraseña
            <input
              id="password"
              name="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Tu contraseña"
              autoComplete="current-password"
              required
              disabled={isSubmitting}
            />
          </label>

          {message && (
            <p className="form-message" role="status">
              {message}
            </p>
          )}

          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Iniciando sesión…' : 'Iniciar sesión'}
          </button>
        </form>

        <p className="register-hint">
          ¿Aún no tienes una cuenta? El registro será el siguiente paso.
        </p>
      </section>
    </main>
  )
}

export default App