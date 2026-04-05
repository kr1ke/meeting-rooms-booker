<script setup lang="ts">
import { Plus } from 'lucide-vue-next'

// Страница управления комнатами, доступна только администраторам
definePageMeta({ middleware: ['auth', 'role'] })
useHead({ title: 'Управление комнатами' })

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
  <div class="animate-fade-in">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold">Управление комнатами</h1>
        <p class="text-muted-foreground text-sm mt-1">Добавляйте и редактируйте переговорки</p>
      </div>
      <Button @click="openCreate" class="gap-2 font-semibold w-full sm:w-auto">
        <Plus class="h-4 w-4" />
        Добавить комнату
      </Button>
    </div>

    <Card class="shadow-sm border-0 overflow-x-auto">
      <Table class="min-w-[600px]">
        <TableHeader>
          <TableRow class="hover:bg-transparent">
            <TableHead class="font-semibold">Название</TableHead>
            <TableHead class="font-semibold">Этаж</TableHead>
            <TableHead class="font-semibold">Вместимость</TableHead>
            <TableHead class="font-semibold">Подтверждение</TableHead>
            <TableHead class="font-semibold text-right">Действия</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-for="room in rooms" :key="room.id" class="hover:bg-primary/5">
            <TableCell class="font-medium">{{ room.name }}</TableCell>
            <TableCell>{{ room.floor }}</TableCell>
            <TableCell>{{ room.capacity }}</TableCell>
            <TableCell>
              <Badge :class="room.requires_approval
                ? 'bg-amber-50 text-amber-700 border border-amber-200'
                : 'bg-emerald-50 text-emerald-700 border border-emerald-200'">
                {{ room.requires_approval ? 'Да' : 'Нет' }}
              </Badge>
            </TableCell>
            <TableCell class="text-right">
              <div class="flex gap-2 justify-end">
                <Button variant="outline" size="sm" @click="openEdit(room)">Изменить</Button>
                <Button variant="destructive" size="sm" @click="onDelete(room.id)">Удалить</Button>
              </div>
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </Card>

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
            <input type="checkbox" id="approval" v-model="form.requires_approval" class="rounded border-input" />
            <Label for="approval">Требует подтверждения</Label>
          </div>
          <Button type="submit" class="w-full font-semibold">Сохранить</Button>
        </form>
      </DialogContent>
    </Dialog>
  </div>
</template>
