<script setup lang="ts">
const props = defineProps<{ roomId: string; roomName: string }>()

const { createBooking } = useBookings()
const { fetchAvailability } = useRooms()

// Поля формы бронирования
const title = ref('')
const date = ref(new Date().toISOString().split('T')[0])
const startTime = ref('')
const endTime = ref('')
const slots = ref<any[]>([])
const error = ref('')
const loading = ref(false)
const success = ref(false)

async function loadSlots() {
  if (!date.value) return
  slots.value = await fetchAvailability(props.roomId, date.value)
}

// Загружаем доступные слоты при изменении даты
watch(date, loadSlots, { immediate: true })

function onSlotSelect(start: string, end: string) {
  startTime.value = start
  endTime.value = end
}

async function onSubmit() {
  error.value = ''
  loading.value = true
  try {
    await createBooking({
      room_id: props.roomId,
      title: title.value,
      date: date.value,
      start_time: startTime.value,
      end_time: endTime.value,
    })
    success.value = true
    title.value = ''
    startTime.value = ''
    endTime.value = ''
    await loadSlots()
  } catch (e: any) {
    error.value = e.data?.detail || 'Ошибка бронирования'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>Забронировать {{ roomName }}</CardTitle>
    </CardHeader>
    <CardContent>
      <!-- Сообщение об успешном бронировании -->
      <div v-if="success" class="p-4 bg-green-50 text-green-800 rounded-md mb-4">
        Бронирование создано!
        <Button variant="link" size="sm" @click="success = false">Создать ещё</Button>
      </div>

      <form v-else @submit.prevent="onSubmit" class="space-y-4">
        <div class="space-y-2">
          <Label>Название встречи</Label>
          <Input v-model="title" placeholder="Стендап команды" required />
        </div>

        <div class="space-y-2">
          <Label>Дата</Label>
          <Input v-model="date" type="date" required />
        </div>

        <div class="space-y-2">
          <Label>Выберите время (клик для начала, повторный клик для конца)</Label>
          <BookingCalendar :slots="slots" @selectSlot="onSlotSelect" />
        </div>

        <div v-if="startTime && endTime" class="text-sm text-muted-foreground">
          Выбрано: {{ startTime.slice(0, 5) }} – {{ endTime.slice(0, 5) }}
        </div>

        <p v-if="error" class="text-sm text-destructive">{{ error }}</p>

        <Button type="submit" class="w-full" :disabled="loading || !startTime || !endTime">
          {{ loading ? 'Бронирование...' : 'Забронировать' }}
        </Button>
      </form>
    </CardContent>
  </Card>
</template>
