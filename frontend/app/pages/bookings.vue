<script setup lang="ts">
import { CalendarDays, CalendarOff } from 'lucide-vue-next'

definePageMeta({ middleware: ['auth'] })

const { fetchMyBookings, cancelBooking } = useBookings()
const bookings = ref<any[]>([])
const loading = ref(true)

// Активная вкладка: предстоящие или прошедшие брони
const tab = ref<'upcoming' | 'past'>('upcoming')

// Бронирование, ожидающее подтверждения отмены
const cancelTarget = ref<any>(null)

const filtered = computed(() => {
  const _n = new Date()
  const today = `${_n.getFullYear()}-${String(_n.getMonth() + 1).padStart(2, '0')}-${String(_n.getDate()).padStart(2, '0')}`
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

// Показать диалог подтверждения перед отменой
function onCancelRequest(id: string) {
  cancelTarget.value = bookings.value.find(b => b.id === id)
}

// Подтвердить отмену (сохраняем id до сброса, чтобы избежать гонки с @update:open)
async function confirmCancel() {
  const id = cancelTarget.value?.id
  cancelTarget.value = null
  if (!id) return
  await cancelBooking(id)
  await load()
}

onMounted(load)
</script>

<template>
  <div class="animate-fade-in">
    <div class="mb-6">
      <h1 class="text-2xl font-bold">Мои брони</h1>
      <p class="text-muted-foreground text-sm mt-1">Управление бронированиями</p>
    </div>

    <!-- Переключение между предстоящими и прошедшими -->
    <div class="flex gap-1 mb-6 bg-muted p-1 rounded-lg w-fit">
      <button
        class="px-4 py-2 text-sm font-medium rounded-md transition-all duration-150"
        :class="tab === 'upcoming'
          ? 'bg-background text-foreground shadow-sm'
          : 'text-muted-foreground hover:text-foreground'"
        @click="tab = 'upcoming'"
      >
        Предстоящие
      </button>
      <button
        class="px-4 py-2 text-sm font-medium rounded-md transition-all duration-150"
        :class="tab === 'past'
          ? 'bg-background text-foreground shadow-sm'
          : 'text-muted-foreground hover:text-foreground'"
        @click="tab = 'past'"
      >
        Прошедшие
      </button>
    </div>

    <!-- Спиннер -->
    <div v-if="loading" class="flex items-center gap-3 text-muted-foreground py-8">
      <div class="h-5 w-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      Загрузка...
    </div>

    <!-- Пустое состояние -->
    <div v-else-if="filtered.length === 0" class="text-center py-16">
      <CalendarOff class="h-10 w-10 text-muted-foreground/30 mx-auto mb-3" />
      <p class="text-muted-foreground font-medium">
        {{ tab === 'upcoming' ? 'Нет предстоящих бронирований' : 'Нет прошедших бронирований' }}
      </p>
      <Button
        v-if="tab === 'upcoming'"
        variant="link"
        class="mt-2 text-primary"
        @click="navigateTo('/rooms')"
      >
        Забронировать переговорку →
      </Button>
    </div>

    <!-- Список броней -->
    <div v-else class="space-y-3">
      <BookingCard
        v-for="b in filtered"
        :key="b.id"
        :booking="b"
        :show-cancel="tab === 'upcoming'"
        @cancel="onCancelRequest"
      />
    </div>

    <!-- Диалог подтверждения отмены -->
    <AlertDialog :open="!!cancelTarget" @update:open="cancelTarget = null">
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Отменить бронирование?</AlertDialogTitle>
          <AlertDialogDescription>
            {{ cancelTarget?.title }} — {{ cancelTarget?.room_name }},
            {{ cancelTarget?.start_time?.slice(0, 5) }}–{{ cancelTarget?.end_time?.slice(0, 5) }}.
            Это действие нельзя отменить.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel @click="cancelTarget = null">Нет, оставить</AlertDialogCancel>
          <Button class="bg-destructive text-destructive-foreground hover:bg-destructive/90" @click="confirmCancel">
            Да, отменить
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  </div>
</template>
