<script setup lang="ts">
// Страница регистрации нового пользователя
definePageMeta({ layout: 'auth' })

const { register } = useAuth()
const name = ref('')
const email = ref('')
const password = ref('')
const departmentId = ref<string>()
const departments = ref<{ id: string; name: string }[]>([])
const error = ref('')
const loading = ref(false)

// Загрузка списка отделов при монтировании компонента
onMounted(async () => {
  try {
    departments.value = await $fetch('/api/departments')
  } catch {}
})

async function onSubmit() {
  error.value = ''
  loading.value = true
  try {
    await register(email.value, password.value, name.value, departmentId.value)
    navigateTo('/')
  } catch (e: any) {
    error.value = e.data?.detail || 'Ошибка регистрации'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <!-- Форма регистрации без Card-обёртки (правая панель auth-макета выступает карточкой) -->
  <div class="w-full max-w-sm">
    <!-- Заголовок -->
    <div class="mb-8 text-center">
      <h1 class="text-2xl font-semibold text-foreground tracking-tight">
        Создать аккаунт
      </h1>
      <p class="mt-2 text-sm text-muted-foreground">
        Заполните данные для регистрации
      </p>
    </div>

    <!-- Блок ошибки с иконкой и фоном -->
    <div
      v-if="error"
      class="mb-5 flex items-center gap-2.5 rounded-lg bg-destructive/10 border border-destructive/20 px-4 py-3 text-sm text-destructive animate-fade-in"
    >
      <!-- Иконка ошибки -->
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" x2="12" y1="8" y2="12" />
        <line x1="12" x2="12.01" y1="16" y2="16" />
      </svg>
      <span>{{ error }}</span>
    </div>

    <!-- Основная форма -->
    <form @submit.prevent="onSubmit" class="space-y-5">
      <!-- Поле имени -->
      <div class="space-y-2">
        <Label for="name" class="text-sm font-medium">Имя</Label>
        <Input
          id="name"
          v-model="name"
          placeholder="Иван Петров"
          required
          class="h-11 transition-shadow duration-200 focus-visible:ring-2 focus-visible:ring-primary/30"
        />
      </div>

      <!-- Поле Email -->
      <div class="space-y-2">
        <Label for="reg-email" class="text-sm font-medium">Email</Label>
        <Input
          id="reg-email"
          v-model="email"
          type="email"
          placeholder="email@company.com"
          required
          class="h-11 transition-shadow duration-200 focus-visible:ring-2 focus-visible:ring-primary/30"
        />
      </div>

      <!-- Поле пароля -->
      <div class="space-y-2">
        <Label for="reg-password" class="text-sm font-medium">Пароль</Label>
        <Input
          id="reg-password"
          v-model="password"
          type="password"
          placeholder="Минимум 8 символов"
          required
          class="h-11 transition-shadow duration-200 focus-visible:ring-2 focus-visible:ring-primary/30"
        />
      </div>

      <!-- Выбор отдела -->
      <div class="space-y-2">
        <Label for="department" class="text-sm font-medium">Отдел</Label>
        <Select v-model="departmentId">
          <SelectTrigger class="h-11 transition-shadow duration-200 focus:ring-2 focus:ring-primary/30">
            <SelectValue placeholder="Выберите отдел" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem v-for="d in departments" :key="d.id" :value="d.id">
              {{ d.name }}
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <!-- Кнопка регистрации с спиннером загрузки -->
      <Button
        type="submit"
        class="w-full h-11 font-semibold text-base mt-2"
        :disabled="loading"
      >
        <!-- Спиннер при загрузке -->
        <svg
          v-if="loading"
          class="mr-2 h-4 w-4 animate-spin"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
      </Button>
    </form>

    <!-- Ссылка на вход -->
    <p class="mt-6 text-center text-sm text-muted-foreground">
      Уже есть аккаунт?
      <NuxtLink to="/login" class="text-primary font-medium hover:underline">
        Войти
      </NuxtLink>
    </p>
  </div>
</template>
