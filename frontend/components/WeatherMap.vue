<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { Language } from '~/utils/messages'

const props = defineProps<{
  latitude: number
  longitude: number
  label: string
  language: Language
}>()
const emit = defineEmits<{
  select: [point: { latitude: number; longitude: number }]
}>()

const mapElement = ref<HTMLDivElement | null>(null)
let map: import('leaflet').Map | undefined
let marker: import('leaflet').CircleMarker | undefined

onMounted(async () => {
  const L = await import('leaflet')
  await import('leaflet/dist/leaflet.css')
  if (!mapElement.value) return

  map = L.map(mapElement.value, { scrollWheelZoom: false }).setView(
    [props.latitude, props.longitude],
    10,
  )
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map)
  marker = L.circleMarker([props.latitude, props.longitude], {
    radius: 9,
    color: '#ffffff',
    weight: 3,
    fillColor: '#1686a3',
    fillOpacity: 1,
  }).addTo(map).bindPopup(props.label)
  map.on('click', (event) => {
    emit('select', { latitude: event.latlng.lat, longitude: event.latlng.lng })
  })
})

watch(() => [props.latitude, props.longitude, props.label] as const, ([latitude, longitude, label]) => {
  if (!map || !marker) return
  marker.setLatLng([latitude, longitude]).bindPopup(label)
  map.setView([latitude, longitude], map.getZoom())
})

onBeforeUnmount(() => {
  map?.remove()
  map = undefined
  marker = undefined
})
</script>

<template>
  <div ref="mapElement" class="h-[22rem] overflow-hidden rounded-2xl border border-[#dce7df] bg-[#edf2ee] dark:border-slate-700" role="application" :aria-label="language === 'es' ? 'Mapa interactivo del clima' : 'Interactive weather map'" />
</template>
