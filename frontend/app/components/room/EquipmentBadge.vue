<script setup lang="ts">
import { Monitor, Presentation, Video } from 'lucide-vue-next'

const props = defineProps<{ type: string }>()

// Конфигурация типов оборудования: иконка, метка и индивидуальные цвета
const config: Record<string, { label: string; icon: any; classes: string }> = {
  projector: {
    label: 'Проектор',
    icon: Presentation,
    classes: 'bg-blue-50 text-blue-700 border-blue-200',
  },
  whiteboard: {
    label: 'Доска',
    icon: Monitor,
    classes: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  },
  videoconference: {
    label: 'Видеоконференция',
    icon: Video,
    classes: 'bg-violet-50 text-violet-700 border-violet-200',
  },
}

// Фолбэк для неизвестных типов оборудования
const item = computed(() =>
  config[props.type] || {
    label: props.type,
    icon: Monitor,
    classes: 'bg-gray-50 text-gray-700 border-gray-200',
  },
)
</script>

<template>
  <!-- Бейдж оборудования — таблетка с индивидуальным цветом -->
  <span
    class="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium"
    :class="item.classes"
  >
    <component :is="item.icon" class="h-3.5 w-3.5" />
    {{ item.label }}
  </span>
</template>
