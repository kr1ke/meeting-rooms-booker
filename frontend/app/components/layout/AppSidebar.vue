<script setup lang="ts">
import {
  LayoutDashboard, DoorOpen, CalendarDays, Settings, Users, Bookmark, Plus, X
} from 'lucide-vue-next'

const { store } = useAuth()
const route = useRoute()
const sidebarOpen = useState('sidebarOpen', () => false)

const mainLinks = [
  { to: '/', label: 'Дашборд', icon: LayoutDashboard },
  { to: '/rooms', label: 'Переговорки', icon: DoorOpen },
  { to: '/bookings', label: 'Мои брони', icon: CalendarDays },
]

const adminLinks = [
  { to: '/admin/rooms', label: 'Управление комнатами', icon: DoorOpen },
  { to: '/admin/bookings', label: 'Все брони', icon: CalendarDays },
  { to: '/admin/users', label: 'Пользователи', icon: Users },
  { to: '/admin/settings', label: 'Настройки', icon: Settings },
]

function isActive(path: string) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

// Закрытие при переходе на новую страницу
watch(() => route.path, () => {
  sidebarOpen.value = false
})
</script>

<template>
  <!-- Оверлей для мобильных -->
  <Transition name="fade">
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 bg-black/40 z-40 lg:hidden"
      @click="sidebarOpen = false"
    />
  </Transition>

  <aside
    class="w-64 h-screen fixed top-0 left-0 p-4 flex flex-col sidebar-bg overflow-y-auto z-50 transition-transform duration-200 ease-out"
    :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'"
  >
    <!-- Логотип + кнопка закрытия (мобильная) -->
    <div class="flex items-center justify-between mb-6 px-3 pt-2">
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-xl bg-white/10 flex items-center justify-center">
          <Bookmark class="h-5 w-5 text-orange-300" />
        </div>
        <span class="text-lg font-bold text-white tracking-tight">
          BookRoom
        </span>
      </div>
      <button
        class="lg:hidden h-8 w-8 flex items-center justify-center rounded-lg text-white/50 hover:text-white hover:bg-white/10 transition-colors"
        @click="sidebarOpen = false"
      >
        <X class="h-5 w-5" />
      </button>
    </div>

    <!-- CTA — бронирование -->
    <NuxtLink
      to="/rooms"
      class="flex items-center justify-center gap-2 mx-1 mb-5 px-4 py-2.5 rounded-lg bg-primary text-white text-sm font-semibold transition-all duration-150 hover:brightness-110 active:scale-[0.98]"
    >
      <Plus class="h-4 w-4" />
      Забронировать
    </NuxtLink>

    <!-- Навигация -->
    <nav class="flex-1 space-y-1">
      <NuxtLink
        v-for="link in mainLinks"
        :key="link.to"
        :to="link.to"
        class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150"
        :class="isActive(link.to)
          ? 'bg-white/15 text-white'
          : 'text-white/60 hover:text-white hover:bg-white/8'"
      >
        <component :is="link.icon" class="h-[18px] w-[18px]" />
        {{ link.label }}
      </NuxtLink>

      <!-- Администратор -->
      <template v-if="store.isAdmin">
        <div class="mt-10 mb-4 mx-3 border-t border-white/10 pt-2" />
        <div class="px-3 text-[11px] font-semibold text-white/35 uppercase tracking-wider mb-2">
          Администратор
        </div>
        <NuxtLink
          v-for="link in adminLinks"
          :key="link.to"
          :to="link.to"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150"
          :class="isActive(link.to)
            ? 'bg-white/15 text-white'
            : 'text-white/60 hover:text-white hover:bg-white/8'"
        >
          <component :is="link.icon" class="h-[18px] w-[18px]" />
          {{ link.label }}
        </NuxtLink>
      </template>
    </nav>

    <!-- Нижняя часть -->
    <div class="px-3 py-3 mt-4 rounded-lg bg-white/5">
      <div class="text-xs text-white/40">Система бронирования</div>
      <div class="text-xs text-white/25 mt-0.5">v1.0</div>
    </div>
  </aside>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
