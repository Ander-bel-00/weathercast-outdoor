import assert from 'node:assert/strict'
import test from 'node:test'
import { formatForecastDay, getInitialForecastDate, selectHoursForDay } from './forecast.ts'

test('initial forecast date selects today when it is available', () => {
  assert.equal(
    getInitialForecastDate(['2026-10-25', '2026-10-26'], '2026-10-25T18:00'),
    '2026-10-25',
  )
})

test('initial forecast date falls back to the first available day', () => {
  assert.equal(getInitialForecastDate(['2026-10-26'], '2026-10-25T23:30'), '2026-10-26')
  assert.equal(getInitialForecastDate([], '2026-10-25T23:30'), '')
})

test('selecting today omits elapsed hours and never includes another day', () => {
  const hours = [
    { time: '2026-10-25T17:00' },
    { time: '2026-10-25T18:00' },
    { time: '2026-10-26T00:00' },
  ]

  assert.deepEqual(
    selectHoursForDay(hours, '2026-10-25', '2026-10-25T18:00'),
    [{ time: '2026-10-25T18:00' }],
  )
})

test('selecting a future day returns its full hourly series', () => {
  const hours = [
    { time: '2026-10-25T18:00' },
    { time: '2026-10-26T00:00' },
    { time: '2026-10-26T01:00' },
  ]

  assert.deepEqual(
    selectHoursForDay(hours, '2026-10-26', '2026-10-25T18:00'),
    [{ time: '2026-10-26T00:00' }, { time: '2026-10-26T01:00' }],
  )
})

test('day labels are localized and later dates use a stable timezone', () => {
  assert.equal(formatForecastDay('2026-10-25', 0, 'es', 'Hoy', 'Mañana'), 'Hoy')
  assert.equal(formatForecastDay('2026-10-26', 1, 'en', 'Today', 'Tomorrow'), 'Tomorrow')
  assert.equal(formatForecastDay('2026-10-27', 2, 'en', 'Today', 'Tomorrow'), 'Tue')
})
