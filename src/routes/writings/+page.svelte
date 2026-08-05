<script lang="ts">
  import type { PageProps } from './$types';

  let { data }: PageProps = $props();
</script>

<svelte:head>
  <title>Writings | adore_blvnk</title>
  <meta name="description" content="Published writings by adore_blvnk.">
  <meta property="og:title" content="Writings | adore_blvnk">
  <meta property="og:description" content="Published writings by adore_blvnk.">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://adoreblvnk.com/writings/">
</svelte:head>

<!-- https://www.content-collections.dev/docs/quickstart/svelte-kit -->
<main class="writings-index">
  <p class="writings-label">WRITINGS / INDEX</p>
  <h1>Writing in progress.</h1>

  {#if data.writings.length}
    <ol class="writing-list">
      {#each data.writings as writing}
        <li>
          <a href={`/writings/${writing.slug}/`}>
            <time datetime={writing.date}>{writing.date.replaceAll('-', '.')}</time>
            <span>{writing.title}</span>
            <small>{writing.summary}</small>
          </a>
        </li>
      {/each}
    </ol>
  {:else}
    <p class="empty-index">No writings yet.</p>
  {/if}
</main>
