import * as THREE from 'three';
import { gsap } from 'gsap';
import type { DitherUniforms } from './dither-effect';

export type SculptureLook = 1 | 2 | 3;

export interface TrackerProjection {
  x: number;
  y: number;
  visible: boolean;
}

interface SculptureControllerOptions {
  onReady?: (controller: SculptureController) => void;
  onFrame?: (projections: TrackerProjection[]) => void;
  onStatus?: (ready: boolean) => void;
}

interface LookTarget {
  position: [number, number, number];
  scale: number;
  orientation: number;
  cardY: number;
  rowShear: number;
  staticSlice: number;
  cell: number;
  cols: number;
}

const WEB_RINGS = 8;
const WEB_SEGMENTS = 36;
const WEB_VERTEX_COUNT = WEB_RINGS * WEB_SEGMENTS;
const TAU = Math.PI * 2;

export class SculptureController {
  readonly sculptureGroup = new THREE.Group();
  readonly webGroup = new THREE.Group();

  width = 0;
  height = 0;
  camera: THREE.Camera | null = null;
  ditherUniforms: DitherUniforms | null = null;
  ready = false;
  paused = false;
  sceneAssetsAttached = false;
  elapsed = 0;
  appliedLook: string | null = null;
  scrollVelocity = 0;
  pointer = { x: 0, y: 0, targetX: 0, targetY: 0 };

  portrait: THREE.Mesh<THREE.PlaneGeometry, THREE.MeshBasicMaterial> | null = null;
  webGeometry: THREE.BufferGeometry | null = null;
  webThreadGeometry: THREE.BufferGeometry | null = null;
  webSurface: THREE.Mesh<THREE.BufferGeometry, THREE.ShaderMaterial> | null = null;
  webThreads: THREE.Mesh<THREE.BufferGeometry, THREE.ShaderMaterial> | null = null;
  webCardY = new THREE.Uniform(0.5);
  webResolution = new THREE.Uniform(new THREE.Vector2(1, 1));
  webPortraitRect = new THREE.Uniform(new THREE.Vector4(0, 0, 1, 1));
  portraitCorner = new THREE.Vector3();
  threadSegments: Array<[number, number]> = [];
  webBasePositions = new Float32Array(0);
  webAngles = new Float32Array(0);
  webRadii = new Float32Array(0);
  webPhases = new Float32Array(0);
  trackerVertexIndices: number[] = [];
  trackers: THREE.Object3D[] = [];
  trackerProjections: TrackerProjection[] = [];
  trackerVector = new THREE.Vector3();

  motion = {
    orientationZ: 0,
    spinOffset: 0,
    velocitySlice: 0,
    glitchTarget: 0,
    cameraOffset: 0,
    fold: 0,
  };

  constructor(private readonly callbacks: SculptureControllerOptions) {
    this.sculptureGroup.add(this.webGroup);
  }

  attachCamera(camera: THREE.Camera): void {
    this.camera = camera;
    this.maybeReady();
  }

  attachDither(uniforms: DitherUniforms): void {
    this.ditherUniforms = uniforms;
    this.webCardY.value = uniforms.uCardY.value;
    this.maybeReady();
  }

  attachSceneAssets(portraitTexture: THREE.Texture): void {
    if (this.sceneAssetsAttached) return;
    this.sceneAssetsAttached = true;

    portraitTexture.colorSpace = THREE.SRGBColorSpace;
    const portraitMaterial = new THREE.MeshBasicMaterial({
      map: portraitTexture,
      transparent: true,
      alphaTest: 0.015,
      depthTest: false,
      depthWrite: false,
      side: THREE.DoubleSide,
      toneMapped: false,
    });
    this.portrait = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), portraitMaterial);
    this.portrait.position.z = 0.34;
    this.portrait.renderOrder = 3;
    this.sculptureGroup.add(this.portrait);

    this.createConnectedWeb();
    this.maybeReady();
  }

  createWebMaterial(opacity: number): THREE.ShaderMaterial {
    return new THREE.ShaderMaterial({
      uniforms: {
        uCardY: this.webCardY,
        uResolution: this.webResolution,
        uPortraitRect: this.webPortraitRect,
        uPortraitMap: new THREE.Uniform(this.portrait?.material.map),
        uOpacity: new THREE.Uniform(opacity),
      },
      vertexShader: `
        void main() {
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform float uCardY;
        uniform vec2 uResolution;
        uniform vec4 uPortraitRect;
        uniform sampler2D uPortraitMap;
        uniform float uOpacity;

        void main() {
          vec2 screenUv = gl_FragCoord.xy / max(uResolution, vec2(1.0));
          vec2 portraitUv = (screenUv - uPortraitRect.xy) / uPortraitRect.zw;
          if (all(greaterThanEqual(portraitUv, vec2(0.0))) && all(lessThanEqual(portraitUv, vec2(1.0)))) {
            if (texture2D(uPortraitMap, portraitUv).a > 0.015) discard;
          }
          float paperField = step(uCardY, screenUv.y);
          vec3 coldPaper = vec3(0.812, 0.824, 0.824);
          vec3 ink = vec3(0.03);
          gl_FragColor = vec4(mix(coldPaper, ink, paperField), uOpacity);
        }
      `,
      transparent: true,
      side: THREE.DoubleSide,
      depthTest: false,
      depthWrite: false,
      toneMapped: false,
    });
  }

  createConnectedWeb(): void {
    const positions = new Float32Array(WEB_VERTEX_COUNT * 3);
    const indices: number[] = [];
    this.webAngles = new Float32Array(WEB_VERTEX_COUNT);
    this.webRadii = new Float32Array(WEB_VERTEX_COUNT);
    this.webPhases = new Float32Array(WEB_VERTEX_COUNT);

    for (let ring = 0; ring < WEB_RINGS; ring += 1) {
      const radialProgress = ring / (WEB_RINGS - 1);
      for (let segment = 0; segment < WEB_SEGMENTS; segment += 1) {
        const index = ring * WEB_SEGMENTS + segment;
        const angle = (segment / WEB_SEGMENTS) * TAU;
        const contour = Math.sin(angle * 3 + ring * 0.72) * 0.07
          + Math.cos(angle * 5 - ring * 0.38) * 0.035;
        const radius = 0.5 + radialProgress * 0.78 + contour;
        const upperLift = Math.max(0, Math.sin(angle)) * 0.13 * radialProgress;
        const rightPull = Math.max(0, Math.cos(angle)) * 0.18 * radialProgress;
        const x = Math.cos(angle) * radius * 1.12 + rightPull + 0.04;
        const y = Math.sin(angle) * radius * 1.24 + upperLift - 0.05;
        const z = -0.34
          + Math.sin(angle * 2 + radialProgress * 2.7) * 0.17
          + Math.cos(angle - radialProgress * 4.1) * 0.07;

        positions[index * 3] = x;
        positions[index * 3 + 1] = y;
        positions[index * 3 + 2] = z;
        this.webAngles[index] = angle;
        this.webRadii[index] = radialProgress;
        this.webPhases[index] = angle * 2.3 + ring * 0.83;
      }
    }

    for (let ring = 0; ring < WEB_RINGS - 1; ring += 1) {
      for (let segment = 0; segment < WEB_SEGMENTS; segment += 1) {
        const nextSegment = (segment + 1) % WEB_SEGMENTS;
        const a = ring * WEB_SEGMENTS + segment;
        const b = ring * WEB_SEGMENTS + nextSegment;
        const c = (ring + 1) * WEB_SEGMENTS + segment;
        const d = (ring + 1) * WEB_SEGMENTS + nextSegment;
        const alternate = (ring + segment) % 2 === 0;
        if (alternate) indices.push(a, c, d, a, d, b);
        else indices.push(a, c, b, b, c, d);
      }
    }

    this.webBasePositions = positions.slice();
    this.webGeometry = new THREE.BufferGeometry();
    this.webGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    this.webGeometry.setIndex(indices);
    this.webGeometry.computeVertexNormals();

    const surfaceMaterial = this.createWebMaterial(0.022);
    this.webSurface = new THREE.Mesh(this.webGeometry, surfaceMaterial);
    this.webSurface.layers.set(1);
    this.webSurface.renderOrder = 1;

    for (let ring = 0; ring < WEB_RINGS; ring += 1) {
      for (let segment = 0; segment < WEB_SEGMENTS; segment += 1) {
        const current = ring * WEB_SEGMENTS + segment;
        const next = ring * WEB_SEGMENTS + ((segment + 1) % WEB_SEGMENTS);
        this.threadSegments.push([current, next]);
        if (ring < WEB_RINGS - 1 && segment % 3 === 0) {
          this.threadSegments.push([current, (ring + 1) * WEB_SEGMENTS + segment]);
        }
      }
    }

    this.webThreadGeometry = new THREE.BufferGeometry();
    this.webThreadGeometry.setAttribute(
      'position',
      new THREE.BufferAttribute(new Float32Array(this.threadSegments.length * 12), 3),
    );
    const threadIndices: number[] = [];
    for (let segment = 0; segment < this.threadSegments.length; segment += 1) {
      const vertex = segment * 4;
      threadIndices.push(vertex, vertex + 1, vertex + 2, vertex, vertex + 2, vertex + 3);
    }
    this.webThreadGeometry.setIndex(threadIndices);

    const threadMaterial = this.createWebMaterial(0.46);
    this.webThreads = new THREE.Mesh(this.webThreadGeometry, threadMaterial);
    this.webThreads.layers.set(1);
    this.webThreads.renderOrder = 2;
    this.webGroup.add(this.webSurface, this.webThreads);
    this.updateThreadGeometry();

    this.trackerVertexIndices = [
      1 * WEB_SEGMENTS + 4,
      3 * WEB_SEGMENTS + 8,
      5 * WEB_SEGMENTS + 14,
      7 * WEB_SEGMENTS + 19,
      4 * WEB_SEGMENTS + 24,
      6 * WEB_SEGMENTS + 29,
      2 * WEB_SEGMENTS + 33,
    ];
    this.trackers = this.trackerVertexIndices.map((vertexIndex) => {
      const anchor = new THREE.Object3D();
      anchor.position.fromBufferAttribute(this.webGeometry!.getAttribute('position'), vertexIndex);
      this.webGroup.add(anchor);
      return anchor;
    });
    this.trackerProjections = this.trackers.map(() => ({ x: 0, y: 0, visible: false }));

    this.motion.cameraOffset = 0.5;
    gsap.to(this.motion, { cameraOffset: 0, duration: 1.8, ease: 'power4.out' });
    this.webGroup.scale.setScalar(0.82);
    gsap.to(this.webGroup.scale, {
      x: 1,
      y: 1,
      z: 1,
      duration: 1.8,
      ease: 'power4.out',
    });
  }

  maybeReady(): void {
    if (this.ready || !this.sceneAssetsAttached || !this.camera || !this.ditherUniforms) return;
    this.ready = true;
    this.applySculptureLayout();
    this.callbacks.onReady?.(this);
  }

  setContextAvailable(available: boolean): void {
    this.paused = !available;
    this.callbacks.onStatus?.(available && this.ready);
  }

  setViewport(width: number, height: number): void {
    this.width = width;
    this.height = height;
    this.applySculptureLayout();
  }

  setRenderResolution(width: number, height: number): void {
    this.webResolution.value.set(width, height);
  }

  setPointerTarget(x: number, y: number): void {
    this.pointer.targetX = x;
    this.pointer.targetY = y;
  }

  setScrollVelocity(velocity: number): void {
    this.scrollVelocity = velocity || 0;
  }

  applyLook(look: SculptureLook, { force = false, immediate = false } = {}): void {
    if (!this.ditherUniforms) return;

    const desktop = this.width > 768;
    const progress = gsap.utils.clamp(0, 1, (this.width - 768) / 512);
    const interpolate = (start: number, end: number): number => start + (end - start) * progress;
    const targets: Record<SculptureLook, LookTarget> = {
      1: {
        position: [interpolate(-0.25, 1.5), interpolate(0.05, 0.24), interpolate(-1.4, 0)],
        scale: interpolate(1.5, 1.978),
        orientation: 0,
        cardY: 0.5,
        rowShear: 0,
        staticSlice: 0,
        cell: 2.25,
        cols: 22,
      },
      2: {
        position: [desktop ? interpolate(-0.35, -1.2) : -0.32, desktop ? 0 : 0.52, desktop ? -0.8 : -1.1],
        scale: desktop ? 1.7802 : 1.15,
        orientation: 0.035,
        cardY: -0.01,
        rowShear: 0,
        staticSlice: desktop ? 0.38 : 0.2,
        cell: 2.75,
        cols: 14,
      },
      3: {
        position: [desktop ? 1.65 : 0.3, desktop ? -0.45 : -1.55, desktop ? 0.35 : -1.45],
        scale: desktop ? 1.3824 : 1.2,
        orientation: -0.05,
        cardY: 1.01,
        rowShear: 1,
        staticSlice: 0,
        cell: 2,
        cols: 22,
      },
    };
    const target = targets[look];

    const lookKey = `${look}:${desktop ? 'desktop' : 'mobile'}`;
    if (!force && this.appliedLook === lookKey) return;
    const previousLook = this.appliedLook?.split(':')[0];
    this.appliedLook = lookKey;

    if (!immediate && previousLook && previousLook !== String(look)) this.triggerGlitch(0.9);
    const uniforms = this.ditherUniforms;
    const transition = { duration: immediate ? 0 : 0.72, ease: 'power4.inOut', overwrite: 'auto' } as const;
    uniforms.uCols.value = target.cols;
    if (immediate) uniforms.uGlitch.value = 0;

    gsap.to(this.sculptureGroup.position, {
      x: target.position[0],
      y: target.position[1],
      z: target.position[2],
      ...transition,
    });
    gsap.to(this.sculptureGroup.scale, {
      x: target.scale,
      y: target.scale,
      z: target.scale,
      ...transition,
    });
    gsap.to(this.motion, { orientationZ: target.orientation, ...transition });
    const uniformTargets: Array<[THREE.Uniform<number>, number]> = [
      [uniforms.uCardY, target.cardY],
      [this.webCardY, target.cardY],
      [uniforms.uRowShear, target.rowShear],
      [uniforms.uStaticSlice, target.staticSlice],
      [uniforms.uCell, target.cell],
    ];
    uniformTargets.forEach(([uniform, value]) => {
      gsap.to(uniform, { value, ...transition, duration: immediate ? 0 : 0.82, overwrite: true });
    });
  }

  spinSculpture(rotations = 1, duration = 1.4): void {
    gsap.to(this.motion, {
      spinOffset: `+=${Math.PI * 2 * rotations}`,
      fold: 1,
      duration,
      ease: 'power3.inOut',
      overwrite: false,
      onComplete: () => gsap.to(this.motion, { fold: 0, duration: 0.9, ease: 'power4.out' }),
    });
  }

  applySculptureLayout(): void {
    const compact = this.width < 700;
    const portraitHeight = compact ? 1.863 : 2.162;
    if (this.portrait) this.portrait.scale.setScalar(portraitHeight);
    this.webGroup.scale.setScalar(compact ? 0.78 : 0.92);
  }

  updateThreadGeometry(): void {
    if (!this.webGeometry || !this.webThreadGeometry) return;
    const webPositions = (this.webGeometry.getAttribute('position') as THREE.BufferAttribute).array as Float32Array;
    const threadAttribute = this.webThreadGeometry.getAttribute('position') as THREE.BufferAttribute;
    const threadPositions = threadAttribute.array as Float32Array;

    this.threadSegments.forEach(([start, end], segmentIndex) => {
      const startOffset = start * 3;
      const endOffset = end * 3;
      const x1 = webPositions[startOffset];
      const y1 = webPositions[startOffset + 1];
      const z1 = webPositions[startOffset + 2] + 0.012;
      const x2 = webPositions[endOffset];
      const y2 = webPositions[endOffset + 1];
      const z2 = webPositions[endOffset + 2] + 0.012;
      const dx = x2 - x1;
      const dy = y2 - y1;
      const inverseLength = 1 / Math.max(Math.hypot(dx, dy), 0.0001);
      const width = 0.008;
      const nx = -dy * inverseLength * width;
      const ny = dx * inverseLength * width;
      const output = segmentIndex * 12;

      threadPositions[output] = x1 + nx;
      threadPositions[output + 1] = y1 + ny;
      threadPositions[output + 2] = z1;
      threadPositions[output + 3] = x1 - nx;
      threadPositions[output + 4] = y1 - ny;
      threadPositions[output + 5] = z1;
      threadPositions[output + 6] = x2 - nx;
      threadPositions[output + 7] = y2 - ny;
      threadPositions[output + 8] = z2;
      threadPositions[output + 9] = x2 + nx;
      threadPositions[output + 10] = y2 + ny;
      threadPositions[output + 11] = z2;
    });
    threadAttribute.needsUpdate = true;
  }

  updateWeb(): void {
    if (!this.webGeometry) return;
    const positionAttribute = this.webGeometry.getAttribute('position') as THREE.BufferAttribute;
    const positions = positionAttribute.array as Float32Array;
    const velocityEnergy = Math.min(Math.abs(this.scrollVelocity) * 0.006, 0.2);

    for (let index = 0; index < WEB_VERTEX_COUNT; index += 1) {
      const offset = index * 3;
      const angle = this.webAngles[index];
      const radialProgress = this.webRadii[index];
      const phase = this.webPhases[index];
      const breath = Math.sin(this.elapsed * 0.62 + phase) * (0.012 + radialProgress * 0.032);
      const travelingWave = Math.sin(this.elapsed * 2.4 + phase * 1.8) * velocityEnergy * radialProgress;
      const foldWave = Math.sin(angle * 2 + radialProgress * Math.PI) * this.motion.fold * 0.16;
      const tangentX = -Math.sin(angle);
      const tangentY = Math.cos(angle);

      positions[offset] = this.webBasePositions[offset] + tangentX * (breath + travelingWave) * 0.28;
      positions[offset + 1] = this.webBasePositions[offset + 1] + tangentY * (breath + travelingWave) * 0.2;
      positions[offset + 2] = this.webBasePositions[offset + 2] + breath + travelingWave + foldWave;
    }
    positionAttribute.needsUpdate = true;
    this.updateThreadGeometry();

    this.trackers.forEach((tracker, trackerIndex) => {
      tracker.position.fromBufferAttribute(positionAttribute, this.trackerVertexIndices[trackerIndex]);
    });
  }

  updatePortraitMask(): void {
    const portrait = this.portrait;
    const camera = this.camera;
    if (!portrait || !camera) return;
    portrait.updateWorldMatrix(true, false);
    const corners: Array<[number, number]> = [
      [-0.5, -0.5],
      [0.5, -0.5],
      [0.5, 0.5],
      [-0.5, 0.5],
    ];
    let minX = 1;
    let minY = 1;
    let maxX = 0;
    let maxY = 0;
    corners.forEach(([x, y]) => {
      this.portraitCorner.set(x, y, 0);
      portrait.localToWorld(this.portraitCorner);
      this.portraitCorner.project(camera);
      const screenX = this.portraitCorner.x * 0.5 + 0.5;
      const screenY = this.portraitCorner.y * 0.5 + 0.5;
      minX = Math.min(minX, screenX);
      minY = Math.min(minY, screenY);
      maxX = Math.max(maxX, screenX);
      maxY = Math.max(maxY, screenY);
    });
    this.webPortraitRect.value.set(minX, minY, maxX - minX, maxY - minY);
  }

  projectTrackers(): TrackerProjection[] {
    this.sculptureGroup.updateMatrixWorld(true);
    for (let index = 0; index < this.trackers.length; index += 1) {
      const projected = this.trackerProjections[index];
      this.trackers[index].getWorldPosition(this.trackerVector);
      this.trackerVector.project(this.camera!);
      projected.x = (this.trackerVector.x * 0.5 + 0.5) * this.width;
      projected.y = (-this.trackerVector.y * 0.5 + 0.5) * this.height;
      projected.visible = this.trackerVector.z >= -1 && this.trackerVector.z <= 1;
    }
    return this.trackerProjections;
  }

  triggerGlitch(amount: number): void {
    this.motion.glitchTarget = Math.max(this.motion.glitchTarget, amount);
  }

  update(deltaTime: number): void {
    if (!this.ready || this.paused || !this.camera || !this.ditherUniforms) return;
    this.elapsed += Math.min(deltaTime, 0.05);
    this.pointer.x += (this.pointer.targetX - this.pointer.x) * 0.07;
    this.pointer.y += (this.pointer.targetY - this.pointer.y) * 0.07;

    const pointerX = this.pointer.x;
    const pointerY = this.pointer.y;
    this.sculptureGroup.rotation.x = pointerY * 0.008;
    this.sculptureGroup.rotation.y = pointerX * 0.01;
    this.sculptureGroup.rotation.z = this.motion.orientationZ + pointerX * 0.004;
    this.webGroup.rotation.x = pointerY * 0.12;
    this.webGroup.rotation.y = pointerX * 0.08 + this.motion.spinOffset;
    this.webGroup.rotation.z = pointerX * 0.035;
    this.updateWeb();

    const uniforms = this.ditherUniforms;
    const velocityTarget = Math.min(Math.abs(this.scrollVelocity) * 0.0009, 0.16);
    this.motion.velocitySlice += (velocityTarget - this.motion.velocitySlice) * 0.18;
    const velocityGlitch = Math.min(Math.abs(this.scrollVelocity) * 0.0013, 1);
    this.motion.glitchTarget = Math.max(this.motion.glitchTarget, velocityGlitch);
    const glitch = uniforms.uGlitch;
    const attack = this.motion.glitchTarget > glitch.value ? 0.5 : 0.1;
    glitch.value += (this.motion.glitchTarget - glitch.value) * attack;
    this.motion.glitchTarget *= 0.9;
    uniforms.uTime.value = this.elapsed;
    uniforms.uVelocitySlice.value = this.motion.velocitySlice;
    this.scrollVelocity *= 0.88;

    this.camera.position.x = pointerX * 0.015;
    this.camera.position.y = pointerY * 0.01;
    this.camera.position.z = 8 + this.motion.cameraOffset;
    this.camera.lookAt(0, 0, 0);
    this.camera.updateMatrixWorld();
    this.sculptureGroup.updateMatrixWorld(true);
    this.updatePortraitMask();
    this.callbacks.onFrame?.(this.projectTrackers());
  }

  dispose(): void {
    gsap.killTweensOf(this.motion);
    gsap.killTweensOf(this.sculptureGroup.position);
    gsap.killTweensOf(this.sculptureGroup.scale);
    gsap.killTweensOf(this.webGroup.scale);
    this.portrait?.geometry.dispose();
    this.portrait?.material.dispose();
    this.webGeometry?.dispose();
    this.webThreadGeometry?.dispose();
    this.webSurface?.material.dispose();
    this.webThreads?.material.dispose();
  }
}
