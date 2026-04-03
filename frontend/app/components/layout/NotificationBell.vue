<script setup lang="ts">
import { Bell } from 'lucide-vue-next'

const { fetchNotifications, markAsRead, store } = useNotifications()

const open = ref(false)

onMounted(() => {
  fetchNotifications()
  // Обновлять каждые 30 секунд
  setInterval(fetchNotifications, 30000)
})
</script>

<template>
  <DropdownMenu v-model:open="open">
    <DropdownMenuTrigger as-child>
      <Button variant="ghost" size="icon" class="relative">
        <Bell class="h-5 w-5" />
        <span
          v-if="store.unreadCount > 0"
          class="absolute -top-1 -right-1 bg-primary text-primary-foreground text-xs rounded-full h-5 w-5 flex items-center justify-center"
        >
          {{ store.unreadCount }}
        </span>
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end" class="w-80">
      <div class="p-2 font-semibold text-sm">Уведомления</div>
      <Separator />
      <div v-if="store.items.length === 0" class="p-4 text-sm text-muted-foreground text-center">
        Нет уведомлений
      </div>
      <DropdownMenuItem
        v-for="n in store.items.slice(0, 10)"
        :key="n.id"
        class="flex flex-col items-start gap-1 p-3"
        :class="{ 'opacity-50': n.is_read }"
        @click="markAsRead(n.id)"
      >
        <span class="text-sm">{{ n.message }}</span>
        <span class="text-xs text-muted-foreground">{{ new Date(n.created_at).toLocaleString('ru') }}</span>
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
