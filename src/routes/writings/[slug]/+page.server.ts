import type { PageServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import { allWritings } from 'content-collections';

// https://www.content-collections.dev/docs/quickstart/svelte-kit
export const load: PageServerLoad = ({ params }) => {
  const writing = allWritings.find(({ slug }) => slug === params.slug);
  if (!writing) error(404, `Could not find ${params.slug}`);
  return { writing };
};
