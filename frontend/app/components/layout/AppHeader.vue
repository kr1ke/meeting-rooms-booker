<script setup lang="ts">
import { LogOut, ChevronRight, Menu } from 'lucide-vue-next'

const { logout, store } = useAuth()
const route = useRoute()
const roomBreadcrumb = useState('roomBreadcrumb', () => '')
const sidebarOpen = useState('sidebarOpen', () => false)

// Карта путей → человекопонятных названий
const routeLabels: Record<string, string> = {
  '/': 'Дашборд',
  '/rooms': 'Переговорки',
  '/bookings': 'Мои брони',
  '/admin/rooms': 'Комнаты',
  '/admin/bookings': 'Все брони',
  '/admin/users': 'Пользователи',
  '/admin/settings': 'Настройки',
  '/login': 'Вход',
  '/register': 'Регистрация',
}

// Хлебные крошки из текущего маршрута
const breadcrumbs = computed(() => {
  const path = route.path
  const crumbs: { label: string; to?: string }[] = []

  if (path.startsWith('/admin/')) {
    crumbs.push({ label: 'Админ' })
    crumbs.push({ label: routeLabels[path] || path.split('/').pop() || '' })
  } else if (path.startsWith('/rooms/') && path !== '/rooms') {
    crumbs.push({ label: 'Переговорки', to: '/rooms' })
    crumbs.push({ label: roomBreadcrumb.value || 'Загрузка...' })
  } else {
    crumbs.push({ label: routeLabels[path] || path })
  }

  return crumbs
})

// Текущая дата
const _now = new Date()
const formattedDate = _now.toLocaleDateString('ru', {
  weekday: 'short',
  day: 'numeric',
  month: 'long',
})
</script>

<template>
  <header class="h-14 border-b bg-background px-3 sm:px-6 flex items-center justify-between sticky top-0 z-10">
    <!-- Левая часть — гамбургер (мобильный) + хлебные крошки + дата -->
    <div class="flex items-center gap-2 sm:gap-4 min-w-0">
      <!-- Гамбургер для мобильных -->
      <button
        class="lg:hidden h-9 w-9 flex items-center justify-center rounded-lg text-muted-foreground hover:bg-muted hover:text-foreground transition-colors shrink-0"
        @click="sidebarOpen = !sidebarOpen"
      >
        <Menu class="h-5 w-5" />
      </button>

      <!-- Хлебные крошки -->
      <nav class="flex items-center gap-1 text-sm min-w-0">
        <template v-for="(crumb, i) in breadcrumbs" :key="i">
          <ChevronRight v-if="i > 0" class="h-3.5 w-3.5 text-muted-foreground/40 shrink-0" />
          <NuxtLink
            v-if="crumb.to"
            :to="crumb.to"
            class="text-muted-foreground hover:text-foreground transition-colors shrink-0"
          >
            {{ crumb.label }}
          </NuxtLink>
          <span
            v-else
            class="font-medium truncate"
            :class="i === breadcrumbs.length - 1 ? 'text-foreground' : 'text-muted-foreground'"
          >
            {{ crumb.label }}
          </span>
        </template>
      </nav>

      <span class="text-muted-foreground/30 hidden sm:inline">·</span>

      <!-- Текущая дата -->
      <span class="text-xs text-muted-foreground/60 tabular-nums hidden sm:inline">{{ formattedDate }}</span>
    </div>

    <!-- Правая часть — уведомления + профиль -->
    <div class="flex items-center gap-2 sm:gap-3 shrink-0">
      <LayoutNotificationBell />

      <div class="w-px h-8 bg-border hidden sm:block" />

      <DropdownMenu>
        <DropdownMenuTrigger as-child>
          <Button variant="ghost" class="flex items-center gap-2 rounded-lg hover:bg-primary/5 px-2 sm:px-3">
            <Avatar class="h-8 w-8 bg-transparent">
              <AvatarFallback class="text-sm font-semibold bg-primary/10 text-primary">
                {{ store.user?.name?.charAt(0) }}
              </AvatarFallback>
            </Avatar>
            <span class="text-sm font-medium hidden sm:inline">{{ store.user?.name }}</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" class="w-48">
          <DropdownMenuItem @click="logout" class="text-destructive cursor-pointer">
            <LogOut class="h-4 w-4 mr-2" />
            Выйти
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  </header>
</template>
