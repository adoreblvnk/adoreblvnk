import adapter from '@sveltejs/adapter-static';
import contentCollections from '@content-collections/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import { viteStaticCopy } from 'vite-plugin-static-copy';

export default defineConfig({
  plugins: [
    sveltekit({
      compilerOptions: {
        // Force runes mode for the project, except for libraries. Can be removed in Svelte 6.
        runes: ({ filename }) =>
          filename.split(/[/\\]/).includes('node_modules') ? undefined : true,
      },
      adapter: adapter({
        pages: 'dist',
        assets: 'dist',
      }),
      // https://www.content-collections.dev/docs/quickstart/svelte-kit
      alias: {
        'content-collections': './.content-collections/generated',
      },
      files: {
        assets: 'public',
      },
      prerender: {
        handleUnseenRoutes({ routes, message }) {
          const unexpected = routes.filter((route) => route !== '/writings/[slug]');
          if (unexpected.length) throw new Error(message);
        },
      },
    }),
    contentCollections(),
    // https://github.com/sapphi-red/vite-plugin-static-copy
    viteStaticCopy({
      targets: [
        {
          src: 'src/writings/**/*.{avif,gif,jpeg,jpg,png,svg,webp}',
          dest: 'writings',
          rename: { stripBase: 2 },
        },
      ],
      silent: true,
    }),
  ],
});
