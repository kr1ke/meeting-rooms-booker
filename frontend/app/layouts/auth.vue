<template>
  <!-- Макет авторизации: тёплая тёмная панель слева + светлая область формы справа -->
  <div class="min-h-screen flex flex-col md:flex-row">

    <!-- Левая панель — тёплый тёмный фон с точечным паттерном -->
    <div class="hidden md:flex md:w-1/2 lg:w-[55%] auth-panel relative overflow-hidden items-center justify-center">

      <!-- Точечный паттерн -->
      <div class="absolute inset-0 auth-dot-pattern" />

      <!-- Контент: логотип и слоган -->
      <div class="relative z-10 text-center px-10 max-w-md">
        <div class="flex items-center justify-center gap-3 mb-8">
          <div class="h-14 w-14 rounded-2xl bg-white/8 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-orange-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z" />
            </svg>
          </div>
          <span class="text-3xl font-bold text-white tracking-tight">
            BookRoom
          </span>
        </div>

        <p class="text-lg text-white/75 leading-relaxed font-medium">
          Бронирование переговорных для вашей команды
        </p>
        <p class="mt-4 text-sm text-white/40">
          Планируйте встречи и управляйте ресурсами
        </p>
      </div>
    </div>

    <!-- Правая панель с формой -->
    <div class="flex-1 flex items-center justify-center bg-secondary md:bg-background px-4 py-12 md:px-8">
      <div class="w-full max-w-sm animate-fade-in">
        <slot />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Тёплый тёмный фон */
.auth-panel {
  background: hsl(25, 15%, 12%);
}

/* Точечный паттерн вместо сетки */
.auth-dot-pattern {
  background-image: radial-gradient(circle, rgba(255, 255, 255, 0.04) 1px, transparent 1px);
  background-size: 24px 24px;
}
</style>
