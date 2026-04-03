<script setup lang="ts">
import {
  LayoutDashboard, DoorOpen, CalendarDays, Building2, Settings, Users, ShieldCheck
} from 'lucide-vue-next'

const { store } = useAuth()
const route = useRoute()

const mainLinks = [
  { to: '/', label: 'Дашборд', icon: LayoutDashboard },
  { to: '/rooms', label: 'Переговорки', icon: DoorOpen },
  { to: '/bookings', label: 'Мои брони', icon: CalendarDays },
]

const managerLinks = [
  { to: '/department', label: 'Брони отдела', icon: Building2 },
]

const adminLinks = [
  { to: '/admin/rooms', label: 'Управление комнатами', icon: DoorOpen },
  { to: '/admin/bookings', label: 'Все брони', icon: CalendarDays },
  { to: '/admin/users', label: 'Пользователи', icon: Users },
  { to: '/admin/settings', label: 'Настройки', icon: Settings },
]
</script>

<template>
  <aside class="w-64 border-r bg-card min-h-screen p-4 flex flex-col">
    <div class="flex items-center gap-2 mb-8 px-2">
      <ShieldCheck class="h-8 w-8 text-primary" />
      <span class="text-lg font-bold">BookRoom</span>
    </div>

    <nav class="flex-1 space-y-1">
      <NuxtLink
        v-for="link in mainLinks"
        :key="link.to"
        :to="link.to"
        class="flex items-center gap-3 px-3 py-2 rounded-md text-sm hover:bg-accent transition-colors"
        :class="{ 'bg-accent text-accent-foreground': route.path === link.to }"
      >
        <component :is="link.icon" class="h-4 w-4" />
        {{ link.label }}
      </NuxtLink>

      <template v-if="store.isManager || store.isAdmin">
        <Separator class="my-4" />
        <div class="px-3 text-xs font-medium text-muted-foreground mb-2">Менеджер</div>
        <NuxtLink
          v-for="link in managerLinks"
          :key="link.to"
          :to="link.to"
          class="flex items-center gap-3 px-3 py-2 rounded-md text-sm hover:bg-accent transition-colors"
          :class="{ 'bg-accent text-accent-foreground': route.path === link.to }"
        >
          <component :is="link.icon" class="h-4 w-4" />
          {{ link.label }}
        </NuxtLink>
      </template>

      <template v-if="store.isAdmin">
        <Separator class="my-4" />
        <div class="px-3 text-xs font-medium text-muted-foreground mb-2">Администратор</div>
        <NuxtLink
          v-for="link in adminLinks"
          :key="link.to"
          :to="link.to"
          class="flex items-center gap-3 px-3 py-2 rounded-md text-sm hover:bg-accent transition-colors"
          :class="{ 'bg-accent text-accent-foreground': route.path === link.to }"
        >
          <component :is="link.icon" class="h-4 w-4" />
          {{ link.label }}
        </NuxtLink>
      </template>
    </nav>
  </aside>
</template>
