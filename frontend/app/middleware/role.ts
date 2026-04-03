export default defineNuxtRouteMiddleware((to) => {
  const { store } = useAuth()

  // Страницы админа
  if (to.path.startsWith('/admin') && !store.isAdmin) {
    return navigateTo('/')
  }

  // Страница менеджера
  if (to.path === '/department' && !store.isManager && !store.isAdmin) {
    return navigateTo('/')
  }
})
