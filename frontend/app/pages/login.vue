<script setup lang="ts">
definePageMeta({ layout: 'auth' })

const { login } = useAuth()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function onSubmit() {
  error.value = ''
  loading.value = true
  try {
    await login(email.value, password.value)
    navigateTo('/')
  } catch (e: any) {
    error.value = e.data?.detail || 'Ошибка входа'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Card class="w-full max-w-md">
    <CardHeader class="text-center">
      <CardTitle class="text-2xl">Вход</CardTitle>
      <CardDescription>Введите email и пароль</CardDescription>
    </CardHeader>
    <CardContent>
      <form @submit.prevent="onSubmit" class="space-y-4">
        <div class="space-y-2">
          <Label for="email">Email</Label>
          <Input id="email" v-model="email" type="email" placeholder="email@company.com" required />
        </div>
        <div class="space-y-2">
          <Label for="password">Пароль</Label>
          <Input id="password" v-model="password" type="password" required />
        </div>
        <p v-if="error" class="text-sm text-destructive">{{ error }}</p>
        <Button type="submit" class="w-full" :disabled="loading">
          {{ loading ? 'Вход...' : 'Войти' }}
        </Button>
      </form>
      <p class="mt-4 text-center text-sm text-muted-foreground">
        Нет аккаунта?
        <NuxtLink to="/register" class="text-primary hover:underline">Зарегистрироваться</NuxtLink>
      </p>
    </CardContent>
  </Card>
</template>
