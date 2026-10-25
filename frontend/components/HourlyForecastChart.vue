<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { HourlyPoint } from '~/types/weather'

const props = defineProps<{ hours: HourlyPoint[]; timezone: string }>()

const chart = { left: 48, right: 782, top: 24, bottom: 244 }
const selectedIndex = ref(0)
const points = computed(() => props.hours.slice(0, 24))

watch(points, () => { selectedIndex.value = 0 })

const temperatures = computed(() => points.value.map((point) => point.temperature_c))
const minTemperature = computed(() => Math.floor(Math.min(...temperatures.value) - 2))
const maxTemperature = computed(() => Math.ceil(Math.max(...temperatures.value) + 2))
const temperatureRange = computed(() => Math.max(maxTemperature.value - minTemperature.value, 1))
const activePoint = computed(() => points.value[selectedIndex.value])
const gridValues = computed(() => [0, 1, 2, 3].map((step) => maxTemperature.value - (temperatureRange.value * step) / 3))

function xPosition(index: number) {
  if (points.value.length <= 1) return (chart.left + chart.right) / 2
  return chart.left + (index * (chart.right - chart.left)) / (points.value.length - 1)
}

function yPosition(temperature: number) {
  return chart.top + ((maxTemperature.value - temperature) / temperatureRange.value) * (chart.bottom - chart.top)
}

const temperaturePath = computed(() => points.value
  .map((point, index) => `${index === 0 ? 'M' : 'L'} ${xPosition(index).toFixed(1)} ${yPosition(point.temperature_c).toFixed(1)}`)
  .join(' '))

function hourLabel(value: string) {
  return value.slice(11, 16)
}

function temperatureLabel(value: number) {
  return `${Math.round(value)}°`
}
</script>

<template>
  <div v-if="points.length" class="mt-7">
    <div class="mb-3 flex flex-wrap items-center justify-between gap-3">
      <div aria-live="polite" class="flex items-baseline gap-3">
        <span class="display text-2xl font-bold text-[#21483d]">{{ Math.round(activePoint?.temperature_c ?? 0) }}°</span>
        <span class="text-xs text-[#74867c]">{{ activePoint ? hourLabel(activePoint.time) : '' }} · {{ activePoint?.precipitation_probability_pct ?? 0 }}% chance of rain</span>
      </div>
      <div class="flex gap-4 text-[11px] font-medium text-[#73857b]" aria-label="Chart legend">
        <span class="flex items-center gap-1.5"><i class="h-2 w-2 rounded-full bg-[#42856b]" /> Temperature</span>
        <span class="flex items-center gap-1.5"><i class="h-2 w-2 rounded-sm bg-[#9dc9d2]" /> Rain chance</span>
      </div>
    </div>

    <div class="overflow-x-auto">
      <svg
        class="h-[260px] min-w-[620px] w-full overflow-visible"
        viewBox="0 0 800 300"
        role="group"
        aria-label="Hourly temperature and precipitation forecast. Focus a point to inspect its values."
      >
        <g v-for="(value, index) in gridValues" :key="index">
          <line :x1="chart.left" :y1="chart.top + (index * (chart.bottom - chart.top)) / 3" :x2="chart.right" :y2="chart.top + (index * (chart.bottom - chart.top)) / 3" stroke="#e9efea" stroke-dasharray="3 6" />
          <text :x="chart.left - 12" :y="chart.top + (index * (chart.bottom - chart.top)) / 3 + 4" text-anchor="end" class="fill-[#829389] text-[11px]">{{ temperatureLabel(value) }}</text>
        </g>

        <g v-for="(point, index) in points" :key="`rain-${point.time}`">
          <rect
            :x="xPosition(index) - 5"
            :y="chart.bottom - (point.precipitation_probability_pct / 100) * 92"
            width="10"
            :height="(point.precipitation_probability_pct / 100) * 92"
            rx="5"
            fill="#9dc9d2"
            fill-opacity=".62"
          />
        </g>

        <path :d="temperaturePath" fill="none" stroke="#42856b" stroke-linecap="round" stroke-linejoin="round" stroke-width="3.5" />

        <g v-for="(point, index) in points" :key="point.time">
          <line v-if="index % 4 === 0 || index === points.length - 1" :x1="xPosition(index)" y1="258" :x2="xPosition(index)" y2="263" stroke="#b7c6bc" />
          <text v-if="index % 4 === 0 || index === points.length - 1" :x="xPosition(index)" y="283" text-anchor="middle" class="fill-[#829389] text-[11px]">{{ hourLabel(point.time) }}</text>
          <circle
            :cx="xPosition(index)"
            :cy="yPosition(point.temperature_c)"
            :r="selectedIndex === index ? 7 : 4"
            :fill="selectedIndex === index ? '#ffffff' : '#42856b'"
            stroke="#42856b"
            :stroke-width="selectedIndex === index ? 3 : 0"
            class="cursor-pointer transition-all"
            tabindex="0"
            role="button"
            :aria-label="`${hourLabel(point.time)}: ${Math.round(point.temperature_c)} degrees, ${point.precipitation_probability_pct}% chance of rain`"
            @mouseenter="selectedIndex = index"
            @focus="selectedIndex = index"
            @click="selectedIndex = index"
            @keydown.enter.space.prevent="selectedIndex = index"
          />
        </g>
      </svg>
    </div>
    <p class="mt-1 text-[11px] leading-5 text-[#8a9a90]">Hourly forecast in {{ timezone }} local time. Select or focus a temperature point for details.</p>
  </div>
  <p v-else class="mt-7 rounded-2xl bg-[#f5f8f4] px-4 py-6 text-center text-sm text-[#82958b]">No hourly forecast is available for this location.</p>
</template>
