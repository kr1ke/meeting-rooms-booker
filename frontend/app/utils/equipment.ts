import type { Component } from 'vue'
import { Presentation, Monitor, Video } from 'lucide-vue-next'
// Component импортируется как тип, чтобы TS знал о ручке для lucide-иконок

// Описание одного типа оборудования переговорки.
// Используется EquipmentBadge (отображение) и EquipmentPicker (выбор).
export interface EquipmentType {
  key: string           // идентификатор в JSONB БД
  label: string         // человекочитаемое название
  icon: Component       // lucide-иконка
  badgeClasses: string  // Tailwind-классы для цветного бейджа
}

// Единый список всех типов оборудования.
// При добавлении нового типа — расширяй этот массив, EquipmentBadge
// и EquipmentPicker подхватят автоматически.
export const EQUIPMENT_TYPES: readonly EquipmentType[] = [
  {
    key: 'projector',
    label: 'Проектор',
    icon: Presentation,
    badgeClasses: 'bg-blue-50 text-blue-700 border-blue-200',
  },
  {
    key: 'whiteboard',
    label: 'Доска',
    icon: Monitor,
    badgeClasses: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  },
  {
    key: 'videoconference',
    label: 'Видеоконференция',
    icon: Video,
    badgeClasses: 'bg-violet-50 text-violet-700 border-violet-200',
  },
]

// Найти тип по ключу. Возвращает undefined, если тип неизвестен —
// потребитель должен уметь показать fallback.
export function getEquipmentType(key: string): EquipmentType | undefined {
  return EQUIPMENT_TYPES.find(t => t.key === key)
}
