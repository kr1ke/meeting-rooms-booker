import { defineStore } from 'pinia'

interface User {
  id: string
  email: string
  name: string
  role: 'employee' | 'manager' | 'admin'
  department_id: string | null
  is_active: boolean
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    loading: true,
  }),
  getters: {
    isAuthenticated: (state) => !!state.user,
    isAdmin: (state) => state.user?.role === 'admin',
    isManager: (state) => state.user?.role === 'manager',
  },
  actions: {
    setUser(user: User | null) {
      this.user = user
      this.loading = false
    },
  },
})
