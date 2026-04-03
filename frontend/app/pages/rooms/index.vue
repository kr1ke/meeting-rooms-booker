<script setup lang="ts">
definePageMeta({ middleware: ['auth'] })

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
  <div>
    <h1 class="text-2xl font-bold mb-6">Переговорки</h1>
    <RoomFilters @filter="loadRooms" class="mb-6" />
    <div v-if="loading" class="text-muted-foreground">Загрузка...</div>
    <div v-else class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <RoomCard v-for="room in rooms" :key="room.id" :room="room" />
    </div>
    <div v-if="!loading && rooms.length === 0" class="text-muted-foreground">
      Нет комнат по выбранным фильтрам
    </div>
  </div>
</template>
