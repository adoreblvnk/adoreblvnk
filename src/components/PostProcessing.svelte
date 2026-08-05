<script lang="ts">
  import { onDestroy, untrack } from 'svelte';
  import { useTask, useThrelte } from '@threlte/core';
  import { EffectComposer, EffectPass, RenderPass } from 'postprocessing';
  import { DitherEffect } from '../lib/dither-effect';
  import type { SculptureController } from '../lib/sculpture-controller';

  let { controller }: { controller: SculptureController } = $props();
  const { renderer, scene, camera, size, renderStage } = useThrelte();
  const composer = new EffectComposer(renderer);
  const ditherEffect = new DitherEffect();
  untrack(() => controller.attachDither(ditherEffect.values));

  $effect(() => {
    composer.removeAllPasses();
    composer.addPass(new RenderPass(scene, $camera));
    composer.addPass(new EffectPass($camera, ditherEffect));
  });

  $effect(() => {
    composer.setSize($size.width, $size.height);
  });

  useTask(
    (delta) => composer.render(delta),
    { stage: renderStage, autoInvalidate: false },
  );

  onDestroy(() => {
    composer.dispose();
    ditherEffect.dispose();
  });
</script>
