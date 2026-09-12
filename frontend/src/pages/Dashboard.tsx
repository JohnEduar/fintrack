import { useEffect, useState } from 'react'
import {
  getFinancialSummary,
  type FinancialSummary,
  UnauthorizedError,
} from '../api/client'
import { getAccessToken } from '../auth/token'

type DashboardProps = {
  onLogout: (message?: string) => void
}

function formatAmount(amount: string): string {
  return new Intl.NumberFormat('es-CO', {
    maximumFractionDigits: 2,
  }).format(Number(amount))
}

function Dashboard({ onLogout }: DashboardProps) {
  const [summary, setSummary] = useState<FinancialSummary | null>(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function loadSummary() {
      const accessToken = getAccessToken()

      if (!accessToken) {
        onLogout('No se encontró una sesión activa.')
        return
      }

      try {
        const financialSummary = await getFinancialSummary(accessToken)
        setSummary(financialSummary)
      } catch (requestError) {
        if (requestError instanceof UnauthorizedError) {
          onLogout(requestError.message)
          return
        }

        const errorMessage =
          requestError instanceof Error
            ? requestError.message
            : 'Ocurrió un error inesperado al cargar el resumen.'

        setError(errorMessage)
      } finally {
        setIsLoading(false)
      }
    }

    void loadSummary()
  }, [onLogout])

  return (
    <main className="dashboard-page">
      <header className="dashboard-header">
        <div>
          <p className="eyebrow">Finanzas personales</p>
          <h1>FinTrack</h1>
        </div>

        <button type="button" className="logout-button" onClick={() => onLogout()}>
          Cerrar sesión
        </button>
      </header>

      <section className="dashboard-content" aria-labelledby="dashboard-title">
        <p className="eyebrow">Resumen financiero</p>
        <h2 id="dashboard-title">Tu situación actual</h2>

        {isLoading && <p>Cargando resumen financiero…</p>}

        {error && (
          <p className="form-message" role="alert">
            {error}
          </p>
        )}

        {summary && (
          <dl>
            <dt>Ingresos</dt>
            <dd>{formatAmount(summary.total_income)}</dd>

            <dt>Gastos</dt>
            <dd>{formatAmount(summary.total_expense)}</dd>

            <dt>Balance neto</dt>
            <dd>{formatAmount(summary.net_balance)}</dd>
          </dl>
        )}
      </section>
    </main>
  )
}

export default Dashboard