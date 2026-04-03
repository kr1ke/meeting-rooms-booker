<script setup lang="ts">
definePageMeta({ layout: 'auth' })

const { register } = useAuth()
const name = ref('')
const email = ref('')
const password = ref('')
const departmentId = ref<string>()
const departments = ref<{ id: string; name: string }[]>([])
const error = ref('')
const loading = ref(false)

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
  <Card class="w-full max-w-md">
    <CardHeader class="text-center">
      <CardTitle class="text-2xl">Регистрация</CardTitle>
      <CardDescription>Создайте аккаунт</CardDescription>
    </CardHeader>
    <CardContent>
      <form @submit.prevent="onSubmit" class="space-y-4">
        <div class="space-y-2">
          <Label for="name">Имя</Label>
          <Input id="name" v-model="name" placeholder="Иван Петров" required />
        </div>
        <div class="space-y-2">
          <Label for="reg-email">Email</Label>
          <Input id="reg-email" v-model="email" type="email" placeholder="email@company.com" required />
        </div>
        <div class="space-y-2">
          <Label for="reg-password">Пароль</Label>
          <Input id="reg-password" v-model="password" type="password" required />
        </div>
        <div class="space-y-2">
          <Label for="department">Отдел</Label>
          <Select v-model="departmentId">
            <SelectTrigger>
              <SelectValue placeholder="Выберите отдел" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="d in departments" :key="d.id" :value="d.id">
                {{ d.name }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
        <p v-if="error" class="text-sm text-destructive">{{ error }}</p>
        <Button type="submit" class="w-full" :disabled="loading">
          {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
        </Button>
      </form>
      <p class="mt-4 text-center text-sm text-muted-foreground">
        Уже есть аккаунт?
        <NuxtLink to="/login" class="text-primary hover:underline">Войти</NuxtLink>
      </p>
    </CardContent>
  </Card>
</template>
