<script lang="ts">
  import type { PageProps } from './$types';

  let { data }: PageProps = $props();
</script>

<svelte:head>
  <title>{data.writing.title} | adore_blvnk</title>
  <meta name="description" content={data.writing.summary}>
  <meta property="og:title" content={data.writing.title}>
  <meta property="og:description" content={data.writing.summary}>
  <meta property="og:type" content="article">
  <meta property="og:url" content={`https://adoreblvnk.com/writings/${data.writing.slug}/`}>
  <meta property="article:published_time" content={data.writing.date}>
</svelte:head>

<!-- https://www.content-collections.dev/docs/quickstart/svelte-kit -->
<main class="writing-page">
  <header class="writing-header">
    <h1>{data.writing.title}</h1>
    <p>{data.writing.summary}</p>
    <div class="writing-meta">
      <time class="writing-date" datetime={data.writing.date}>{data.writing.date}</time>
      {#if data.writing.tags.length}
        <ul class="tag-list" aria-label="Tags">
          {#each data.writing.tags as tag}<li>{tag}</li>{/each}
        </ul>
      {/if}
    </div>
  </header>

  <article class="writing-content markdown-body">
    <!-- https://www.content-collections.dev/docs/content/markdown -->
    {@html data.writing.html}
  </article>
</main>
