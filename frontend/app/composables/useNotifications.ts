export function useNotifications() {
  const store = useNotificationsStore()

  async function fetchNotifications() {
    const data = await $fetch<any[]>('/api/notifications')
    store.setItems(data)
    return data
  }

  async function markAsRead(id: string) {
    await $fetch(`/api/notifications/${id}/read`, { method: 'PATCH' })
    store.markAsRead(id)
  }

  return { fetchNotifications, markAsRead, store }
}
