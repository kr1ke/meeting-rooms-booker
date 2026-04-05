export default defineNuxtRouteMiddleware((to) => {
  const { store } = useAuth()

  // Страницы админа
  if (to.path.startsWith('/admin') && !store.isAdmin) {
    return navigateTo('/')
  }
})
