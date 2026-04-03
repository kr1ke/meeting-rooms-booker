<script setup lang="ts">
import { Users, MapPin } from 'lucide-vue-next'

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
  <!-- Карточка переговорной комнаты с навигацией на страницу детали -->
  <Card class="hover:border-primary/50 transition-colors cursor-pointer" @click="navigateTo(`/rooms/${room.id}`)">
    <CardHeader>
      <div class="flex items-center justify-between">
        <CardTitle class="text-lg">{{ room.name }}</CardTitle>
        <Badge v-if="room.requires_approval" variant="outline" class="text-xs">Требует подтверждения</Badge>
      </div>
    </CardHeader>
    <CardContent>
      <div class="flex items-center gap-4 text-sm text-muted-foreground mb-3">
        <span class="flex items-center gap-1"><MapPin class="h-4 w-4" /> Этаж {{ room.floor }}</span>
        <span class="flex items-center gap-1"><Users class="h-4 w-4" /> до {{ room.capacity }} чел.</span>
      </div>
      <div class="flex flex-wrap gap-1">
        <EquipmentBadge v-for="(val, key) in room.equipment" :key="key" v-show="val" :type="String(key)" />
      </div>
    </CardContent>
  </Card>
</template>
