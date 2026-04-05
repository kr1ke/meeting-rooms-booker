<script setup lang="ts">
import { CalendarOff } from 'lucide-vue-next'

// Страница всех бронирований для администратора
definePageMeta({ middleware: ['auth', 'role'] })

const { fetchAllBookings, cancelBooking, approveBooking, rejectBooking } = useBookings()
const bookings = ref<any[]>([])
const loading = ref(true)

// Целевое бронирование для confirm-диалога
const actionTarget = ref<{ booking: any; action: 'cancel' | 'reject' } | null>(null)

async function load() {
  loading.value = true
  bookings.value = await fetchAllBookings()
  loading.value = false
}

function onCancelRequest(id: string) {
  actionTarget.value = { booking: bookings.value.find(b => b.id === id), action: 'cancel' }
}

function onRejectRequest(id: string) {
  actionTarget.value = { booking: bookings.value.find(b => b.id === id), action: 'reject' }
}

async function confirmAction() {
  const target = actionTarget.value
  actionTarget.value = null
  if (!target) return
  const { booking, action } = target
  if (action === 'cancel') await cancelBooking(booking.id)
  else await rejectBooking(booking.id)
  await load()
}

async function onApprove(id: string) {
  await approveBooking(id)
  await load()
}

onMounted(load)
</script>

<template>
  <div class="animate-fade-in">
    <div class="mb-6">
      <h1 class="text-2xl font-bold">Все бронирования</h1>
      <p class="text-muted-foreground text-sm mt-1">Управление бронированиями сотрудников</p>
    </div>

    <!-- Спиннер -->
    <div v-if="loading" class="flex items-center gap-3 text-muted-foreground py-8">
      <div class="h-5 w-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      Загрузка...
    </div>

    <!-- Пустое состояние -->
    <div v-else-if="bookings.length === 0" class="text-center py-16">
      <CalendarOff class="h-10 w-10 text-muted-foreground/30 mx-auto mb-3" />
      <p class="text-muted-foreground font-medium">Нет бронирований</p>
    </div>

    <div v-else class="space-y-3">
      <div v-for="b in bookings" :key="b.id">
        <BookingCard
          :booking="b"
          show-cancel
          show-actions
          @cancel="onCancelRequest"
          @approve="onApprove"
          @reject="onRejectRequest"
        />
        <p class="text-xs text-muted-foreground ml-4 mt-1">Автор: {{ b.user_name }}</p>
      </div>
    </div>

    <!-- Диалог подтверждения отмены/отклонения -->
    <AlertDialog :open="!!actionTarget" @update:open="actionTarget = null">
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>
            {{ actionTarget?.action === 'cancel' ? 'Отменить бронирование?' : 'Отклонить бронирование?' }}
          </AlertDialogTitle>
          <AlertDialogDescription>
            {{ actionTarget?.booking?.title }} — {{ actionTarget?.booking?.room_name }},
            {{ actionTarget?.booking?.start_time?.slice(0, 5) }}–{{ actionTarget?.booking?.end_time?.slice(0, 5) }}.
            Это действие нельзя отменить.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel @click="actionTarget = null">Нет</AlertDialogCancel>
          <Button class="bg-destructive text-destructive-foreground hover:bg-destructive/90" @click="confirmAction">
            {{ actionTarget?.action === 'cancel' ? 'Да, отменить' : 'Да, отклонить' }}
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  </div>
</template>
