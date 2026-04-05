<script setup lang="ts">
import { Users, MapPin, ChevronRight } from 'lucide-vue-next'

const props = defineProps<{
  room: {
    id: string
    name: string
    floor: number
    capacity: number
    equipment: Record<string, boolean>
    requires_approval: boolean
  }
}>()
</script>

<template>
  <!-- Строка комнаты — list view в стиле Notion -->
  <NuxtLink :to="`/rooms/${room.id}`" class="block group">
    <div class="flex items-center gap-4 px-4 py-3.5 rounded-xl border border-transparent hover:border-border hover:bg-secondary/50 transition-all duration-150">
      <!-- Имя комнаты -->
      <div class="min-w-0 flex-1">
        <div class="flex items-center gap-2.5">
          <h3 class="font-semibold text-foreground truncate">{{ room.name }}</h3>
          <Badge
            v-if="room.requires_approval"
            class="shrink-0 bg-amber-50 text-amber-700 border border-amber-200 text-[11px]"
          >
            Подтверждение
          </Badge>
        </div>
      </div>

      <!-- Мета: этаж + вместимость -->
      <div class="hidden sm:flex items-center gap-4 text-sm text-muted-foreground shrink-0">
        <span class="flex items-center gap-1.5">
          <MapPin class="h-3.5 w-3.5" />
          {{ room.floor }} эт.
        </span>
        <span class="flex items-center gap-1.5">
          <Users class="h-3.5 w-3.5" />
          {{ room.capacity }}
        </span>
      </div>

      <!-- Оборудование -->
      <div class="hidden md:flex items-center gap-1.5 shrink-0">
        <RoomEquipmentBadge
          v-for="(val, key) in room.equipment"
          :key="key"
          v-show="val"
          :type="String(key)"
        />
      </div>

      <!-- Стрелка перехода -->
      <ChevronRight class="h-4 w-4 text-muted-foreground/40 group-hover:text-foreground/60 transition-colors shrink-0" />
    </div>
  </NuxtLink>
</template>
