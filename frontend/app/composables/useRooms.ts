interface Room {
  id: string
  name: string
  floor: number
  capacity: number
  equipment: Record<string, boolean>
  requires_approval: boolean
  is_active: boolean
}

interface AvailabilitySlot {
  start_time: string
  end_time: string
  is_available: boolean
  booking_title: string | null
}

export function useRooms() {
  async function fetchRooms(params?: { floor?: number; min_capacity?: number; equipment?: string }) {
    return await $fetch<Room[]>('/api/rooms', { params })
  }

  async function fetchRoom(id: string) {
    return await $fetch<Room>(`/api/rooms/${id}`)
  }

  async function fetchAvailability(roomId: string, date: string) {
    return await $fetch<AvailabilitySlot[]>(`/api/rooms/${roomId}/availability`, {
      params: { date },
    })
  }

  async function createRoom(data: Partial<Room>) {
    return await $fetch<Room>('/api/rooms', { method: 'POST', body: data })
  }

  async function updateRoom(id: string, data: Partial<Room>) {
    return await $fetch<Room>(`/api/rooms/${id}`, { method: 'PUT', body: data })
  }

  async function deleteRoom(id: string) {
    return await $fetch(`/api/rooms/${id}`, { method: 'DELETE' })
  }

  return { fetchRooms, fetchRoom, fetchAvailability, createRoom, updateRoom, deleteRoom }
}
