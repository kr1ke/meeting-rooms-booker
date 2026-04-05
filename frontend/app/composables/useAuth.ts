import { useAuthStore } from '~/stores/auth'

export function useAuth() {
  const store = useAuthStore()

  async function login(email: string, password: string) {
    const data = await $fetch<any>('/api/auth/login', {
      method: 'POST',
      body: { email, password },
    })
    store.setUser(data)
    return data
  }

  async function register(email: string, password: string, name: string, departmentId?: string) {
    const data = await $fetch<any>('/api/auth/register', {
      method: 'POST',
      body: { email, password, name, department_id: departmentId },
    })
    store.setUser(data)
    return data
  }

  async function fetchMe() {
    try {
      const data = await $fetch<any>('/api/auth/me')
      store.setUser(data)
    } catch {
      store.setUser(null)
    }
  }

  async function logout() {
    await $fetch('/api/auth/logout', { method: 'POST' })
    store.setUser(null)
    navigateTo('/login')
  }

  return { login, register, fetchMe, logout, store }
}
