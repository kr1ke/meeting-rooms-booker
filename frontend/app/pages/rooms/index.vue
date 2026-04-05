<script setup lang="ts">
import { DoorOpen } from 'lucide-vue-next'

definePageMeta({ middleware: ['auth'] })
useHead({ title: 'Переговорки' })

const { fetchRooms } = useRooms()
const rooms = ref<any[]>([])
const loading = ref(true)

// Загрузка списка комнат с опциональными параметрами фильтрации
async function loadRooms(params?: any) {
  loading.value = true
  rooms.value = await fetchRooms(params)
  loading.value = false
}

onMounted(() => loadRooms())
</script>

<template>
  <div class="animate-fade-in">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold">Переговорки</h1>
        <p class="text-muted-foreground text-sm mt-1">Выберите комнату для бронирования</p>
      </div>
    </div>

    <RoomFilters @filter="loadRooms" class="mb-4" />

    <!-- Спиннер загрузки -->
    <div v-if="loading" class="flex items-center gap-3 text-muted-foreground py-8">
      <div class="h-5 w-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      Загрузка...
    </div>

    <!-- Список комнат -->
    <div v-else-if="rooms.length > 0" class="divide-y divide-border/50">
      <RoomCard v-for="room in rooms" :key="room.id" :room="room" />
    </div>

    <!-- Пустое состояние -->
    <div v-if="!loading && rooms.length === 0" class="text-center py-16">
      <DoorOpen class="h-10 w-10 text-muted-foreground/30 mx-auto mb-3" />
      <p class="text-muted-foreground font-medium">Нет комнат по выбранным фильтрам</p>
      <p class="text-sm text-muted-foreground/60 mt-1">Попробуйте сбросить фильтры</p>
    </div>
  </div>
</template>
