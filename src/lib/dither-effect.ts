import * as THREE from 'three';
import { BlendFunction, Effect } from 'postprocessing';

export interface DitherUniforms {
  uCardY: THREE.Uniform<number>;
  uCell: THREE.Uniform<number>;
  uCols: THREE.Uniform<number>;
}

const DITHER_FRAGMENT_SHADER = `
  uniform float uCardY;
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

  void mainImage(const in vec4 inputColor, const in vec2 uv, out vec4 outputColor) {
    vec3 sourceColor = inputColor.rgb / max(inputColor.a, 0.001);
    float gray = dot(sourceColor, vec3(0.299, 0.587, 0.114));
    gray = pow(clamp(gray, 0.0, 1.0), 1.15) * 1.25;
    gray = smoothstep(0.10, 1.0, gray);
    vec2 ditherPoint = gl_FragCoord.xy / uCell;
    float tileVariation = hash(floor(ditherPoint / 8.0)) - 0.5;
    float variation = tileVariation * 0.10;
    float threshold = clamp(bayer8(ditherPoint) + variation, 0.0, 1.0);
    float modelTone = step(threshold + 0.001, gray);

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
      uCell: new THREE.Uniform(2.5),
      uCols: new THREE.Uniform(22),
    };

    super('DitherEffect', DITHER_FRAGMENT_SHADER, {
      blendFunction: BlendFunction.NORMAL,
      uniforms: new Map(Object.entries(uniforms)),
    });

    this.values = uniforms;
  }
}
