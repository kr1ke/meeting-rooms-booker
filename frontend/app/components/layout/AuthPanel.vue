<template>
  <!-- Левая декоративная панель авторизации (скрыта на мобильных) -->
  <div class="hidden md:flex md:w-1/2 lg:w-[55%] auth-gradient relative overflow-hidden items-center justify-center">
    <!-- Геометрические декоративные фигуры -->
    <div class="absolute inset-0 pointer-events-none">
      <div class="auth-shape auth-shape--circle-lg" />
      <div class="auth-shape auth-shape--circle-md" />
      <div class="auth-shape auth-shape--circle-sm" />
      <div class="auth-shape auth-shape--square" />
      <div class="auth-shape auth-shape--diamond" />
      <div class="auth-shape auth-shape--line-1" />
      <div class="auth-shape auth-shape--line-2" />
    </div>

    <!-- Точечный паттерн-фон -->
    <div
      class="absolute inset-0 opacity-[0.07]"
      style="background-image: radial-gradient(circle, rgba(255,255,255,0.8) 1px, transparent 1px); background-size: 24px 24px;"
    />

    <!-- Контент: логотип и слоган -->
    <div class="relative z-10 text-center px-10 max-w-md">
      <div class="flex items-center justify-center gap-3 mb-8">
        <div class="h-14 w-14 rounded-2xl bg-white/15 flex items-center justify-center backdrop-blur-sm border border-white/10">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
            <path d="m9 12 2 2 4-4" />
          </svg>
        </div>
        <span class="text-3xl font-bold text-white tracking-tight" style="font-family: 'Plus Jakarta Sans', sans-serif;">
          BookRoom
        </span>
      </div>
      <p class="text-lg text-white/80 leading-relaxed font-medium">
        Умная система бронирования переговорных комнат для вашей компании
      </p>
      <p class="mt-4 text-sm text-white/50">
        Планируйте встречи, управляйте ресурсами и повышайте эффективность команды
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-gradient {
  background: linear-gradient(180deg, #1a2744 0%, #2d3555 100%);
}

.auth-shape {
  position: absolute;
  border-radius: 50%;
  border: 1.5px solid rgba(255, 255, 255, 0.1);
}

.auth-shape--circle-lg {
  width: 400px; height: 400px; top: -80px; right: -100px;
  background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 70%);
  animation: auth-pulse 8s ease-in-out infinite;
}
.auth-shape--circle-md {
  width: 250px; height: 250px; bottom: 10%; left: -60px;
  background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
  animation: auth-float 10s ease-in-out infinite;
}
.auth-shape--circle-sm {
  width: 120px; height: 120px; top: 40%; right: 15%;
  background: rgba(255, 255, 255, 0.04);
  animation: auth-orbit 12s ease-in-out infinite;
}
.auth-shape--square {
  width: 80px; height: 80px; border-radius: 16px; top: 20%; left: 15%;
  background: rgba(255, 255, 255, 0.04);
  animation: auth-rotate 15s linear infinite;
}
.auth-shape--diamond {
  width: 60px; height: 60px; border-radius: 12px; bottom: 20%; right: 20%;
  background: rgba(255, 255, 255, 0.03);
  transform: rotate(45deg);
  animation: auth-float-reverse 9s ease-in-out infinite;
}
.auth-shape--line-1, .auth-shape--line-2 {
  border-radius: 2px; border: none;
  background: rgba(255, 255, 255, 0.08);
}
.auth-shape--line-1 {
  width: 120px; height: 2px; top: 30%; left: 10%;
  animation: auth-slide 7s ease-in-out infinite;
}
.auth-shape--line-2 {
  width: 80px; height: 2px; bottom: 35%; right: 10%;
  animation: auth-slide 7s ease-in-out infinite reverse;
}

@keyframes auth-pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.08); opacity: 0.7; }
}
@keyframes auth-float {
  0%, 100% { transform: translateY(0) translateX(0); }
  50% { transform: translateY(-20px) translateX(10px); }
}
@keyframes auth-float-reverse {
  0%, 100% { transform: rotate(45deg) translateY(0); }
  50% { transform: rotate(45deg) translateY(-15px); }
}
@keyframes auth-orbit {
  0%, 100% { transform: translate(0, 0); }
  25% { transform: translate(10px, -10px); }
  50% { transform: translate(0, -20px); }
  75% { transform: translate(-10px, -10px); }
}
@keyframes auth-rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
@keyframes auth-slide {
  0%, 100% { opacity: 0.5; transform: scaleX(1); }
  50% { opacity: 1; transform: scaleX(1.3); }
}
</style>
