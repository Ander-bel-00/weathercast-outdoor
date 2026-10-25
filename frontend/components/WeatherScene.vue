<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ code: number }>()

type WeatherSceneType = 'sunny' | 'cloudy' | 'foggy' | 'rainy' | 'snowy' | 'stormy'

const scene = computed<WeatherSceneType>(() => {
  const code = props.code
  if (code === 0) return 'sunny'
  if ([1, 2, 3].includes(code)) return 'cloudy'
  if ([45, 48].includes(code)) return 'foggy'
  if ((code >= 51 && code <= 67) || (code >= 80 && code <= 82)) return 'rainy'
  if (code >= 71 && code <= 77) return 'snowy'
  if (code >= 95) return 'stormy'
  return 'cloudy'
})

const atmospheres: Record<WeatherSceneType, string> = {
  sunny: 'from-[#24564b] via-[#3f7561] to-[#a48455]',
  cloudy: 'from-[#23464a] via-[#3e686b] to-[#78908d]',
  foggy: 'from-[#344e51] via-[#5f7778] to-[#879a99]',
  rainy: 'from-[#193e4b] via-[#315d6b] to-[#6c8b91]',
  snowy: 'from-[#334d60] via-[#536e80] to-[#8197a0]',
  stormy: 'from-[#202d44] via-[#354b66] to-[#617387]',
}

const atmosphere = computed(() => atmospheres[scene.value])
</script>

<template>
  <div
    class="pointer-events-none absolute inset-0 overflow-hidden bg-gradient-to-br transition-colors duration-700 motion-reduce:transition-none"
    :class="atmosphere"
    aria-hidden="true"
  >
    <div class="weather-scene-glow absolute -right-12 -top-24 h-72 w-72 rounded-full" />
    <svg
      class="weather-scene-art absolute -right-2 top-16 w-40 sm:right-4 sm:top-12 sm:w-52"
      viewBox="0 0 240 180"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <g v-if="scene === 'sunny'">
        <circle cx="161" cy="76" r="53" fill="#FFD985" fill-opacity=".12" />
        <g class="weather-sun-rays" stroke="#FFE6AE" stroke-linecap="round" stroke-width="4" stroke-opacity=".82">
          <path d="M161 13v14M161 125v14M98 76h14M210 76h14M117 32l10 10M195 110l10 10M205 32l-10 10M127 110l-10 10" />
        </g>
        <circle cx="161" cy="76" r="31" fill="#FFD985" />
        <path d="M50 143c-7-20 9-40 31-40 9-22 42-24 55-3 13 1 22 10 24 22 20 0 29 9 29 21H50Z" fill="#F3F7E9" fill-opacity=".87" />
      </g>

      <g v-else-if="scene === 'cloudy'">
        <circle cx="168" cy="57" r="45" fill="#DAE9DE" fill-opacity=".12" />
        <path d="M36 133c-8-19 5-37 26-38 3-20 22-33 42-26 12-27 52-25 62 4 18-1 31 12 31 29 0 4-1 8-3 12 17 2 27 10 27 23H36v-4Z" fill="#EFF5EF" fill-opacity=".87" />
        <path d="M57 144h141" stroke="#D8E8DF" stroke-opacity=".48" stroke-width="3" stroke-linecap="round" />
      </g>

      <g v-else-if="scene === 'foggy'" stroke="#E8F0EC" stroke-linecap="round">
        <path d="M53 67c-6-15 5-29 22-30 3-16 18-26 34-20 10-21 42-20 50 3 15-1 25 10 25 23 0 3-1 7-2 10 14 2 22 8 22 18H53v-4Z" fill="#EFF5EF" fill-opacity=".76" stroke="none" />
        <path d="M39 101h157M54 122h136M72 143h112" stroke-width="5" stroke-opacity=".75" />
      </g>

      <g v-else-if="scene === 'rainy'">
        <path d="M35 100c-7-18 5-34 24-35 3-18 20-29 38-23 11-24 46-22 55 3 17-1 28 11 28 25 0 4-1 7-3 11 16 2 24 9 24 21H35v-2Z" fill="#E7F0EB" fill-opacity=".88" />
        <g class="weather-rain" stroke="#A8DCE0" stroke-linecap="round" stroke-width="5">
          <path d="m73 118-7 18M113 118l-7 18M153 118l-7 18M193 118l-7 18" />
        </g>
      </g>

      <g v-else-if="scene === 'snowy'">
        <path d="M35 96c-7-18 5-34 24-35 3-18 20-29 38-23 11-24 46-22 55 3 17-1 28 11 28 25 0 4-1 7-3 11 16 2 24 9 24 21H35v-2Z" fill="#F1F5F2" fill-opacity=".9" />
        <g fill="#D8F1F1">
          <circle cx="68" cy="129" r="4" /><circle cx="108" cy="145" r="4" /><circle cx="148" cy="128" r="4" /><circle cx="188" cy="145" r="4" />
        </g>
      </g>

      <g v-else>
        <path d="M35 91c-7-18 5-34 24-35 3-18 20-29 38-23 11-24 46-22 55 3 17-1 28 11 28 25 0 4-1 7-3 11 16 2 24 9 24 21H35v-2Z" fill="#CBD7E0" />
        <path d="m126 101-20 32h17l-7 26 31-40h-19l11-18h-13Z" fill="#FFD985" />
      </g>
    </svg>
    <div class="absolute inset-x-0 bottom-0 h-28 bg-gradient-to-t from-black/10 to-transparent" />
  </div>
</template>
