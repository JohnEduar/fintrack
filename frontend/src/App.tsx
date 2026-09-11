import { useState } from 'react'
import { getApiHealth } from './api/client'

type ApiStatus = 'idle' | 'checking' | 'connected' | 'error'

function App() {
  const [apiStatus, setApiStatus] = useState<ApiStatus>('idle')
  const [statusMessage, setStatusMessage] = useState('Aún no se ha comprobado la conexión.')

  async function checkApiConnection() {
    setApiStatus('checking')
    setStatusMessage('Comprobando conexión con FastAPI…')

    try {
      const health = await getApiHealth()
      setApiStatus('connected')
      setStatusMessage(`${health.message} Base de datos: conectada.`)
    } catch {
      setApiStatus('error')
      setStatusMessage('No se pudo conectar. Verifica que FastAPI esté ejecutándose en el puerto 8000.')
    }
  }

  return (
    <main className="page-shell">
      <section className="hero" aria-labelledby="app-title">
        <p className="eyebrow">Finanzas personales</p>
        <h1 id="app-title">FinTrack</h1>
        <p className="intro">
          La base visual está lista. El próximo paso será convertir esta pantalla en el inicio de sesión.
        </p>

        <div className="api-card">
          <div>
            <p className="card-label">Estado de la API</p>
            <p className={`status status--${apiStatus}`} role="status">
              {statusMessage}
            </p>
          </div>
          <button type="button" onClick={checkApiConnection} disabled={apiStatus === 'checking'}>
            {apiStatus === 'checking' ? 'Comprobando…' : 'Probar conexión'}
          </button>
        </div>
      </section>
    </main>
  )
}

export default App
