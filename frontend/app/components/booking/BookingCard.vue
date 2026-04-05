<script setup lang="ts">
import { Clock, MapPin, CalendarDays } from 'lucide-vue-next'

const props = defineProps<{
  booking: {
    id: string
    title: string
    date: string
    start_time: string
    end_time: string
    status: string
    room_name: string | null
  }
  showCancel?: boolean
  showActions?: boolean
}>()

const emit = defineEmits<{
  cancel: [id: string]
  approve: [id: string]
  reject: [id: string]
}>()

// Цвета левой акцентной полоски по статусу
const statusBorderColors: Record<string, string> = {
  confirmed: 'border-l-emerald-500',
  pending: 'border-l-amber-500',
  rejected: 'border-l-red-500',
  cancelled: 'border-l-gray-400',
}

// Стили бейджа статуса: фон, текст и рамка
const statusBadgeStyles: Record<string, string> = {
  confirmed: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
  pending: 'bg-amber-50 text-amber-700 border border-amber-200',
  rejected: 'bg-red-50 text-red-700 border border-red-200',
  cancelled: 'bg-gray-50 text-gray-500 border border-gray-200',
}

// Русские метки статусов
const statusLabels: Record<string, string> = {
  confirmed: 'Подтверждена',
  pending: 'Ожидает',
  rejected: 'Отклонена',
  cancelled: 'Отменена',
}

// Форматирование даты в человекочитаемый вид на русском
function formatDate(dateStr: string): string {
  const _n = new Date()
  const today = `${_n.getFullYear()}-${String(_n.getMonth() + 1).padStart(2, '0')}-${String(_n.getDate()).padStart(2, '0')}`
  const _t = new Date(_n.getTime() + 86400000)
  const tomorrow = `${_t.getFullYear()}-${String(_t.getMonth() + 1).padStart(2, '0')}-${String(_t.getDate()).padStart(2, '0')}`
  if (dateStr === today) return 'Сегодня'
  if (dateStr === tomorrow) return 'Завтра'
  const d = new Date(dateStr)
  const months = ['янв', 'фев', 'мар', 'апр', 'мая', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']
  return `${d.getDate()} ${months[d.getMonth()]}`
}
</script>

<template>
  <Card
    class="shadow-sm border-l-4 transition-all duration-200 hover:shadow-md hover:-translate-y-0.5"
    :class="statusBorderColors[booking.status]"
  >
    <CardContent class="p-5">
      <div class="flex items-start justify-between gap-3">
        <!-- Информация о бронировании -->
        <div class="min-w-0 flex-1">
          <h3 class="font-semibold text-foreground truncate">
            {{ booking.title }}
          </h3>

          <!-- Место и время — разделены на две строки для лучшей читаемости -->
          <div class="mt-2 space-y-1">
            <div class="flex items-center gap-1.5 text-sm text-muted-foreground">
              <MapPin class="h-3.5 w-3.5 shrink-0 text-primary/60" />
              <span>{{ booking.room_name }}</span>
            </div>
            <div class="flex flex-wrap items-center gap-x-1.5 gap-y-0.5 text-sm text-muted-foreground">
              <CalendarDays class="h-3.5 w-3.5 shrink-0 text-primary/60" />
              <span>{{ formatDate(booking.date) }}</span>
              <span class="text-muted-foreground/40">|</span>
              <Clock class="h-3.5 w-3.5 shrink-0 text-primary/60" />
              <span class="font-medium text-foreground/80 whitespace-nowrap">
                {{ booking.start_time.slice(0, 5) }}&ndash;{{ booking.end_time.slice(0, 5) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Бейдж статуса -->
        <span
          class="inline-flex items-center shrink-0 text-xs font-medium px-2.5 py-1 rounded-full"
          :class="statusBadgeStyles[booking.status]"
        >
          {{ statusLabels[booking.status] }}
        </span>
      </div>

      <!-- Кнопки действий: отмена, подтверждение, отклонение -->
      <div v-if="showCancel || showActions" class="mt-4 flex gap-2 pt-3 border-t border-border/50">
        <Button
          v-if="showCancel && (booking.status === 'confirmed' || booking.status === 'pending')"
          variant="outline"
          size="sm"
          class="text-muted-foreground hover:text-foreground"
          @click="emit('cancel', booking.id)"
        >
          Отменить
        </Button>
        <Button
          v-if="showActions && booking.status === 'pending'"
          size="sm"
          class="bg-emerald-600 hover:bg-emerald-700 text-white"
          @click="emit('approve', booking.id)"
        >
          Подтвердить
        </Button>
        <Button
          v-if="showActions && booking.status === 'pending'"
          variant="destructive"
          size="sm"
          @click="emit('reject', booking.id)"
        >
          Отклонить
        </Button>
      </div>
    </CardContent>
  </Card>
</template>
