// Shared motion system. Every animated component in this app draws its
// timing/easing/stagger from here -- no ad-hoc durations or curves anywhere
// else. Mirrors the CSS custom properties in index.css (kept in sync by
// hand since Framer Motion needs numeric values, not var() references).
//
// Only `transform`/`opacity` are ever animated -- never layout-affecting
// properties (width/height/top/left) -- so everything stays GPU-accelerated
// and there's zero layout shift.

import { useEffect, useState } from 'react';
import { useMotionValue, useTransform, animate } from 'framer-motion';

export const DUR = {
  instant: 0.1, // press feedback
  micro: 0.18, // hover/focus, small state changes
  base: 0.32, // entrances, panel-level transitions
  relaxed: 0.48, // tab switches, larger reveals
};

// Cubic-bezier curves standing in for spring physics on fixed-duration UI
// motion. `spring`/`softSpring` overshoot-and-settle like a real spring;
// `out` is a decisive ease-out for entrances; `inOut` is symmetric, used
// for cross-fades where nothing needs to feel "thrown".
export const EASE = {
  out: [0.16, 1, 0.3, 1],
  spring: [0.34, 1.56, 0.64, 1],
  softSpring: [0.22, 1, 0.36, 1],
  inOut: [0.4, 0, 0.2, 1],
};

export const STAGGER_STEP = 0.045; // seconds, per sibling in a revealed list
export const STAGGER_CAP = 10; // items beyond this share the max delay

// Genuine mass/stiffness/damping spring physics (Framer Motion's own
// simulator, not a fixed-duration curve) -- used for layoutId shared-element
// transitions, where a real spring reads much better than an eased tween.
export const SPRING = { type: 'spring', stiffness: 420, damping: 38 }; // snappy: tab indicator
export const SPRING_GENTLE = { type: 'spring', stiffness: 260, damping: 24 }; // softer settle

/** Capped per-index stagger delay -- so a 50-item list doesn't take
 * seconds to finish revealing; everything past the cap arrives together. */
export function staggerDelay(index) {
  return Math.min(index, STAGGER_CAP) * STAGGER_STEP;
}

/** Tracks the user's prefers-reduced-motion setting live (not just at
 * mount), so toggling it in OS settings updates the app immediately. */
export function usePrefersReducedMotion() {
  const [reduced, setReduced] = useState(
    () => typeof window !== 'undefined'
      && window.matchMedia('(prefers-reduced-motion: reduce)').matches,
  );
  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    const onChange = (e) => setReduced(e.matches);
    mq.addEventListener('change', onChange);
    return () => mq.removeEventListener('change', onChange);
  }, []);
  return reduced;
}

/** Entrance preset: slide-up + fade, staggered by index. Collapses to an
 * instant opacity-only fade under prefers-reduced-motion. */
export function entranceVariant(index, reduced) {
  if (reduced) {
    return {
      hidden: { opacity: 0 },
      show: { opacity: 1, transition: { duration: 0 } },
    };
  }
  return {
    hidden: { opacity: 0, y: 14 },
    show: {
      opacity: 1,
      y: 0,
      transition: { duration: DUR.base, ease: EASE.out, delay: staggerDelay(index) },
    },
  };
}

/** Press-feedback props to spread onto any tappable element:
 * <motion.button {...pressFeedback(reduced)}>. Scales down on press with a
 * spring back on release; no-op under reduced motion. */
export function pressFeedback(reduced) {
  if (reduced) return {};
  return {
    whileTap: { scale: 0.97 },
    transition: { duration: DUR.instant, ease: EASE.spring },
  };
}

/** Hover-glow transition props (combine with a hover-driven style/variant
 * change in the component, e.g. whileHover={{ borderColor: ... }}). */
export const hoverGlowTransition = { duration: DUR.micro, ease: EASE.softSpring };

/** Cross-fade + slight slide, used for tab-switches and similar
 * mount/unmount transitions inside <AnimatePresence>. */
export function tabSwitchVariant(reduced) {
  if (reduced) {
    return {
      initial: { opacity: 0 },
      animate: { opacity: 1, transition: { duration: 0 } },
      exit: { opacity: 0, transition: { duration: 0 } },
    };
  }
  return {
    initial: { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0, transition: { duration: DUR.relaxed, ease: EASE.inOut } },
    exit: { opacity: 0, y: -10, transition: { duration: DUR.relaxed * 0.6, ease: EASE.inOut } },
  };
}

/** Number that tweens up to `value` whenever it changes, instead of
 * snapping. Returns a Framer Motion MotionValue<string> ready to render
 * inside <motion.span>{display}</motion.span>. Snaps instantly under
 * reduced motion. `format` defaults to a thousands-separated integer. */
export function useCountUp(value, { reduced, format } = {}) {
  const fmt = format || ((n) => Math.round(n).toLocaleString());
  const motionValue = useMotionValue(value ?? 0);
  const display = useTransform(motionValue, (v) => fmt(v));

  useEffect(() => {
    const target = value ?? 0;
    if (reduced) {
      motionValue.set(target);
      return undefined;
    }
    const controls = animate(motionValue, target, {
      duration: DUR.relaxed * 1.4,
      ease: EASE.out,
    });
    return () => controls.stop();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value, reduced]);

  return display;
}
