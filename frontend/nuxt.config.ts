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
      title: 'WeatherCast — clima con contexto',
      meta: [{ name: 'description', content: 'Decide mejor qué hacer al aire libre con el clima de las próximas horas.' }],
    },
  },
})
