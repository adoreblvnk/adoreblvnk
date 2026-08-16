import * as THREE from 'three';
import type { GLTF } from 'three/addons/loaders/GLTFLoader.js';
import type { DitherUniforms } from './dither-effect';

export type WorkstationSection = 'identity' | 'position' | 'contact';
export type WorkstationLook = 1 | 2 | 3;
type SequenceState = 'IDENTITY' | 'POSITION' | 'CONTACT';

export interface TrackerProjection {
  x: number;
  y: number;
  visible: boolean;
  label: string;
}

interface WorkstationControllerOptions {
  onReady?: (controller: WorkstationController) => void;
  onFrame?: (projections: TrackerProjection[]) => void;
  onStatus?: (ready: boolean) => void;
}

interface StateAnchors {
  camera: THREE.Vector3;
  target: THREE.Vector3;
  portrait: THREE.Vector3;
}

interface TerminalLine {
  text: string;
  start: number;
  duration: number;
  mode: 'type' | 'print';
  bright?: boolean;
}

const STATES: SequenceState[] = ['IDENTITY', 'POSITION', 'CONTACT'];
const REDUCED_MOTION_TIME = 10.5;
const TERMINAL_CYCLE = 12;
const TERMINAL_STATIC_TIME = 10.5;
const TERMINAL_LINES: TerminalLine[] = [
  { text: 'adore@debian:~/src/workstation', start: 0.2, duration: 1.2, mode: 'type', bright: true },
  { text: '$ cargo build --release', start: 1.55, duration: 1.15, mode: 'type', bright: true },
  { text: '   Compiling proc-macro2 v1.0.95', start: 2.95, duration: 0.16, mode: 'print' },
  { text: '   Compiling serde v1.0.219', start: 3.35, duration: 0.16, mode: 'print' },
  { text: '   Compiling tokio v1.47.1', start: 3.75, duration: 0.16, mode: 'print' },
  { text: '   Compiling workstation v0.1.0', start: 4.15, duration: 0.16, mode: 'print' },
  { text: '    Finished release [optimized] in 3.81s', start: 4.85, duration: 0.18, mode: 'print', bright: true },
  { text: '$ cargo test --release', start: 5.45, duration: 1.1, mode: 'type', bright: true },
  { text: 'running 12 tests ............', start: 6.8, duration: 0.18, mode: 'print' },
  { text: 'test result: ok. 12 passed; 0 failed', start: 7.45, duration: 0.18, mode: 'print', bright: true },
];
const STATE_TONE = {
  IDENTITY: { cardY: 0.50, cell: 2.25, cols: 22 },
  POSITION: { cardY: -0.01, cell: 2.75, cols: 14 },
  CONTACT: { cardY: 1.01, cell: 2.00, cols: 22 },
} as const;

const STATE_ORIENTATION_Z = {
  IDENTITY: 0,
  POSITION: 0.035,
  CONTACT: -0.05,
} as const;

const STATE_MODEL_X = {
  desktop: { IDENTITY: 6.80, POSITION: -1.40, CONTACT: 4.20 },
  compact: { IDENTITY: 4.50, POSITION: 3.70, CONTACT: 5.60 },
} as const;

const STATE_MODEL_Y = {
  desktop: { IDENTITY: -2.80, POSITION: -0.04, CONTACT: -1.30 },
  compact: { IDENTITY: -2.30, POSITION: -5.30, CONTACT: -1.30 },
} as const;

const STATE_MODEL_Z = {
  desktop: { IDENTITY: -0.80, POSITION: 0.35, CONTACT: -0.80 },
  compact: { IDENTITY: -1.00, POSITION: 0.15, CONTACT: -1.25 },
} as const;

const STATE_MODEL_SCALE = {
  desktop: { IDENTITY: 0.65, POSITION: 0.64, CONTACT: 0.64 },
  compact: { IDENTITY: 0.55, POSITION: 0.24, CONTACT: 0.50 },
} as const;

const STATE_MODEL_YAW = {
  IDENTITY: -0.20,
  POSITION: -0.38,
  CONTACT: 0.38,
} as const;

const STATE_CAMERA_Y_OFFSET = {
  IDENTITY: 0.90,
  POSITION: 1.25,
  CONTACT: 0.70,
} as const;

const STATE_TARGET_Y_OFFSET = {
  IDENTITY: -0.30,
  POSITION: -0.20,
  CONTACT: -0.40,
} as const;

const STATE_PORTRAIT_SCALE = {
  desktop: { IDENTITY: 5.90, POSITION: 4.40, CONTACT: 2.00 },
  compact: { IDENTITY: 3.20, POSITION: 0, CONTACT: 0.80 },
} as const;

const STATE_PORTRAIT_X_OFFSET = {
  desktop: { IDENTITY: 2.40, POSITION: -4.40, CONTACT: 2.80 },
  compact: { IDENTITY: 0.65, POSITION: -0.80, CONTACT: 1.60 },
} as const;

const STATE_PORTRAIT_Z_OFFSET = {
  desktop: { IDENTITY: 0, POSITION: -0.80, CONTACT: 2.00 },
  compact: { IDENTITY: 0, POSITION: 1.90, CONTACT: 1.00 },
} as const;

const STATE_PORTRAIT_DEPTH = {
  IDENTITY: 0,
  POSITION: 1.60,
  CONTACT: 1.40,
} as const;

const smoothstep = (start: number, end: number, value: number): number => {
  const progress = THREE.MathUtils.clamp((value - start) / (end - start), 0, 1);
  return progress * progress * (3 - 2 * progress);
};

export class WorkstationController {
  readonly worldGroup = new THREE.Group();

  width = 0;
  height = 0;
  ready = false;
  paused = false;
  appliedLook: WorkstationLook | null = null;

  private camera: THREE.Camera | null = null;
  private ditherUniforms: DitherUniforms | null = null;
  private model: THREE.Group | null = null;
  private portrait: THREE.Mesh<THREE.PlaneGeometry, THREE.MeshBasicMaterial> | null = null;
  private terminalPlane: THREE.Mesh<THREE.PlaneGeometry, THREE.MeshBasicMaterial> | null = null;
  private terminalTexture: THREE.CanvasTexture | null = null;
  private terminalContext: CanvasRenderingContext2D | null = null;
  private terminalFrame = -1;
  private mixer: THREE.AnimationMixer | null = null;
  private sceneAssetsAttached = false;
  private anchors = new Map<SequenceState, StateAnchors>();
  private trackers: THREE.Object3D[] = [];
  private trackerProjections: TrackerProjection[] = [];
  private elapsed = 0;
  private scrollProgress = 0;
  private targetScrollProgress = 0;
  private perspectiveProgress = 0;
  private targetPerspectiveProgress = 0;

  private reducedMotion = false;
  private finePointer = true;
  private pointer = { x: 0, y: 0, targetX: 0, targetY: 0 };
  private readonly cameraPosition = new THREE.Vector3();
  private readonly cameraTarget = new THREE.Vector3();
  private readonly portraitPosition = new THREE.Vector3();
  private readonly portraitDepthDirection = new THREE.Vector3();
  private readonly trackerVector = new THREE.Vector3();

  constructor(private readonly callbacks: WorkstationControllerOptions) {
    this.worldGroup.name = 'WORKSTATION_COMPOSITION';
  }

  attachCamera(camera: THREE.Camera): void {
    this.camera = camera;
    this.applyViewport();
    this.maybeReady();
  }

  attachDither(uniforms: DitherUniforms): void {
    this.ditherUniforms = uniforms;
    this.maybeReady();
  }

  attachSceneAssets(portraitTexture: THREE.Texture, workstationModel: GLTF): void {
    if (this.sceneAssetsAttached) return;
    this.sceneAssetsAttached = true;

    portraitTexture.colorSpace = THREE.SRGBColorSpace;
    const portraitMaterial = new THREE.MeshBasicMaterial({
      map: portraitTexture,
      transparent: true,
      alphaTest: 0.015,
      depthTest: true,
      depthWrite: true,
      side: THREE.DoubleSide,
      toneMapped: false,
    });
    this.portrait = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), portraitMaterial);
    this.portrait.name = 'PORTRAIT_RUNTIME';

    this.model = workstationModel.scene;
    this.model.name = 'WORKSTATION_AUTHORED';
    this.model.traverse((node) => {
      if (!(node instanceof THREE.Mesh)) return;
      node.castShadow = false;
      node.receiveShadow = false;
      const materials = Array.isArray(node.material) ? node.material : [node.material];
      materials.forEach((material) => {
        material.depthTest = true;
        material.depthWrite = true;
        material.needsUpdate = true;
      });
    });

    this.worldGroup.add(this.model, this.portrait);
    this.model.updateMatrixWorld(true);
    this.readAnchors();
    this.readTrackers();
    this.attachTerminal();

    if (workstationModel.animations.length) {
      this.mixer = new THREE.AnimationMixer(this.model);
      workstationModel.animations.forEach((clip) => this.mixer?.clipAction(clip).play());
      if (this.reducedMotion) this.mixer.setTime(REDUCED_MOTION_TIME);
    }

    this.applyViewport();
    this.maybeReady();
  }

  private readAnchors(): void {
    if (!this.model) return;
    STATES.forEach((state) => {
      const camera = this.requireObject(`CAM_${state}`);
      const target = this.requireObject(`TARGET_${state}`);
      const portrait = this.requireObject(`PORTRAIT_${state}`);
      this.anchors.set(state, {
        camera: camera.position.clone(),
        target: target.position.clone(),
        portrait: portrait.position.clone(),
      });
    });
  }

  private readTrackers(): void {
    if (!this.model) return;
    const trackers: THREE.Object3D[] = [];
    this.model.traverse((node) => {
      const index = node.userData.tracker_index;
      if (Number.isInteger(index)) trackers[index] = node;
    });
    this.trackers = trackers.filter(Boolean);
    this.trackerProjections = this.trackers.map((tracker) => ({
      x: 0,
      y: 0,
      visible: false,
      label: String(tracker.userData.tracker_label || tracker.name),
    }));
  }

  private requireObject(name: string): THREE.Object3D {
    const result = this.model?.getObjectByName(name);
    if (!result) throw new Error(`Missing authored workstation anchor: ${name}`);
    return result;
  }

  private attachTerminal(): void {
    if (!this.model) return;
    const screen = this.requireObject('DISPLAY_SCREEN');
    const bounds = new THREE.Box3().setFromObject(screen);
    const size = bounds.getSize(new THREE.Vector3());
    const center = bounds.getCenter(new THREE.Vector3());
    const canvas = document.createElement('canvas');
    canvas.width = 1024;
    canvas.height = 512;
    const context = canvas.getContext('2d');
    if (!context) throw new Error('Unable to create workstation terminal canvas');
    context.imageSmoothingEnabled = false;

    const texture = new THREE.CanvasTexture(canvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.generateMipmaps = false;
    texture.minFilter = THREE.LinearFilter;
    texture.magFilter = THREE.LinearFilter;
    const material = new THREE.MeshBasicMaterial({
      map: texture,
      depthTest: true,
      depthWrite: true,
      side: THREE.DoubleSide,
      toneMapped: false,
    });
    const plane = new THREE.Mesh(new THREE.PlaneGeometry(size.x * 0.95, size.y * 0.94), material);
    plane.name = 'TERMINAL_RUNTIME';
    plane.position.set(center.x, center.y, bounds.max.z + 0.012);
    this.model.add(plane);

    this.terminalPlane = plane;
    this.terminalTexture = texture;
    this.terminalContext = context;
    this.renderTerminal(this.reducedMotion ? TERMINAL_STATIC_TIME : 0, true);
  }

  private renderTerminal(elapsed: number, force = false): void {
    const context = this.terminalContext;
    const texture = this.terminalTexture;
    if (!context || !texture) return;
    const time = this.reducedMotion ? TERMINAL_STATIC_TIME : elapsed % TERMINAL_CYCLE;
    const frame = Math.floor(time * 20);
    if (!force && frame === this.terminalFrame) return;
    this.terminalFrame = frame;

    const { width, height } = context.canvas;
    context.fillStyle = '#050505';
    context.fillRect(0, 0, width, height);
    context.fillStyle = '#111111';
    for (let y = 20; y < height; y += 16) context.fillRect(0, y, width, 1);

    context.font = '600 27px "Space Mono", monospace';
    context.textBaseline = 'middle';
    const left = 42;
    const top = 42;
    const lineHeight = 43;
    let cursorLine = -1;
    let cursorText = '';
    TERMINAL_LINES.forEach((line, index) => {
      if (time < line.start) return;
      const progress = THREE.MathUtils.clamp((time - line.start) / line.duration, 0, 1);
      const count = line.mode === 'type' ? Math.floor(progress * line.text.length) : line.text.length;
      const visible = line.text.slice(0, count);
      context.fillStyle = line.bright ? '#f4f4f0' : '#a8a8a2';
      context.fillText(visible, left, top + index * lineHeight);
      cursorLine = index;
      cursorText = visible;
    });

    if (cursorLine >= 0 && Math.floor(time * 3) % 2 === 0) {
      const x = left + context.measureText(cursorText).width + 3;
      const y = top + cursorLine * lineHeight - 14;
      context.fillStyle = '#f8f8f4';
      context.fillRect(x, y, 13, 28);
    }
    texture.needsUpdate = true;
  }

  private maybeReady(): void {
    if (this.ready || !this.sceneAssetsAttached || !this.camera || !this.ditherUniforms) return;
    this.ready = true;
    this.scrollProgress = this.targetScrollProgress;
    this.evaluateSequence();
    this.callbacks.onReady?.(this);
  }

  setContextAvailable(available: boolean): void {
    this.paused = !available;
    this.callbacks.onStatus?.(available && this.ready);
  }

  setViewport(width: number, height: number): void {
    this.width = width;
    this.height = height;
    this.applyViewport();
  }

  private applyViewport(): void {
    if (!(this.camera instanceof THREE.PerspectiveCamera)) return;
    this.camera.fov = this.width <= 768 ? 48 : 38;
    this.camera.updateProjectionMatrix();
  }

  setReducedMotion(reducedMotion: boolean): void {
    this.reducedMotion = reducedMotion;
    this.terminalFrame = -1;
    if (reducedMotion) {
      this.resetPointerMotion();
      this.mixer?.setTime(REDUCED_MOTION_TIME);
    }
    this.renderTerminal(reducedMotion ? TERMINAL_STATIC_TIME : this.elapsed, true);
  }

  setFinePointer(finePointer: boolean): void {
    this.finePointer = finePointer;
    if (!finePointer) this.resetPointerMotion();
  }

  private resetPointerMotion(): void {
    this.pointer.x = 0;
    this.pointer.y = 0;
    this.pointer.targetX = 0;
    this.pointer.targetY = 0;
  }

  setPointerTarget(x: number, y: number): void {
    if (!this.finePointer || this.reducedMotion) return;
    this.pointer.targetX = x;
    this.pointer.targetY = y;
  }

  applyLook(
    look: WorkstationLook,
    { force = false, immediate = false }: { force?: boolean; immediate?: boolean } = {},
  ): void {
    if (!force && this.appliedLook === look) return;
    this.appliedLook = look;
    this.setScrollProgress(look === 1 ? 0 : look === 2 ? 0.52 : 1, immediate);
  }

  setScrollProgress(progress: number, immediate = false): void {
    this.targetScrollProgress = THREE.MathUtils.clamp(progress, 0, 1);
    if (immediate || this.reducedMotion) {
      this.scrollProgress = this.targetScrollProgress;
      this.evaluateSequence();
    }
  }

  setPerspectiveProgress(progress: number, immediate = false): void {
    this.targetPerspectiveProgress = THREE.MathUtils.clamp(progress, 0, 1);
    if (immediate || this.reducedMotion) {
      this.perspectiveProgress = this.targetPerspectiveProgress;
      this.evaluateSequence();
    }
  }

  private resolveSequence(value: number): { from: SequenceState; to: SequenceState; progress: number } {
    if (value <= 0.52) {
      return {
        from: 'IDENTITY',
        to: 'POSITION',
        progress: smoothstep(0.08, 0.48, value),
      };
    }
    return {
      from: 'POSITION',
      to: 'CONTACT',
      progress: smoothstep(0.56, 0.94, value),
    };
  }

  private evaluateSequence(): void {
    if (!this.camera || !this.portrait || !this.ditherUniforms || !this.anchors.size) return;

    const theme = this.resolveSequence(this.scrollProgress);
    const perspective = this.resolveSequence(this.perspectiveProgress);
    const themeStart = this.anchors.get(theme.from);
    const themeEnd = this.anchors.get(theme.to);
    const viewStart = this.anchors.get(perspective.from);
    const viewEnd = this.anchors.get(perspective.to);
    if (!themeStart || !themeEnd || !viewStart || !viewEnd) throw new Error('Missing workstation sequence anchors');

    const camera = this.cameraPosition.lerpVectors(viewStart.camera, viewEnd.camera, perspective.progress);
    const target = this.cameraTarget.lerpVectors(viewStart.target, viewEnd.target, perspective.progress);
    camera.y += THREE.MathUtils.lerp(
      STATE_CAMERA_Y_OFFSET[perspective.from],
      STATE_CAMERA_Y_OFFSET[perspective.to],
      perspective.progress,
    );
    target.y += THREE.MathUtils.lerp(
      STATE_TARGET_Y_OFFSET[perspective.from],
      STATE_TARGET_Y_OFFSET[perspective.to],
      perspective.progress,
    );
    const portrait = this.portraitPosition.lerpVectors(themeStart.portrait, themeEnd.portrait, theme.progress);
    const compact = this.width <= 768;

    if (this.model) {
      const modelXs = compact ? STATE_MODEL_X.compact : STATE_MODEL_X.desktop;
      const modelYs = compact ? STATE_MODEL_Y.compact : STATE_MODEL_Y.desktop;
      const modelZs = compact ? STATE_MODEL_Z.compact : STATE_MODEL_Z.desktop;
      const modelX = THREE.MathUtils.lerp(modelXs[theme.from], modelXs[theme.to], theme.progress);
      this.model.position.x = modelX - (compact ? this.scrollProgress * 1.4 : 0);
      this.model.position.y = THREE.MathUtils.lerp(modelYs[theme.from], modelYs[theme.to], theme.progress);
      this.model.position.z = THREE.MathUtils.lerp(modelZs[theme.from], modelZs[theme.to], theme.progress);
      this.model.rotation.y = THREE.MathUtils.lerp(
        STATE_MODEL_YAW[perspective.from],
        STATE_MODEL_YAW[perspective.to],
        perspective.progress,
      );
      const modelScales = compact ? STATE_MODEL_SCALE.compact : STATE_MODEL_SCALE.desktop;
      const modelScale = THREE.MathUtils.lerp(modelScales[theme.from], modelScales[theme.to], theme.progress);
      this.model.scale.setScalar(modelScale);
    }
    this.worldGroup.rotation.z = THREE.MathUtils.lerp(
      STATE_ORIENTATION_Z[theme.from],
      STATE_ORIENTATION_Z[theme.to],
      theme.progress,
    );

    if (compact) {
      portrait.x -= this.scrollProgress * 1.5;
      camera.z += 3.5;
      camera.x += 0.45;
      target.x += 0.38;
    }

    camera.x += this.pointer.x * (compact ? 0 : 0.065);
    camera.y += this.pointer.y * (compact ? 0 : 0.045);
    this.camera.position.copy(camera);
    this.camera.lookAt(target);
    if (this.camera instanceof THREE.PerspectiveCamera) {
      const fov = (compact ? 48 : 38) + this.perspectiveProgress * (compact ? 5 : 9);
      if (Math.abs(this.camera.fov - fov) > 0.001) {
        this.camera.fov = fov;
        this.camera.updateProjectionMatrix();
      }
    }

    const portraitOffsets = compact ? STATE_PORTRAIT_X_OFFSET.compact : STATE_PORTRAIT_X_OFFSET.desktop;
    portrait.x += THREE.MathUtils.lerp(portraitOffsets[theme.from], portraitOffsets[theme.to], theme.progress);
    const portraitZOffsets = compact ? STATE_PORTRAIT_Z_OFFSET.compact : STATE_PORTRAIT_Z_OFFSET.desktop;
    portrait.z += THREE.MathUtils.lerp(portraitZOffsets[theme.from], portraitZOffsets[theme.to], theme.progress);
    const portraitDepth = THREE.MathUtils.lerp(
      STATE_PORTRAIT_DEPTH[theme.from],
      STATE_PORTRAIT_DEPTH[theme.to],
      theme.progress,
    );
    portrait.addScaledVector(this.portraitDepthDirection.subVectors(portrait, camera).normalize(), portraitDepth);
    this.portrait.position.copy(portrait);
    const portraitScales = compact ? STATE_PORTRAIT_SCALE.compact : STATE_PORTRAIT_SCALE.desktop;
    const portraitScale = THREE.MathUtils.lerp(portraitScales[theme.from], portraitScales[theme.to], theme.progress);
    this.portrait.scale.setScalar(portraitScale);
    this.portrait.lookAt(this.camera.position);

    const startTone = STATE_TONE[theme.from];
    const endTone = STATE_TONE[theme.to];
    const uniforms = this.ditherUniforms;
    uniforms.uCardY.value = THREE.MathUtils.lerp(startTone.cardY, endTone.cardY, theme.progress);
    uniforms.uCell.value = THREE.MathUtils.lerp(startTone.cell, endTone.cell, theme.progress);
    uniforms.uCols.value = STATE_TONE[STATES[(this.appliedLook ?? 1) - 1]].cols;
  }

  private projectTrackers(): TrackerProjection[] {
    if (!this.camera) return this.trackerProjections;
    for (let index = 0; index < this.trackers.length; index += 1) {
      const tracker = this.trackers[index];
      const projection = this.trackerProjections[index];
      tracker.getWorldPosition(this.trackerVector);
      this.trackerVector.project(this.camera);
      projection.x = (this.trackerVector.x * 0.5 + 0.5) * this.width;
      projection.y = (-this.trackerVector.y * 0.5 + 0.5) * this.height;
      projection.visible = this.trackerVector.z >= -1 && this.trackerVector.z <= 1;
    }
    return this.trackerProjections;
  }

  update(deltaTime: number): void {
    if (!this.ready || this.paused || !this.camera || !this.ditherUniforms) return;
    const delta = Math.min(deltaTime, 0.05);
    if (!this.reducedMotion) this.elapsed += delta;
    this.pointer.x += (this.pointer.targetX - this.pointer.x) * 0.07;
    this.pointer.y += (this.pointer.targetY - this.pointer.y) * 0.07;
    const themeSmoothing = this.reducedMotion ? 1 : 1 - Math.exp(-delta * 2.8);
    const perspectiveSmoothing = this.reducedMotion ? 1 : 1 - Math.exp(-delta * 6.5);
    this.scrollProgress += (this.targetScrollProgress - this.scrollProgress) * themeSmoothing;
    this.perspectiveProgress += (this.targetPerspectiveProgress - this.perspectiveProgress) * perspectiveSmoothing;

    if (!this.reducedMotion) this.mixer?.update(delta);
    this.renderTerminal(this.elapsed);
    this.evaluateSequence();
    this.callbacks.onFrame?.(this.projectTrackers());
  }

  dispose(): void {
    this.mixer?.stopAllAction();
    this.terminalPlane?.removeFromParent();
    this.terminalPlane?.geometry.dispose();
    this.terminalPlane?.material.dispose();
    this.terminalTexture?.dispose();
    this.portrait?.geometry.dispose();
    this.portrait?.material.dispose();
    const materials = new Set<THREE.Material>();
    this.model?.traverse((node) => {
      if (!(node instanceof THREE.Mesh)) return;
      node.geometry.dispose();
      const nodeMaterials = Array.isArray(node.material) ? node.material : [node.material];
      nodeMaterials.forEach((material) => materials.add(material));
    });
    materials.forEach((material) => material.dispose());
  }
}
