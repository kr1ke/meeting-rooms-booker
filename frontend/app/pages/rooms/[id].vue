<script setup lang="ts">
import { MapPin, Users } from 'lucide-vue-next'

definePageMeta({ middleware: ['auth'] })

const route = useRoute()
const { fetchRoom } = useRooms()

const room = ref<any>(null)
const loading = ref(true)

// Загружаем детали комнаты по идентификатору из маршрута
onMounted(async () => {
  room.value = await fetchRoom(route.params.id as string)
  loading.value = false
})
</script>

<template>
  <div v-if="loading" class="text-muted-foreground">Загрузка...</div>
  <div v-else-if="room" class="max-w-4xl">
    <div class="mb-6">
      <h1 class="text-2xl font-bold">{{ room.name }}</h1>
      <div class="flex items-center gap-4 mt-2 text-muted-foreground">
        <span class="flex items-center gap-1"><MapPin class="h-4 w-4" /> Этаж {{ room.floor }}</span>
        <span class="flex items-center gap-1"><Users class="h-4 w-4" /> до {{ room.capacity }} чел.</span>
      </div>
      <div class="flex gap-1 mt-3">
        <EquipmentBadge v-for="(val, key) in room.equipment" :key="key" v-show="val" :type="String(key)" />
      </div>
      <Badge v-if="room.requires_approval" variant="outline" class="mt-2">
        Требует подтверждения администратором
      </Badge>
    </div>

    <!-- Форма бронирования для выбранной комнаты -->
    <BookingForm :room-id="room.id" :room-name="room.name" />
  </div>
</template>
