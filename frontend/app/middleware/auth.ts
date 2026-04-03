export default defineNuxtRouteMiddleware(async (to) => {
  const { fetchMe, store } = useAuth()

  if (store.loading) {
    await fetchMe()
  }

  if (!store.isAuthenticated && to.path !== '/login' && to.path !== '/register') {
    return navigateTo('/login')
  }

  if (store.isAuthenticated && (to.path === '/login' || to.path === '/register')) {
    return navigateTo('/')
  }
})
