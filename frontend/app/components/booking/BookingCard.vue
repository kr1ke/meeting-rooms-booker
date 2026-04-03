<script setup lang="ts">
import { Clock, MapPin } from 'lucide-vue-next'

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

// Цвета статусов бронирования
const statusColors: Record<string, string> = {
  confirmed: 'bg-green-100 text-green-800',
  pending: 'bg-yellow-100 text-yellow-800',
  rejected: 'bg-red-100 text-red-800',
  cancelled: 'bg-gray-100 text-gray-800',
}

// Русские метки статусов
const statusLabels: Record<string, string> = {
  confirmed: 'Подтверждена',
  pending: 'Ожидает',
  rejected: 'Отклонена',
  cancelled: 'Отменена',
}
</script>

<template>
  <Card>
    <CardContent class="p-4">
      <div class="flex items-start justify-between">
        <div>
          <h3 class="font-medium">{{ booking.title }}</h3>
          <div class="flex items-center gap-3 mt-1 text-sm text-muted-foreground">
            <span class="flex items-center gap-1"><MapPin class="h-3 w-3" /> {{ booking.room_name }}</span>
            <span class="flex items-center gap-1">
              <Clock class="h-3 w-3" />
              {{ booking.date }} {{ booking.start_time.slice(0, 5) }}–{{ booking.end_time.slice(0, 5) }}
            </span>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-xs px-2 py-1 rounded-full" :class="statusColors[booking.status]">
            {{ statusLabels[booking.status] }}
          </span>
        </div>
      </div>
      <!-- Кнопки действий: отмена, подтверждение, отклонение -->
      <div v-if="showCancel || showActions" class="mt-3 flex gap-2">
        <Button
          v-if="showCancel && (booking.status === 'confirmed' || booking.status === 'pending')"
          variant="outline" size="sm"
          @click="emit('cancel', booking.id)"
        >
          Отменить
        </Button>
        <Button
          v-if="showActions && booking.status === 'pending'"
          size="sm"
          @click="emit('approve', booking.id)"
        >
          Подтвердить
        </Button>
        <Button
          v-if="showActions && booking.status === 'pending'"
          variant="destructive" size="sm"
          @click="emit('reject', booking.id)"
        >
          Отклонить
        </Button>
      </div>
    </CardContent>
  </Card>
</template>
