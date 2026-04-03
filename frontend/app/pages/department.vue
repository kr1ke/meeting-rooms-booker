<script setup lang="ts">
// Страница доступна только менеджерам и администраторам
definePageMeta({ middleware: ['auth', 'role'] })

const { fetchDepartmentBookings } = useBookings()
const bookings = ref<any[]>([])
const loading = ref(true)

// Загружаем брони отдела при монтировании компонента
onMounted(async () => {
  bookings.value = await fetchDepartmentBookings()
  loading.value = false
})
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Брони отдела</h1>

    <div v-if="loading" class="text-muted-foreground">Загрузка...</div>
    <div v-else-if="bookings.length === 0" class="text-muted-foreground">Нет бронирований</div>
    <div v-else class="space-y-3">
      <BookingCard v-for="b in bookings" :key="b.id" :booking="b" />
    </div>
  </div>
</template>
