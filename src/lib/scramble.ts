import { gsap } from 'gsap';
import ScrambleTextPlugin from 'gsap/ScrambleTextPlugin';
import SplitText from 'gsap/SplitText';

interface ScrambleOptions {
  focus?: boolean;
  enabled?: boolean;
}

gsap.registerPlugin(ScrambleTextPlugin, SplitText);

export function scramble(
  node: HTMLElement,
  { focus = true, enabled = true }: ScrambleOptions = {},
): { destroy(): void } | undefined {
  if (!enabled) return;
  const accessibleLabel = node.getAttribute('aria-label');
  const split = SplitText.create(node, {
    type: 'words',
    wordsClass: 'scramble-text',
    tag: 'span',
    deepSlice: false,
    aria: 'auto',
  });
  if (accessibleLabel) node.setAttribute('aria-label', accessibleLabel);
  if (node.lastChild?.nodeType === Node.TEXT_NODE && !node.lastChild.textContent?.trim()) node.lastChild.remove();

  const spans = split.words as HTMLElement[];
  if (!spans.length) {
    split.revert();
    return;
  }
  const originals = spans.map((span) => span.textContent ?? '');

  const restore = () => {
    spans.forEach((span, index) => {
      span.textContent = originals[index];
      span.classList.remove('is-scrambling');
      span.style.removeProperty('width');
    });
  };

  const run = () => {
    if (node.matches(':disabled')) return;
    gsap.killTweensOf(spans);
    restore();

    spans.forEach((span) => {
      span.style.width = `${Math.ceil(span.getBoundingClientRect().width)}px`;
      span.classList.add('is-scrambling');
    });

    gsap.to(spans, {
      duration: 0.27,
      ease: 'none',
      scrambleText: {
        text: '{original}',
        revealDelay: 0.11,
        speed: 1.4,
      },
      onComplete: restore,
    });
  };

  const hoverCapable = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  if (hoverCapable) node.addEventListener('pointerenter', run);
  if (focus) node.addEventListener('focus', run);

  return {
    destroy() {
      if (hoverCapable) node.removeEventListener('pointerenter', run);
      if (focus) node.removeEventListener('focus', run);
      gsap.killTweensOf(spans);
      split.revert();
    },
  };
}
