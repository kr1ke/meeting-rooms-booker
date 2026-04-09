<script setup lang="ts">
import { EQUIPMENT_TYPES } from '~/utils/equipment'

// Выбор оборудования переговорки чекбоксами.
// v-model принимает объект вида { projector: true, whiteboard: true }.
// Неотмеченные типы удаляются из объекта (не хранятся как false),
// чтобы JSONB в БД оставался компактным — так же, как в seed-данных.
const props = defineProps<{
  modelValue: Record<string, boolean>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, boolean>]
}>()

// Проверка активности конкретного типа в текущем значении
function isChecked(key: string): boolean {
  return !!props.modelValue[key]
}

// Переключение чекбокса — иммутабельно собираем новый объект.
// НЕ мутируем props.modelValue.
function toggle(key: string, checked: boolean) {
  const next = { ...props.modelValue }
  if (checked) {
    next[key] = true
  } else {
    delete next[key]
  }
  emit('update:modelValue', next)
}
</script>

<template>
  <!-- Вертикальный стек кликабельных строк с чекбоксами -->
  <div class="space-y-2">
    <label
      v-for="type in EQUIPMENT_TYPES"
      :key="type.key"
      class="flex items-center gap-2.5 px-3 py-2 rounded-lg border border-border hover:bg-muted/30 cursor-pointer transition-colors"
    >
      <input
        type="checkbox"
        :checked="isChecked(type.key)"
        class="rounded border-input h-4 w-4"
        @change="toggle(type.key, ($event.target as HTMLInputElement).checked)"
      />
      <component :is="type.icon" class="h-4 w-4 text-muted-foreground" />
      <span class="text-sm font-medium">{{ type.label }}</span>
    </label>
  </div>
</template>
