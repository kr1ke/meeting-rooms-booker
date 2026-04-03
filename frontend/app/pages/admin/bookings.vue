<script setup lang="ts">
// Страница всех бронирований для администратора
definePageMeta({ middleware: ['auth', 'role'] })

const { fetchAllBookings, cancelBooking, approveBooking, rejectBooking } = useBookings()
const bookings = ref<any[]>([])
const loading = ref(true)

async function load() {
  loading.value = true
  bookings.value = await fetchAllBookings()
  loading.value = false
}

async function onCancel(id: string) {
  await cancelBooking(id)
  await load()
}

async function onApprove(id: string) {
  await approveBooking(id)
  await load()
}

async function onReject(id: string) {
  await rejectBooking(id)
  await load()
}

onMounted(load)
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Все бронирования</h1>

    <div v-if="loading" class="text-muted-foreground">Загрузка...</div>
    <div v-else class="space-y-3">
      <div v-for="b in bookings" :key="b.id">
        <!-- Карточка брони с действиями подтверждения/отклонения -->
        <BookingCard
          :booking="b"
          show-cancel
          show-actions
          @cancel="onCancel"
          @approve="onApprove"
          @reject="onReject"
        />
        <p class="text-xs text-muted-foreground ml-4 mt-1">Автор: {{ b.user_name }}</p>
      </div>
    </div>
  </div>
</template>
