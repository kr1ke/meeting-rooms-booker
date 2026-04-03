<template>
  <div class="flex min-h-screen bg-background">
    <AppSidebar />
    <div class="flex-1 flex flex-col">
      <AppHeader />
      <main class="flex-1 p-6">
        <slot />
      </main>
    </div>
  </div>
</template>
