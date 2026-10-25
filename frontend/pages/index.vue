<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import type { Location, WeatherReport } from '~/types/weather'
import { messages, type Language } from '~/utils/messages'

const config = useRuntimeConfig()
const language = ref<Language>('en')
const themePreference = ref<'system' | 'light' | 'dark'>('system')
const prefersDark = ref(false)
const activeTheme = computed<'light' | 'dark'>(() => themePreference.value === 'system'
  ? (prefersDark.value ? 'dark' : 'light')
  : themePreference.value)
const copy = computed(() => messages[language.value])
const query = ref('')
const locations = ref<Location[]>([])
const DEFAULT_LOCATION: Location = {
  id: 0,
  name: 'Dosquebradas',
  country: 'Colombia',
  latitude: 4.8394,
  longitude: -75.6673,
  timezone: 'America/Bogota',
}
const selected = ref<Location>({ ...DEFAULT_LOCATION })
const report = ref<WeatherReport | null>(null)
const loading = ref(false)
const searching = ref(false)
const locating = ref(false)
const isCurrentLocation = ref(false)
const error = ref('')
const locationNoticeKey = ref<'locationDetected' | 'locationDenied' | 'locationUnavailable' | 'locationLookupFailed' | null>(null)
const locationNotice = computed(() => locationNoticeKey.value ? copy.value[locationNoticeKey.value] : '')
const upcomingHours = computed(() => {
  if (!report.value) return []
  return report.value.hourly
    .filter((hour) => hour.time >= report.value!.current.time)
    .slice(0, 24)
})

const ratingIcons: Record<string, string> = { good: '↗', caution: '◷', poor: '↘' }
let weatherRequestId = 0

async function loadWeather(location: Location) {
  const requestId = ++weatherRequestId
  selected.value = location
  loading.value = true
  error.value = ''
  try {
    const nextReport = await $fetch<WeatherReport>(`${config.public.apiBase}/weather`, {
      method: 'POST',
      body: {
        latitude: location.latitude,
        longitude: location.longitude,
        location_name: location.name,
        language: language.value,
      },
    })
    if (requestId === weatherRequestId) report.value = nextReport
  } catch {
    if (requestId === weatherRequestId) error.value = copy.value.loadError
  } finally {
    if (requestId === weatherRequestId) loading.value = false
  }
}

async function searchLocations() {
  const term = query.value.trim()
  if (term.length < 2) return
  searching.value = true
  error.value = ''
  try {
    locations.value = await $fetch<Location[]>(`${config.public.apiBase}/locations/search`, {
      query: { q: term, language: language.value },
    })
    if (!locations.value.length) error.value = copy.value.noCities
  } catch {
    error.value = copy.value.searchError
  } finally {
    searching.value = false
  }
}

function chooseLocation(location: Location) {
  query.value = ''
  locations.value = []
  locationNoticeKey.value = null
  isCurrentLocation.value = false
  void loadWeather(location)
}

function getBrowserPosition() {
  return new Promise<GeolocationPosition>((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(resolve, reject, {
      enableHighAccuracy: false,
      maximumAge: 5 * 60 * 1000,
      timeout: 7_000,
    })
  })
}

async function locateUser() {
  locating.value = true
  locationNoticeKey.value = null
  error.value = ''
  if (!navigator.geolocation) {
    isCurrentLocation.value = false
    locationNoticeKey.value = 'locationUnavailable'
    const wasAlreadyShowingDefault = selected.value.latitude === DEFAULT_LOCATION.latitude
      && selected.value.longitude === DEFAULT_LOCATION.longitude
    selected.value = { ...DEFAULT_LOCATION }
    if (!wasAlreadyShowingDefault || (!report.value && !loading.value)) await loadWeather(selected.value)
    locating.value = false
    return
  }

  try {
    const position = await getBrowserPosition()
    const latitude = position.coords.latitude
    const longitude = position.coords.longitude
    const nearby: Location = {
      id: 0,
      name: copy.value.nearYou,
      country: '',
      latitude,
      longitude,
      timezone: 'UTC',
    }
    isCurrentLocation.value = true

    const placePromise = $fetch<Location>(`${config.public.apiBase}/locations/reverse`, {
      method: 'POST',
      body: { latitude, longitude, language: language.value },
    }).catch(() => null)
    await loadWeather(nearby)
    const nearbyPlace = await placePromise
    if (nearbyPlace) {
      selected.value = { ...nearbyPlace, latitude, longitude }
      locationNoticeKey.value = 'locationDetected'
    } else {
      locationNoticeKey.value = 'locationLookupFailed'
    }
  } catch (reason) {
    isCurrentLocation.value = false
    const denied = typeof reason === 'object' && reason !== null && 'code' in reason && reason.code === 1
    locationNoticeKey.value = denied ? 'locationDenied' : 'locationUnavailable'
    const wasAlreadyShowingDefault = selected.value.latitude === DEFAULT_LOCATION.latitude
      && selected.value.longitude === DEFAULT_LOCATION.longitude
    selected.value = { ...DEFAULT_LOCATION }
    if (!wasAlreadyShowingDefault || (!report.value && !loading.value)) await loadWeather(selected.value)
  } finally {
    locating.value = false
  }
}

function setLanguage(nextLanguage: Language) {
  language.value = nextLanguage
  localStorage.setItem('weathercast-language', nextLanguage)
  if (isCurrentLocation.value) {
    void locateUser()
  } else if (report.value) {
    void loadWeather(selected.value)
  }
}

function setThemePreference(nextTheme: 'system' | 'light' | 'dark') {
  themePreference.value = nextTheme
  localStorage.setItem('weathercast-theme', nextTheme)
  syncTheme()
}

function syncTheme() {
  if (typeof document !== 'undefined') document.documentElement.dataset.theme = activeTheme.value
}

watch(activeTheme, syncTheme, { immediate: true })

function conditionLabel(code: number) {
  const conditions = copy.value.conditions
  if (code === 0) return conditions.clear
  if ([1, 2].includes(code)) return conditions.partlyCloudy
  if (code === 3) return conditions.overcast
  if ([45, 48].includes(code)) return conditions.fog
  if (code >= 51 && code <= 67) return conditions.lightRain
  if (code >= 71 && code <= 77) return conditions.snow
  if (code >= 80 && code <= 82) return conditions.showers
  if (code >= 95) return conditions.storm
  return conditions.variable
}

let colorSchemeQuery: MediaQueryList | undefined
let systemThemeChangeHandler: (() => void) | undefined

onMounted(() => {
  const savedLanguage = localStorage.getItem('weathercast-language')
  const savedTheme = localStorage.getItem('weathercast-theme')
  colorSchemeQuery = window.matchMedia('(prefers-color-scheme: dark)')
  const updateSystemTheme = () => {
    prefersDark.value = colorSchemeQuery?.matches ?? false
    syncTheme()
  }
  systemThemeChangeHandler = updateSystemTheme
  if (savedLanguage === 'en' || savedLanguage === 'es') language.value = savedLanguage
  if (savedTheme === 'system' || savedTheme === 'light' || savedTheme === 'dark') themePreference.value = savedTheme
  colorSchemeQuery.addEventListener('change', updateSystemTheme)
  updateSystemTheme()
  void loadWeather(selected.value)
  void locateUser()
})

onUnmounted(() => {
  if (systemThemeChangeHandler) colorSchemeQuery?.removeEventListener('change', systemThemeChangeHandler)
})
</script>

<template>
  <main class="weather-page min-h-screen bg-[#f4f7f3] px-4 py-6 text-[#16322e] dark:bg-[#0b1220] dark:text-slate-100" :data-theme="activeTheme">
    <div class="relative z-10 mx-auto max-w-6xl">
      <header class="flex flex-wrap items-center justify-between gap-4">
        <a href="#home" class="flex items-center gap-3 no-underline" :aria-label="copy.brandHome">
          <img src="/weathercast-icon.svg" alt="" aria-hidden="true" class="h-10 w-10 rounded-2xl shadow-sm" width="40" height="40">
          <span class="display text-lg font-extrabold tracking-tight text-[#173e37] dark:text-slate-100">weathercast<span class="text-[#76aa91] dark:text-sky-300">.</span></span>
        </a>
        <div class="ml-auto flex flex-wrap items-center justify-end gap-2">
          <div class="flex rounded-full border border-[#dce7df] bg-white p-1 dark:border-slate-700 dark:bg-slate-800" role="group" :aria-label="copy.languageName">
            <button type="button" class="rounded-full px-2.5 py-1 text-[11px] font-bold" :class="language === 'en' ? 'bg-[#173e37] text-white dark:bg-sky-500 dark:text-slate-950' : 'text-[#55716a] dark:text-slate-300'" :aria-pressed="language === 'en'" @click="setLanguage('en')">EN</button>
            <button type="button" class="rounded-full px-2.5 py-1 text-[11px] font-bold" :class="language === 'es' ? 'bg-[#173e37] text-white dark:bg-sky-500 dark:text-slate-950' : 'text-[#55716a] dark:text-slate-300'" :aria-pressed="language === 'es'" @click="setLanguage('es')">ES</button>
          </div>
          <div class="flex rounded-full border border-[#dce7df] bg-white p-1 dark:border-slate-700 dark:bg-slate-900" role="group" :aria-label="copy.themeName">
            <button type="button" class="rounded-full px-2.5 py-1 text-[11px] font-bold" :class="themePreference === 'system' ? 'bg-[#173e37] text-white dark:bg-sky-500 dark:text-slate-950' : 'text-[#55716a] dark:text-slate-300'" :aria-pressed="themePreference === 'system'" @click="setThemePreference('system')">{{ copy.systemTheme }}</button>
            <button type="button" class="rounded-full px-2.5 py-1 text-[11px] font-bold" :class="themePreference === 'light' ? 'bg-[#173e37] text-white dark:bg-sky-500 dark:text-slate-950' : 'text-[#55716a] dark:text-slate-300'" :aria-pressed="themePreference === 'light'" @click="setThemePreference('light')">{{ copy.lightTheme }}</button>
            <button type="button" class="rounded-full px-2.5 py-1 text-[11px] font-bold" :class="themePreference === 'dark' ? 'bg-[#173e37] text-white dark:bg-sky-500 dark:text-slate-950' : 'text-[#55716a] dark:text-slate-300'" :aria-pressed="themePreference === 'dark'" @click="setThemePreference('dark')">{{ copy.darkTheme }}</button>
          </div>
          <button type="button" class="inline-flex h-9 items-center gap-2 rounded-full border border-[#dce7df] bg-white px-3 text-xs font-semibold text-[#55716a] hover:bg-[#f1f6f1] disabled:opacity-60 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800" :disabled="locating" :aria-label="locating ? copy.locating : copy.useLocation" @click="locateUser">
            <span aria-hidden="true">◎</span><span>{{ locating ? copy.locating : copy.useLocation }}</span>
          </button>
        </div>
      </header>
      <p class="mt-3 text-right text-[11px] text-[#829389] dark:text-slate-400">{{ copy.locationPrivacy }}</p>

      <section id="home" class="mt-12 grid gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-end">
        <div>
          <p class="mb-3 text-xs font-bold uppercase tracking-[0.2em] text-[#638477] dark:text-sky-300">{{ copy.heroEyebrow }}</p>
          <h1 class="display max-w-2xl text-4xl font-semibold leading-tight tracking-[-0.04em] text-[#163a33] dark:text-slate-100 sm:text-5xl">
            {{ copy.heroTitle }}<br><span class="text-[#76a88e] dark:text-sky-300">{{ copy.heroTitleAccent }}</span>
          </h1>
          <p class="mt-4 max-w-xl text-base leading-7 text-[#62736c] dark:text-slate-300">{{ copy.heroDescription }}</p>
        </div>
        <form class="relative" @submit.prevent="searchLocations">
          <label for="city-search" class="mb-2 block text-xs font-bold uppercase tracking-wider text-[#55716a] dark:text-slate-300">{{ copy.findCity }}</label>
          <div class="flex rounded-2xl border border-[#dce7df] bg-white p-1.5 shadow-[0_10px_36px_rgba(28,65,53,0.06)] dark:border-slate-700 dark:bg-slate-900">
            <input id="city-search" v-model="query" class="min-w-0 flex-1 rounded-xl bg-transparent px-4 py-3 text-sm text-[#173e37] outline-none placeholder:text-[#97a9a0] dark:text-white dark:placeholder:text-slate-400" :placeholder="copy.searchPlaceholder" autocomplete="off">
            <button class="rounded-xl bg-[#173e37] px-5 text-sm font-semibold text-white transition hover:bg-[#27584c] disabled:opacity-60 dark:bg-sky-500 dark:text-slate-950 dark:hover:bg-sky-400" :disabled="searching || query.trim().length < 2">
              {{ searching ? copy.searching : copy.search }}
            </button>
          </div>
          <ul v-if="locations.length" class="absolute z-10 mt-2 max-h-64 w-full overflow-auto rounded-2xl border border-[#dce7df] bg-white p-2 shadow-xl dark:border-slate-700 dark:bg-slate-800" :aria-label="copy.citySearchResults">
            <li v-for="location in locations" :key="location.id">
              <button type="button" class="w-full rounded-xl px-3 py-3 text-left text-sm text-[#24473e] hover:bg-[#f1f6f1] dark:text-slate-100 dark:hover:bg-slate-700" @click="chooseLocation(location)">
                <span class="font-semibold">{{ location.name }}</span><span class="text-[#7a8d84] dark:text-slate-400"> · {{ [location.admin1, location.country].filter(Boolean).join(', ') }}</span>
              </button>
            </li>
          </ul>
        </form>
      </section>

      <p v-if="error" role="alert" class="mt-6 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{{ error }}</p>
      <p v-if="locationNotice" role="status" class="mt-4 text-sm text-[#55796b] dark:text-sky-300">{{ locationNotice }}</p>

      <section class="mt-10 grid gap-5 lg:grid-cols-[0.9fr_1.1fr]" aria-live="polite">
        <article class="relative overflow-hidden rounded-[2rem] p-7 text-white shadow-[0_22px_55px_rgba(23,62,55,0.15)] sm:p-9">
          <WeatherScene :code="report?.current.weather_code ?? 2" />
          <div class="relative z-10">
            <div class="flex items-start justify-between gap-4">
              <div>
                <p class="text-sm font-medium text-[#b9d2c4]">{{ selected.name }}<span v-if="selected.country">, {{ selected.country }}</span></p>
                <h2 class="display mt-1 text-xl font-semibold">{{ copy.rightNow }}</h2>
              </div>
              <span class="rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-xs text-[#d8e9df]">{{ report ? conditionLabel(report.current.weather_code) : '…' }}</span>
            </div>
            <div class="mt-10 flex items-end gap-4">
              <span class="display text-7xl font-medium leading-none tracking-[-0.07em]">{{ loading && !report ? '—' : Math.round(report?.current.temperature_c ?? 0) }}°</span>
              <div class="mb-1 pb-1 text-sm leading-6 text-[#c6ddd0]">{{ copy.feelsLike }} {{ Math.round(report?.current.apparent_temperature_c ?? 0) }}°<br>{{ report ? conditionLabel(report.current.weather_code) : copy.loadingForecast }}</div>
            </div>
            <div class="mt-10 grid grid-cols-3 gap-3 border-t border-white/15 pt-5">
              <div><p class="text-xs text-[#b9d2c4]">{{ copy.wind }}</p><p class="mt-1 text-sm font-semibold">{{ Math.round(report?.current.wind_speed_kmh ?? 0) }} <small class="font-normal text-[#b9d2c4]">km/h</small></p></div>
              <div><p class="text-xs text-[#b9d2c4]">{{ copy.humidity }}</p><p class="mt-1 text-sm font-semibold">{{ report?.current.relative_humidity_pct ?? '—' }}<small class="font-normal text-[#b9d2c4]"> %</small></p></div>
              <div><p class="text-xs text-[#b9d2c4]">{{ copy.rain }}</p><p class="mt-1 text-sm font-semibold">{{ report?.current.precipitation_mm ?? '—' }} <small class="font-normal text-[#b9d2c4]">mm</small></p></div>
            </div>
          </div>
        </article>

        <article class="rounded-[2rem] border border-[#e1e9e2] bg-white p-7 shadow-[0_10px_36px_rgba(28,65,53,0.04)] dark:border-slate-700 dark:bg-slate-900 sm:p-9">
          <div class="flex items-center justify-between gap-4">
            <div><p class="text-xs font-bold uppercase tracking-[0.16em] text-[#789185] dark:text-sky-300">{{ copy.recommendationEyebrow }}</p><h2 class="display mt-2 text-xl font-bold text-[#193f36] dark:text-slate-100">{{ copy.recommendationTitle }}</h2></div>
            <span class="grid h-11 w-11 place-items-center rounded-2xl bg-[#eef5ef] text-xl text-[#448267] dark:bg-slate-800 dark:text-sky-300">✳</span>
          </div>
          <div v-if="loading && !report" class="mt-7 text-sm text-[#82958b] dark:text-slate-400">{{ copy.preparing }}</div>
          <div v-else class="mt-6 divide-y divide-[#edf1ed] dark:divide-slate-700">
            <div v-for="recommendation in report?.recommendations" :key="recommendation.activity" class="flex gap-4 py-4 first:pt-0 last:pb-0">
              <span class="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-[#f2f6f1] text-lg text-[#4a8368] dark:bg-slate-800 dark:text-sky-300">{{ ratingIcons[recommendation.rating] }}</span>
              <div class="min-w-0 flex-1">
                <div class="flex flex-wrap items-center justify-between gap-2"><h3 class="text-sm font-bold text-[#21453b] dark:text-slate-100">{{ copy.activities[recommendation.activity] }}</h3><span class="rounded-full px-2.5 py-1 text-[11px] font-bold" :class="{ 'bg-[#eaf5ee] text-[#458266]': recommendation.rating === 'good', 'bg-[#fff5df] text-[#987329]': recommendation.rating === 'caution', 'bg-[#faece8] text-[#a75d4b]': recommendation.rating === 'poor' }">{{ copy.ratings[recommendation.rating] }}</span></div>
                <p class="mt-1 text-xs leading-5 text-[#74867c] dark:text-slate-300">{{ recommendation.reasons.join(' · ') }}</p>
              </div>
            </div>
          </div>
          <p class="mt-6 border-t border-[#edf1ed] pt-4 text-[11px] leading-5 text-[#89988f] dark:border-slate-700 dark:text-slate-400">{{ copy.generalGuidance }}</p>
        </article>
      </section>

      <section class="mb-10 mt-5 rounded-[2rem] border border-[#e1e9e2] bg-white p-7 shadow-[0_10px_36px_rgba(28,65,53,0.04)] dark:border-slate-700 dark:bg-slate-900 sm:p-9">
        <div class="flex flex-wrap items-end justify-between gap-4">
          <div><p class="text-xs font-bold uppercase tracking-[0.16em] text-[#789185] dark:text-sky-300">{{ copy.outlookEyebrow }}</p><h2 class="display mt-2 text-xl font-bold text-[#193f36] dark:text-slate-100">{{ copy.nextDay }}</h2></div>
          <span class="text-xs text-[#82958b] dark:text-slate-400">{{ copy.chartSubtitle }}</span>
        </div>
        <div v-if="loading && !report" class="mt-8 text-sm text-[#82958b] dark:text-slate-400">{{ copy.loadingHours }}</div>
        <HourlyForecastChart v-else-if="report" :hours="upcomingHours" :timezone="report.timezone" :language="language" />
      </section>

      <footer class="flex flex-wrap items-center justify-between gap-3 border-t border-[#dfe8e0] py-5 text-xs text-[#85958c] dark:border-slate-700 dark:text-slate-400">
        <span>{{ copy.dataSources }}</span>
        <span v-if="report">{{ copy.forecastFetched }} {{ new Date(report.fetched_at).toLocaleTimeString(language === 'en' ? 'en-US' : 'es-CO', { hour: '2-digit', minute: '2-digit' }) }}</span>
        <span class="flex gap-3"><a href="https://open-meteo.com/" target="_blank" rel="noreferrer" class="font-semibold text-[#55796b] hover:text-[#244b3d] dark:text-sky-300">{{ copy.source }} ↗</a><a href="https://www.geonames.org/" target="_blank" rel="noreferrer" class="font-semibold text-[#55796b] hover:text-[#244b3d] dark:text-sky-300">GeoNames ↗</a><a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer" class="font-semibold text-[#55796b] hover:text-[#244b3d] dark:text-sky-300">© OpenStreetMap</a></span>
      </footer>
    </div>
  </main>
</template>
