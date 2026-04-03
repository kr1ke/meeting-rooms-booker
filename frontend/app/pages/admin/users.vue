<script setup lang="ts">
// Страница управления пользователями для администратора
definePageMeta({ middleware: ['auth', 'role'] })

const users = ref<any[]>([])
const departments = ref<any[]>([])
const loading = ref(true)

async function load() {
  loading.value = true
  // Параллельная загрузка пользователей и отделов
  const [u, d] = await Promise.all([
    $fetch<any[]>('/api/users'),
    $fetch<any[]>('/api/departments'),
  ])
  users.value = u
  departments.value = d
  loading.value = false
}

// Обновление данных пользователя (роль или статус активности)
async function updateUser(userId: string, data: any) {
  await $fetch(`/api/users/${userId}`, { method: 'PATCH', body: data })
  await load()
}

onMounted(load)
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Пользователи</h1>

    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Имя</TableHead>
          <TableHead>Email</TableHead>
          <TableHead>Роль</TableHead>
          <TableHead>Статус</TableHead>
          <TableHead>Действия</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow v-for="user in users" :key="user.id">
          <TableCell class="font-medium">{{ user.name }}</TableCell>
          <TableCell>{{ user.email }}</TableCell>
          <TableCell>
            <!-- Выпадающий список для изменения роли пользователя -->
            <Select
              :model-value="user.role"
              @update:model-value="(v: string) => updateUser(user.id, { role: v })"
            >
              <SelectTrigger class="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="employee">Сотрудник</SelectItem>
                <SelectItem value="manager">Менеджер</SelectItem>
                <SelectItem value="admin">Админ</SelectItem>
              </SelectContent>
            </Select>
          </TableCell>
          <TableCell>
            <Badge :variant="user.is_active ? 'default' : 'destructive'">
              {{ user.is_active ? 'Активен' : 'Заблокирован' }}
            </Badge>
          </TableCell>
          <TableCell>
            <Button
              variant="outline" size="sm"
              @click="updateUser(user.id, { is_active: !user.is_active })"
            >
              {{ user.is_active ? 'Заблокировать' : 'Разблокировать' }}
            </Button>
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>
  </div>
</template>
