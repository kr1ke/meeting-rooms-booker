<script setup lang="ts">
import { Monitor } from 'lucide-vue-next'
import { getEquipmentType } from '~/utils/equipment'

const props = defineProps<{ type: string }>()

// Находим метаданные по ключу. Для неизвестных ключей — серый фолбэк.
const item = computed(() => {
  const known = getEquipmentType(props.type)
  if (known) return known
  return {
    key: props.type,
    label: props.type,
    icon: Monitor,
    badgeClasses: 'bg-gray-50 text-gray-700 border-gray-200',
  }
})
</script>

<template>
  <!-- Бейдж оборудования — таблетка с индивидуальным цветом -->
  <span
    class="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium"
    :class="item.badgeClasses"
  >
    <component :is="item.icon" class="h-3.5 w-3.5" />
    {{ item.label }}
  </span>
</template>
