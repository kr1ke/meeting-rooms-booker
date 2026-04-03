<script setup lang="ts">
// Страница управления комнатами, доступна только администраторам
definePageMeta({ middleware: ['auth', 'role'] })

const { fetchRooms, createRoom, updateRoom, deleteRoom } = useRooms()
const rooms = ref<any[]>([])
const showDialog = ref(false)
const editingRoom = ref<any>(null)
// Форма создания/редактирования комнаты
const form = ref({ name: '', floor: 1, capacity: 4, equipment: {}, requires_approval: false })
const loading = ref(true)

async function load() {
  loading.value = true
  rooms.value = await fetchRooms()
  loading.value = false
}

function openCreate() {
  editingRoom.value = null
  form.value = { name: '', floor: 1, capacity: 4, equipment: {}, requires_approval: false }
  showDialog.value = true
}

function openEdit(room: any) {
  editingRoom.value = room
  form.value = { ...room }
  showDialog.value = true
}

// Сохранение: создание или обновление в зависимости от режима
async function onSubmit() {
  if (editingRoom.value) {
    await updateRoom(editingRoom.value.id, form.value)
  } else {
    await createRoom(form.value)
  }
  showDialog.value = false
  await load()
}

async function onDelete(id: string) {
  await deleteRoom(id)
  await load()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Управление комнатами</h1>
      <Button @click="openCreate">Добавить комнату</Button>
    </div>

    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Название</TableHead>
          <TableHead>Этаж</TableHead>
          <TableHead>Вместимость</TableHead>
          <TableHead>Подтверждение</TableHead>
          <TableHead>Действия</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow v-for="room in rooms" :key="room.id">
          <TableCell class="font-medium">{{ room.name }}</TableCell>
          <TableCell>{{ room.floor }}</TableCell>
          <TableCell>{{ room.capacity }}</TableCell>
          <TableCell>
            <Badge :variant="room.requires_approval ? 'default' : 'secondary'">
              {{ room.requires_approval ? 'Да' : 'Нет' }}
            </Badge>
          </TableCell>
          <TableCell>
            <div class="flex gap-2">
              <Button variant="outline" size="sm" @click="openEdit(room)">Изменить</Button>
              <Button variant="destructive" size="sm" @click="onDelete(room.id)">Удалить</Button>
            </div>
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>

    <!-- Диалог создания/редактирования комнаты -->
    <Dialog v-model:open="showDialog">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{{ editingRoom ? 'Редактировать' : 'Создать' }} комнату</DialogTitle>
        </DialogHeader>
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
            <input type="checkbox" id="approval" v-model="form.requires_approval" />
            <Label for="approval">Требует подтверждения</Label>
          </div>
          <Button type="submit" class="w-full">Сохранить</Button>
        </form>
      </DialogContent>
    </Dialog>
  </div>
</template>
