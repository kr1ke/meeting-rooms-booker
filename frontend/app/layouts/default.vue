<template>
  <div class="min-h-screen">
    <LayoutAppSidebar />
    <div class="ml-64 flex flex-col bg-background min-h-screen">
      <LayoutAppHeader />
      <main class="flex-1 p-6 lg:p-8">
        <slot />
      </main>
    </div>
  </div>
</template>
