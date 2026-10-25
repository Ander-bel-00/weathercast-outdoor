export default defineNuxtConfig({
  compatibilityDate: '2026-10-25',
  devtools: { enabled: true },
  modules: ['@nuxtjs/tailwindcss'],
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1',
    },
  },
  app: {
    head: {
      title: 'WeatherCast — weather with context',
      meta: [{ name: 'description', content: 'Make better outdoor plans with weather context for the hours ahead.' }],
    },
  },
})
