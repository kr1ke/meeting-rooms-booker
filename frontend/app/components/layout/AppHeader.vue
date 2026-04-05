<script setup lang="ts">
import { LogOut } from 'lucide-vue-next'

const { logout, store } = useAuth()
</script>

<template>
  <header class="h-14 border-b bg-background px-6 flex items-center justify-between sticky top-0 z-10">
    <!-- Левая часть — хлебные крошки или заголовок -->
    <div class="text-sm text-muted-foreground font-medium">
      <!-- пустое пространство для будущих breadcrumbs -->
    </div>

    <!-- Правая часть — уведомления + профиль -->
    <div class="flex items-center gap-3">
      <LayoutNotificationBell />

      <div class="w-px h-8 bg-border" />

      <DropdownMenu>
        <DropdownMenuTrigger as-child>
          <Button variant="ghost" class="flex items-center gap-2.5 rounded-lg hover:bg-primary/5 px-3">
            <Avatar class="h-8 w-8 bg-primary/10 text-primary">
              <AvatarFallback class="text-sm font-semibold bg-primary/10 text-primary">
                {{ store.user?.name?.charAt(0) }}
              </AvatarFallback>
            </Avatar>
            <span class="text-sm font-medium">{{ store.user?.name }}</span>
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
