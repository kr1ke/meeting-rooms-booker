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
  booking_user_name: string | null
}

interface BookingBlock {
  start_time: string
  end_time: string
  title: string
  user_name: string
}

interface RoomDaySchedule {
  slots: AvailabilitySlot[]
  bookings: BookingBlock[]
}

export function useRooms() {
  async function fetchRooms(params?: { floor?: number; min_capacity?: number; equipment?: string }) {
    return await $fetch<Room[]>('/api/rooms', { params })
  }

  async function fetchRoom(id: string) {
    return await $fetch<Room>(`/api/rooms/${id}`)
  }

  async function fetchAvailability(roomId: string, date: string) {
    return await $fetch<RoomDaySchedule>(`/api/rooms/${roomId}/availability`, {
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

  async function fetchSchedule(date: string) {
    return await $fetch<{
      room_id: string
      room_name: string
      floor: number
      bookings: BookingBlock[]
    }[]>('/api/rooms/schedule', { params: { date } })
  }

  return { fetchRooms, fetchRoom, fetchAvailability, fetchSchedule, createRoom, updateRoom, deleteRoom }
}
