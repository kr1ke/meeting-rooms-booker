<script setup lang="ts">
definePageMeta({ middleware: ['auth'] })

const { store } = useAuth()
const { fetchMyBookings } = useBookings()

const bookings = ref<any[]>([])

onMounted(async () => {
  const all = await fetchMyBookings()
  // Показать только предстоящие подтверждённые или ожидающие брони
  const today = new Date().toISOString().split('T')[0]
  bookings.value = all.filter(b =>
    b.date >= today && (b.status === 'confirmed' || b.status === 'pending')
  ).slice(0, 5)
})
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Привет, {{ store.user?.name }}!</h1>

    <div class="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Ближайшие брони</CardTitle>
        </CardHeader>
        <CardContent>
          <div v-if="bookings.length === 0" class="text-muted-foreground text-sm">
            У вас нет предстоящих бронирований
          </div>
          <div class="space-y-3">
            <BookingCard v-for="b in bookings" :key="b.id" :booking="b" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Быстрое бронирование</CardTitle>
        </CardHeader>
        <CardContent>
          <p class="text-muted-foreground text-sm mb-4">Найдите свободную переговорку</p>
          <Button @click="navigateTo('/rooms')" class="w-full">Смотреть переговорки</Button>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
