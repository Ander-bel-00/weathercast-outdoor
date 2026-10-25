<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { messages, type Language } from '~/utils/messages'
import type { WeatherMapPoint } from '~/types/weather'

type WeatherLayer = 'temperature' | 'rain' | 'wind'
type GridState = 'loading' | 'ready' | 'zoom' | 'error'

const props = defineProps<{
  latitude: number
  longitude: number
  label: string
  language: Language
}>()
const emit = defineEmits<{
  select: [point: { latitude: number; longitude: number }]
}>()

const config = useRuntimeConfig()
const mapElement = ref<HTMLDivElement | null>(null)
const activeLayer = ref<WeatherLayer>('temperature')
const points = ref<WeatherMapPoint[]>([])
const gridState = ref<GridState>('loading')
const copy = computed(() => messages[props.language])
const layerNames = computed<Record<WeatherLayer, string>>(() => ({
  temperature: copy.value.temperatureLayer,
  rain: copy.value.rainLayer,
  wind: copy.value.windLayer,
}))
const legendGradient: Record<WeatherLayer, string> = {
  temperature: 'from-[#4b86bd] via-[#ddaa3c] to-[#cf6951]',
  rain: 'from-[#3d9c9a] via-[#3979b8] to-[#6859b8]',
  wind: 'from-[#238a9c] via-[#ddaa3c] to-[#cf6951]',
}

let map: import('leaflet').Map | undefined
let locationMarker: import('leaflet').CircleMarker | undefined
let weatherLayer: import('leaflet').LayerGroup | undefined
let gridTimer: ReturnType<typeof setTimeout> | undefined
let gridController: AbortController | undefined
let gridRequestId = 0

function valueFor(point: WeatherMapPoint, layer: WeatherLayer) {
  if (layer === 'temperature') return `${Math.round(point.temperature_c)}°`
  if (layer === 'rain') return `${point.precipitation_probability_pct}%`
  return `${Math.round(point.wind_speed_kmh)}`
}

function colorFor(point: WeatherMapPoint, layer: WeatherLayer) {
  const value = layer === 'temperature'
    ? point.temperature_c
    : layer === 'rain'
      ? point.precipitation_probability_pct
      : point.wind_speed_kmh
  if (layer === 'temperature') {
    if (value < 10) return '#4b86bd'
    if (value < 20) return '#238a9c'
    if (value < 28) return '#ddaa3c'
    return '#cf6951'
  }
  if (layer === 'rain') {
    if (value < 20) return '#3d9c9a'
    if (value < 60) return '#3979b8'
    return '#6859b8'
  }
  if (value < 15) return '#238a9c'
  if (value < 30) return '#ddaa3c'
  return '#cf6951'
}

function radiusFor(point: WeatherMapPoint, layer: WeatherLayer) {
  const value = layer === 'temperature'
    ? point.temperature_c
    : layer === 'rain'
      ? point.precipitation_probability_pct
      : point.wind_speed_kmh
  return layer === 'rain'
    ? 9 + Math.min(7, value / 15)
    : 9 + Math.min(7, Math.max(0, value) / 8)
}

function popupFor(L: typeof import('leaflet'), point: WeatherMapPoint) {
  const rows = [
    `${copy.value.temperatureLayer}: ${Math.round(point.temperature_c)}°C`,
    `${copy.value.rainLayer}: ${point.precipitation_probability_pct}%`,
    `${copy.value.windLayer}: ${Math.round(point.wind_speed_kmh)} km/h`,
  ]
  const content = L.DomUtil.create('div', 'weather-map-popup')
  for (const row of rows) {
    const line = L.DomUtil.create('div', '', content)
    line.textContent = row
  }
  return content
}

async function drawWeatherPoints(L: typeof import('leaflet')) {
  if (!weatherLayer) return
  weatherLayer.clearLayers()
  for (const point of points.value) {
    const marker = L.circleMarker([point.latitude, point.longitude], {
      radius: radiusFor(point, activeLayer.value),
      color: '#ffffff',
      weight: 2,
      fillColor: colorFor(point, activeLayer.value),
      fillOpacity: 0.9,
      bubblingMouseEvents: false,
    })
      .bindTooltip(valueFor(point, activeLayer.value), { direction: 'top', offset: [0, -8], opacity: 0.98 })
      .bindPopup(popupFor(L, point))
      .addTo(weatherLayer)
    marker.on('click', (event) => L.DomEvent.stopPropagation(event))
  }
}

function refreshGrid() {
  if (!map) return
  map.closePopup()
  if (gridTimer) clearTimeout(gridTimer)
  gridController?.abort()
  const requestId = ++gridRequestId
  const bounds = map.getBounds()
  const north = bounds.getNorth()
  const east = bounds.getEast()
  const south = bounds.getSouth()
  const west = bounds.getWest()
  if (map.getZoom() < 7 || north - south > 20 || east - west > 20) {
    gridState.value = 'zoom'
    points.value = []
    void import('leaflet').then(drawWeatherPoints)
    return
  }

  gridState.value = 'loading'
  points.value = []
  void import('leaflet').then(drawWeatherPoints)
  gridTimer = setTimeout(async () => {
    const controller = new AbortController()
    gridController = controller
    try {
      const results = await $fetch<WeatherMapPoint[]>(`${config.public.apiBase}/weather/map-grid`, {
        query: { north, east, south, west },
        signal: controller.signal,
      })
      if (requestId !== gridRequestId) return
      points.value = results
      gridState.value = 'ready'
      const L = await import('leaflet')
      await drawWeatherPoints(L)
    } catch {
      if (requestId === gridRequestId && !controller.signal.aborted) {
        points.value = []
        const L = await import('leaflet')
        await drawWeatherPoints(L)
        gridState.value = 'error'
      }
    }
  }, 450)
}

function setLayer(layer: WeatherLayer) {
  activeLayer.value = layer
}

onMounted(async () => {
  const L = await import('leaflet')
  await import('leaflet/dist/leaflet.css')
  if (!mapElement.value) return

  map = L.map(mapElement.value, {
    scrollWheelZoom: true,
    maxBounds: [[-85, -180], [85, 180]],
    maxBoundsViscosity: 1,
  }).setView([props.latitude, props.longitude], 10)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map)
  locationMarker = L.circleMarker([props.latitude, props.longitude], {
    radius: 9,
    color: '#ffffff',
    weight: 3,
    fillColor: '#1686a3',
    fillOpacity: 1,
    bubblingMouseEvents: false,
  }).addTo(map).bindPopup(props.label)
  weatherLayer = L.layerGroup().addTo(map)
  locationMarker.on('click', (event) => L.DomEvent.stopPropagation(event))
  map.on('click', (event) => {
    emit('select', { latitude: event.latlng.lat, longitude: event.latlng.lng })
  })
  map.on('moveend', refreshGrid)
  window.setTimeout(() => map?.invalidateSize(), 50)
  refreshGrid()
})

watch(() => [props.latitude, props.longitude, props.label] as const, ([latitude, longitude, label]) => {
  if (!map || !locationMarker) return
  locationMarker.setLatLng([latitude, longitude]).bindPopup(label)
  map.setView([latitude, longitude], map.getZoom())
})

watch(activeLayer, async () => {
  const L = await import('leaflet')
  await drawWeatherPoints(L)
})

onBeforeUnmount(() => {
  if (gridTimer) clearTimeout(gridTimer)
  gridController?.abort()
  gridRequestId += 1
  map?.remove()
  map = undefined
  locationMarker = undefined
  weatherLayer = undefined
})
</script>

<template>
  <div class="relative overflow-hidden rounded-2xl border border-[#dce7df] bg-[#edf2ee] dark:border-slate-700">
    <div ref="mapElement" class="h-[22rem]" role="application" :aria-label="language === 'es' ? 'Mapa interactivo del clima' : 'Interactive weather map'" />
    <div class="absolute right-3 top-3 z-[1000] flex max-w-[calc(100%-1.5rem)] flex-wrap justify-end gap-1 rounded-xl border border-white/70 bg-white/95 p-1 shadow-lg backdrop-blur dark:border-slate-600 dark:bg-slate-900/95" role="group" :aria-label="copy.mapLayers">
      <button
        v-for="layer in (['temperature', 'rain', 'wind'] as const)"
        :key="layer"
        type="button"
        class="rounded-lg px-2.5 py-2 text-xs font-semibold transition"
        :class="activeLayer === layer ? 'bg-[#173e37] text-white dark:bg-sky-500 dark:text-slate-950' : 'text-[#55716a] hover:bg-[#edf3ee] dark:text-slate-200 dark:hover:bg-slate-800'"
        :aria-pressed="activeLayer === layer"
        @click="setLayer(layer)"
      >{{ layerNames[layer] }}</button>
    </div>
    <div class="absolute bottom-3 left-3 z-[1000] rounded-xl border border-white/70 bg-white/95 px-3 py-2 text-[11px] shadow-lg backdrop-blur dark:border-slate-600 dark:bg-slate-900/95">
      <div class="flex items-center justify-between gap-5 font-semibold text-[#315b4d] dark:text-slate-100">
        <span>{{ layerNames[activeLayer] }}</span>
        <span class="text-[#74867c] dark:text-slate-300">{{ copy.mapLegendLow }} <span class="mx-1 inline-block h-2 w-12 rounded-full bg-gradient-to-r align-middle" :class="legendGradient[activeLayer]" /> {{ copy.mapLegendHigh }}</span>
      </div>
      <p v-if="gridState !== 'ready'" class="mt-1 text-[#74867c] dark:text-slate-300" role="status" aria-live="polite">
        {{ gridState === 'loading' ? copy.mapLoading : gridState === 'zoom' ? copy.mapZoomIn : copy.mapDataUnavailable }}
      </p>
    </div>
  </div>
</template>
