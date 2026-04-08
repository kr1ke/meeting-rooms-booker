# Попап бронирований на BookingCalendar + EquipmentPicker — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Добавить попап с деталями брони при клике на занятые блоки в `BookingCalendar` (на странице бронирования), и подключить выбор оборудования через чекбоксы в форму создания/редактирования комнаты в админке.

**Architecture:** Выносим общий `BookingDetailPopup` и используем его на дашборде и в форме бронирования (устраняем дублирование). Выносим метаданные типов оборудования в утилиту `utils/equipment.ts`, которую используют и `EquipmentBadge`, и новый `EquipmentPicker`. Никаких изменений на backend — API уже поддерживает `equipment: dict`.

**Tech Stack:** Nuxt 3 (SPA, `ssr: false`), Vue 3 (`<script setup>`, Composition API), Tailwind CSS, shadcn-vue, lucide-vue-next, Docker Compose (hot reload через volume mount), Chrome DevTools MCP для E2E-тестов.

**Spec:** `docs/superpowers/specs/2026-04-08-booking-timeline-popup-and-equipment-design.md`

---

## File Structure

### Создаваемые файлы

| Файл | Ответственность |
|---|---|
| `frontend/app/utils/equipment.ts` | Источник правды для типов оборудования. Экспортирует `EquipmentType` interface, `EQUIPMENT_TYPES` массив и `getEquipmentType(key)`. Чистый TS, без Vue API. |
| `frontend/app/components/booking/BookingDetailPopup.vue` | Презентационный компонент всплывающего окна. Teleport в body, закрытие по клику вне и Escape, позиционирование по координатам курсора. |
| `frontend/app/components/room/EquipmentPicker.vue` | Форм-контрол выбора оборудования. Рендерит чекбоксы по `EQUIPMENT_TYPES`. `v-model` для `Record<string, boolean>`. Immutable emit. |

### Модифицируемые файлы

| Файл | Изменения |
|---|---|
| `frontend/app/components/room/EquipmentBadge.vue` | Убрать локальный `config`, использовать `getEquipmentType()` из утилиты. |
| `frontend/app/pages/index.vue` | Удалить inline-попап и его логику, подключить `BookingDetailPopup`. Обработчик клика передаёт координаты и данные в попап. |
| `frontend/app/components/booking/BookingCalendar.vue` | Блоки бронирований становятся кликабельными. Emit `booking-click` с координатами и данными брони. Убрать `pointer-events-none`. |
| `frontend/app/components/booking/BookingForm.vue` | Подписка на `booking-click` от `BookingCalendar`, state `activeBooking`, рендер `BookingDetailPopup`. |
| `frontend/app/pages/admin/rooms.vue` | Глубокая копия `equipment` при `openEdit`, подключить `RoomEquipmentPicker` в диалог. |

### Nuxt auto-import naming

- `components/booking/BookingCalendar.vue` → `<BookingCalendar>` (префикс уже в имени)
- `components/booking/BookingDetailPopup.vue` → `<BookingDetailPopup>` (префикс уже в имени)
- `components/room/EquipmentBadge.vue` → `<RoomEquipmentBadge>` (добавляется префикс)
- `components/room/EquipmentPicker.vue` → `<RoomEquipmentPicker>` (добавляется префикс)

---

## Тестовая стратегия

Проект не содержит unit-тестов для фронтенда. Используем **Chrome DevTools MCP** как acceptance-тесты: после каждой значимой задачи прогоняем сценарий в живом Docker-стеке через hot reload. Это соответствует явному запросу пользователя ("use chrome mcp for tests").

Предусловие для любых тестов: запущен `docker compose up -d`, все сервисы health-ready (frontend :3000, backend :8000, db :5434). Seed создаёт комнаты и пользователей, но НЕ брони — для тестов попапа нужно заранее создать несколько броней под разными учётками.

---

## Task 1: Утилита EQUIPMENT_TYPES + рефактор EquipmentBadge

**Files:**
- Create: `frontend/app/utils/equipment.ts`
- Modify: `frontend/app/components/room/EquipmentBadge.vue`

- [ ] **Step 1: Убедиться, что Docker-стек запущен**

Run: `docker compose ps`
Expected: три сервиса (db, backend, frontend) в состоянии `Up` / `running`. Если нет — `docker compose up -d`.

- [ ] **Step 2: Создать утилиту `frontend/app/utils/equipment.ts`**

Создать файл со следующим содержимым:

```ts
import type { Component } from 'vue'
import { Presentation, Monitor, Video } from 'lucide-vue-next'

// Описание одного типа оборудования переговорки.
// Используется EquipmentBadge (отображение) и EquipmentPicker (выбор).
export interface EquipmentType {
  key: string           // идентификатор в JSONB БД
  label: string         // человекочитаемое название
  icon: Component       // lucide-иконка
  badgeClasses: string  // Tailwind-классы для цветного бейджа
}

// Единый список всех типов оборудования.
// При добавлении нового типа — расширяй этот массив, EquipmentBadge
// и EquipmentPicker подхватят автоматически.
export const EQUIPMENT_TYPES: readonly EquipmentType[] = [
  {
    key: 'projector',
    label: 'Проектор',
    icon: Presentation,
    badgeClasses: 'bg-blue-50 text-blue-700 border-blue-200',
  },
  {
    key: 'whiteboard',
    label: 'Доска',
    icon: Monitor,
    badgeClasses: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  },
  {
    key: 'videoconference',
    label: 'Видеоконференция',
    icon: Video,
    badgeClasses: 'bg-violet-50 text-violet-700 border-violet-200',
  },
] as const

// Найти тип по ключу. Возвращает undefined, если тип неизвестен —
// потребитель должен уметь показать fallback.
export function getEquipmentType(key: string): EquipmentType | undefined {
  return EQUIPMENT_TYPES.find(t => t.key === key)
}
```

- [ ] **Step 3: Рефакторить `EquipmentBadge.vue` на использование утилиты**

Заменить содержимое файла `frontend/app/components/room/EquipmentBadge.vue` на:

```vue
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
```

- [ ] **Step 4: Визуально проверить регрессию EquipmentBadge через Chrome DevTools MCP**

Открыть страницу `http://localhost:3000/rooms` (понадобится логин `user@company.com` / `user123`). На карточках комнат должны быть те же бейджи, что и до рефакторинга: Альфа (Доска), Бета (Проектор + Доска), Гамма (Проектор + Видеоконференция), Эпсилон (Проектор + Видеоконференция + Доска), Дельта (пусто).

Сравнить скриншот до/после — визуальных отличий быть не должно.

- [ ] **Step 5: Коммит**

```bash
git add frontend/app/utils/equipment.ts frontend/app/components/room/EquipmentBadge.vue
git commit -m "♻️ refactor: вынести типы оборудования в utils/equipment.ts"
```

---

## Task 2: Компонент EquipmentPicker

**Files:**
- Create: `frontend/app/components/room/EquipmentPicker.vue`

- [ ] **Step 1: Создать `EquipmentPicker.vue`**

Создать файл `frontend/app/components/room/EquipmentPicker.vue` со следующим содержимым:

```vue
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
```

- [ ] **Step 2: Коммит**

```bash
git add frontend/app/components/room/EquipmentPicker.vue
git commit -m "✨ feat: EquipmentPicker — чекбоксы выбора оборудования комнаты"
```

---

## Task 3: Интеграция EquipmentPicker в admin/rooms.vue + E2E

**Files:**
- Modify: `frontend/app/pages/admin/rooms.vue`

- [ ] **Step 1: Добавить глубокую копию equipment в openEdit**

В файле `frontend/app/pages/admin/rooms.vue` найти функцию `openEdit` (строки 28-32) и заменить:

```ts
function openEdit(room: any) {
  editingRoom.value = room
  form.value = { ...room }
  showDialog.value = true
}
```

на:

```ts
function openEdit(room: any) {
  editingRoom.value = room
  // Глубокая копия equipment, чтобы EquipmentPicker не мутировал исходный объект
  // в массиве rooms (он использует { ...props.modelValue, delete ... }).
  form.value = { ...room, equipment: { ...(room.equipment || {}) } }
  showDialog.value = true
}
```

- [ ] **Step 2: Подключить EquipmentPicker в диалог**

В том же файле, внутри `<form @submit.prevent="onSubmit" class="space-y-4">` (строка 106), после блока с `requires_approval` (строки 121-124) и перед кнопкой `<Button type="submit" ...>` (строка 125), добавить:

```vue
<div class="space-y-2">
  <Label>Оборудование</Label>
  <RoomEquipmentPicker v-model="form.equipment" />
</div>
```

Полностью секция формы после правки должна выглядеть так:

```vue
<form @submit.prevent="onSubmit" class="space-y-4">
  <div class="space-y-2">
    <Label>Название</Label>
    <Input v-model="form.name" required />
  </div>
  <div class="grid grid-cols-2 gap-4">
    <div class="space-y-2">
      <Label>Этаж</Label>
      <Input v-model.number="form.floor" type="number" min="1" required />
    </div>
    <div class="space-y-2">
      <Label>Вместимость</Label>
      <Input v-model.number="form.capacity" type="number" min="1" required />
    </div>
  </div>
  <div class="flex items-center gap-2">
    <input type="checkbox" id="approval" v-model="form.requires_approval" class="rounded border-input" />
    <Label for="approval">Требует подтверждения</Label>
  </div>
  <div class="space-y-2">
    <Label>Оборудование</Label>
    <RoomEquipmentPicker v-model="form.equipment" />
  </div>
  <Button type="submit" class="w-full font-semibold">Сохранить</Button>
</form>
```

- [ ] **Step 3: E2E — создание новой комнаты с оборудованием через Chrome DevTools MCP**

Сценарий:

1. `mcp__plugin_chrome-devtools-mcp__chrome-devtools__new_page` → `http://localhost:3000/login`
2. Залогиниться как `admin@company.com` / `admin123` (через `fill_form` или `fill` + `click`).
3. Перейти на `http://localhost:3000/admin/rooms`.
4. Клик «Добавить комнату» → диалог открывается.
5. Заполнить: название «Тест-попап», этаж 2, вместимость 6.
6. В секции «Оборудование» отметить «Проектор» и «Доска».
7. Клик «Сохранить».
8. Сделать `take_screenshot` с таблицей комнат — комната «Тест-попап» должна появиться.
9. Перейти на `http://localhost:3000/rooms` (каталог).
10. Найти карточку «Тест-попап» — на ней должны быть бейджи `Проектор` и `Доска`. Сделать `take_screenshot`.

Expected: комната создана, бейджи отображаются.

- [ ] **Step 4: E2E — редактирование существующей комнаты**

Сценарий:

1. Вернуться на `http://localhost:3000/admin/rooms`.
2. Клик «Изменить» на только что созданной комнате «Тест-попап».
3. Проверить, что чекбоксы «Проектор» и «Доска» уже отмечены. Сделать `take_screenshot`.
4. Снять «Доска», отметить «Видеоконференция».
5. Клик «Сохранить».
6. Перейти на `http://localhost:3000/rooms` и обновить. Карточка «Тест-попап» теперь показывает бейджи `Проектор` + `Видеоконференция` (без «Доска»).

Expected: изменения сохранены, старые значения не «залипли» в других комнатах (регрессия — сделать скриншот списка всех комнат и убедиться, что бейджи Альфы/Беты/Гаммы не изменились).

- [ ] **Step 5: Коммит**

```bash
git add frontend/app/pages/admin/rooms.vue
git commit -m "✨ feat: выбор оборудования в форме создания/редактирования комнаты"
```

---

## Task 4: Компонент BookingDetailPopup

**Files:**
- Create: `frontend/app/components/booking/BookingDetailPopup.vue`

- [ ] **Step 1: Создать `BookingDetailPopup.vue`**

Создать файл `frontend/app/components/booking/BookingDetailPopup.vue` со следующим содержимым:

```vue
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
        class="fixed z-50 bg-popover border border-border rounded-lg shadow-lg p-3 min-w-[200px] max-w-[280px]"
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
```

- [ ] **Step 2: Коммит**

```bash
git add frontend/app/components/booking/BookingDetailPopup.vue
git commit -m "✨ feat: BookingDetailPopup — переиспользуемый попап деталей брони"
```

---

## Task 5: Миграция pages/index.vue на новый BookingDetailPopup

**Files:**
- Modify: `frontend/app/pages/index.vue`

**Цель:** не изменить поведение дашборда (регрессия), а только перевести его на общий компонент.

- [ ] **Step 1: Удалить локальный state и обработчики попапа из `<script setup>`**

В файле `frontend/app/pages/index.vue` найти блок (строки 86-112):

```ts
// Попап деталей бронирования
const activeBooking = ref<{ title: string; user_name: string; start_time: string; end_time: string; room_name: string; x: number; y: number } | null>(null)

function showBookingDetail(b: any, roomName: string, e: MouseEvent) {
  e.stopPropagation()
  activeBooking.value = {
    title: b.title,
    user_name: b.user_name,
    start_time: b.start_time,
    end_time: b.end_time,
    room_name: roomName,
    x: e.clientX,
    y: e.clientY,
  }
}

function hideBookingDetail() {
  activeBooking.value = null
}

// Закрытие по клику вне
onMounted(() => {
  document.addEventListener('click', hideBookingDetail)
})
onUnmounted(() => {
  document.removeEventListener('click', hideBookingDetail)
})
```

и заменить на:

```ts
// Попап деталей бронирования. Контракт такой же, как в BookingDetailPopup:
// открыт ⇔ activeBooking !== null. Закрытие по клику вне и Escape обрабатывает сам попап.
const activeBooking = ref<{
  booking: { title: string; user_name: string; start_time: string; end_time: string }
  roomName: string
  x: number
  y: number
} | null>(null)

// Клик по блоку бронирования на таймлайне комнаты. stopPropagation обязателен —
// иначе document listener внутри BookingDetailPopup закроет попап тем же кликом.
function showBookingDetail(b: any, roomName: string, e: MouseEvent) {
  e.stopPropagation()
  activeBooking.value = {
    booking: {
      title: b.title,
      user_name: b.user_name,
      start_time: b.start_time,
      end_time: b.end_time,
    },
    roomName,
    x: e.clientX,
    y: e.clientY,
  }
}
```

**Важно:** функции `hideBookingDetail`, `onMounted` для document listener и `onUnmounted` удаляются полностью. Их логика теперь внутри `BookingDetailPopup`.

Оставить `onMounted(async () => { ... fetchMyBookings ... })` — он другой, его трогать не нужно.

- [ ] **Step 2: Заменить inline-Teleport попапа в шаблоне на компонент**

В том же файле найти блок `<Teleport to="body">` (строки 253-276):

```vue
<!-- Попап деталей бронирования -->
<Teleport to="body">
  <Transition name="fade">
    <div
      v-if="activeBooking"
      class="fixed z-50 bg-popover border border-border rounded-lg shadow-lg p-3 min-w-[200px] max-w-[280px]"
      :style="{ top: (activeBooking.y + 8) + 'px', left: activeBooking.x + 'px', transform: 'translateX(-50%)' }"
      @click.stop
    >
      <p class="font-semibold text-sm text-foreground mb-1.5">{{ activeBooking.title }}</p>
      <div class="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
        <UserIcon class="h-3 w-3 shrink-0" />
        {{ activeBooking.user_name }}
      </div>
      <div class="flex items-center gap-1.5 text-xs text-muted-foreground mb-1">
        <DoorOpen class="h-3 w-3 shrink-0" />
        {{ activeBooking.room_name }}
      </div>
      <div class="flex items-center gap-1.5 text-xs text-muted-foreground">
        <Clock class="h-3 w-3 shrink-0" />
        {{ activeBooking.start_time }} – {{ activeBooking.end_time }}
      </div>
    </div>
  </Transition>
</Teleport>
```

и заменить на:

```vue
<!-- Попап деталей бронирования — общий компонент -->
<BookingDetailPopup
  :booking="activeBooking?.booking ?? null"
  :room-name="activeBooking?.roomName"
  :x="activeBooking?.x ?? 0"
  :y="activeBooking?.y ?? 0"
  @close="activeBooking = null"
/>
```

- [ ] **Step 3: Удалить неиспользуемые импорты**

В `<script setup>` index.vue, в импортах из `lucide-vue-next` (строка 2):

```ts
import { CalendarDays, DoorOpen, ArrowRight, CalendarOff, Clock, User as UserIcon, ChevronLeft, ChevronRight } from 'lucide-vue-next'
```

После удаления inline-попапа не используются `UserIcon`, `Clock` (они теперь только внутри `BookingDetailPopup`). `DoorOpen` остаётся — он используется в кнопке «Забронировать переговорку» и в «Быстрое бронирование».

Заменить на:

```ts
import { CalendarDays, DoorOpen, ArrowRight, CalendarOff, ChevronLeft, ChevronRight } from 'lucide-vue-next'
```

- [ ] **Step 4: E2E — регрессия дашборда через Chrome DevTools MCP**

**Подготовка данных:** для теста нужны брони на сегодня. Если их нет — создать заранее:
1. Логин под `maria@company.com` / `user456`, `http://localhost:3000/rooms`, выбрать Альфу, забронировать 10:00-11:00 «Стендап команды». Разлогин.
2. Логин под `user@company.com` / `user123`, забронировать Бету 14:00-15:00 «Демо продукта». Разлогин.

Сценарий теста:
1. Оставаться залогиненным как `user@company.com`, перейти на `http://localhost:3000/`.
2. Дождаться загрузки таймлайна «Загруженность». `take_screenshot`.
3. Найти на таймлайне Альфы синий блок «Стендап команды» (по вычисленным координатам). Клик.
4. Попап открывается. Содержит:
   - заголовок «Стендап команды»
   - автор «Мария Иванова»
   - комната «Альфа»
   - время «10:00:00 – 11:00:00» (точный формат из BookingBlock API)
5. `take_screenshot` — видно и таймлайн, и открытый попап.
6. Клик в пустое место (вне попапа) → попап закрывается. `take_screenshot` подтверждения.
7. Клик снова по блоку → попап открыт. Нажать Escape (`press_key` с `key: 'Escape'`) → попап закрывается.

Expected: поведение идентично предыдущей версии. Никаких регрессий.

- [ ] **Step 5: Коммит**

```bash
git add frontend/app/pages/index.vue
git commit -m "♻️ refactor: дашборд использует общий BookingDetailPopup"
```

---

## Task 6: Кликабельные блоки в BookingCalendar

**Files:**
- Modify: `frontend/app/components/booking/BookingCalendar.vue`

- [ ] **Step 1: Добавить emit `booking-click` в defineEmits**

В файле `frontend/app/components/booking/BookingCalendar.vue` найти блок `defineEmits` (строки 26-29):

```ts
const emit = defineEmits<{
  'update:startTime': [value: string]
  'update:endTime': [value: string]
}>()
```

и заменить на:

```ts
const emit = defineEmits<{
  'update:startTime': [value: string]
  'update:endTime': [value: string]
  'booking-click': [payload: {
    booking: { title: string; user_name: string; start_time: string; end_time: string }
    x: number
    y: number
  }]
}>()
```

- [ ] **Step 2: Добавить обработчик клика по блоку брони**

В том же файле, после функции `handleMouseLeave` (после строки 262), добавить новую функцию:

```ts
// Клик / тап по блоку существующего бронирования.
// Защита: не срабатывает во время drag и сразу после (justDragged).
// stopPropagation критичен — иначе handleTimelineClick тоже сработает,
// а также document listener в BookingDetailPopup закроет попап.
function handleBookingBlockClick(block: typeof bookingBlocks.value[number], e: MouseEvent) {
  if (dragging.value || justDragged) return
  e.stopPropagation()
  emit('booking-click', {
    booking: {
      title: block.title,
      user_name: block.user_name,
      start_time: block.start_time,
      end_time: block.end_time,
    },
    x: e.clientX,
    y: e.clientY,
  })
}

function handleBookingBlockTouch(block: typeof bookingBlocks.value[number], e: TouchEvent) {
  if (dragging.value || justDragged) return
  const touch = e.changedTouches[0]
  if (!touch) return
  e.stopPropagation()
  emit('booking-click', {
    booking: {
      title: block.title,
      user_name: block.user_name,
      start_time: block.start_time,
      end_time: block.end_time,
    },
    x: touch.clientX,
    y: touch.clientY,
  })
}
```

- [ ] **Step 3: Сделать блоки бронирований кликабельными в шаблоне**

В том же файле найти блок в `<template>` (строки 316-332):

```vue
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
```

и заменить на:

```vue
<!-- Блоки существующих бронирований (кликабельные — показывают попап) -->
<div
  v-for="(block, i) in bookingBlocks"
  :key="i"
  class="absolute top-1 bottom-1 rounded-md bg-muted border border-border/80 flex items-center overflow-hidden cursor-pointer hover:bg-muted/80 hover:border-border transition-colors z-10"
  :style="{ left: block.left + '%', width: block.width + '%' }"
  @click="handleBookingBlockClick(block, $event)"
  @touchend.prevent="handleBookingBlockTouch(block, $event)"
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
```

**Ключевые отличия:**
- Убран `pointer-events-none`.
- Добавлен `cursor-pointer`.
- Добавлен `hover:bg-muted/80 hover:border-border transition-colors` — визуальная обратная связь.
- Добавлены обработчики `@click` и `@touchend.prevent`.

- [ ] **Step 4: Коммит**

```bash
git add frontend/app/components/booking/BookingCalendar.vue
git commit -m "✨ feat: BookingCalendar — клик по блоку брони эмитит booking-click"
```

---

## Task 7: Интеграция попапа в BookingForm + E2E

**Files:**
- Modify: `frontend/app/components/booking/BookingForm.vue`

- [ ] **Step 1: Добавить state для активной брони**

В файле `frontend/app/components/booking/BookingForm.vue`, в `<script setup>`, после строки `const success = ref(false)` (строка 17), добавить:

```ts
// Активный попап деталей занятой брони.
// Открывается при клике на блок бронирования в BookingCalendar.
const activeBooking = ref<{
  booking: { title: string; user_name: string; start_time: string; end_time: string }
  x: number
  y: number
} | null>(null)

// Обработчик клика по чужой брони — показывает попап
// (позиционирование — по координатам курсора).
function onBookingClick(payload: { booking: any; x: number; y: number }) {
  activeBooking.value = payload
}
```

- [ ] **Step 2: Подключить обработчик и попап в шаблоне**

В том же файле найти `<BookingCalendar>` (строки 138-145):

```vue
<BookingCalendar
  :slots="slots"
  :bookings="bookings"
  :start-time="startTime"
  :end-time="endTime"
  @update:start-time="startTime = $event"
  @update:end-time="endTime = $event"
/>
```

и заменить на:

```vue
<BookingCalendar
  :slots="slots"
  :bookings="bookings"
  :start-time="startTime"
  :end-time="endTime"
  @update:start-time="startTime = $event"
  @update:end-time="endTime = $event"
  @booking-click="onBookingClick"
/>

<!-- Попап деталей занятой брони (без названия комнаты — мы уже на странице комнаты) -->
<BookingDetailPopup
  :booking="activeBooking?.booking ?? null"
  :x="activeBooking?.x ?? 0"
  :y="activeBooking?.y ?? 0"
  @close="activeBooking = null"
/>
```

- [ ] **Step 3: E2E — попап на форме бронирования через Chrome DevTools MCP**

Предусловие: брони «Стендап команды» на Альфе и «Демо продукта» на Бете уже созданы (в Task 5 step 4).

Сценарий:
1. Логин под `admin@company.com` / `admin123` (чтобы попап показывал чужую бронь).
2. Перейти на `http://localhost:3000/rooms/<id-Альфы>` (найти id через UI — клик по карточке Альфы на `/rooms`).
3. На странице видна форма «Забронировать Альфа» с `BookingCalendar` внутри.
4. Убедиться, что дата — сегодня. На таймлайне виден занятый блок «Стендап команды».
5. Клик по блоку. `take_screenshot`.
   - **Expected:** попап открыт, содержит: `Стендап команды`, `Мария Иванова`, `10:00:00 – 11:00:00`. **Нет** названия комнаты.
6. Клик в пустое место вне попапа → попап закрывается. `take_screenshot`.
7. Клик снова по блоку → попап. Нажать Escape → попап закрывается.
8. Клик по ПУСТОЙ области таймлайна (например, 13:00) → выделение создаётся, попап НЕ открывается. `take_screenshot` с выделением.
9. Попробовать drag-resize правой ручки выделения → тянуть, отпустить рядом с «Стендап команды» → выделение не перекрывает блок, попап НЕ открывается после отпускания drag. Это проверка на `justDragged`.

Expected:
- Попап открывается только по клику на блок брони.
- Закрывается по клику вне и по Escape.
- Drag-выделение свободных слотов работает, как раньше.
- Попап без названия комнаты.

- [ ] **Step 4: E2E — мобильный viewport (touch)**

Сценарий:
1. `mcp__plugin_chrome-devtools-mcp__chrome-devtools__emulate` → iPhone или любой мобильный viewport.
2. Перезагрузить страницу `/rooms/<id-Альфы>`.
3. Тап по блоку «Стендап команды» → попап открывается в правильной позиции.
4. `take_screenshot`.
5. Тап вне попапа → закрывается.

Expected: touch работает идентично клику.

- [ ] **Step 5: Коммит**

```bash
git add frontend/app/components/booking/BookingForm.vue
git commit -m "✨ feat: попап деталей брони на форме бронирования переговорки"
```

---

## Task 8: Финальный прогон и impeccable review

**Files:** (никаких модификаций, только тесты)

- [ ] **Step 1: Полный регрессионный прогон**

Быстрая проверка всех изменённых точек:

1. `http://localhost:3000/` — дашборд, попап работает, содержит имя комнаты.
2. `http://localhost:3000/rooms` — бейджи оборудования на карточках не сломались.
3. `http://localhost:3000/rooms/<id>` — форма бронирования, попап работает, без имени комнаты.
4. `http://localhost:3000/admin/rooms` — диалог создания/редактирования содержит EquipmentPicker, сохраняет корректно.

`take_screenshot` на каждом шаге.

- [ ] **Step 2: Собрать финальные скриншоты для impeccable**

Нужны три ключевых скриншота:

1. `/rooms/<id>` с открытым попапом занятой брони.
2. `/` с открытым попапом брони (видно, что название комнаты показано).
3. `/admin/rooms` с открытым диалогом редактирования и отмеченными чекбоксами.

Сохранить в `docs/screenshots/` с именами:
- `booking-form-popup-<дата>.png`
- `dashboard-popup-<дата>.png`
- `admin-equipment-picker-<дата>.png`

- [ ] **Step 3: Прогнать impeccable critique**

Run: Вызвать skill `impeccable:critique` с указанием на собранные скриншоты.

Expected: отчёт о визуальных проблемах. Если проблемы критические — открыть отдельную задачу / доработать.

- [ ] **Step 4: Коммит скриншотов**

```bash
git add docs/screenshots/
git commit -m "📸 docs: скриншоты BookingDetailPopup и EquipmentPicker"
```

- [ ] **Step 5: Финальная проверка спеки — все критерии приёмки выполнены**

Открыть `docs/superpowers/specs/2026-04-08-booking-timeline-popup-and-equipment-design.md`, пройтись по секции «Критерии приёмки». Каждый пункт должен быть подтверждён либо визуально, либо логически.

Если все галочки стоят — фича готова.

---

## Spec coverage self-review

| Требование из спеки | Задача |
|---|---|
| Клик по занятому блоку в BookingCalendar открывает попап | Task 6 + 7 |
| Попап на форме бронирования без названия комнаты | Task 7 Step 2 |
| Оба попапа используют один компонент BookingDetailPopup | Task 4 + Task 5 + Task 7 |
| Закрытие по клику вне | Task 4 `onDocumentClick` |
| Закрытие по Escape | Task 4 `onKeydown` |
| Регрессия дашборда сохранена | Task 5 + Task 5 Step 4 |
| EquipmentPicker в форме создания комнаты | Task 2 + Task 3 |
| EquipmentPicker в форме редактирования комнаты | Task 3 Step 1 + Step 4 |
| Глубокая копия equipment при edit | Task 3 Step 1 |
| EquipmentBadge и EquipmentPicker используют общий EQUIPMENT_TYPES | Task 1 + Task 2 |
| E2E-тесты через Chrome DevTools MCP | Task 3 + 5 + 7 + 8 |
| Impeccable design review | Task 8 |
| Drag vs click защита | Task 6 Step 2 (`if (dragging.value || justDragged) return`) |
| Touch-поддержка | Task 6 Step 2 `handleBookingBlockTouch` + Task 7 Step 4 |
| `delete newObj[key]` вместо `false` | Task 2 Step 1 `toggle` функция |
