export default defineNuxtConfig({
  modules: [
    '@nuxtjs/tailwindcss',
    'shadcn-nuxt',
    '@pinia/nuxt',
  ],
  css: [
    '~/assets/css/variables.css',
  ],
  shadcn: {
    prefix: '',
    componentDir: './app/components/ui',
  },
  app: {
    head: {
      title: 'BookRoom',
      titleTemplate: '%s — BookRoom',
      htmlAttrs: { lang: 'ru' },
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Система бронирования переговорных комнат для вашей команды' },
        { property: 'og:title', content: 'BookRoom — бронирование переговорных' },
        { property: 'og:description', content: 'Планируйте встречи и управляйте ресурсами офиса' },
        { property: 'og:type', content: 'website' },
        { name: 'theme-color', content: 'hsl(25, 80%, 52%)' },
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        {
          rel: 'preconnect',
          href: 'https://fonts.googleapis.com',
        },
        {
          rel: 'preconnect',
          href: 'https://fonts.gstatic.com',
          crossorigin: '',
        },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap',
        },
      ],
    },
  },
  runtimeConfig: {
    backendUrl: process.env.BACKEND_URL || 'http://localhost:8000',
  },
  ssr: false,
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },
})
