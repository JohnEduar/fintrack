const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? '/api'

type ApiHealth = {
  message: string
  database_connection: number
}

export async function getApiHealth(): Promise<ApiHealth> {
  const response = await fetch(`${apiBaseUrl}/`)

  if (!response.ok) {
    throw new Error('No fue posible conectar con la API.')
  }

  return response.json() as Promise<ApiHealth>
}
