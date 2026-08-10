<script lang="ts">
  import { T, useLoader, useTask, useThrelte } from '@threlte/core';
  import { TextureLoader } from 'three';
  import type { SculptureController } from '../lib/sculpture-controller';

  let { controller }: { controller: SculptureController } = $props();
  const { camera, canvas, size } = useThrelte();
  const portraitTexture = useLoader(TextureLoader).load('/images/portrait.png');

  $effect(() => {
    controller.attachCamera($camera);
  });

  $effect(() => {
    controller.setViewport($size.width, $size.height);
  });

  $effect(() => {
    if ($portraitTexture) controller.attachSceneAssets($portraitTexture);
  });

  $effect(() => {
    const handleLost = (event: Event) => {
      event.preventDefault();
      controller.setContextAvailable(false);
    };
    const handleRestored = () => controller.setContextAvailable(true);
    canvas.addEventListener('webglcontextlost', handleLost);
    canvas.addEventListener('webglcontextrestored', handleRestored);
    return () => {
      canvas.removeEventListener('webglcontextlost', handleLost);
      canvas.removeEventListener('webglcontextrestored', handleRestored);
    };
  });

  useTask((delta) => controller.update(delta));
</script>

<T.PerspectiveCamera makeDefault fov={38} near={0.1} far={100} position={[0, 0, 8]} />
<T.DirectionalLight color={0xffffff} intensity={3.4} position={[4, 5, 7]} />
<T.DirectionalLight color={0xcfd2d2} intensity={1.8} position={[-5, -1, 4]} />
<T.HemisphereLight args={[0xffffff, 0x161616, 1.35]} />
<T is={controller.sculptureGroup} />
