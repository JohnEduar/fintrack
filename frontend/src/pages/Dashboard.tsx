import { useEffect, useState, type FormEvent } from 'react'
import {
  createAccount,
  deactivateAccount,
  getAccounts,
  getFinancialSummary,
  type Account,
  type AccountType,
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
  const [accounts, setAccounts] = useState<Account[]>([])
  const [accountName, setAccountName] = useState('')
  const [accountType, setAccountType] = useState<AccountType>('CHECKING')
  const [accountMessage, setAccountMessage] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isCreatingAccount, setIsCreatingAccount] = useState(false)
  const [deactivatingAccountId, setDeactivatingAccountId] = useState<
    number | null
  >(null)

  useEffect(() => {
    async function loadDashboardData() {
      const accessToken = getAccessToken()

      if (!accessToken) {
        onLogout('No se encontró una sesión activa.')
        return
      }

      try {
        const [financialSummary, userAccounts] = await Promise.all([
          getFinancialSummary(accessToken),
          getAccounts(accessToken),
        ])

        setSummary(financialSummary)
        setAccounts(userAccounts)
      } catch (requestError) {
        if (requestError instanceof UnauthorizedError) {
          onLogout(requestError.message)
          return
        }

        const errorMessage =
          requestError instanceof Error
            ? requestError.message
            : 'Ocurrió un error inesperado al cargar el dashboard.'

        setError(errorMessage)
      } finally {
        setIsLoading(false)
      }
    }

    void loadDashboardData()
  }, [onLogout])

  async function handleCreateAccount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!accountName.trim()) {
      setAccountMessage('Escribe un nombre para la cuenta.')
      return
    }

    const accessToken = getAccessToken()

    if (!accessToken) {
      onLogout('No se encontró una sesión activa.')
      return
    }

    setIsCreatingAccount(true)
    setAccountMessage('')

    try {
      const newAccount = await createAccount(accessToken, {
        name: accountName.trim(),
        type: accountType,
      })

      setAccounts((currentAccounts) => [...currentAccounts, newAccount])
      setAccountName('')
      setAccountType('CHECKING')
      setAccountMessage('Cuenta creada correctamente.')
    } catch (requestError) {
      if (requestError instanceof UnauthorizedError) {
        onLogout(requestError.message)
        return
      }

      const errorMessage =
        requestError instanceof Error
          ? requestError.message
          : 'Ocurrió un error inesperado al crear la cuenta.'

      setAccountMessage(errorMessage)
    } finally {
      setIsCreatingAccount(false)
    }
  }

  async function handleDeactivateAccount(account: Account) {
    const confirmation = window.confirm(
      `¿Quieres desactivar la cuenta "${account.name}"?`,
    )

    if (!confirmation) {
      return
    }

    const accessToken = getAccessToken()

    if (!accessToken) {
      onLogout('No se encontró una sesión activa.')
      return
    }

    setDeactivatingAccountId(account.id)
    setAccountMessage('')

    try {
      await deactivateAccount(accessToken, account.id)

      setAccounts((currentAccounts) =>
        currentAccounts.filter((currentAccount) => currentAccount.id !== account.id),
      )

      setAccountMessage('Cuenta desactivada correctamente.')
    } catch (requestError) {
      if (requestError instanceof UnauthorizedError) {
        onLogout(requestError.message)
        return
      }

      const errorMessage =
        requestError instanceof Error
          ? requestError.message
          : 'Ocurrió un error inesperado al desactivar la cuenta.'

      setAccountMessage(errorMessage)
    } finally {
      setDeactivatingAccountId(null)
    }
  }

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

        {isLoading && <p>Cargando información…</p>}

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

      {summary && (
        <>
          <section className="dashboard-content" aria-labelledby="accounts-title">
            <p className="eyebrow">Cuentas</p>
            <h2 id="accounts-title">Tus cuentas activas</h2>

            {accounts.length === 0 ? (
              <p>Aún no tienes cuentas creadas.</p>
            ) : (
              <ul>
                {accounts.map((account) => (
                  <li key={account.id}>
                    <strong>{account.name}</strong> — {account.type} —{' '}
                    {formatAmount(account.balance)}{' '}
                    <button
                      type="button"
                      className="logout-button"
                      onClick={() => void handleDeactivateAccount(account)}
                      disabled={deactivatingAccountId === account.id}
                    >
                      {deactivatingAccountId === account.id
                        ? 'Desactivando…'
                        : 'Desactivar'}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="dashboard-content" aria-labelledby="new-account-title">
            <p className="eyebrow">Nueva cuenta</p>
            <h2 id="new-account-title">Agrega una cuenta</h2>

            <form className="login-form" onSubmit={handleCreateAccount}>
              <label htmlFor="account-name">
                Nombre
                <input
                  id="account-name"
                  name="account-name"
                  type="text"
                  value={accountName}
                  onChange={(event) => setAccountName(event.target.value)}
                  placeholder="Ejemplo: Cuenta principal"
                  required
                  disabled={isCreatingAccount}
                />
              </label>

              <label htmlFor="account-type">
                Tipo
                <select
                  id="account-type"
                  name="account-type"
                  value={accountType}
                  onChange={(event) =>
                    setAccountType(event.target.value as AccountType)
                  }
                  disabled={isCreatingAccount}
                >
                  <option value="CHECKING">Cuenta corriente</option>
                  <option value="SAVINGS">Cuenta de ahorros</option>
                  <option value="CREDIT_CARD">Tarjeta de crédito</option>
                  <option value="CASH">Efectivo</option>
                </select>
              </label>

              {accountMessage && (
                <p className="form-message" role="status">
                  {accountMessage}
                </p>
              )}

              <button type="submit" disabled={isCreatingAccount}>
                {isCreatingAccount ? 'Creando cuenta…' : 'Crear cuenta'}
              </button>
            </form>
          </section>
        </>
      )}
    </main>
  )
}

export default Dashboard