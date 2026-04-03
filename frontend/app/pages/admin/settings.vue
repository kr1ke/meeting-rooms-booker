<script setup lang="ts">
// Страница настроек бронирования для администратора
definePageMeta({ middleware: ['auth', 'role'] })

// Настройки системы бронирования
const form = ref({
  max_duration_minutes: 120,
  max_days_ahead: 14,
  min_minutes_before_start: 15,
})
const loading = ref(true)
const saved = ref(false)

// Загружаем текущие настройки при монтировании
onMounted(async () => {
  const data = await $fetch<any>('/api/settings')
  form.value = data
  loading.value = false
})

async function onSubmit() {
  await $fetch('/api/settings', { method: 'PUT', body: form.value })
  saved.value = true
  // Скрываем сообщение об успехе через 3 секунды
  setTimeout(() => (saved.value = false), 3000)
}
</script>

<template>
  <div class="max-w-lg">
    <h1 class="text-2xl font-bold mb-6">Настройки бронирования</h1>

    <Card>
      <CardContent class="pt-6">
        <form @submit.prevent="onSubmit" class="space-y-4">
          <div class="space-y-2">
            <Label>Максимальная длительность (минуты)</Label>
            <Input v-model.number="form.max_duration_minutes" type="number" min="15" />
          </div>
          <div class="space-y-2">
            <Label>Горизонт бронирования (дней вперёд)</Label>
            <Input v-model.number="form.max_days_ahead" type="number" min="1" />
          </div>
          <div class="space-y-2">
            <Label>Минимум минут до начала встречи</Label>
            <Input v-model.number="form.min_minutes_before_start" type="number" min="0" />
          </div>
          <Button type="submit" class="w-full">Сохранить</Button>
          <p v-if="saved" class="text-sm text-green-600 text-center">Настройки сохранены</p>
        </form>
      </CardContent>
    </Card>
  </div>
</template>
