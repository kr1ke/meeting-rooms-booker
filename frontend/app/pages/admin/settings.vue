<script setup lang="ts">
import { CheckCircle } from 'lucide-vue-next'

// Страница настроек бронирования для администратора
definePageMeta({ middleware: ['auth', 'role'] })
useHead({ title: 'Настройки' })

const form = ref({
  max_duration_minutes: 120,
  max_days_ahead: 14,
  min_minutes_before_start: 15,
})
const loading = ref(true)
const saved = ref(false)

onMounted(async () => {
  const data = await $fetch<any>('/api/settings')
  form.value = data
  loading.value = false
})

async function onSubmit() {
  await $fetch('/api/settings', { method: 'PUT', body: form.value })
  saved.value = true
  setTimeout(() => (saved.value = false), 3000)
}
</script>

<template>
  <div class="animate-fade-in max-w-xl">
    <div class="mb-8">
      <h1 class="text-2xl font-bold">Настройки</h1>
      <p class="text-muted-foreground text-sm mt-1">Правила и ограничения бронирования</p>
    </div>

    <form @submit.prevent="onSubmit" class="space-y-8">
      <!-- Секция: Длительность -->
      <div>
        <div class="mb-3">
          <h3 class="text-sm font-semibold">Максимальная длительность</h3>
          <p class="text-xs text-muted-foreground mt-0.5">Лимит продолжительности одного бронирования</p>
        </div>
        <div class="flex items-center gap-3">
          <Input v-model.number="form.max_duration_minutes" type="number" min="15" class="w-28" />
          <span class="text-sm text-muted-foreground">минут</span>
        </div>
      </div>

      <Separator />

      <!-- Секция: Горизонт -->
      <div>
        <div class="mb-3">
          <h3 class="text-sm font-semibold">Горизонт бронирования</h3>
          <p class="text-xs text-muted-foreground mt-0.5">На сколько дней вперёд можно бронировать</p>
        </div>
        <div class="flex items-center gap-3">
          <Input v-model.number="form.max_days_ahead" type="number" min="1" class="w-28" />
          <span class="text-sm text-muted-foreground">дней</span>
        </div>
      </div>

      <Separator />

      <!-- Секция: Минимальное время -->
      <div>
        <div class="mb-3">
          <h3 class="text-sm font-semibold">Минимальное время до начала</h3>
          <p class="text-xs text-muted-foreground mt-0.5">За сколько минут до встречи ещё можно забронировать</p>
        </div>
        <div class="flex items-center gap-3">
          <Input v-model.number="form.min_minutes_before_start" type="number" min="0" class="w-28" />
          <span class="text-sm text-muted-foreground">минут</span>
        </div>
      </div>

      <div class="flex items-center gap-3 pt-2">
        <Button type="submit" class="font-semibold">Сохранить настройки</Button>
        <!-- Уведомление об успешном сохранении -->
        <div v-if="saved" class="flex items-center gap-1.5 text-sm text-emerald-600">
          <CheckCircle class="h-4 w-4" />
          Сохранено
        </div>
      </div>
    </form>
  </div>
</template>
