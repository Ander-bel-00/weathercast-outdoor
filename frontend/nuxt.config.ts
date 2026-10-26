export default defineNuxtConfig({
  compatibilityDate: '2026-10-25',
  devtools: { enabled: true },
  // Keep route matching exact; this also avoids relying on Nuxt 3's vulnerable
  // case-insensitive route-rule matching. This app currently defines no routeRules.
  router: { options: { sensitive: true } },
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
      meta: [
        { name: 'description', content: 'Make better outdoor plans with weather context for the hours ahead.' },
        { name: 'theme-color', content: '#173e37' },
        { property: 'og:type', content: 'website' },
        { property: 'og:site_name', content: 'WeatherCast' },
        { property: 'og:title', content: 'WeatherCast — weather with context' },
        { property: 'og:description', content: 'Make better outdoor plans with weather context for the hours ahead.' },
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/weathercast-icon.svg' },
      ],
    },
  },
})
