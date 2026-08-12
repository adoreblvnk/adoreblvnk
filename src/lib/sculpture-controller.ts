import * as THREE from 'three';
import type { GLTF } from 'three/addons/loaders/GLTFLoader.js';
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

interface EntropyMetadata {
  entropy_clip: string;
  entropy_name: string;
  entropy_gain: number;
  entropy_attack: number;
  entropy_release: number;
}

interface AssemblyMetadata {
  assembly_clip: string;
  assembly_duration: number;
}

interface AuthoredMetadata extends Partial<EntropyMetadata>, Partial<AssemblyMetadata> {
  tracker_index?: number;
}

interface EntropyFamily {
  name: string;
  gain: number;
  attack: number;
  release: number;
  action: THREE.AnimationAction;
  speed: number;
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

export class SculptureController {
  readonly sculptureGroup = new THREE.Group();

  width = 0;
  height = 0;
  camera: THREE.Camera | null = null;
  ditherUniforms: DitherUniforms | null = null;
  ready = false;
  paused = false;
  reducedMotion = false;
  sceneAssetsAttached = false;
  elapsed = 0;
  appliedLook: string | null = null;
  scrollVelocity = 0;
  pointer = { x: 0, y: 0, targetX: 0, targetY: 0 };

  portrait: THREE.Mesh<THREE.PlaneGeometry, THREE.MeshBasicMaterial> | null = null;
  orbit: THREE.Group | null = null;
  mixer: THREE.AnimationMixer | null = null;
  entropyFamilies: EntropyFamily[] = [];
  trackers: THREE.Object3D[] = [];
  trackerProjections: TrackerProjection[] = [];
  trackerVector = new THREE.Vector3();

  motion = {
    orientationZ: 0,
    spinOffset: 0,
    velocitySlice: 0,
    glitchTarget: 0,
    cameraOffset: 0,
  };

  constructor(private readonly callbacks: SculptureControllerOptions) {}

  attachCamera(camera: THREE.Camera): void {
    this.camera = camera;
    this.maybeReady();
  }

  attachDither(uniforms: DitherUniforms): void {
    this.ditherUniforms = uniforms;
    this.maybeReady();
  }

  attachSceneAssets(portraitTexture: THREE.Texture, orbitModel: GLTF): void {
    if (this.sceneAssetsAttached) return;
    this.sceneAssetsAttached = true;

    portraitTexture.colorSpace = THREE.SRGBColorSpace;
    const portraitMaterial = new THREE.MeshBasicMaterial({
      map: portraitTexture,
      transparent: true,
      alphaTest: 0.015,
      depthTest: true,
      depthWrite: false,
      side: THREE.DoubleSide,
      toneMapped: false,
    });
    this.portrait = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), portraitMaterial);
    this.portrait.position.z = 0;
    this.portrait.renderOrder = 2;
    this.sculptureGroup.add(this.portrait);

    this.orbit = orbitModel.scene;
    this.orbit.traverse((node) => {
      if (!(node instanceof THREE.Mesh)) return;
      const materials: THREE.Material[] = Array.isArray(node.material) ? node.material : [node.material];
      materials.forEach((material) => {
        if ('flatShading' in material) material.flatShading = false;
        material.transparent = false;
        material.depthTest = true;
        material.depthWrite = true;
        material.needsUpdate = true;
      });
      node.renderOrder = 1;
    });
    this.sculptureGroup.add(this.orbit);

    this.configureAuthoredModel(orbitModel.animations);
    this.maybeReady();
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

  setPointerTarget(x: number, y: number): void {
    this.pointer.targetX = x;
    this.pointer.targetY = y;
  }

  setScrollVelocity(velocity: number): void {
    this.scrollVelocity = velocity || 0;
  }

  setReducedMotion(reduced: boolean): void {
    this.reducedMotion = reduced;
    this.pointer.targetX = 0;
    this.pointer.targetY = 0;
    this.motion.spinOffset = 0;
    this.entropyFamilies.forEach((family) => {
      family.action.paused = reduced;
      if (reduced) family.action.time = 0;
    });
    if (reduced) this.mixer?.update(0);
  }

  configureAuthoredModel(animations: THREE.AnimationClip[]): void {
    if (!this.orbit) return;
    this.mixer = new THREE.AnimationMixer(this.orbit);
    const families: EntropyMetadata[] = [];
    let assembly: AssemblyMetadata | undefined;

    this.orbit.traverse((node) => {
      const metadata = node.userData as AuthoredMetadata;
      if (metadata.entropy_clip) families.push(metadata as EntropyMetadata);
      if (Number.isInteger(metadata.tracker_index)) this.trackers[metadata.tracker_index as number] = node;
      if (metadata.assembly_clip) assembly = metadata as AssemblyMetadata;
    });
    this.trackerProjections = this.trackers.map(() => ({ x: 0, y: 0, visible: false }));

    const clip = (name: string): THREE.AnimationClip => {
      const result = THREE.AnimationClip.findByName(animations, name);
      if (!result) throw new Error(`Missing authored animation clip: ${name}`);
      return result;
    };
    this.entropyFamilies = families.map((metadata) => {
      const action = this.mixer!.clipAction(clip(metadata.entropy_clip));
      action.play();
      action.paused = this.reducedMotion;
      return {
        name: metadata.entropy_name,
        gain: metadata.entropy_gain,
        attack: metadata.entropy_attack,
        release: metadata.entropy_release,
        action,
        speed: 1,
      };
    });

    if (!assembly) throw new Error('Missing authored assembly metadata');
    const assemblyAction = this.mixer.clipAction(clip(assembly.assembly_clip));
    assemblyAction.setLoop(THREE.LoopOnce, 1);
    assemblyAction.clampWhenFinished = true;
    assemblyAction.play();
    if (this.reducedMotion) {
      assemblyAction.time = assemblyAction.getClip().duration;
      assemblyAction.paused = true;
      this.mixer.update(0);
      this.motion.cameraOffset = 0;
      return;
    }
    this.motion.cameraOffset = 0.65;
    gsap.to(this.motion, {
      cameraOffset: 0,
      duration: assembly.assembly_duration,
      ease: 'power4.out',
    });
  }


  applyLook(look: SculptureLook, { force = false, immediate = false } = {}): void {
    if (!this.ditherUniforms) return;

    const desktop = this.width > 768;
    const shortViewport = desktop && this.height < 720;
    const progress = gsap.utils.clamp(0, 1, (this.width - 768) / 512);
    const interpolate = (start: number, end: number): number => start + (end - start) * progress;
    const positionX = shortViewport ? interpolate(-1.9, -1.45) : desktop ? interpolate(0.70, 0.35) : 0.65;
    const positionY = shortViewport ? -1.45 : desktop ? interpolate(-1.30, -1.10) : -1.8;
    const positionScale = shortViewport ? interpolate(0.9, 1.05) : desktop ? interpolate(1.0, 1.35) : 0.85;
    const targets: Record<SculptureLook, LookTarget> = {
      1: {
        position: [interpolate(-0.25, 1.50), interpolate(0.05, 0.24), interpolate(-1.4, 0)],
        scale: interpolate(1.5, 1.978),
        orientation: 0, cardY: 0.5, rowShear: 0, staticSlice: 0, cell: 2.25, cols: 22,
      },
      2: {
        position: [positionX, positionY, desktop ? -0.8 : -1.1],
        scale: positionScale,
        orientation: 0.035, cardY: -0.01, rowShear: 0, staticSlice: desktop ? 0.38 : 0.2, cell: 2.75, cols: 14,
      },
      3: {
        position: [desktop ? 1.65 : 0.30, desktop ? -0.45 : -1.55, desktop ? 0.35 : -1.45],
        scale: desktop ? 1.3824 : 1.2,
        orientation: -0.05, cardY: 1.01, rowShear: 1, staticSlice: 0, cell: 2, cols: 22,
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
      x: target.position[0], y: target.position[1], z: target.position[2], ...transition,
    });
    gsap.to(this.sculptureGroup.scale, {
      x: target.scale, y: target.scale, z: target.scale, ...transition,
    });
    gsap.to(this.motion, { orientationZ: target.orientation, ...transition });
    const uniformTargets: Array<[THREE.Uniform<number>, number]> = [
      [uniforms.uCardY, target.cardY],
      [uniforms.uRowShear, target.rowShear],
      [uniforms.uStaticSlice, target.staticSlice],
      [uniforms.uCell, target.cell],
    ];
    uniformTargets.forEach(([uniform, value]) => {
      gsap.to(uniform, { value, ...transition, duration: immediate ? 0 : 0.82, overwrite: true });
    });
  }

  pulseSculpture(): void {
    if (this.reducedMotion) return;
    gsap.timeline({ defaults: { ease: 'sine.inOut', overwrite: true } })
      .to(this.motion, { spinOffset: 0.055, duration: 0.24 })
      .to(this.motion, { spinOffset: -0.038, duration: 0.32 })
      .to(this.motion, { spinOffset: 0, duration: 0.28 });
  }

  applySculptureLayout(): void {
    const compact = this.width < 700;
    const portraitHeight = compact ? 1.863 : 2.162;
    if (this.portrait) this.portrait.scale.setScalar(portraitHeight);
    if (this.orbit) this.orbit.scale.setScalar(0.92);
  }

  projectTrackers(): TrackerProjection[] {
    for (let index = 0; index < this.trackers.length; index += 1) {
      const projected = this.trackerProjections[index];
      this.trackers[index].getWorldPosition(this.trackerVector);
      this.trackerVector.project(this.camera!);
      projected.x = (this.trackerVector.x * 0.5 + 0.5) * this.width;
      projected.y = (-this.trackerVector.y * 0.5 + 0.5) * this.height;
      projected.visible = this.trackerVector.z <= 1;
    }
    return this.trackerProjections;
  }

  triggerGlitch(amount: number): void {
    this.motion.glitchTarget = Math.max(this.motion.glitchTarget, amount);
  }

  update(deltaTime: number): void {
    if (!this.ready || this.paused || !this.camera || !this.ditherUniforms) return;
    if (this.reducedMotion) {
      this.ditherUniforms.uTime.value = 0;
      this.callbacks.onFrame?.(this.projectTrackers());
      return;
    }
    this.elapsed += Math.min(deltaTime, 0.05);
    this.pointer.x += (this.pointer.targetX - this.pointer.x) * 0.07;
    this.pointer.y += (this.pointer.targetY - this.pointer.y) * 0.07;

    if (this.mixer) {
      const entropyTarget = Math.min(Math.sqrt(Math.abs(this.scrollVelocity)) * 0.12, 1.8);
      this.entropyFamilies.forEach((family) => {
        const targetSpeed = 1 + entropyTarget * family.gain;
        const response = targetSpeed > family.speed ? family.attack : family.release;
        family.speed += (targetSpeed - family.speed) * response;
        family.action.timeScale = family.speed;
      });
      this.mixer.update(deltaTime);
    }

    const pointerX = this.pointer.x;
    const pointerY = this.pointer.y;
    this.sculptureGroup.rotation.x = pointerY * 0.008;
    this.sculptureGroup.rotation.y = pointerX * 0.010;
    this.sculptureGroup.rotation.z = this.motion.orientationZ + pointerX * 0.004;
    if (this.orbit) {
      this.orbit.rotation.x = pointerY * 0.18;
      this.orbit.rotation.y = pointerX * 0.10;
      this.orbit.rotation.z = pointerX * 0.07 + this.motion.spinOffset;
    }

    const uniforms = this.ditherUniforms;
    const velocityTarget = Math.min(Math.abs(this.scrollVelocity) * 0.0009, 0.16);
    this.motion.velocitySlice += (velocityTarget - this.motion.velocitySlice) * 0.18;
    const velocityGlitch = Math.min(Math.abs(this.scrollVelocity) * 0.0013, 1);
    this.motion.glitchTarget = Math.max(this.motion.glitchTarget, velocityGlitch);
    const glitch = uniforms.uGlitch;
    const attack = this.motion.glitchTarget > glitch.value ? 0.5 : 0.10;
    glitch.value += (this.motion.glitchTarget - glitch.value) * attack;
    this.motion.glitchTarget *= 0.90;
    uniforms.uTime.value = this.elapsed;
    uniforms.uVelocitySlice.value = this.motion.velocitySlice;
    this.scrollVelocity *= 0.88;

    this.camera.position.x = pointerX * 0.015;
    this.camera.position.y = pointerY * 0.010;
    this.camera.position.z = 8 + this.motion.cameraOffset;
    this.camera.lookAt(0, 0, 0);
    this.callbacks.onFrame?.(this.projectTrackers());
  }

  dispose(): void {
    gsap.killTweensOf(this.motion);
    gsap.killTweensOf(this.sculptureGroup.position);
    gsap.killTweensOf(this.sculptureGroup.scale);
    this.mixer?.stopAllAction();
  }
}
