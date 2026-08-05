import * as THREE from 'three';
import { BlendFunction, Effect } from 'postprocessing';

export interface DitherUniforms {
  uCardY: THREE.Uniform<number>;
  uStaticSlice: THREE.Uniform<number>;
  uVelocitySlice: THREE.Uniform<number>;
  uRowShear: THREE.Uniform<number>;
  uGlitch: THREE.Uniform<number>;
  uCols: THREE.Uniform<number>;
  uTime: THREE.Uniform<number>;
  uCell: THREE.Uniform<number>;
}

const DITHER_FRAGMENT_SHADER = `
  uniform float uCardY;
  uniform float uStaticSlice;
  uniform float uVelocitySlice;
  uniform float uRowShear;
  uniform float uGlitch;
  uniform float uCols;
  uniform float uTime;
  uniform float uCell;


  float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
  }

  float bayer2(vec2 point) {
    point = floor(point);
    return fract(dot(point, vec2(0.5, point.y * 0.75)));
  }

  float bayer4(vec2 point) {
    return bayer2(point * 0.5) * 0.25 + bayer2(point);
  }

  float bayer8(vec2 point) {
    return bayer4(point * 0.5) * 0.25 + bayer2(point);
  }

  void mainUv(inout vec2 uv) {
    if (uStaticSlice > 0.0 || uVelocitySlice > 0.0) {
      float column = floor(uv.x * uCols);
      float sway = 0.5 + 0.5 * sin(uTime * 0.25 + column * 1.7);
      float amount = 0.16 * uStaticSlice * sway + uVelocitySlice;
      uv.y = fract(uv.y + (hash(vec2(column, 19.0)) - 0.5) * amount);
    }
    if (uRowShear > 0.0) {
      float row = floor(uv.y * 16.0);
      uv.x += (hash(vec2(row, 57.0)) - 0.5) * 0.045 * uRowShear;
    }

    if (uGlitch > 0.001) {
      float seed = floor(uTime * 8.0);
      vec2 block = floor(uv * vec2(9.0, 14.0));
      float noise = hash(vec2(block.x * 7.13 + seed * 0.371, block.y * 113.7));
      float blockOn = step(1.0 - 0.42 * uGlitch, noise);
      vec2 shift = vec2(
        hash(vec2(noise * 91.7, seed + 3.0)),
        hash(vec2(noise * 41.3, seed + 7.0))
      ) - 0.5;
      uv += blockOn * shift * vec2(0.16, 0.06) * uGlitch;
    }

    uv = clamp(uv, 0.0, 1.0);
  }

  void mainImage(const in vec4 inputColor, const in vec2 uv, out vec4 outputColor) {
    vec3 sourceColor = inputColor.rgb / max(inputColor.a, 0.001);
    float gray = dot(sourceColor, vec3(0.299, 0.587, 0.114));
    gray = pow(clamp(gray, 0.0, 1.0), 1.15) * 1.25;
    gray = smoothstep(0.10, 1.0, gray);
    float modelTone = step(bayer8(gl_FragCoord.xy / uCell) + 0.001, gray);

    float fieldTone = step(uCardY, gl_FragCoord.y / resolution.y);
    float modelInversion = 1.0 - fieldTone;
    modelTone = mix(modelTone, 1.0 - modelTone, modelInversion);
    float modelCoverage = smoothstep(0.01, 0.08, inputColor.a);
    float tone = mix(fieldTone, modelTone, modelCoverage);

    outputColor = vec4(mix(vec3(0.0), vec3(0.812, 0.824, 0.824), tone), 1.0);
  }
`;

export class DitherEffect extends Effect {
  readonly values: DitherUniforms;

  constructor() {
    const uniforms: DitherUniforms = {
      uCardY: new THREE.Uniform(0.5),
      uStaticSlice: new THREE.Uniform(0),
      uVelocitySlice: new THREE.Uniform(0),
      uRowShear: new THREE.Uniform(0),
      uGlitch: new THREE.Uniform(0),
      uCols: new THREE.Uniform(22),
      uTime: new THREE.Uniform(0),
      uCell: new THREE.Uniform(2.5),
    };

    super('DitherEffect', DITHER_FRAGMENT_SHADER, {
      blendFunction: BlendFunction.NORMAL,
      uniforms: new Map(Object.entries(uniforms)),
    });

    this.values = uniforms;
  }
}
