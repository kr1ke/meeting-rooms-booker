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
      link: [
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
