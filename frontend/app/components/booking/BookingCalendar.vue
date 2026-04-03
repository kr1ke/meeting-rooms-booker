<script setup lang="ts">
const props = defineProps<{
  slots: {
    start_time: string
    end_time: string
    is_available: boolean
    booking_title: string | null
  }[]
}>()

const emit = defineEmits<{
  selectSlot: [startTime: string, endTime: string]
}>()

// Выбранный диапазон времени
const selectedStart = ref<string | null>(null)
const selectedEnd = ref<string | null>(null)

function toggleSlot(slot: typeof props.slots[0]) {
  if (!slot.is_available) return

  if (!selectedStart.value || selectedEnd.value) {
    // Начать новый выбор диапазона
    selectedStart.value = slot.start_time
    selectedEnd.value = slot.end_time
    emit('selectSlot', selectedStart.value, selectedEnd.value)
  } else {
    // Расширить текущий выбор
    if (slot.start_time >= selectedStart.value) {
      selectedEnd.value = slot.end_time
      emit('selectSlot', selectedStart.value, selectedEnd.value)
    } else {
      selectedStart.value = slot.start_time
      emit('selectSlot', selectedStart.value, selectedEnd.value!)
    }
  }
}

// Проверяем, входит ли слот в выбранный диапазон
function isSelected(slot: typeof props.slots[0]) {
  if (!selectedStart.value || !selectedEnd.value) return false
  return slot.start_time >= selectedStart.value && slot.end_time <= selectedEnd.value
}
</script>

<template>
  <div class="grid grid-cols-4 gap-1">
    <button
      v-for="slot in slots"
      :key="slot.start_time"
      class="p-2 text-xs rounded border text-center transition-colors"
      :class="{
        'bg-primary text-primary-foreground': isSelected(slot),
        'hover:bg-accent cursor-pointer': slot.is_available && !isSelected(slot),
        'bg-muted text-muted-foreground cursor-not-allowed': !slot.is_available,
      }"
      :disabled="!slot.is_available"
      @click="toggleSlot(slot)"
    >
      {{ slot.start_time.slice(0, 5) }}
      <span v-if="!slot.is_available" class="block text-[10px]">занято</span>
    </button>
  </div>
</template>
