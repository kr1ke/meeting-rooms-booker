<script setup lang="ts">
import { User as UserIcon, DoorOpen, Clock } from 'lucide-vue-next'

// Всплывающее окно с деталями бронирования.
// Используется на дашборде (с roomName) и в форме бронирования (без roomName).
//
// Родитель управляет state: при клике по блоку брони устанавливает booking
// в non-null, при закрытии — обнуляет. Позиционирование: fixed, координаты
// курсора приходят в props.
//
// ВАЖНО: родитель ОБЯЗАН делать e.stopPropagation() в обработчике клика
// по блоку брони — иначе document click listener внутри попапа закроет
// его тем же кликом, которым он открылся.

const props = defineProps<{
  booking: {
    title: string
    user_name: string
    start_time: string
    end_time: string
  } | null
  roomName?: string
  x: number
  y: number
}>()

const emit = defineEmits<{
  close: []
}>()

const popupRef = ref<HTMLElement | null>(null)

// Клик где-то в документе → если не внутри попапа и попап открыт, закрываем.
function onDocumentClick(e: MouseEvent) {
  if (!props.booking) return
  if (popupRef.value && popupRef.value.contains(e.target as Node)) return
  emit('close')
}

// Escape → закрываем попап.
function onKeydown(e: KeyboardEvent) {
  if (!props.booking) return
  if (e.key === 'Escape') emit('close')
}

onMounted(() => {
  document.addEventListener('click', onDocumentClick)
  document.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.removeEventListener('click', onDocumentClick)
  document.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="booking"
        ref="popupRef"
        class="fixed z-[60] bg-popover border border-border rounded-lg shadow-lg p-3 min-w-[200px] max-w-[280px]"
        :style="{ top: (y + 8) + 'px', left: x + 'px', transform: 'translateX(-50%)' }"
        @click.stop
      >
        <!-- Название встречи -->
        <p class="font-semibold text-sm text-foreground mb-1.5">{{ booking.title }}</p>

        <!-- Автор -->
        <div class="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
          <UserIcon class="h-3 w-3 shrink-0" />
          {{ booking.user_name }}
        </div>

        <!-- Комната (только если передана) -->
        <div v-if="roomName" class="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
          <DoorOpen class="h-3 w-3 shrink-0" />
          {{ roomName }}
        </div>

        <!-- Время -->
        <div class="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Clock class="h-3 w-3 shrink-0" />
          {{ booking.start_time }} – {{ booking.end_time }}
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
