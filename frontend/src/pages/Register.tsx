import { useState, type FormEvent } from 'react'
import { registerUser } from '../api/client'

type RegisterProps = {
  onBackToLogin: () => void
  onRegistrationSuccess: (email: string) => void
}

function Register({
  onBackToLogin,
  onRegistrationSuccess,
}: RegisterProps) {
  const [name, setName] = useState('')
  const [lastName, setLastName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (
      !name.trim() ||
      !lastName.trim() ||
      !email.trim() ||
      !password.trim()
    ) {
      setMessage('Completa todos los campos.')
      return
    }

    setIsSubmitting(true)
    setMessage('')

    try {
      await registerUser({
        name: name.trim(),
        last_name: lastName.trim(),
        email: email.trim(),
        password,
      })

      onRegistrationSuccess(email.trim())
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : 'Ocurrió un error inesperado al crear la cuenta.'

      setMessage(errorMessage)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card" aria-labelledby="register-title">
        <div className="brand">
          <p className="eyebrow">Finanzas personales</p>
          <h1>FinTrack</h1>
        </div>

        <div>
          <h2 id="register-title">Crea tu cuenta</h2>
          <p className="description">
            Empieza a organizar tus ingresos, gastos y presupuestos.
          </p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <label htmlFor="name">
            Nombre
            <input
              id="name"
              name="name"
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Tu nombre"
              autoComplete="given-name"
              required
              disabled={isSubmitting}
            />
          </label>

          <label htmlFor="last-name">
            Apellido
            <input
              id="last-name"
              name="last-name"
              type="text"
              value={lastName}
              onChange={(event) => setLastName(event.target.value)}
              placeholder="Tu apellido"
              autoComplete="family-name"
              required
              disabled={isSubmitting}
            />
          </label>

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
              placeholder="Crea una contraseña"
              autoComplete="new-password"
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
            {isSubmitting ? 'Creando cuenta…' : 'Crear cuenta'}
          </button>
        </form>

        <button
          type="button"
          className="logout-button"
          onClick={onBackToLogin}
          disabled={isSubmitting}
        >
          Ya tengo una cuenta
        </button>
      </section>
    </main>
  )
}

export default Register