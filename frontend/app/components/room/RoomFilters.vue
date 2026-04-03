<script setup lang="ts">
const emit = defineEmits<{
  filter: [params: { floor?: number; min_capacity?: number; equipment?: string }]
}>()

// Параметры фильтрации комнат
const floor = ref<string>()
const minCapacity = ref<string>()

function applyFilters() {
  emit('filter', {
    floor: floor.value ? Number(floor.value) : undefined,
    min_capacity: minCapacity.value ? Number(minCapacity.value) : undefined,
  })
}

// Автоматически применяем фильтры при изменении значений
watch([floor, minCapacity], applyFilters)
</script>

<template>
  <div class="flex flex-wrap items-center gap-4">
    <Select v-model="floor">
      <SelectTrigger class="w-36">
        <SelectValue placeholder="Этаж" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="">Все этажи</SelectItem>
        <SelectItem v-for="f in [1, 2, 3]" :key="f" :value="String(f)">Этаж {{ f }}</SelectItem>
      </SelectContent>
    </Select>

    <Select v-model="minCapacity">
      <SelectTrigger class="w-44">
        <SelectValue placeholder="Вместимость" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="">Любая</SelectItem>
        <SelectItem value="4">от 4 человек</SelectItem>
        <SelectItem value="8">от 8 человек</SelectItem>
        <SelectItem value="12">от 12 человек</SelectItem>
      </SelectContent>
    </Select>
  </div>
</template>
