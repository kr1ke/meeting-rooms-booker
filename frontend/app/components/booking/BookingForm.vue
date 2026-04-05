<script setup lang="ts">
import { CheckCircle, Clock } from 'lucide-vue-next'

const props = defineProps<{ roomId: string; roomName: string }>()

const { createBooking } = useBookings()
const { fetchAvailability } = useRooms()

// Поля формы
const title = ref('')
const _now = new Date()
const date = ref(`${_now.getFullYear()}-${String(_now.getMonth() + 1).padStart(2, '0')}-${String(_now.getDate()).padStart(2, '0')}`)
const startTime = ref('')
const endTime = ref('')
const error = ref('')
const loading = ref(false)
const success = ref(false)

// Данные расписания (слоты + бронирования)
const slots = ref<any[]>([])
const bookings = ref<any[]>([])

// Пресеты длительности
const presets = [
  { label: '30 мин', minutes: 30 },
  { label: '1 час', minutes: 60 },
  { label: '1.5 ч', minutes: 90 },
  { label: '2 часа', minutes: 120 },
]

// Загрузка расписания комнаты на выбранную дату
async function loadSchedule() {
  if (!date.value) return
  try {
    const data = await fetchAvailability(props.roomId, date.value)
    slots.value = data.slots
    bookings.value = data.bookings
  } catch {
    slots.value = []
    bookings.value = []
  }
}

watch(date, () => {
  startTime.value = ''
  endTime.value = ''
  loadSchedule()
}, { immediate: true })

// Применение пресета длительности
function applyPreset(minutes: number) {
  if (!startTime.value) return
  const [h, m] = startTime.value.split(':').map(Number)
  const startMins = h * 60 + m
  const endMins = Math.min(startMins + minutes, 20 * 60) // не позже 20:00
  const endH = Math.floor(endMins / 60)
  const endM = endMins % 60
  endTime.value = `${String(endH).padStart(2, '0')}:${String(endM).padStart(2, '0')}`
}

// Вычисленная длительность для отображения
const duration = computed(() => {
  if (!startTime.value || !endTime.value) return null
  const [sh, sm] = startTime.value.split(':').map(Number)
  const [eh, em] = endTime.value.split(':').map(Number)
  const mins = (eh * 60 + em) - (sh * 60 + sm)
  if (mins <= 0) return null
  const hours = Math.floor(mins / 60)
  const remMins = mins % 60
  if (hours === 0) return `${remMins} мин`
  if (remMins === 0) return `${hours} ч`
  return `${hours} ч ${remMins} мин`
})

// Можно ли отправить форму
const canSubmit = computed(() =>
  title.value.trim() && startTime.value && endTime.value && duration.value && !loading.value
)

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
    await loadSchedule()
  } catch (e: any) {
    error.value = e.data?.detail || 'Ошибка бронирования'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Card class="shadow-sm">
    <CardHeader>
      <CardTitle class="text-xl">Забронировать {{ roomName }}</CardTitle>
    </CardHeader>
    <CardContent>
      <!-- Сообщение об успешном бронировании -->
      <div v-if="success" class="flex items-center gap-3 p-4 bg-emerald-50 border border-emerald-200 rounded-lg mb-4">
        <CheckCircle class="h-5 w-5 text-emerald-600 shrink-0" />
        <div>
          <p class="text-sm font-medium text-emerald-800">Бронирование создано!</p>
          <Button variant="link" size="sm" class="h-auto p-0 text-emerald-700" @click="success = false">
            Создать ещё
          </Button>
        </div>
      </div>

      <form v-else @submit.prevent="onSubmit" class="space-y-5">
        <!-- Название встречи -->
        <div class="space-y-2">
          <Label class="font-medium">Название встречи</Label>
          <Input v-model="title" placeholder="Стендап команды" required />
        </div>

        <!-- Дата -->
        <div class="space-y-2">
          <Label class="font-medium">Дата</Label>
          <Input v-model="date" type="date" required />
        </div>

        <!-- Таймлайн загруженности -->
        <div class="space-y-2">
          <Label class="font-medium">Расписание</Label>
          <p class="text-xs text-muted-foreground">Кликните по свободной области для выбора времени</p>
          <BookingCalendar
            :slots="slots"
            :bookings="bookings"
            :start-time="startTime"
            :end-time="endTime"
            @update:start-time="startTime = $event"
            @update:end-time="endTime = $event"
          />
        </div>

        <!-- Ручной ввод времени + пресеты -->
        <div class="space-y-3">
          <Label class="font-medium flex items-center gap-1.5">
            <Clock class="h-3.5 w-3.5 text-muted-foreground" />
            Время
          </Label>

          <!-- Ввод начала и конца -->
          <div class="flex flex-wrap items-center gap-2">
            <Input
              v-model="startTime"
              type="time"
              class="w-[7rem] sm:w-[7.5rem] tabular-nums text-center"
              placeholder="09:00"
              min="08:00"
              max="20:00"
            />
            <span class="text-muted-foreground text-sm">—</span>
            <Input
              v-model="endTime"
              type="time"
              class="w-[7rem] sm:w-[7.5rem] tabular-nums text-center"
              placeholder="10:00"
              min="08:00"
              max="20:00"
            />
            <!-- Длительность -->
            <span v-if="duration" class="text-xs text-muted-foreground whitespace-nowrap ml-1">
              {{ duration }}
            </span>
          </div>

          <!-- Пресеты -->
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="p in presets"
              :key="p.minutes"
              type="button"
              class="px-2.5 py-1 text-xs font-medium rounded-md border transition-colors"
              :class="startTime
                ? 'border-primary/30 text-primary hover:bg-primary/5 cursor-pointer'
                : 'border-border text-muted-foreground/50 cursor-not-allowed'"
              :disabled="!startTime"
              @click="applyPreset(p.minutes)"
            >
              {{ p.label }}
            </button>
          </div>
        </div>

        <!-- Выбранный диапазон -->
        <div
          v-if="startTime && endTime && duration"
          class="flex items-center gap-2 text-sm bg-primary/5 text-primary px-3 py-2 rounded-lg font-medium"
        >
          <Clock class="h-4 w-4 shrink-0" />
          Выбрано: {{ startTime.slice(0, 5) }} – {{ endTime.slice(0, 5) }}
          <span class="text-primary/60 text-xs">({{ duration }})</span>
        </div>

        <!-- Ошибка -->
        <div v-if="error" class="text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-lg px-3 py-2">
          {{ error }}
        </div>

        <!-- Кнопка отправки -->
        <Button type="submit" class="w-full font-semibold" :disabled="!canSubmit">
          <span v-if="loading" class="flex items-center gap-2">
            <span class="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            Бронирование...
          </span>
          <span v-else>Забронировать</span>
        </Button>
      </form>
    </CardContent>
  </Card>
</template>
