import { defineCollection, defineConfig } from '@content-collections/core';
import { compileMarkdown } from '@content-collections/markdown';
import { transformerCopyButton } from '@rehype-pretty/transformers';
import rehypeSlug from 'rehype-slug';
import rehypePrettyCode from 'rehype-pretty-code';
import remarkGfm from 'remark-gfm';
import { z } from 'zod';

// https://www.content-collections.dev/docs/quickstart/svelte-kit
const writings = defineCollection({
  name: 'writings',
  directory: 'src/writings',
  include: '*/index.md',
  schema: z.object({
    title: z.string().min(1),
    summary: z.string().min(1),
    date: z.coerce.date().transform((date) => date.toISOString().slice(0, 10)),
    tags: z.array(z.string()).default([]),
    content: z.string(),
  }),
  // https://www.content-collections.dev/docs/content/markdown
  transform: async (document, context) => {
    const slug = document._meta.path.replace(/\/index\.md$/i, '');
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) {
      throw new Error(`${document._meta.filePath}: directory must be lowercase kebab-case`);
    }
    const html = await compileMarkdown(context, document, {
      allowDangerousHtml: true,
      remarkPlugins: [remarkGfm],
      rehypePlugins: [
        rehypeSlug,
        [rehypePrettyCode, {
          defaultLang: { block: 'plaintext' },
          theme: 'vesper',
          transformers: [transformerCopyButton({ visibility: 'always', feedbackDuration: 2_000 })],
        }],
      ],
    });
    const { content: _content, _meta, ...metadata } = document;
    return { ...metadata, slug, html };
  },
});

export default defineConfig({ content: [writings] });