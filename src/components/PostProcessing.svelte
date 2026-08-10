<script lang="ts">
  import { onDestroy, untrack } from 'svelte';
  import { useTask, useThrelte } from '@threlte/core';
  import { EffectComposer, EffectPass, RenderPass } from 'postprocessing';
  import { Vector2 } from 'three';
  import { DitherEffect } from '../lib/dither-effect';
  import type { SculptureController } from '../lib/sculpture-controller';

  let { controller }: { controller: SculptureController } = $props();
  const { renderer, scene, camera, size, renderStage } = useThrelte();
  const composer = new EffectComposer(renderer);
  const ditherEffect = new DitherEffect();
  const drawingBufferSize = new Vector2();
  untrack(() => controller.attachDither(ditherEffect.values));

  $effect(() => {
    composer.removeAllPasses();
    composer.addPass(new RenderPass(scene, $camera));
    composer.addPass(new EffectPass($camera, ditherEffect));
  });

  $effect(() => {
    composer.setSize($size.width, $size.height);
    renderer.getDrawingBufferSize(drawingBufferSize);
    controller.setRenderResolution(drawingBufferSize.x, drawingBufferSize.y);
  });

  useTask(
    (delta) => {
      const activeCamera = $camera;
      activeCamera.layers.set(0);
      composer.render(delta);
      renderer.autoClear = false;
      activeCamera.layers.set(1);
      renderer.render(scene, activeCamera);
      activeCamera.layers.set(0);
      renderer.autoClear = true;
    },
    { stage: renderStage, autoInvalidate: false },
  );

  onDestroy(() => {
    composer.dispose();
    ditherEffect.dispose();
  });
</script>
