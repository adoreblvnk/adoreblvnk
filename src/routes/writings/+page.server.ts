import { allWritings } from 'content-collections';
import type { PageServerLoad } from './$types';

// https://www.content-collections.dev/docs/quickstart/svelte-kit
export const load: PageServerLoad = () => ({
  writings: allWritings
    .toSorted((left, right) => right.date.localeCompare(left.date))
    .map(({ html, ...writing }) => writing),
});
