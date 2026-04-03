import { defineStore } from 'pinia'

interface Notification {
  id: string
  type: string
  message: string
  is_read: boolean
  booking_id: string
  created_at: string
}

export const useNotificationsStore = defineStore('notifications', {
  state: () => ({
    items: [] as Notification[],
  }),
  getters: {
    unreadCount: (state) => state.items.filter(n => !n.is_read).length,
  },
  actions: {
    setItems(items: Notification[]) {
      this.items = items
    },
    markAsRead(id: string) {
      const item = this.items.find(n => n.id === id)
      if (item) item.is_read = true
    },
  },
})
