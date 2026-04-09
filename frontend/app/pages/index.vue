<script setup lang="ts">
import { CalendarDays, DoorOpen, ArrowRight, CalendarOff, ChevronLeft, ChevronRight } from 'lucide-vue-next'

definePageMeta({ middleware: ['auth'] })
useHead({ title: 'Дашборд' })

const { store } = useAuth()
const { fetchMyBookings } = useBookings()
const { fetchSchedule } = useRooms()

const bookings = ref<any[]>([])
const schedule = ref<any[]>([])
const scheduleLoading = ref(false)

// Локальная дата (не UTC, чтобы не сдвигать день из-за таймзоны)
const now = new Date()
const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`

// Выбранная дата для таймлайна (переключаемая)
const selectedDate = ref(today)

function formatLocalDate(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function shiftDate(offset: number) {
  const d = new Date(selectedDate.value + 'T12:00:00')
  d.setDate(d.getDate() + offset)
  selectedDate.value = formatLocalDate(d)
}

// Человекопонятный заголовок даты
const dateLabel = computed(() => {
  if (selectedDate.value === today) return 'Сегодня'
  const tomorrow = new Date(now)
  tomorrow.setDate(tomorrow.getDate() + 1)
  if (selectedDate.value === formatLocalDate(tomorrow)) return 'Завтра'
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (selectedDate.value === formatLocalDate(yesterday)) return 'Вчера'
  const d = new Date(selectedDate.value + 'T12:00:00')
  return d.toLocaleDateString('ru', { day: 'numeric', month: 'long', weekday: 'short' })
})

const isToday = computed(() => selectedDate.value === today)

// Загрузка расписания при смене даты
async function loadSchedule() {
  scheduleLoading.value = true
  try {
    schedule.value = await fetchSchedule(selectedDate.value)
  } catch {
    schedule.value = []
  } finally {
    scheduleLoading.value = false
  }
}

watch(selectedDate, () => loadSchedule())

// Константы таймлайна (общие с BookingCalendar)
const TIMELINE_START = 8 * 60
const TIMELINE_END = 20 * 60
const TIMELINE_DURATION = TIMELINE_END - TIMELINE_START

function toMinutes(time: string): number {
  const [h, m] = time.split(':').map(Number)
  return h * 60 + m
}

function timeToPercent(mins: number): number {
  return ((mins - TIMELINE_START) / TIMELINE_DURATION) * 100
}

// Часовые метки
const hourLabels = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

// Индикатор «сейчас»
const nowPercent = computed(() => {
  const now = new Date()
  const mins = now.getHours() * 60 + now.getMinutes()
  if (mins < TIMELINE_START || mins > TIMELINE_END) return null
  return timeToPercent(mins)
})

// Попап деталей бронирования. Контракт такой же, как в BookingDetailPopup:
// открыт ⇔ activeBooking !== null. Закрытие по клику вне и Escape обрабатывает сам попап.
const activeBooking = ref<{
  booking: { title: string; user_name: string; start_time: string; end_time: string }
  roomName: string
  x: number
  y: number
} | null>(null)

// Клик по блоку бронирования на таймлайне комнаты. stopPropagation обязателен —
// иначе document listener внутри BookingDetailPopup закроет попап тем же кликом.
function showBookingDetail(b: any, roomName: string, e: MouseEvent) {
  e.stopPropagation()
  activeBooking.value = {
    booking: {
      title: b.title,
      user_name: b.user_name,
      start_time: b.start_time,
      end_time: b.end_time,
    },
    roomName,
    x: e.clientX,
    y: e.clientY,
  }
}

onMounted(async () => {
  // Параллельная загрузка
  const [allBookings] = await Promise.all([
    fetchMyBookings().catch(() => []),
    loadSchedule(),
  ])

  bookings.value = allBookings.filter((b: any) =>
    b.date >= today && (b.status === 'confirmed' || b.status === 'pending')
  ).slice(0, 5)
})
</script>

<template>
  <div class="animate-fade-in">
    <!-- CTA мобильная — видна только на малых экранах -->
    <Button
      @click="navigateTo('/rooms')"
      class="w-full font-semibold gap-2 mb-6 md:hidden"
    >
      <DoorOpen class="h-4 w-4" />
      Забронировать переговорку
      <ArrowRight class="h-4 w-4" />
    </Button>

    <!-- Приветствие -->
    <div class="mb-6 sm:mb-8">
      <h1 class="text-xl sm:text-2xl font-semibold mb-1">
        {{ store.user?.name }}
      </h1>
      <p class="text-muted-foreground text-sm hidden sm:block">Ваши бронирования и переговорки</p>
    </div>

    <!-- Загруженность переговорок — полноширинный таймлайн -->
    <div class="mb-6 sm:mb-8">
      <div class="flex flex-wrap items-center gap-2 sm:gap-3 mb-4">
        <h2 class="text-base font-semibold">Загруженность</h2>
        <div class="flex items-center gap-1">
          <button
            @click="shiftDate(-1)"
            class="h-7 w-7 rounded-md flex items-center justify-center text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
          >
            <ChevronLeft class="h-4 w-4" />
          </button>
          <button
            @click="selectedDate = today"
            class="px-2.5 py-1 rounded-md text-sm font-medium transition-colors min-w-[5.5rem] text-center"
            :class="isToday
              ? 'bg-primary/10 text-primary'
              : 'text-foreground hover:bg-muted'"
          >
            {{ dateLabel }}
          </button>
          <button
            @click="shiftDate(1)"
            class="h-7 w-7 rounded-md flex items-center justify-center text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
          >
            <ChevronRight class="h-4 w-4" />
          </button>
        </div>
        <div v-if="scheduleLoading" class="h-4 w-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>

      <div v-if="schedule.length === 0 && !scheduleLoading" class="text-sm text-muted-foreground py-4">
        Нет комнат для отображения
      </div>

      <div class="border border-border/60 rounded-lg overflow-x-auto">
        <div class="min-w-[600px]">
        <!-- Шкала часов -->
        <div class="flex border-b border-border/40 bg-muted/20">
          <div class="w-20 sm:w-28 shrink-0" />
          <div class="flex-1 relative h-7">
            <span
              v-for="h in hourLabels"
              :key="h"
              class="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 text-[11px] text-muted-foreground/60 font-medium tabular-nums"
              :style="{ left: timeToPercent(h * 60) + '%' }"
            >
              {{ String(h).padStart(2, '0') }}
            </span>
          </div>
        </div>

        <!-- Строки комнат -->
        <div
          v-for="(room, idx) in schedule"
          :key="room.room_id"
          class="flex items-center group transition-colors hover:bg-muted/20"
          :class="idx < schedule.length - 1 ? 'border-b border-border/30' : ''"
        >
          <!-- Название комнаты -->
          <NuxtLink
            :to="`/rooms/${room.room_id}`"
            class="w-20 sm:w-28 shrink-0 px-2 sm:px-3 py-2.5 text-xs sm:text-sm font-medium text-foreground/80 hover:text-primary transition-colors truncate"
          >
            {{ room.room_name }}
          </NuxtLink>

          <!-- Таймлайн комнаты -->
          <div class="flex-1 relative h-10">
            <!-- Вертикальные линии часов -->
            <div
              v-for="h in hourLabels.slice(1, -1)"
              :key="'g-' + h"
              class="absolute top-0 bottom-0 w-px bg-border/20"
              :style="{ left: timeToPercent(h * 60) + '%' }"
            />

            <!-- Блоки бронирований (кликабельные) -->
            <div
              v-for="(b, bi) in room.bookings"
              :key="bi"
              class="absolute top-1.5 bottom-1.5 rounded bg-primary/15 border border-primary/25 flex items-center overflow-hidden cursor-pointer hover:bg-primary/25 hover:border-primary/40 transition-colors z-10"
              :style="{
                left: timeToPercent(toMinutes(b.start_time)) + '%',
                width: ((toMinutes(b.end_time) - toMinutes(b.start_time)) / TIMELINE_DURATION) * 100 + '%'
              }"
              @click="showBookingDetail(b, room.room_name, $event)"
            >
              <div class="w-0.5 self-stretch bg-primary/50 shrink-0" />
              <span class="text-[10px] text-primary/70 font-medium truncate px-1">
                {{ b.title }}
              </span>
            </div>

            <!-- Индикатор «сейчас» (только для сегодня) -->
            <div
              v-if="isToday && nowPercent !== null"
              class="absolute top-0 bottom-0 w-0.5 bg-destructive/50 pointer-events-none"
              :style="{ left: nowPercent + '%' }"
            />
          </div>
        </div>
        </div>
      </div>
    </div>

    <!-- Попап деталей бронирования — общий компонент -->
    <BookingDetailPopup
      :booking="activeBooking?.booking ?? null"
      :room-name="activeBooking?.roomName"
      :x="activeBooking?.x ?? 0"
      :y="activeBooking?.y ?? 0"
      @close="activeBooking = null"
    />

    <div class="grid gap-6 md:grid-cols-2">
      <!-- Ближайшие брони -->
      <Card class="shadow-none border">
        <CardHeader class="pb-3">
          <div class="flex items-center gap-3">
            <div class="h-9 w-9 rounded-lg bg-primary/10 flex items-center justify-center">
              <CalendarDays class="h-4.5 w-4.5 text-primary" />
            </div>
            <CardTitle class="text-base">Ближайшие брони</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div v-if="bookings.length === 0" class="text-center py-6">
            <CalendarOff class="h-8 w-8 text-muted-foreground/25 mx-auto mb-2" />
            <p class="text-sm text-muted-foreground">Нет предстоящих встреч</p>
            <Button
              variant="link"
              size="sm"
              class="mt-1 text-primary h-auto p-0"
              @click="navigateTo('/rooms')"
            >
              Забронировать →
            </Button>
          </div>
          <div v-else class="space-y-3">
            <BookingCard v-for="b in bookings" :key="b.id" :booking="b" />
          </div>
        </CardContent>
      </Card>

      <!-- Быстрое бронирование -->
      <Card class="shadow-none border">
        <CardHeader class="pb-3">
          <div class="flex items-center gap-3">
            <div class="h-9 w-9 rounded-lg bg-emerald-500/10 flex items-center justify-center">
              <DoorOpen class="h-4.5 w-4.5 text-emerald-600" />
            </div>
            <CardTitle class="text-base">Быстрое бронирование</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <p class="text-muted-foreground text-sm mb-4">
            Выберите подходящую комнату и забронируйте время
          </p>
          <Button @click="navigateTo('/rooms')" class="w-full font-semibold gap-2">
            Смотреть переговорки
            <ArrowRight class="h-4 w-4" />
          </Button>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
