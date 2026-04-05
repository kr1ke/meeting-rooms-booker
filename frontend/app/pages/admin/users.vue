<script setup lang="ts">
import { Plus } from 'lucide-vue-next'

// Страница управления пользователями для администратора
definePageMeta({ middleware: ['auth', 'role'] })
useHead({ title: 'Пользователи' })

const users = ref<any[]>([])
const departments = ref<any[]>([])
const loading = ref(true)

// Пользователь, ожидающий подтверждения блокировки
const blockTarget = ref<any>(null)

// Форма добавления пользователя
const showAddDialog = ref(false)
const newUser = ref({ name: '', email: '', password: '', role: 'employee', department_id: '' })
const addError = ref('')
const addLoading = ref(false)

async function load() {
  loading.value = true
  users.value = await $fetch<any[]>('/api/users')
  loading.value = false
}

async function addUser() {
  addError.value = ''
  if (!newUser.value.name || !newUser.value.email || !newUser.value.password) {
    addError.value = 'Заполните все обязательные поля'
    return
  }
  addLoading.value = true
  try {
    await $fetch('/api/users', {
      method: 'POST',
      body: {
        ...newUser.value,
        department_id: newUser.value.department_id || null,
      },
    })
    showAddDialog.value = false
    newUser.value = { name: '', email: '', password: '', role: 'employee', department_id: '' }
    await load()
  } catch (e: any) {
    addError.value = e?.data?.detail || 'Ошибка создания пользователя'
  } finally {
    addLoading.value = false
  }
}

// Обновление роли (без подтверждения)
async function updateRole(userId: string, role: string) {
  await $fetch(`/api/users/${userId}`, { method: 'PATCH', body: { role } })
  await load()
}

// Показать диалог подтверждения блокировки
function onToggleBlock(user: any) {
  blockTarget.value = user
}

// Подтвердить блокировку/разблокировку (сохраняем данные до сброса — гонка с @update:open)
async function confirmToggleBlock() {
  const target = blockTarget.value
  blockTarget.value = null
  if (!target) return
  await $fetch(`/api/users/${target.id}`, {
    method: 'PATCH',
    body: { is_active: !target.is_active },
  })
  await load()
}

onMounted(async () => {
  await load()
  departments.value = await $fetch<any[]>('/api/departments').catch(() => [])
})
</script>

<template>
  <div class="animate-fade-in">
    <div class="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold">Пользователи</h1>
        <p class="text-muted-foreground text-sm mt-1">Управление ролями и доступом</p>
      </div>
      <Button @click="showAddDialog = true" class="gap-2 w-full sm:w-auto">
        <Plus class="h-4 w-4" />
        Добавить пользователя
      </Button>
    </div>

    <Card class="shadow-none border overflow-x-auto">
      <Table class="min-w-[640px]">
        <TableHeader>
          <TableRow class="hover:bg-transparent">
            <TableHead class="font-semibold">Имя</TableHead>
            <TableHead class="font-semibold">Email</TableHead>
            <TableHead class="font-semibold">Роль</TableHead>
            <TableHead class="font-semibold">Статус</TableHead>
            <TableHead class="font-semibold text-right">Действия</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-for="user in users" :key="user.id" class="hover:bg-primary/5">
            <TableCell class="font-medium">{{ user.name }}</TableCell>
            <TableCell class="text-muted-foreground">{{ user.email }}</TableCell>
            <TableCell>
              <Select
                :model-value="user.role"
                @update:model-value="(v: string) => updateRole(user.id, v)"
              >
                <SelectTrigger class="w-36">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="employee">Сотрудник</SelectItem>
                  <SelectItem value="admin">Админ</SelectItem>
                </SelectContent>
              </Select>
            </TableCell>
            <TableCell>
              <Badge :class="user.is_active
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                : 'bg-red-50 text-red-700 border border-red-200'">
                {{ user.is_active ? 'Активен' : 'Заблокирован' }}
              </Badge>
            </TableCell>
            <TableCell class="text-right">
              <Button
                variant="outline" size="sm"
                @click="onToggleBlock(user)"
              >
                {{ user.is_active ? 'Заблокировать' : 'Разблокировать' }}
              </Button>
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </Card>

    <!-- Диалог подтверждения блокировки -->
    <AlertDialog :open="!!blockTarget" @update:open="blockTarget = null">
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>
            {{ blockTarget?.is_active ? 'Заблокировать пользователя?' : 'Разблокировать пользователя?' }}
          </AlertDialogTitle>
          <AlertDialogDescription>
            {{ blockTarget?.name }} ({{ blockTarget?.email }})
            {{ blockTarget?.is_active ? 'не сможет входить в систему и бронировать комнаты.' : 'снова получит доступ к системе.' }}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel @click="blockTarget = null">Отмена</AlertDialogCancel>
          <Button
            :class="blockTarget?.is_active
              ? 'bg-destructive text-destructive-foreground hover:bg-destructive/90'
              : 'bg-primary text-primary-foreground hover:bg-primary/90'"
            @click="confirmToggleBlock"
          >
            {{ blockTarget?.is_active ? 'Заблокировать' : 'Разблокировать' }}
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
    <!-- Диалог добавления пользователя -->
    <AlertDialog :open="showAddDialog" @update:open="showAddDialog = false">
      <AlertDialogContent class="max-w-md">
        <AlertDialogHeader>
          <AlertDialogTitle>Новый пользователь</AlertDialogTitle>
          <AlertDialogDescription>Заполните данные для создания аккаунта</AlertDialogDescription>
        </AlertDialogHeader>

        <div class="space-y-4 py-2">
          <div>
            <label class="text-sm font-medium mb-1.5 block">Имя *</label>
            <Input v-model="newUser.name" placeholder="Иван Иванов" />
          </div>
          <div>
            <label class="text-sm font-medium mb-1.5 block">Email *</label>
            <Input v-model="newUser.email" type="email" placeholder="user@company.com" />
          </div>
          <div>
            <label class="text-sm font-medium mb-1.5 block">Пароль *</label>
            <Input v-model="newUser.password" type="password" placeholder="Минимум 6 символов" />
          </div>
          <div>
            <label class="text-sm font-medium mb-1.5 block">Роль</label>
            <Select v-model="newUser.role">
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="employee">Сотрудник</SelectItem>
                <SelectItem value="admin">Админ</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <label class="text-sm font-medium mb-1.5 block">Отдел</label>
            <Select v-model="newUser.department_id">
              <SelectTrigger>
                <SelectValue placeholder="Не указан" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="d in departments" :key="d.id" :value="d.id">
                  {{ d.name }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <p v-if="addError" class="text-sm text-destructive">{{ addError }}</p>
        </div>

        <AlertDialogFooter>
          <AlertDialogCancel @click="showAddDialog = false">Отмена</AlertDialogCancel>
          <Button @click="addUser" :disabled="addLoading">
            {{ addLoading ? 'Создание...' : 'Создать' }}
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  </div>
</template>
