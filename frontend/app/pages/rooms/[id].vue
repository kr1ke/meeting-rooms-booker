<script setup lang="ts">
import { ArrowLeft, MapPin, Users, AlertCircle } from 'lucide-vue-next'

definePageMeta({ middleware: ['auth'] })

const route = useRoute()
const { fetchRoom } = useRooms()

const room = ref<any>(null)
const loading = ref(true)
const error = ref('')

// Динамический тайтл и хлебная крошка
const breadcrumbLabel = useState('roomBreadcrumb', () => '')
useHead({ title: computed(() => breadcrumbLabel.value || 'Переговорка') })

onMounted(async () => {
  try {
    room.value = await fetchRoom(route.params.id as string)
    if (room.value?.name) {
      breadcrumbLabel.value = room.value.name
    }
  } catch (e: any) {
    error.value = e.data?.detail || 'Не удалось загрузить комнату'
  } finally {
    loading.value = false
  }
})

// Сбрасываем при уходе со страницы
onUnmounted(() => {
  breadcrumbLabel.value = ''
})
</script>

<template>
  <div class="animate-fade-in">
    <!-- Кнопка назад -->
    <NuxtLink to="/rooms" class="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors mb-6">
      <ArrowLeft class="h-4 w-4" />
      Назад к комнатам
    </NuxtLink>

    <!-- Спиннер загрузки -->
    <div v-if="loading" class="flex items-center gap-3 text-muted-foreground py-8">
      <div class="h-5 w-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      Загрузка...
    </div>

    <!-- Ошибка -->
    <div v-else-if="error" class="flex items-center gap-3 p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
      <AlertCircle class="h-5 w-5 text-destructive shrink-0" />
      <p class="text-sm text-destructive">{{ error }}</p>
    </div>

    <!-- Содержимое страницы комнаты -->
    <div v-else-if="room" class="space-y-6">
      <!-- Шапка: название + мета + оборудование -->
      <div class="flex items-start justify-between gap-4">
        <div>
          <div class="flex flex-wrap items-center gap-2 sm:gap-3 mb-2">
            <h1 class="text-xl sm:text-2xl font-bold">{{ room.name }}</h1>
            <Badge
              v-if="room.requires_approval"
              class="shrink-0 bg-amber-50 text-amber-700 border border-amber-200 text-xs"
            >
              Требует подтверждения
            </Badge>
          </div>
          <div class="flex flex-wrap items-center gap-3 sm:gap-6 text-sm text-muted-foreground">
            <span class="flex items-center gap-1.5">
              <MapPin class="h-4 w-4 text-primary/70" />
              Этаж {{ room.floor }}
            </span>
            <span class="flex items-center gap-1.5">
              <Users class="h-4 w-4 text-primary/70" />
              до {{ room.capacity }} чел.
            </span>
          </div>
          <div class="flex flex-wrap gap-1.5 mt-3">
            <RoomEquipmentBadge
              v-for="(val, key) in room.equipment"
              :key="key"
              v-show="val"
              :type="String(key)"
            />
          </div>
        </div>
      </div>

      <!-- Форма бронирования (полная ширина — таймлайн не сжимается) -->
      <div class="max-w-2xl">
        <BookingForm :room-id="room.id" :room-name="room.name" />
      </div>
    </div>
  </div>
</template>
