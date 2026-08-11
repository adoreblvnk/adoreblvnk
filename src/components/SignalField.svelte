<script lang="ts">
  import { onDestroy } from 'svelte';
  import { Canvas } from '@threlte/core';
  import { NoToneMapping, SRGBColorSpace, WebGLRenderer } from 'three';
  import type { TrackerProjection } from '../lib/sculpture-controller';
  import { SculptureController } from '../lib/sculpture-controller';
  import PostProcessing from './PostProcessing.svelte';
  import Scene from './Scene.svelte';

  interface Props {
    onReady?: (controller: SculptureController) => void;
    onFrame?: (projections: TrackerProjection[]) => void;
    onStatus?: (ready: boolean) => void;
  }

  let { onReady, onFrame, onStatus }: Props = $props();
  const controller = new SculptureController({
    onReady: (sceneController) => onReady?.(sceneController),
    onFrame: (projections) => onFrame?.(projections),
    onStatus: (ready) => onStatus?.(ready),
  });

  const createRenderer = (canvas: HTMLCanvasElement): WebGLRenderer => new WebGLRenderer({
    canvas,
    antialias: true,
    alpha: true,
    powerPreference: 'high-performance',
  });

  onDestroy(() => controller.dispose());
</script>

<div class="signal-field" aria-hidden="true">
  <Canvas
    {createRenderer}
    colorSpace={SRGBColorSpace}
    toneMapping={NoToneMapping}
    dpr={[1, 2]}
    autoRender={false}
    renderMode="always"
  >
    <Scene {controller} />
    <PostProcessing {controller} />
  </Canvas>
</div>
