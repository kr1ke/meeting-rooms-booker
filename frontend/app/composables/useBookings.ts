interface Booking {
  id: string
  user_id: string
  room_id: string
  title: string
  date: string
  start_time: string
  end_time: string
  status: string
  created_at: string
  user_name: string | null
  room_name: string | null
}

interface BookingCreate {
  room_id: string
  title: string
  date: string
  start_time: string
  end_time: string
}

export function useBookings() {
  async function fetchMyBookings() {
    return await $fetch<Booking[]>('/api/bookings')
  }

  async function fetchAllBookings() {
    return await $fetch<Booking[]>('/api/bookings/all')
  }

  async function createBooking(data: BookingCreate) {
    return await $fetch<Booking>('/api/bookings', { method: 'POST', body: data })
  }

  async function cancelBooking(id: string) {
    return await $fetch<Booking>(`/api/bookings/${id}/cancel`, { method: 'PATCH' })
  }

  async function approveBooking(id: string) {
    return await $fetch<Booking>(`/api/bookings/${id}/approve`, { method: 'PATCH' })
  }

  async function rejectBooking(id: string) {
    return await $fetch<Booking>(`/api/bookings/${id}/reject`, { method: 'PATCH' })
  }

  return {
    fetchMyBookings, fetchAllBookings,
    createBooking, cancelBooking, approveBooking, rejectBooking,
  }
}
