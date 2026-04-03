export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const path = event.path

  // Проксировать все /api/* запросы на бэкенд
  const target = `${config.backendUrl}${path}`

  return proxyRequest(event, target)
})
