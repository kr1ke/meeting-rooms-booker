<script setup lang="ts">
/**
 * Таймлайн бронирования с визуализацией загруженности.
 * Показывает сетку 08:00–20:00, занятые блоки, индикатор «сейчас».
 * Позволяет выбрать диапазон кликом и растянуть за края ползунка.
 */

const props = defineProps<{
  slots: {
    start_time: string
    end_time: string
    is_available: boolean
    booking_title: string | null
    booking_user_name: string | null
  }[]
  bookings: {
    start_time: string
    end_time: string
    title: string
    user_name: string
  }[]
  startTime: string
  endTime: string
}>()

const emit = defineEmits<{
  'update:startTime': [value: string]
  'update:endTime': [value: string]
}>()

const TIMELINE_START = 8 * 60
const TIMELINE_END = 20 * 60
const TIMELINE_DURATION = TIMELINE_END - TIMELINE_START
const SNAP_MINUTES = 5

const timelineRef = ref<HTMLElement | null>(null)

function toMinutes(time: string): number {
  const [h, m] = time.split(':').map(Number)
  return h * 60 + m
}

function fromMinutes(mins: number): string {
  const h = Math.floor(mins / 60)
  const m = mins % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
}

function timeToPercent(mins: number): number {
  return ((mins - TIMELINE_START) / TIMELINE_DURATION) * 100
}

const hourLabels = computed(() => {
  const labels: number[] = []
  for (let h = 8; h <= 20; h++) labels.push(h)
  return labels
})

const halfHourLines = computed(() => {
  const lines: number[] = []
  for (let m = TIMELINE_START + 30; m < TIMELINE_END; m += 30) {
    if (m % 60 !== 0) lines.push(m)
  }
  return lines
})

const nowPercent = computed(() => {
  const now = new Date()
  const mins = now.getHours() * 60 + now.getMinutes()
  if (mins < TIMELINE_START || mins > TIMELINE_END) return null
  return timeToPercent(mins)
})

const bookingBlocks = computed(() =>
  props.bookings.map(b => {
    const start = toMinutes(b.start_time)
    const end = toMinutes(b.end_time)
    return {
      ...b,
      left: timeToPercent(start),
      width: ((end - start) / TIMELINE_DURATION) * 100,
      startMins: start,
      endMins: end,
    }
  })
)

const selection = computed(() => {
  if (!props.startTime || !props.endTime) return null
  const start = toMinutes(props.startTime)
  const end = toMinutes(props.endTime)
  if (start >= end) return null
  return {
    left: timeToPercent(start),
    width: ((end - start) / TIMELINE_DURATION) * 100,
  }
})

function isTimeOccupied(mins: number): boolean {
  return bookingBlocks.value.some(b => mins >= b.startMins && mins < b.endMins)
}

function findFreeEnd(startMins: number): number {
  let maxEnd = TIMELINE_END
  for (const b of bookingBlocks.value) {
    if (b.startMins > startMins && b.startMins < maxEnd) {
      maxEnd = b.startMins
    }
  }
  return maxEnd
}

function findFreeStart(endMins: number): number {
  let minStart = TIMELINE_START
  for (const b of bookingBlocks.value) {
    if (b.endMins <= endMins && b.endMins > minStart) {
      minStart = b.endMins
    }
  }
  return minStart
}

function snap(mins: number): number {
  return Math.round(mins / SNAP_MINUTES) * SNAP_MINUTES
}

// Преобразовать позицию мыши в минуты
function mouseToMinutes(e: MouseEvent): number {
  if (!timelineRef.value) return TIMELINE_START
  const rect = timelineRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const percent = x / rect.width
  const rawMins = TIMELINE_START + percent * TIMELINE_DURATION
  return snap(Math.max(TIMELINE_START, Math.min(TIMELINE_END, rawMins)))
}

// --- Drag-ресайз выделения ---
const dragging = ref<'start' | 'end' | null>(null)
let justDragged = false

function startDrag(edge: 'start' | 'end', e: MouseEvent) {
  e.preventDefault()
  e.stopPropagation()
  dragging.value = edge
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

function onDrag(e: MouseEvent) {
  if (!dragging.value || !timelineRef.value) return
  const mins = mouseToMinutes(e)

  if (dragging.value === 'start') {
    const endMins = toMinutes(props.endTime)
    // Не позволяем старту пересечь конец (минимум 5 мин)
    if (mins < endMins - SNAP_MINUTES && !isTimeOccupied(mins)) {
      const freeStart = findFreeStart(endMins)
      emit('update:startTime', fromMinutes(Math.max(mins, freeStart)))
    }
  } else {
    const startMins = toMinutes(props.startTime)
    if (mins > startMins + SNAP_MINUTES) {
      const maxEnd = findFreeEnd(startMins)
      emit('update:endTime', fromMinutes(Math.min(mins, maxEnd)))
    }
  }
}

function stopDrag() {
  dragging.value = null
  justDragged = true
  // Сбросим флаг после всплытия click
  requestAnimationFrame(() => { justDragged = false })
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

onUnmounted(() => {
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
})

// --- Клик по таймлайну ---
function handleTimelineClick(e: MouseEvent) {
  // Не обрабатываем клик во время или сразу после drag
  if (dragging.value || justDragged) return
  const mins = mouseToMinutes(e)
  if (isTimeOccupied(mins)) return

  if (!props.startTime || (props.startTime && props.endTime)) {
    const maxEnd = findFreeEnd(mins)
    const defaultEnd = Math.min(mins + 30, maxEnd)
    emit('update:startTime', fromMinutes(mins))
    emit('update:endTime', fromMinutes(defaultEnd))
  } else {
    let start = toMinutes(props.startTime)
    let end = mins
    if (end <= start) {
      const freeStart = findFreeStart(start)
      end = start + (toMinutes(props.endTime) - start)
      start = Math.max(mins, freeStart)
      emit('update:startTime', fromMinutes(start))
    } else {
      const maxEnd = findFreeEnd(start)
      end = Math.min(end, maxEnd)
      emit('update:endTime', fromMinutes(end))
    }
  }
}

// --- Hover-превью ---
const hoverMinutes = ref<number | null>(null)

function handleMouseMove(e: MouseEvent) {
  if (dragging.value) return
  const mins = mouseToMinutes(e)
  hoverMinutes.value = isTimeOccupied(mins) ? null : mins
}

function handleMouseLeave() {
  if (!dragging.value) hoverMinutes.value = null
}

const hoverPercent = computed(() => {
  if (hoverMinutes.value === null) return null
  return timeToPercent(hoverMinutes.value)
})

const hoverTimeLabel = computed(() => {
  if (hoverMinutes.value === null) return ''
  return fromMinutes(hoverMinutes.value)
})
</script>

<template>
  <div class="space-y-1">
    <!-- Часовые метки -->
    <div class="relative h-5 select-none">
      <span
        v-for="h in hourLabels"
        :key="h"
        class="absolute text-[11px] text-muted-foreground/70 font-medium -translate-x-1/2 tabular-nums"
        :style="{ left: timeToPercent(h * 60) + '%' }"
      >
        {{ String(h).padStart(2, '0') }}
      </span>
    </div>

    <!-- Основной таймлайн -->
    <div
      ref="timelineRef"
      class="relative h-16 rounded-lg bg-muted/40 border border-border/60 overflow-hidden select-none"
      :class="dragging ? 'cursor-col-resize' : 'cursor-crosshair'"
      @click="handleTimelineClick"
      @mousemove="handleMouseMove"
      @mouseleave="handleMouseLeave"
    >
      <!-- Вертикальные линии часов -->
      <div
        v-for="h in hourLabels.slice(1)"
        :key="'hour-' + h"
        class="absolute top-0 bottom-0 w-px bg-border/50"
        :style="{ left: timeToPercent(h * 60) + '%' }"
      />

      <!-- Вертикальные линии получасов -->
      <div
        v-for="m in halfHourLines"
        :key="'half-' + m"
        class="absolute top-0 bottom-0 w-px bg-border/25"
        :style="{ left: timeToPercent(m) + '%' }"
      />

      <!-- Блоки существующих бронирований -->
      <div
        v-for="(block, i) in bookingBlocks"
        :key="i"
        class="absolute top-1 bottom-1 rounded-md bg-muted border border-border/80 flex items-center overflow-hidden pointer-events-none z-10"
        :style="{ left: block.left + '%', width: block.width + '%' }"
      >
        <div class="w-1 self-stretch bg-foreground/20 rounded-l-md shrink-0" />
        <div class="truncate min-w-0 px-1.5">
          <p class="text-[11px] font-medium text-foreground/70 truncate leading-tight">
            {{ block.title }}
          </p>
          <p class="text-[10px] text-muted-foreground truncate leading-tight">
            {{ block.user_name }}
          </p>
        </div>
      </div>

      <!-- Выбранный диапазон с drag-ручками -->
      <div
        v-if="selection"
        class="absolute top-0.5 bottom-0.5 rounded-md bg-primary/20 border-2 border-primary/60 z-20 pointer-events-none transition-all duration-75"
        :style="{ left: selection.left + '%', width: selection.width + '%' }"
      >
        <!-- Левая drag-ручка -->
        <div
          class="absolute -left-1.5 top-0 bottom-0 w-4 cursor-col-resize pointer-events-auto z-40 group"
          @mousedown="startDrag('start', $event)"
        >
          <div class="absolute left-1.5 top-1 bottom-1 w-1.5 rounded-l-md bg-primary group-hover:bg-primary/80 transition-colors" />
        </div>
        <!-- Правая drag-ручка -->
        <div
          class="absolute -right-1.5 top-0 bottom-0 w-4 cursor-col-resize pointer-events-auto z-40 group"
          @mousedown="startDrag('end', $event)"
        >
          <div class="absolute right-1.5 top-1 bottom-1 w-1.5 rounded-r-md bg-primary group-hover:bg-primary/80 transition-colors" />
        </div>
      </div>

      <!-- Hover-линия -->
      <div
        v-if="hoverPercent !== null && !dragging"
        class="absolute top-0 bottom-0 w-px bg-primary/30 z-30 pointer-events-none transition-[left] duration-75"
        :style="{ left: hoverPercent + '%' }"
      >
        <span class="absolute -top-6 left-1/2 -translate-x-1/2 text-[10px] font-medium text-primary bg-primary/10 px-1.5 py-0.5 rounded tabular-nums whitespace-nowrap">
          {{ hoverTimeLabel }}
        </span>
      </div>

      <!-- Индикатор «сейчас» -->
      <div
        v-if="nowPercent !== null"
        class="absolute top-0 bottom-0 w-0.5 bg-destructive/70 z-30 pointer-events-none"
        :style="{ left: nowPercent + '%' }"
      >
        <div class="absolute -top-1 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full bg-destructive/70" />
      </div>
    </div>

    <!-- Легенда -->
    <div class="flex items-center gap-4 pt-1">
      <span class="flex items-center gap-1.5 text-[11px] text-muted-foreground">
        <span class="w-3 h-2.5 rounded-sm bg-primary/20 border border-primary/50 inline-block" />
        Ваш выбор
      </span>
      <span class="flex items-center gap-1.5 text-[11px] text-muted-foreground">
        <span class="w-3 h-2.5 rounded-sm bg-muted border border-border/80 inline-block" />
        Занято
      </span>
      <span v-if="nowPercent !== null" class="flex items-center gap-1.5 text-[11px] text-muted-foreground">
        <span class="w-2 h-2 rounded-full bg-destructive/70 inline-block" />
        Сейчас
      </span>
    </div>
  </div>
</template>
