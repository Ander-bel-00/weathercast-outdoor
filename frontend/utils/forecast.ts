export interface TimedForecastPoint {
  time: string
}

export function getInitialForecastDate(dates: string[], currentTime: string): string {
  const currentDate = currentTime.slice(0, 10)
  return dates.includes(currentDate) ? currentDate : dates[0] ?? ''
}

export function selectHoursForDay<T extends TimedForecastPoint>(
  hours: T[],
  date: string,
  currentTime: string,
): T[] {
  return hours
    .filter((hour) => hour.time.slice(0, 10) === date)
    .filter((hour) => date !== currentTime.slice(0, 10) || hour.time >= currentTime)
    .slice(0, 24)
}

export function formatForecastDay(
  date: string,
  index: number,
  language: 'en' | 'es',
  todayLabel: string,
  tomorrowLabel: string,
): string {
  if (index === 0) return todayLabel
  if (index === 1) return tomorrowLabel
  return new Intl.DateTimeFormat(language === 'en' ? 'en-US' : 'es-CO', {
    weekday: 'short',
    timeZone: 'UTC',
  }).format(new Date(`${date}T12:00:00Z`))
}
