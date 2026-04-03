<script setup lang="ts">
definePageMeta({ middleware: ['auth'] })

const { fetchMyBookings, cancelBooking } = useBookings()
const bookings = ref<any[]>([])
const loading = ref(true)

// Активная вкладка: предстоящие или прошедшие брони
const tab = ref<'upcoming' | 'past'>('upcoming')

const filtered = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  if (tab.value === 'upcoming') {
    return bookings.value.filter(b => b.date >= today && b.status !== 'cancelled' && b.status !== 'rejected')
  }
  return bookings.value.filter(b => b.date < today || b.status === 'cancelled' || b.status === 'rejected')
})

async function load() {
  loading.value = true
  bookings.value = await fetchMyBookings()
  loading.value = false
}

async function onCancel(id: string) {
  await cancelBooking(id)
  await load()
}

onMounted(load)
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Мои брони</h1>

    <!-- Переключение между предстоящими и прошедшими бронями -->
    <div class="flex gap-2 mb-6">
      <Button :variant="tab === 'upcoming' ? 'default' : 'outline'" size="sm" @click="tab = 'upcoming'">
        Предстоящие
      </Button>
      <Button :variant="tab === 'past' ? 'default' : 'outline'" size="sm" @click="tab = 'past'">
        Прошедшие
      </Button>
    </div>

    <div v-if="loading" class="text-muted-foreground">Загрузка...</div>
    <div v-else-if="filtered.length === 0" class="text-muted-foreground">Нет бронирований</div>
    <div v-else class="space-y-3">
      <BookingCard
        v-for="b in filtered"
        :key="b.id"
        :booking="b"
        :show-cancel="tab === 'upcoming'"
        @cancel="onCancel"
      />
    </div>
  </div>
</template>
