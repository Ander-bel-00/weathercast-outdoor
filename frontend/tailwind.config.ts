import type { Config } from 'tailwindcss'

export default <Partial<Config>>{
  darkMode: ['selector', '[data-theme="dark"]'],
  theme: {
    extend: {},
  },
}
