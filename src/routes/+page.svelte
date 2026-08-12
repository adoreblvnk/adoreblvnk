<script lang="ts">
  import { onMount } from 'svelte';
  import { gsap } from 'gsap';
  import { ScrollTrigger } from 'gsap/ScrollTrigger';
  import SignalField from '../components/SignalField.svelte';
  import { scramble } from '../lib/scramble';
  import type { SculptureLook, TrackerProjection } from '../lib/sculpture-controller';
  import { SculptureController } from '../lib/sculpture-controller';

  interface Section {
    id: 'identity' | 'position' | 'contact';
    look: SculptureLook;
    theme: 'ink' | 'paper';
    animateEntrance?: boolean;
  }

  interface DisplayTracker extends TrackerProjection {
    alignLeft: boolean;
    label: string;
  }

  interface Contact {
    prefix: string;
    address: string;
    label: string;
    href?: string;
    external?: boolean;
  }

  gsap.registerPlugin(ScrollTrigger);


  const sections: Section[] = [
    { id: 'identity', look: 1, theme: 'ink' },
    { id: 'position', look: 2, theme: 'paper', animateEntrance: true },
    { id: 'contact', look: 3, theme: 'ink' },
  ];
  const contacts: Contact[] = [
    { prefix: 'EMAIL', address: 'adore_blvnk@proton.me', href: 'mailto:adore_blvnk@proton.me', label: 'Send email to adore_blvnk@proton.me' },
    { prefix: 'X', address: '@adore_blvnk', href: 'https://x.com/adore_blvnk', label: 'X profile: @adore_blvnk', external: true },
    { prefix: 'GITHUB', address: '@adoreblvnk', href: 'https://github.com/adoreblvnk', label: 'GitHub profile: @adoreblvnk', external: true },
    { prefix: 'DISCORD', address: 'adore_blvnk', label: 'Discord username: adore_blvnk' },
    { prefix: 'RESUME', address: 'VIEW PDF ↗', href: '/resume/resume.pdf', label: 'View resume PDF', external: true },
  ];

  let activeSection = $state<Section['id']>('identity');
  let sceneReady = $state(false);
  let controller = $state<SculptureController | null>(null);
  let trackers = $state<DisplayTracker[]>([]);

  const activeConfig = () => sections.find((section) => section.id === activeSection) || sections[0];

  $effect(() => {
    const theme = activeConfig().theme;
    document.body.classList.toggle('paper-theme', theme === 'paper');

    return () => {
      document.body.classList.remove('paper-theme');
    };
  });

  function applyCurrentLook({ force = false, immediate = false }: { force?: boolean; immediate?: boolean } = {}): void {
    controller?.applyLook(activeConfig().look, { force, immediate });
  }

  function handleReady(sceneController: SculptureController): void {
    controller = sceneController;
    sceneReady = true;
    applyCurrentLook({ force: true, immediate: true });
  }

  function handleStatus(ready: boolean): void {
    sceneReady = ready;
  }

  function handleFrame(projections: TrackerProjection[]): void {
    const hide = activeSection === 'contact' || window.innerWidth <= 768;
    trackers = projections.map((projection) => {
      const inside = projection.x >= 10 && projection.x <= window.innerWidth - 10
        && projection.y >= 10 && projection.y <= window.innerHeight - 24;
      return {
        x: projection.x,
        y: projection.y,
        visible: projection.visible && inside && !hide,
        alignLeft: projection.x > window.innerWidth - 130,
        label: `x: ${Math.round(projection.x)} y: ${Math.round(projection.y)}`,
      };
    });
  }

  function triggerSectionEntrance(): void {
    const rows = '.kinetic-word-row';
    gsap.killTweensOf(rows);
    gsap.fromTo(
      rows,
      { opacity: 0.15, scale: 0.96 },
      { opacity: 1, scale: 1.03, duration: 0.8, stagger: 0.15, ease: 'power3.out' },
    );
  }

  function activateSection(section: Section): void {
    if (activeSection === section.id && controller?.appliedLook !== null) return;
    activeSection = section.id;
    controller?.applyLook(section.look);
    if (section.animateEntrance) triggerSectionEntrance();
  }

  onMount(() => {
    const handlePointerMove = (event: PointerEvent) => {
      const x = (event.clientX - window.innerWidth / 2) / (window.innerWidth / 2);
      const y = (event.clientY - window.innerHeight / 2) / (window.innerHeight / 2);
      controller?.setPointerTarget(x, y);
      document.documentElement.style.setProperty('--pointer-screen-x', `${event.clientX}px`);
      document.documentElement.style.setProperty('--pointer-screen-y', `${event.clientY}px`);
    };
    window.addEventListener('pointermove', handlePointerMove, { passive: true });

    const sectionTriggers = sections.map((section) => ScrollTrigger.create({
      trigger: `#${section.id}`,
      start: 'top center',
      end: 'bottom center',
      onEnter: () => activateSection(section),
      onEnterBack: () => activateSection(section),
    }));
    const velocityTrigger = ScrollTrigger.create({
      onUpdate: (self) => controller?.setScrollVelocity(self.getVelocity() / 60),
    });

    const entrance = gsap.timeline()
      .fromTo('.hud-chrome', { opacity: 0 }, { opacity: 1, duration: 1.2, ease: 'power1.out' })
      .fromTo('.display-name, .hero-phrase', { x: -20, opacity: 0 }, { x: 0, opacity: 1, duration: 0.8, stagger: 0.08, ease: 'power3.out' }, '-=0.8')
      .fromTo('.role-subheading, .action-btn', { y: 15, opacity: 0 }, { y: 0, opacity: 1, duration: 0.8, stagger: 0.15, ease: 'power2.out' }, '-=0.6');

    let resizeFrame: number | null = null;
    const handleResize = () => {
      if (resizeFrame !== null) cancelAnimationFrame(resizeFrame);
      resizeFrame = requestAnimationFrame(() => applyCurrentLook({ force: true, immediate: true }));
    };
    window.addEventListener('resize', handleResize);

    return () => {
      sectionTriggers.forEach((trigger) => trigger.kill());
      velocityTrigger.kill();
      entrance.kill();
      window.removeEventListener('pointermove', handlePointerMove);
      window.removeEventListener('resize', handleResize);
      if (resizeFrame !== null) cancelAnimationFrame(resizeFrame);
    };
  });
</script>

<svelte:head>
  <title>adore_blvnk</title>
  <meta name="description" content="adore_blvnk: CLI user, software architect. Pattern your position.">
  <meta property="og:site_name" content="adore_blvnk">
  <meta property="og:title" content="adore_blvnk">
  <meta property="og:description" content="Pattern your position.">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://adoreblvnk.com">
  <meta property="og:image" content="https://adoreblvnk.com/og-image.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:type" content="image/png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:site" content="@adore_blvnk">
  <meta name="twitter:title" content="adore_blvnk">
  <meta name="twitter:description" content="Pattern your position.">
  <meta name="twitter:image" content="https://adoreblvnk.com/og-image.png">
</svelte:head>

<a class="skip-link" href="#main-content" use:scramble>Skip to main content</a>

<SignalField onReady={handleReady} onFrame={handleFrame} onStatus={handleStatus} />

<div class="hud-lattice" aria-hidden="true"></div>
<div class="hud-lattice-focus" aria-hidden="true"></div>

<div class="hud-chrome" aria-hidden="true">
  <div class="reg-corner top-left"></div>
  <div class="reg-corner top-right"></div>
  <div class="reg-corner bottom-left"></div>
  <div class="reg-corner bottom-right"></div>
</div>

<div class="hud-trackers-container" aria-hidden="true">
  {#each trackers as tracker}
    <div
      class="hud-tracker"
      class:visible={tracker.visible}
      class:align-left={tracker.alignLeft}
      style:left={`${tracker.x}px`}
      style:top={`${tracker.y}px`}
    >
      <div class="tracker-dot"></div>
      <div class="tracker-label">{tracker.label}</div>
    </div>
  {/each}
</div>

  <main id="main-content" tabindex="-1">
    <section id="identity" class="movement-section" aria-labelledby="identity-heading">
      <div class="ghost-type" aria-hidden="true">PATTERN POSITION</div>
      <div class="section-content">
        <div class="hero-lockup hero-specimen">
            <h1 id="identity-heading" class="display-name">adore_blvnk</h1>
            <p class="hero-phrase" use:scramble={{ focus: false }}>pattern your position</p>
            <p class="role-subheading">CLI user, software architect</p>
            {#if sceneReady}
              <button
                type="button"
                class="action-btn"
                aria-label="Pulse fluid structure"
                onclick={() => controller?.pulseSculpture()}
                use:scramble
              >PULSE</button>
            {/if}
        </div>
      </div>
    </section>

    <section id="position" class="movement-section" aria-labelledby="position-heading">
      <div class="section-content">
        <h2 id="position-heading" class="sr-only">Pattern your position</h2>
        <div class="position-layout">
          <div class="kinetic-stacked-composition" aria-hidden="true">
            <div class="kinetic-word-row">PATTERN</div>
            <div class="kinetic-word-row">YOUR</div>
            <div class="kinetic-word-row">POSITION</div>
          </div>
          <p class="position-bio">aspiring farmer, software architect, Linux dev. i prolly use too much CLIs / TUIs but then again, i'm on Debian. used to handwrite Rust &amp; Go, now i'm washed. does DevOps (K8s, Helm charts &amp; addons) (unwillingly). $35k+ from hackathons
          <br>
          i would liek to raise my own ducks 🦆 on my log cabin 1 day...
          </p>
        </div>
      </div>
    </section>

    <section id="contact" class="movement-section" aria-labelledby="contact-heading">
      <div class="section-content">
        <div class="contact-index">
          <h2 id="contact-heading" class="section-title">CONTACT INDEX</h2>
          <ul class="contact-list">
            {#each contacts as contact}
              <li class="contact-item">
                <svelte:element
                  this={contact.href ? 'a' : 'div'} href={contact.href}
                  target={contact.external ? '_blank' : undefined} rel={contact.external ? 'noopener noreferrer' : undefined}
                  class={contact.href ? 'contact-link' : 'contact-entry'}
                  aria-label={contact.label} use:scramble={{ enabled: Boolean(contact.href) }}
                >
                  <span class="link-prefix">{contact.prefix}</span>
                  <span class="link-address">{contact.address}</span>
                </svelte:element>
              </li>
            {/each}
          </ul>
          <div class="colophon-text" aria-hidden="true">adore_blvnk</div>
          <p class="asset-credit">
            ORIGINAL PROCEDURAL ADAPTATION OF
            <a href="https://sketchfab.com/3d-models/abstract-geometry-fluid-seamless-loop-animation-5eb25e2015e94f9ba17450ac342a8b08" target="_blank" rel="noopener noreferrer">ABSTRACT GEOMETRY FLUID SEAMLESS LOOP BY GUZDEK ADAM ↗</a>.
            FORM AND MOTION RE-AUTHORED FOR THIS PORTRAIT UNDER
            <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener noreferrer">CC BY 4.0 ↗</a>.
          </p>
        </div>
      </div>
    </section>
  </main>
