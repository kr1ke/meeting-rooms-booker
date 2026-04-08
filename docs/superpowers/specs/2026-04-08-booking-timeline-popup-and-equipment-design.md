# Попап бронирований на BookingCalendar + оборудование в форме комнаты

**Дата:** 2026-04-08
**Статус:** Дизайн согласован
**Скоуп:** фронтенд (Nuxt 3 / Vue 3), без изменений на бэкенде

## Мотивация

В приложении BookRoom сейчас две точки трения:

1. **На странице бронирования переговорки** (`/rooms/:id`) таймлайн `BookingCalendar` показывает занятые слоты, но они некликабельны. Пользователь видит только название встречи в блоке (или обрезанное название, если блок узкий) и не может быстро узнать: кто бронировал, точное время, полное название. На дашборде (`/`) такой попап уже реализован — нужно распространить это поведение на форму бронирования.
2. **В админ-панели** (`/admin/rooms`) при создании или редактировании комнаты нельзя выбрать оборудование. Поле `equipment` присутствует в модели (`backend/app/models/room.py:18`) и отображается на карточках комнат, но в форме его нет — admin вынужден править данные через seed или SQL. Нужно добавить чекбоксы для трёх существующих типов: проектор, доска, видеоконференция.

## Цели

- Клик по занятому блоку в `BookingCalendar` показывает тот же попап, что на дашборде (Teleport, закрытие по клику вне).
- Попап на форме бронирования не дублирует название комнаты (мы уже на странице комнаты).
- Дашборд использует ту же компонентную реализацию попапа (устраняем дублирование).
- Форма создания/редактирования комнаты включает выбор оборудования (три фиксированных типа).
- Единый источник правды для типов оборудования — общая утилита, используется и в пикере, и в бейдже.

## Не-цели

- Расширение списка типов оборудования (только 3 существующих).
- Backend-изменения (API и схемы уже поддерживают `equipment: dict`).
- Произвольный свободный ввод типов оборудования.
- Перепозиционирование попапа при выходе за край экрана (существующее поведение дашборда сохраняем как есть — не регрессия).

## Архитектура

### Новые файлы

#### `frontend/app/utils/equipment.ts`

Источник правды для типов оборудования. Экспортирует:

```ts
import type { Component } from 'vue'
import { Presentation, Monitor, Video } from 'lucide-vue-next'
// Component импортируется как тип, чтобы TS знал о ручке для lucide-иконок

export interface EquipmentType {
  key: string         // идентификатор для JSONB: projector | whiteboard | videoconference
  label: string       // отображаемое название: Проектор
  icon: Component     // lucide-иконка
  badgeClasses: string // Tailwind-классы для EquipmentBadge
}

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

export function getEquipmentType(key: string): EquipmentType | undefined {
  return EQUIPMENT_TYPES.find(t => t.key === key)
}
```

#### `frontend/app/components/booking/BookingDetailPopup.vue`

Презентационный компонент попапа.

**Props:**
```ts
interface Props {
  booking: {
    title: string
    user_name: string
    start_time: string
    end_time: string
  } | null
  roomName?: string  // опционально, не показываем на странице бронирования
  x: number          // клиентские координаты курсора
  y: number
}
```

**Emits:**
- `close` — попап запросил закрытие (по клику вне, по Escape)

**Поведение:**
- Всегда рендерит `<Teleport to="body"><Transition name="fade"><div v-if="booking" ref="popupRef" @click.stop>...</div></Transition></Teleport>`. Div внутри появляется/исчезает по `v-if`.
- При монтировании компонента (`onMounted`) добавляет `document.addEventListener('click', onDocumentClick)` и `document.addEventListener('keydown', onKeydown)`. При размонтировании (`onUnmounted`) удаляет.
- `onDocumentClick` проверяет: `props.booking === null` → игнорировать; `popupRef?.contains(e.target)` → игнорировать (клик внутри); иначе → emit `close`.
- `onKeydown` на Escape — emit `close` (только если `booking !== null`).
- На самом div попапа `@click.stop` — дополнительная страховка от всплытия.
- Позиционирование: `position: fixed; top: (y + 8)px; left: x; transform: translateX(-50%)`.
- Контент: `title` (жирно), `user_name` (UserIcon), `roomName` (DoorOpen) — только если передан, `start_time – end_time` (Clock).
- **Важно:** родительский компонент, открывающий попап, должен сделать `e.stopPropagation()` на исходном клике по блоку — иначе document listener закроет попап тем же кликом, которым он открылся.

#### `frontend/app/components/room/EquipmentPicker.vue`

Выбор оборудования чекбоксами.

**Props:**
```ts
interface Props {
  modelValue: Record<string, boolean>
}
```

**Emits:**
- `update:modelValue` — новый объект equipment (**без** мутации старого).

**Поведение:**
- Итерирует `EQUIPMENT_TYPES`, для каждого типа рендерит строку: чекбокс + иконка + label.
- Чекбокс `checked` = `!!props.modelValue[type.key]`.
- При переключении собирает новый объект:
  - Копия `props.modelValue`.
  - Если включили — `newObj[key] = true`.
  - Если выключили — `delete newObj[key]` (чтобы JSONB оставался компактным, как в seed).
  - `emit('update:modelValue', newObj)`.
- Визуально: вертикальный стек, каждая строка — кликабельная (клик по label переключает чекбокс через `for` или `@click`).

### Изменения в существующих файлах

#### `frontend/app/components/room/EquipmentBadge.vue`
- Удалить локальный `config`.
- Использовать `getEquipmentType(props.type)` из `utils/equipment.ts`.
- Fallback для неизвестного типа — серый бейдж с текстом ключа (оставляем текущее поведение).

#### `frontend/app/components/booking/BookingCalendar.vue`
- Блоки бронирований (строки 316-332): убрать `pointer-events-none`, добавить `cursor-pointer` и `@click` / `@touchend`.
- Добавить emit: `'booking-click': [payload: { booking: BookingBlock, x: number, y: number }]`.
- Обработчик клика:
  ```ts
  function onBookingClick(block: BookingBlock, e: MouseEvent) {
    if (dragging.value || justDragged) return  // защита от drag
    e.stopPropagation()
    emit('booking-click', { booking: block, x: e.clientX, y: e.clientY })
  }
  ```
- Touchend-обработчик: `e.changedTouches[0]` → `clientX/Y`.
- **Важно:** обработчик `handleTimelineClick` (клик по таймлайну) не должен срабатывать одновременно с кликом по блоку. `e.stopPropagation()` уже должно это обеспечить, поскольку блок — дочерний элемент таймлайна.

#### `frontend/app/components/booking/BookingForm.vue`
- Добавить state:
  ```ts
  const activeBooking = ref<{
    booking: { title: string; user_name: string; start_time: string; end_time: string }
    x: number
    y: number
  } | null>(null)
  ```
- В шаблоне:
  ```vue
  <BookingCalendar
    ...
    @booking-click="activeBooking = $event"
  />
  <BookingDetailPopup
    :booking="activeBooking?.booking ?? null"
    :x="activeBooking?.x ?? 0"
    :y="activeBooking?.y ?? 0"
    @close="activeBooking = null"
  />
  ```
- `roomName` не передаём.

#### `frontend/app/pages/index.vue`
- Удалить локальные state `activeBooking` + функции `showBookingDetail` / `hideBookingDetail` + `onMounted`/`onUnmounted` document listener (строки 86-112).
- Удалить inline-`Teleport` попапа (строки 253-276).
- Добавить:
  ```ts
  const activeBooking = ref<{
    booking: { title: string; user_name: string; start_time: string; end_time: string }
    roomName: string
    x: number
    y: number
  } | null>(null)

  function onBookingClick(b, roomName, e) {
    e.stopPropagation()
    activeBooking.value = { booking: b, roomName, x: e.clientX, y: e.clientY }
  }
  ```
- В шаблоне заменить inline-попап на `<BookingDetailPopup :booking="activeBooking?.booking ?? null" :room-name="activeBooking?.roomName" ... @close="activeBooking = null" />`.

#### `frontend/app/pages/admin/rooms.vue`
- В `openEdit` заменить `form.value = { ...room }` на `form.value = { ...room, equipment: { ...room.equipment } }` (глубокая копия equipment, чтобы пикер не мутировал исходный объект).
- В шаблоне диалога добавить секцию:
  ```vue
  <div class="space-y-2">
    <Label>Оборудование</Label>
    <EquipmentPicker v-model="form.equipment" />
  </div>
  ```
- Секция стоит после `requires_approval` и перед кнопкой «Сохранить».

## Data flow

### Попап в BookingCalendar (форма бронирования)

```
Пользователь кликает по блоку брони
  → BookingCalendar.onBookingClick(block, e)
    → e.stopPropagation()
    → emit('booking-click', { booking, x, y })
  → BookingForm получает событие
    → activeBooking.value = { booking, x, y }
  → BookingDetailPopup видит booking !== null
    → рендерит Teleport + Transition
    → регистрирует document click / Escape listeners
Пользователь кликает вне попапа
  → document listener проверяет: target внутри попапа?
    → нет → emit('close')
  → BookingForm: activeBooking.value = null
  → BookingDetailPopup: booking === null → не рендерит
```

### Попап на дашборде

Идентично, только родитель — `pages/index.vue`, и он передаёт `roomName` в пропсы попапа.

### Форма комнаты

```
Admin открывает диалог создания/редактирования
  → form.value.equipment инициализируется ({} или копией room.equipment)
  → EquipmentPicker рендерит чекбоксы по EQUIPMENT_TYPES
  → Пользователь переключает чекбокс
    → EquipmentPicker собирает новый объект (иммутабельно)
    → emit('update:modelValue', newObj)
  → form.value.equipment обновляется
Admin нажимает «Сохранить»
  → onSubmit отправляет form.value на backend
  → backend принимает equipment: dict
```

## Обработка ошибок и edge cases

### Попап

- **Drag vs click:** `BookingCalendar` уже имеет флаги `dragging` и `justDragged`. Обработчик `onBookingClick` проверяет оба и возвращается раньше, если активен drag или только что закончился. Это предотвращает открытие попапа после drag-resize над соседним блоком.
- **Повторный клик по одному блоку:** сначала глобальный listener закроет попап (клик не внутри), затем `onBookingClick` откроет его заново на новой позиции. UX: попап «мигнёт». Если мигание некомфортно — в будущем можно добавить проверку «тот же ли это booking» и не переоткрывать. В первой итерации оставляем как есть (соответствует дашборду).
- **Клик по другому блоку:** те же шаги — глобальный listener закрывает старый, emit открывает новый.
- **Попап на краю экрана:** текущее поведение — `translateX(-50%)`, может частично уходить за край. Не в скоупе (существует на дашборде, не регрессия).
- **Touch:** `@touchend.stop` на блоке брони — аналог клика. Не мешает существующему `@touchend.prevent` на таймлайне, потому что блок — дочерний.
- **Размонтирование BookingForm / index.vue при открытом попапе:** `BookingDetailPopup` размонтируется, его `onUnmounted` снимает listeners. Нет утечек.

### Оборудование

- **Глубокая копия при edit:** без неё пикер через `delete newObj[key]` мутировал бы оригинальный объект в `rooms` массиве. Глубокая копия в `openEdit` устраняет проблему.
- **Пустой equipment:** пустой объект → все чекбоксы отжаты → backend получает `{}`. Валидно.
- **Неизвестные ключи (из БД):** если в БД лежит ключ, которого нет в `EQUIPMENT_TYPES` (например, после миграции), `EquipmentPicker` его не покажет. Такие ключи сохранятся в `form.value.equipment` при копировании, но при emit мы полностью заменяем объект на новый → **неизвестные ключи потеряются**. Для первой итерации это приемлемо: расширение типов — отдельная задача. Если пользователь захочет сохранять неизвестные ключи, это правится одной строчкой (сохранять их как `...rest`). Документируем как known limitation.
- **Отжатие чекбокса:** `delete` вместо `false` — JSONB в БД остаётся компактным, seed-данные тоже используют этот формат.

## Тестирование (chrome devtools MCP)

**Предусловия:**
- `docker compose up -d`, дождаться готовности backend/frontend.
- Seed-данные загружены (5 комнат, пользователи admin / maria / user).

**Тест-план:**

**Подготовка данных:** seed создаёт комнаты (Альфа, Бета, Гамма, Дельта, Эпсилон) и пользователей, но НЕ создаёт бронирования. Для тестов нужно предварительно создать несколько броней на сегодня через UI под разными учётками (например, `maria@company.com` бронирует Альфу с 10:00 до 11:00).

1. **Регрессия дашборда (попап на `/`):**
   - Логин под `user@company.com` / `user123`.
   - Перейти на `/`.
   - Клик по блоку брони (созданной на этапе подготовки) → попап виден, содержит название, автора, **комнату**, время.
   - Клик вне → закрылся.
   - Escape → закрылся.

2. **Попап на форме бронирования (`/rooms/:id`):**
   - Открыть `/rooms/<id>`, форма бронирования видна.
   - Выбрать дату с занятыми слотами.
   - Клик по занятому блоку → попап виден, содержит название, автора, время. **Названия комнаты нет.**
   - Клик вне попапа → закрылся.
   - Drag-resize выделения рядом с занятым блоком → попап НЕ открывается после отпускания мыши.
   - Touch-тап (через эмуляцию мобильного viewport в chrome devtools) → попап открывается.

3. **EquipmentPicker — создание:**
   - Логин под `admin@company.com` / `admin123`.
   - `/admin/rooms` → «Добавить комнату».
   - Заполнить: «Тест», этаж 1, вместимость 4.
   - Отметить «Проектор» и «Доску».
   - Сохранить.
   - Проверить, что в таблице появилась комната.
   - Перейти на `/rooms` → на карточке «Тест» видны бейджи «Проектор» и «Доска».

4. **EquipmentPicker — редактирование:**
   - `/admin/rooms` → «Изменить» для созданной комнаты.
   - Проверить, что чекбоксы «Проектор» и «Доска» уже отмечены.
   - Снять «Доску», отметить «Видеоконференцию».
   - Сохранить.
   - На `/rooms` карточка показывает «Проектор» + «Видеоконференция».

5. **Скриншоты:**
   - `/rooms/<id>` с открытым попапом (чтобы было видно и таймлайн, и попап).
   - `/` с открытым попапом.
   - `/admin/rooms` с открытым диалогом и отмеченными чекбоксами.

6. **Impeccable design review:**
   - Прогнать `impeccable:critique` на скриншотах.
   - Исправить найденные проблемы через `impeccable:polish` / `impeccable:normalize`.

## Риски и допущения

- **Допущение:** список из 3 типов оборудования стабилен. Если появятся новые — расширяется одной строкой в `utils/equipment.ts`.
- **Риск:** при удалении типа оборудования из `EQUIPMENT_TYPES` комнаты, у которых в БД остался этот ключ, потеряют его при первом же редактировании. Сейчас не в скоупе, задокументировано как known limitation.
- **Риск:** Teleport попапа и Transition могут давать мерцание при быстром клике по соседним блокам. Если станет ощутимо — добавим проверку «если активный booking === новый, не переоткрывать».

## Критерии приёмки

- [ ] На форме `/rooms/:id` клик по занятому блоку открывает попап с названием, автором, временем.
- [ ] Попап на форме бронирования НЕ содержит название комнаты.
- [ ] Попап закрывается по клику вне и по Escape.
- [ ] На `/` поведение попапа не изменилось (регрессия).
- [ ] Оба попапа используют один и тот же компонент `BookingDetailPopup`.
- [ ] В `/admin/rooms` форма создания комнаты содержит `EquipmentPicker` с 3 чекбоксами.
- [ ] При редактировании существующей комнаты чекбоксы отражают текущее состояние.
- [ ] Сохранение отправляет корректный объект `equipment` на backend.
- [ ] `EquipmentBadge` и `EquipmentPicker` используют общую утилиту `EQUIPMENT_TYPES`.
- [ ] Все тесты из тест-плана пройдены через Chrome DevTools MCP.
- [ ] Impeccable review пройден или правки применены.
