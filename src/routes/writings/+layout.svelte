<script lang="ts">
  import type { LayoutProps } from './$types';
  import 'github-markdown-css/github-markdown-dark.css';
  import './writings.css';

  let { children }: LayoutProps = $props();
</script>

<div class="writings-shell">
  {@render children()}
</div>
