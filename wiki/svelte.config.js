import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

export default {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({ fallback: '404.html' }),
    paths: { base: '/get_domed' },
    prerender: {
      handleHttpError: 'warn',
      crawl: true,
      origin: 'https://cybaxx.github.io',
    }
  }
};
