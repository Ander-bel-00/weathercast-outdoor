export interface Location {
  id: number
  name: string
  country: string
  admin1?: string | null
  latitude: number
  longitude: number
  timezone: string
}

export interface WeatherReport {
  location_name: string
  latitude: number
  longitude: number
  timezone: string
  fetched_at: string
  current: {
    time: string
    temperature_c: number
    apparent_temperature_c: number
    relative_humidity_pct: number
    precipitation_mm: number
    wind_speed_kmh: number
    weather_code: number
  }
  hourly: Array<{
    time: string
    temperature_c: number
    precipitation_probability_pct: number
    wind_speed_kmh: number
  }>
  recommendations: Array<{
    activity: 'walk' | 'run' | 'bike'
    rating: 'good' | 'caution' | 'poor'
    reasons: string[]
  }>
}
