import * as THREE from 'three';
import type { GLTF } from 'three/addons/loaders/GLTFLoader.js';
import { gsap } from 'gsap';
import type { DitherUniforms } from './dither-effect';

export type SculptureLook = 1 | 2 | 3;

interface SculptureControllerOptions {
  onReady?: (controller: SculptureController) => void;
  onStatus?: (ready: boolean) => void;
}

interface AuthoredMetadata {
  veil_clip?: string;
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
  veil: THREE.Group | null = null;
  mixer: THREE.AnimationMixer | null = null;
  masterAction: THREE.AnimationAction | null = null;
  masterSpeed = 1;

  motion = {
    orientationZ: 0,
    turnOffset: 0,
    velocitySlice: 0,
    glitchTarget: 0,
    cameraOffset: 0,
    turn: 0,
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

  attachSceneAssets(portraitTexture: THREE.Texture, veilModel: GLTF): void {
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
    this.portrait.renderOrder = 2;
    this.sculptureGroup.add(this.portrait);

    this.veil = veilModel.scene;
    const sourceVeilMaterials = new Set<THREE.Material>();
    this.veil.traverse((node) => {
      if (!(node instanceof THREE.Mesh)) return;
      const moduleIndex = Number(node.name.match(/(\d+)$/)?.[1] ?? 0);
      const foregroundModule = moduleIndex === 1 || moduleIndex === 5 || moduleIndex === 9;
      const sourceMaterials: THREE.Material[] = Array.isArray(node.material) ? node.material : [node.material];
      const materials = sourceMaterials.map((sourceMaterial) => {
        sourceVeilMaterials.add(sourceMaterial);
        const material = sourceMaterial.clone();
        if (material instanceof THREE.MeshStandardMaterial) {
          const phase = (moduleIndex / 13) * Math.PI * 2;
          material.color.setScalar(0.30 + Math.cos(phase) * 0.08);
          material.emissive.setScalar(0.56 + Math.sin(phase) * 0.14);
          material.emissiveIntensity = 1;
          material.roughness = 1;
          material.metalness = 0;
          material.flatShading = true;
        }
        material.side = THREE.DoubleSide;
        material.transparent = false;
        material.opacity = 1;
        material.depthTest = !foregroundModule;
        material.depthWrite = !foregroundModule;
        material.needsUpdate = true;
        return material;
      });
      node.material = Array.isArray(node.material) ? materials : materials[0];
      node.renderOrder = foregroundModule ? 3 : 1;
    });
    sourceVeilMaterials.forEach((material) => material.dispose());
    this.sculptureGroup.add(this.veil);

    this.configureAuthoredModel(veilModel.animations);
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

  setReducedMotion(reduced: boolean): void {
    this.reducedMotion = reduced;
    if (this.masterAction) {
      if (reduced) {
        this.masterAction.reset();
        this.mixer?.setTime(0);
      }
      this.masterAction.paused = reduced;
    }
    if (reduced) {
      this.pointer.x = 0;
      this.pointer.y = 0;
      this.pointer.targetX = 0;
      this.pointer.targetY = 0;
      this.scrollVelocity = 0;
      this.elapsed = 0;
      gsap.killTweensOf(this.motion);
      gsap.killTweensOf(this.sculptureGroup.position);
      gsap.killTweensOf(this.sculptureGroup.scale);
      if (this.camera) gsap.killTweensOf(this.camera.position);
      if (this.ditherUniforms) {
        gsap.killTweensOf(this.ditherUniforms.uCardY);
        gsap.killTweensOf(this.ditherUniforms.uRowShear);
        gsap.killTweensOf(this.ditherUniforms.uStaticSlice);
        gsap.killTweensOf(this.ditherUniforms.uCell);
        gsap.killTweensOf(this.ditherUniforms.uGlitch);
        gsap.killTweensOf(this.ditherUniforms.uVelocitySlice);
        this.ditherUniforms.uGlitch.value = 0;
        this.ditherUniforms.uVelocitySlice.value = 0;
        this.ditherUniforms.uTime.value = 0;
      }
      this.motion.glitchTarget = 0;
      this.motion.velocitySlice = 0;
      this.motion.turn = 0;
      this.motion.turnOffset = 0;
      if (this.appliedLook) {
        const look = Number(this.appliedLook.split(':')[0]) as SculptureLook;
        this.applyLook(look, { force: true, immediate: true });
      }
    }
  }

  setViewport(width: number, height: number): void {
    const viewportChanged = width !== this.width || height !== this.height;
    this.width = width;
    this.height = height;
    this.applySculptureLayout();
    if (viewportChanged && this.ready && this.appliedLook) {
      const look = Number(this.appliedLook.split(':')[0]) as SculptureLook;
      this.applyLook(look, { force: true, immediate: true });
    }
  }

  setPointerTarget(x: number, y: number): void {
    if (this.reducedMotion) return;
    this.pointer.targetX = x;
    this.pointer.targetY = y;
  }

  setScrollVelocity(velocity: number): void {
    if (this.reducedMotion) return;
    this.scrollVelocity = velocity || 0;
  }

  configureAuthoredModel(animations: THREE.AnimationClip[]): void {
    if (!this.veil) return;
    this.mixer = new THREE.AnimationMixer(this.veil);
    let masterClip: string | undefined;

    this.veil.traverse((node) => {
      const metadata = node.userData as AuthoredMetadata;
      if (metadata.veil_clip) masterClip = metadata.veil_clip;
    });

    if (!masterClip) throw new Error('Missing authored veil animation metadata');
    const clip = THREE.AnimationClip.findByName(animations, masterClip);
    if (!clip) throw new Error(`Missing authored animation clip: ${masterClip}`);
    this.masterAction = this.mixer.clipAction(clip);
    this.masterAction.play();
    this.masterAction.paused = this.reducedMotion;
    this.motion.cameraOffset = 0.65;
    gsap.to(this.motion, {
      cameraOffset: 0,
      duration: this.reducedMotion ? 0 : 1.45,
      ease: 'power4.out',
    });
  }

  applyLook(look: SculptureLook, { force = false, immediate = false } = {}): void {
    if (!this.ditherUniforms) return;

    const desktop = this.width > 900;
    const tablet = this.width > 768 && !desktop;
    const progress = gsap.utils.clamp(0, 1, (this.width - 768) / 512);
    const interpolate = (start: number, end: number): number => start + (end - start) * progress;
    const targets: Record<SculptureLook, LookTarget> = {
      1: {
        position: tablet
          ? [0.55, 0.95, -1.15]
          : [interpolate(-0.1, 1.3), interpolate(0.4, 0.1), interpolate(-1.6, 0)],
        scale: tablet ? 1.1 : interpolate(1.2, 1.6),
        orientation: 0, cardY: 0.5, rowShear: 0, staticSlice: 0, cell: desktop ? 2.25 : tablet ? 1.5 : 1.0, cols: 22,
      },
      2: {
        position: [desktop ? 1.55 : tablet ? 1.25 : 0.35, desktop ? -1.80 : tablet ? 0.75 : 0.05, desktop ? -0.55 : -1.0],
        scale: desktop ? 0.55 : tablet ? 0.75 : 0.70,
        orientation: desktop ? 0.035 : -0.08, cardY: -0.01, rowShear: 0, staticSlice: desktop ? 0.38 : 0.2, cell: desktop ? 2.75 : tablet ? 1.5 : 1.0, cols: 14,
      },
      3: {
        position: [desktop ? 1.95 : tablet ? 0.90 : 0.40, desktop ? -0.68 : tablet ? -2.25 : -2.10, desktop ? 0.35 : -1.25],
        scale: desktop ? 0.95 : tablet ? 0.75 : 0.70,
        orientation: -0.05, cardY: 1.01, rowShear: 1, staticSlice: 0, cell: desktop ? 2.0 : tablet ? 1.5 : 1.0, cols: 22,
      },
    };
    const target = targets[look];

    const lookKey = `${look}:${desktop ? 'desktop' : 'mobile'}`;
    if (!force && this.appliedLook === lookKey) return;
    const previousLook = this.appliedLook?.split(':')[0];
    this.appliedLook = lookKey;

    if (!immediate && previousLook && previousLook !== String(look)) this.triggerGlitch(0.9);
    const uniforms = this.ditherUniforms;
    const transition = {
      duration: immediate || this.reducedMotion ? 0 : 0.72,
      ease: 'power4.inOut',
      overwrite: 'auto',
    } as const;
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
      gsap.to(uniform, {
        value,
        ...transition,
        duration: immediate || this.reducedMotion ? 0 : 0.82,
        overwrite: true,
      });
    });
  }

  turnSculpture(rotations = 1, duration = 1.4): void {
    if (this.reducedMotion) {
      this.motion.turnOffset += Math.PI * 0.5 * rotations;
      return;
    }
    gsap.to(this.motion, {
      turnOffset: `+=${Math.PI * 2 * rotations}`,
      duration,
      ease: 'power3.inOut',
      overwrite: false,
    });
  }

  applySculptureLayout(): void {
    const compact = this.width < 700;
    const portraitHeight = compact ? 1.863 : 2.162;
    if (this.portrait) this.portrait.scale.setScalar(portraitHeight);
    const tablet = this.width >= 700 && this.width <= 900;
    if (this.veil) this.veil.scale.setScalar(compact ? 0.32 : tablet ? 0.36 : 0.40);
  }


  triggerGlitch(amount: number): void {
    if (this.reducedMotion) return;
    this.motion.glitchTarget = Math.max(this.motion.glitchTarget, amount);
  }

  update(deltaTime: number): void {
    if (!this.ready || this.paused || !this.camera || !this.ditherUniforms) return;
    if (!this.reducedMotion) this.elapsed += Math.min(deltaTime, 0.05);
    this.pointer.x += (this.pointer.targetX - this.pointer.x) * 0.07;
    this.pointer.y += (this.pointer.targetY - this.pointer.y) * 0.07;

    if (this.mixer && !this.reducedMotion) {
      const targetSpeed = 1 + Math.min(Math.sqrt(Math.abs(this.scrollVelocity)) * 0.16, 1.6);
      this.masterSpeed += (targetSpeed - this.masterSpeed) * (targetSpeed > this.masterSpeed ? 0.18 : 0.035);
      if (this.masterAction) this.masterAction.timeScale = this.masterSpeed;
      this.mixer.update(deltaTime);
    }

    const pointerX = this.pointer.x;
    const pointerY = this.pointer.y;
    this.sculptureGroup.rotation.x = pointerY * 0.008;
    this.sculptureGroup.rotation.y = pointerX * 0.010;
    this.sculptureGroup.rotation.z = this.motion.orientationZ + pointerX * 0.004;
    if (this.veil) {
      const scrollTurn = Math.min(Math.abs(this.scrollVelocity) * 0.00035, 0.08);
      if (!this.reducedMotion) {
        const ambientTurn = Math.sin(this.elapsed * 0.42) * (0.14 + scrollTurn);
        const turnEase = 1 - Math.exp(-deltaTime * 5);
        this.motion.turn += (ambientTurn - this.motion.turn) * turnEase;
      }
      this.veil.rotation.x = Math.PI / 2 + pointerY * 0.11;
      this.veil.rotation.y = this.motion.turn + pointerX * 0.10 + this.motion.turnOffset;
      const compact = this.width < 700;
      const tablet = this.width >= 700 && this.width <= 900;
      const ambientSway = this.reducedMotion ? 0 : Math.sin(this.elapsed * 0.34) * 0.055;
      const ambientFloat = this.reducedMotion ? 0 : Math.sin(this.elapsed * 0.55) * 0.045;
      this.veil.rotation.z = -0.30 + pointerX * 0.035 + ambientSway;
      this.veil.position.x = compact ? 0.80 : tablet ? 0.90 : 1.0;
      this.veil.position.y = (compact ? -0.35 : tablet ? -0.45 : -0.55) + ambientFloat;
      this.veil.position.z = -0.12;
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
  }

  dispose(): void {
    gsap.killTweensOf(this.motion);
    gsap.killTweensOf(this.sculptureGroup.position);
    gsap.killTweensOf(this.sculptureGroup.scale);
    if (this.camera) gsap.killTweensOf(this.camera.position);
    if (this.ditherUniforms) {
      gsap.killTweensOf(this.ditherUniforms.uCardY);
      gsap.killTweensOf(this.ditherUniforms.uRowShear);
      gsap.killTweensOf(this.ditherUniforms.uStaticSlice);
      gsap.killTweensOf(this.ditherUniforms.uCell);
      gsap.killTweensOf(this.ditherUniforms.uGlitch);
      gsap.killTweensOf(this.ditherUniforms.uVelocitySlice);
    }
    this.mixer?.stopAllAction();
  }
}
