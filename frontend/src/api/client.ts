const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? '/api'

type LoginResponse = {
  access_token: string
  token_type: string
}

export type RegisterRequest = {
  name: string
  last_name: string
  email: string
  password: string
}

export type FinancialSummary = {
  total_income: string
  total_expense: string
  net_balance: string
}

export type AccountType =
  | 'CHECKING'
  | 'SAVINGS'
  | 'CREDIT_CARD'
  | 'CASH'

export type Account = {
  id: number
  name: string
  type: AccountType
  balance: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export type CreateAccountRequest = {
  name: string
  type: AccountType
}

export class UnauthorizedError extends Error {
  constructor() {
    super('Tu sesión venció o ya no es válida.')
    this.name = 'UnauthorizedError'
  }
}

export async function login(
  email: string,
  password: string,
): Promise<LoginResponse> {
  const response = await fetch(`${apiBaseUrl}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      password,
    }),
  })

  if (response.status === 401) {
    throw new Error('El correo o la contraseña no son válidos.')
  }

  if (!response.ok) {
    throw new Error('No fue posible iniciar sesión. Inténtalo de nuevo.')
  }

  return response.json() as Promise<LoginResponse>
}

export async function registerUser(
  userData: RegisterRequest,
): Promise<void> {
  const response = await fetch(`${apiBaseUrl}/users/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  })

  if (response.status === 409) {
    throw new Error('Ya existe una cuenta registrada con este correo.')
  }

  if (!response.ok) {
    throw new Error('No fue posible crear la cuenta. Inténtalo de nuevo.')
  }
}

export async function getFinancialSummary(
  accessToken: string,
): Promise<FinancialSummary> {
  const response = await fetch(`${apiBaseUrl}/reports/summary`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  })

  if (response.status === 401) {
    throw new UnauthorizedError()
  }

  if (!response.ok) {
    throw new Error('No fue posible cargar el resumen financiero.')
  }

  return response.json() as Promise<FinancialSummary>
}

export async function getAccounts(
  accessToken: string,
): Promise<Account[]> {
  const response = await fetch(`${apiBaseUrl}/accounts/`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  })

  if (response.status === 401) {
    throw new UnauthorizedError()
  }

  if (!response.ok) {
    throw new Error('No fue posible cargar tus cuentas.')
  }

  return response.json() as Promise<Account[]>
}

export async function createAccount(
  accessToken: string,
  accountData: CreateAccountRequest,
): Promise<Account> {
  const response = await fetch(`${apiBaseUrl}/accounts/`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(accountData),
  })

  if (response.status === 401) {
    throw new UnauthorizedError()
  }

  if (!response.ok) {
    throw new Error('No fue posible crear la cuenta.')
  }

  return response.json() as Promise<Account>
}

export async function deactivateAccount(
  accessToken: string,
  accountId: number,
): Promise<void> {
  const response = await fetch(`${apiBaseUrl}/accounts/${accountId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  })

  if (response.status === 401) {
    throw new UnauthorizedError()
  }

  if (!response.ok) {
    throw new Error('No fue posible desactivar la cuenta.')
  }
}