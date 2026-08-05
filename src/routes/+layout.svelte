<script lang="ts">
  import type { LayoutProps } from './$types';
  import '../style.css';
  import { scramble } from '../lib/scramble';

  let { children }: LayoutProps = $props();
</script>

<header class="masthead">
  <a href="/" class="logo-link" aria-label="adore_blvnk home" use:scramble>adore_blvnk</a>
  <a href="/writings/" class="writings-portal" use:scramble>WRITINGS ↗</a>
</header>

{@render children()}
