const accessTokenStorageKey = 'fintrack_access_token'

export function saveAccessToken(accessToken: string): void {
  localStorage.setItem(accessTokenStorageKey, accessToken)
}

export function getAccessToken(): string | null {
  return localStorage.getItem(accessTokenStorageKey)
}

export function removeAccessToken(): void {
  localStorage.removeItem(accessTokenStorageKey)
}