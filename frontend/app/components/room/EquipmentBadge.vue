<script setup lang="ts">
import { Monitor, Presentation, Video } from 'lucide-vue-next'

const props = defineProps<{ type: string }>()

// Конфигурация типов оборудования: иконка и метка
const config: Record<string, { label: string; icon: any }> = {
  projector: { label: 'Проектор', icon: Presentation },
  whiteboard: { label: 'Доска', icon: Monitor },
  videoconference: { label: 'Видеоконференция', icon: Video },
}

const item = computed(() => config[props.type] || { label: props.type, icon: Monitor })
</script>

<template>
  <Badge variant="secondary" class="flex items-center gap-1">
    <component :is="item.icon" class="h-3 w-3" />
    {{ item.label }}
  </Badge>
</template>
