<script setup lang="ts">
import type { Location, WeatherReport } from '~/types/weather'

const config = useRuntimeConfig()
const query = ref('')
const locations = ref<Location[]>([])
const selected = ref<Location>({
  id: 3688689,
  name: 'Bogotá',
  country: 'Colombia',
  latitude: 4.711,
  longitude: -74.0721,
  timezone: 'America/Bogota',
})
const report = ref<WeatherReport | null>(null)
const loading = ref(false)
const searching = ref(false)
const error = ref('')
const upcomingHours = computed(() => {
  if (!report.value) return []
  return report.value.hourly
    .filter((hour) => hour.time >= report.value!.current.time)
    .slice(0, 24)
})

const activityNames: Record<string, string> = { walk: 'Walk', run: 'Run', bike: 'Ride a bike' }
const ratingNames: Record<string, string> = { good: 'Good conditions', caution: 'Use caution', poor: 'Better to wait' }
const ratingIcons: Record<string, string> = { good: '↗', caution: '◷', poor: '↘' }

async function loadWeather(location: Location) {
  selected.value = location
  loading.value = true
  error.value = ''
  try {
    report.value = await $fetch<WeatherReport>(`${config.public.apiBase}/weather`, {
      query: { latitude: location.latitude, longitude: location.longitude, location_name: location.name },
    })
  } catch {
    error.value = 'We could not load the forecast. Check your connection and try again.'
  } finally {
    loading.value = false
  }
}

async function searchLocations() {
  const term = query.value.trim()
  if (term.length < 2) return
  searching.value = true
  error.value = ''
  try {
    locations.value = await $fetch<Location[]>(`${config.public.apiBase}/locations/search`, { query: { q: term } })
    if (!locations.value.length) error.value = 'No cities found. Try another name.'
  } catch {
    error.value = 'City search is unavailable right now.'
  } finally {
    searching.value = false
  }
}

function chooseLocation(location: Location) {
  query.value = ''
  locations.value = []
  void loadWeather(location)
}

function conditionLabel(code: number) {
  if (code === 0) return 'Clear sky'
  if ([1, 2].includes(code)) return 'Partly cloudy'
  if (code === 3) return 'Overcast'
  if ([45, 48].includes(code)) return 'Fog'
  if (code >= 51 && code <= 67) return 'Light rain'
  if (code >= 71 && code <= 77) return 'Snow'
  if (code >= 80 && code <= 82) return 'Rain showers'
  if (code >= 95) return 'Thunderstorm'
  return 'Changing conditions'
}

onMounted(() => { void loadWeather(selected.value) })
</script>

<template>
  <main class="min-h-screen px-4 py-6 sm:px-8 lg:px-12">
    <div class="mx-auto max-w-6xl">
      <header class="flex items-center justify-between gap-4">
        <a href="#home" class="flex items-center gap-3 no-underline" aria-label="WeatherCast home">
          <span class="grid h-10 w-10 place-items-center rounded-2xl bg-[#173e37] text-xl text-white">☼</span>
          <span class="display text-lg font-extrabold tracking-tight text-[#173e37]">weathercast<span class="text-[#76aa91]">.</span></span>
        </a>
        <div class="hidden items-center gap-2 rounded-full border border-[#dce7df] bg-white/70 px-3 py-2 text-xs font-semibold text-[#55716a] sm:flex">
          <span class="h-2 w-2 rounded-full bg-[#67b48d]" /> Forecast updated
        </div>
      </header>

      <section id="home" class="mt-12 grid gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-end">
        <div>
          <p class="mb-3 text-xs font-bold uppercase tracking-[0.2em] text-[#638477]">Weather, in context</p>
          <h1 class="display max-w-2xl text-4xl font-semibold leading-tight tracking-[-0.04em] text-[#163a33] sm:text-5xl">
            Better plans<br><span class="text-[#76a88e]">start with context.</span>
          </h1>
          <p class="mt-4 max-w-xl text-base leading-7 text-[#62736c]">A forecast that helps you decide what to do, with clear reasons behind every recommendation.</p>
        </div>
        <form class="relative" @submit.prevent="searchLocations">
          <label for="city-search" class="mb-2 block text-xs font-bold uppercase tracking-wider text-[#55716a]">Find a city</label>
          <div class="flex rounded-2xl border border-[#dce7df] bg-white p-1.5 shadow-[0_10px_36px_rgba(28,65,53,0.06)]">
            <input id="city-search" v-model="query" class="min-w-0 flex-1 rounded-xl bg-transparent px-4 py-3 text-sm text-[#173e37] outline-none placeholder:text-[#97a9a0]" placeholder="e.g. Medellín, Colombia" autocomplete="off">
            <button class="rounded-xl bg-[#173e37] px-5 text-sm font-semibold text-white transition hover:bg-[#27584c] disabled:opacity-60" :disabled="searching || query.trim().length < 2">
              {{ searching ? 'Searching…' : 'Search' }}
            </button>
          </div>
          <ul v-if="locations.length" class="absolute z-10 mt-2 max-h-64 w-full overflow-auto rounded-2xl border border-[#dce7df] bg-white p-2 shadow-xl" aria-label="City search results">
            <li v-for="location in locations" :key="location.id">
              <button type="button" class="w-full rounded-xl px-3 py-3 text-left text-sm text-[#24473e] hover:bg-[#f1f6f1]" @click="chooseLocation(location)">
                <span class="font-semibold">{{ location.name }}</span><span class="text-[#7a8d84]"> · {{ [location.admin1, location.country].filter(Boolean).join(', ') }}</span>
              </button>
            </li>
          </ul>
        </form>
      </section>

      <p v-if="error" role="alert" class="mt-6 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{{ error }}</p>

      <section class="mt-10 grid gap-5 lg:grid-cols-[0.9fr_1.1fr]" aria-live="polite">
        <article class="relative overflow-hidden rounded-[2rem] p-7 text-white shadow-[0_22px_55px_rgba(23,62,55,0.15)] sm:p-9">
          <WeatherScene :code="report?.current.weather_code ?? 2" />
          <div class="relative z-10">
            <div class="flex items-start justify-between gap-4">
              <div>
                <p class="text-sm font-medium text-[#b9d2c4]">{{ selected.name }}<span v-if="selected.country">, {{ selected.country }}</span></p>
                <h2 class="display mt-1 text-xl font-semibold">Right now</h2>
              </div>
              <span class="rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-xs text-[#d8e9df]">{{ report ? conditionLabel(report.current.weather_code) : '…' }}</span>
            </div>
            <div class="mt-10 flex items-end gap-4">
              <span class="display text-7xl font-medium leading-none tracking-[-0.07em]">{{ loading && !report ? '—' : Math.round(report?.current.temperature_c ?? 0) }}°</span>
              <div class="mb-1 pb-1 text-sm leading-6 text-[#c6ddd0]">Feels like {{ Math.round(report?.current.apparent_temperature_c ?? 0) }}°<br>{{ report ? conditionLabel(report.current.weather_code) : 'Loading forecast' }}</div>
            </div>
            <div class="mt-10 grid grid-cols-3 gap-3 border-t border-white/15 pt-5">
              <div><p class="text-xs text-[#b9d2c4]">Wind</p><p class="mt-1 text-sm font-semibold">{{ Math.round(report?.current.wind_speed_kmh ?? 0) }} <small class="font-normal text-[#b9d2c4]">km/h</small></p></div>
              <div><p class="text-xs text-[#b9d2c4]">Humidity</p><p class="mt-1 text-sm font-semibold">{{ report?.current.relative_humidity_pct ?? '—' }}<small class="font-normal text-[#b9d2c4]"> %</small></p></div>
              <div><p class="text-xs text-[#b9d2c4]">Rain</p><p class="mt-1 text-sm font-semibold">{{ report?.current.precipitation_mm ?? '—' }} <small class="font-normal text-[#b9d2c4]">mm</small></p></div>
            </div>
          </div>
        </article>

        <article class="rounded-[2rem] border border-[#e1e9e2] bg-white p-7 shadow-[0_10px_36px_rgba(28,65,53,0.04)] sm:p-9">
          <div class="flex items-center justify-between gap-4">
            <div><p class="text-xs font-bold uppercase tracking-[0.16em] text-[#789185]">A recommendation with reasons</p><h2 class="display mt-2 text-xl font-bold text-[#193f36]">Good time to head out?</h2></div>
            <span class="grid h-11 w-11 place-items-center rounded-2xl bg-[#eef5ef] text-xl text-[#448267]">✳</span>
          </div>
          <div v-if="loading && !report" class="mt-7 text-sm text-[#82958b]">Preparing your weather context…</div>
          <div v-else class="mt-6 divide-y divide-[#edf1ed]">
            <div v-for="recommendation in report?.recommendations" :key="recommendation.activity" class="flex gap-4 py-4 first:pt-0 last:pb-0">
              <span class="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-[#f2f6f1] text-lg text-[#4a8368]">{{ ratingIcons[recommendation.rating] }}</span>
              <div class="min-w-0 flex-1">
                <div class="flex flex-wrap items-center justify-between gap-2"><h3 class="text-sm font-bold text-[#21453b]">{{ activityNames[recommendation.activity] }}</h3><span class="rounded-full px-2.5 py-1 text-[11px] font-bold" :class="{ 'bg-[#eaf5ee] text-[#458266]': recommendation.rating === 'good', 'bg-[#fff5df] text-[#987329]': recommendation.rating === 'caution', 'bg-[#faece8] text-[#a75d4b]': recommendation.rating === 'poor' }">{{ ratingNames[recommendation.rating] }}</span></div>
                <p class="mt-1 text-xs leading-5 text-[#74867c]">{{ recommendation.reasons.join(' · ') }}</p>
              </div>
            </div>
          </div>
          <p class="mt-6 border-t border-[#edf1ed] pt-4 text-[11px] leading-5 text-[#89988f]">General guidance based on current weather. Use your judgment and check official alerts.</p>
        </article>
      </section>

      <section class="mb-10 mt-5 rounded-[2rem] border border-[#e1e9e2] bg-white p-7 shadow-[0_10px_36px_rgba(28,65,53,0.04)] sm:p-9">
        <div class="flex flex-wrap items-end justify-between gap-4">
          <div><p class="text-xs font-bold uppercase tracking-[0.16em] text-[#789185]">The outlook</p><h2 class="display mt-2 text-xl font-bold text-[#193f36]">The next 24 hours</h2></div>
          <span class="text-xs text-[#82958b]">Temperature trend · chance of rain</span>
        </div>
        <div v-if="loading && !report" class="mt-8 text-sm text-[#82958b]">Loading the hourly forecast…</div>
        <HourlyForecastChart v-else-if="report" :hours="upcomingHours" :timezone="report.timezone" />
      </section>

      <footer class="flex flex-wrap items-center justify-between gap-3 border-t border-[#dfe8e0] py-5 text-xs text-[#85958c]">
        <span>WeatherCast · Weather data by Open-Meteo · Geocoding by GeoNames</span>
        <span v-if="report">Forecast fetched {{ new Date(report.fetched_at).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) }}</span>
        <a href="https://open-meteo.com/" target="_blank" rel="noreferrer" class="font-semibold text-[#55796b] hover:text-[#244b3d]">Data source ↗</a>
      </footer>
    </div>
  </main>
</template>
