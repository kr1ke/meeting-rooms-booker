<script setup lang="ts">
import { LogOut } from 'lucide-vue-next'

const { logout, store } = useAuth()
</script>

<template>
  <header class="h-16 border-b bg-card px-6 flex items-center justify-between">
    <div />
    <div class="flex items-center gap-4">
      <NotificationBell />
      <DropdownMenu>
        <DropdownMenuTrigger as-child>
          <Button variant="ghost" class="flex items-center gap-2">
            <Avatar class="h-8 w-8">
              <AvatarFallback>{{ store.user?.name?.charAt(0) }}</AvatarFallback>
            </Avatar>
            <span class="text-sm">{{ store.user?.name }}</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem @click="logout" class="text-destructive">
            <LogOut class="h-4 w-4 mr-2" />
            Выйти
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  </header>
</template>
