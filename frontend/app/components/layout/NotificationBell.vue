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
      <Button variant="ghost" size="icon" class="relative rounded-lg hover:bg-primary/5">
        <Bell class="h-5 w-5 text-muted-foreground" />
        <!-- Счётчик непрочитанных уведомлений -->
        <span
          v-if="store.unreadCount > 0"
          class="absolute -top-0.5 -right-0.5 bg-primary text-primary-foreground text-[10px] font-bold rounded-full h-4.5 w-4.5 min-w-[18px] flex items-center justify-center shadow-sm"
        >
          {{ store.unreadCount }}
        </span>
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end" class="w-80 shadow-lg">
      <div class="px-3 py-2.5 font-semibold text-sm">Уведомления</div>
      <Separator />
      <div v-if="store.items.length === 0" class="p-6 text-sm text-muted-foreground text-center">
        Нет уведомлений
      </div>
      <DropdownMenuItem
        v-for="n in store.items.slice(0, 10)"
        :key="n.id"
        class="flex flex-col items-start gap-1 p-3 cursor-pointer"
        :class="n.is_read ? 'opacity-50' : 'bg-primary/5'"
        @click="markAsRead(n.id)"
      >
        <span class="text-sm leading-snug">{{ n.message }}</span>
        <span class="text-xs text-muted-foreground">{{ new Date(n.created_at).toLocaleString('ru') }}</span>
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
