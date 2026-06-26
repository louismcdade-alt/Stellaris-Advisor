import { motion } from 'framer-motion';
import { DUR, EASE, usePrefersReducedMotion } from '../motion';

/** The signature hero moment: the logo assembles itself in on mount --
 * backdrop, then starfield, then the energy rings, then the core "pops" in
 * with a spring overshoot, then the outer frame traces itself on, then the
 * cardinal ticks settle in. Afterward the core breathes with a slow, low-key
 * glow pulse (opacity only -- never scale, so it never feels busy in the
 * header during normal use). Collapses to a single fade-in under
 * prefers-reduced-motion, with no looping glow. */
export default function Logo({ size = 40 }) {
  const reduced = usePrefersReducedMotion();

  if (reduced) {
    return (
      <svg width={size} height={size} viewBox="0 0 512 512" role="img" aria-label="Stellaris Advisor logo">
        <LogoDefs />
        <LogoStaticArt />
      </svg>
    );
  }

  const container = {
    hidden: {},
    show: { transition: { staggerChildren: 0.12, delayChildren: 0.05 } },
  };
  const fadeGroup = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { duration: DUR.base, ease: EASE.out } },
  };
  const ringGroup = {
    hidden: { opacity: 0, scale: 0.85 },
    show: {
      opacity: 1,
      scale: 1,
      transition: { duration: DUR.relaxed, ease: EASE.softSpring },
    },
  };
  const corePop = {
    hidden: { opacity: 0, scale: 0.4 },
    show: {
      opacity: 1,
      scale: 1,
      transition: { duration: DUR.relaxed, ease: EASE.spring },
    },
  };
  const tickGroup = {
    hidden: { opacity: 0, scale: 0.6 },
    show: {
      opacity: 1,
      scale: 1,
      transition: { duration: DUR.base, ease: EASE.spring },
    },
  };

  return (
    <motion.svg
      width={size}
      height={size}
      viewBox="0 0 512 512"
      role="img"
      aria-label="Stellaris Advisor logo"
      initial="hidden"
      animate="show"
      variants={container}
      style={{ transformOrigin: '256px 256px' }}
    >
      <LogoDefs />

      <motion.circle variants={fadeGroup} cx="256" cy="256" r="242" fill="url(#lgbg)" />

      <motion.g variants={fadeGroup} fill="#bfe8ff" style={{ transformOrigin: '256px 256px' }}>
        <circle cx="120" cy="150" r="2" opacity="0.8" />
        <circle cx="395" cy="135" r="1.6" opacity="0.6" />
        <circle cx="420" cy="300" r="2.2" opacity="0.7" />
        <circle cx="100" cy="350" r="1.6" opacity="0.6" />
        <circle cx="360" cy="395" r="1.8" opacity="0.7" />
        <circle cx="150" cy="410" r="1.4" opacity="0.5" />
        <circle cx="440" cy="210" r="1.4" opacity="0.5" />
        <circle cx="80" cy="240" r="1.6" opacity="0.6" />
      </motion.g>

      <motion.g
        variants={ringGroup}
        fill="none"
        stroke="url(#lgring)"
        strokeWidth="3"
        style={{ transformOrigin: '256px 256px' }}
      >
        <ellipse cx="256" cy="256" rx="168" ry="66" transform="rotate(-24 256 256)" opacity="0.9" />
        <ellipse cx="256" cy="256" rx="150" ry="150" opacity="0.45" />
        <ellipse cx="256" cy="256" rx="172" ry="78" transform="rotate(58 256 256)" opacity="0.65" />
      </motion.g>

      <motion.g variants={fadeGroup} filter="url(#lgsoft)">
        <circle cx="396" cy="206" r="8" fill="#7fe9ff" />
        <circle cx="128" cy="318" r="6" fill="#4fb8ff" />
        <circle cx="316" cy="378" r="5" fill="#9af0ff" />
      </motion.g>

      {/* The core: pops in with a spring overshoot, then breathes forever
          via a separate looping opacity animation layered on top of the
          one-time entrance scale. */}
      <motion.circle
        variants={corePop}
        cx="256"
        cy="256"
        r="96"
        fill="url(#lgcore)"
        filter="url(#lgglow)"
        style={{ transformOrigin: '256px 256px' }}
        animate={{ opacity: [0.75, 1, 0.75] }}
        transition={{ duration: 4, ease: 'easeInOut', repeat: Infinity, delay: DUR.relaxed * 2 }}
      />
      <motion.g variants={corePop} filter="url(#lgsoft)" style={{ transformOrigin: '256px 256px' }}>
        <path
          d="M256 168 C262 222 290 250 344 256 C290 262 262 290 256 344 C250 290 222 262 168 256 C222 250 250 222 256 168 Z"
          fill="url(#lgcore)"
        />
        <circle cx="256" cy="256" r="26" fill="#fff7e6" />
      </motion.g>

      {/* Outer frame traces itself on -- a satisfying "assembling" beat
          using Framer Motion's pathLength support on circles. */}
      <motion.circle
        cx="256"
        cy="256"
        r="242"
        fill="none"
        stroke="url(#lgframe)"
        strokeWidth="6"
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 1 }}
        transition={{ duration: DUR.relaxed * 1.6, ease: EASE.out, delay: DUR.base }}
      />
      <motion.circle
        variants={fadeGroup}
        cx="256"
        cy="256"
        r="230"
        fill="none"
        stroke="#2a89d6"
        strokeWidth="1.5"
        opacity="0.5"
      />

      <motion.g
        variants={tickGroup}
        stroke="#5fe6ff"
        strokeWidth="3"
        strokeLinecap="round"
        opacity="0.85"
        style={{ transformOrigin: '256px 256px' }}
      >
        <line x1="256" y1="20" x2="256" y2="38" />
        <line x1="256" y1="474" x2="256" y2="492" />
        <line x1="20" y1="256" x2="38" y2="256" />
        <line x1="474" y1="256" x2="492" y2="256" />
      </motion.g>
    </motion.svg>
  );
}

function LogoDefs() {
  return (
    <defs>
      <radialGradient id="lgbg" cx="50%" cy="38%" r="75%">
        <stop offset="0%" stopColor="#16233f" />
        <stop offset="55%" stopColor="#0b1326" />
        <stop offset="100%" stopColor="#060a16" />
      </radialGradient>
      <radialGradient id="lgcore" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stopColor="#fff6e0" />
        <stop offset="22%" stopColor="#ffe09a" />
        <stop offset="55%" stopColor="#ffb347" />
        <stop offset="100%" stopColor="#ff8a3c" stopOpacity="0" />
      </radialGradient>
      <linearGradient id="lgring" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#3ee0ff" />
        <stop offset="50%" stopColor="#5ad0ff" stopOpacity="0.55" />
        <stop offset="100%" stopColor="#2a7dff" />
      </linearGradient>
      <linearGradient id="lgframe" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor="#5fe6ff" />
        <stop offset="100%" stopColor="#1f6bd6" />
      </linearGradient>
      <filter id="lgsoft" x="-60%" y="-60%" width="220%" height="220%">
        <feGaussianBlur stdDeviation="6" result="b" />
        <feMerge>
          <feMergeNode in="b" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
      <filter id="lgglow" x="-80%" y="-80%" width="260%" height="260%">
        <feGaussianBlur stdDeviation="10" />
      </filter>
    </defs>
  );
}

/** Fully-assembled, non-animated render used under prefers-reduced-motion. */
function LogoStaticArt() {
  return (
    <>
      <circle cx="256" cy="256" r="242" fill="url(#lgbg)" />
      <g fill="#bfe8ff">
        <circle cx="120" cy="150" r="2" opacity="0.8" />
        <circle cx="395" cy="135" r="1.6" opacity="0.6" />
        <circle cx="420" cy="300" r="2.2" opacity="0.7" />
        <circle cx="100" cy="350" r="1.6" opacity="0.6" />
        <circle cx="360" cy="395" r="1.8" opacity="0.7" />
        <circle cx="150" cy="410" r="1.4" opacity="0.5" />
        <circle cx="440" cy="210" r="1.4" opacity="0.5" />
        <circle cx="80" cy="240" r="1.6" opacity="0.6" />
      </g>
      <g fill="none" stroke="url(#lgring)" strokeWidth="3">
        <ellipse cx="256" cy="256" rx="168" ry="66" transform="rotate(-24 256 256)" opacity="0.9" />
        <ellipse cx="256" cy="256" rx="150" ry="150" opacity="0.45" />
        <ellipse cx="256" cy="256" rx="172" ry="78" transform="rotate(58 256 256)" opacity="0.65" />
      </g>
      <g filter="url(#lgsoft)">
        <circle cx="396" cy="206" r="8" fill="#7fe9ff" />
        <circle cx="128" cy="318" r="6" fill="#4fb8ff" />
        <circle cx="316" cy="378" r="5" fill="#9af0ff" />
      </g>
      <circle cx="256" cy="256" r="96" fill="url(#lgcore)" filter="url(#lgglow)" opacity="0.9" />
      <g filter="url(#lgsoft)">
        <path
          d="M256 168 C262 222 290 250 344 256 C290 262 262 290 256 344 C250 290 222 262 168 256 C222 250 250 222 256 168 Z"
          fill="url(#lgcore)"
        />
        <circle cx="256" cy="256" r="26" fill="#fff7e6" />
      </g>
      <circle cx="256" cy="256" r="242" fill="none" stroke="url(#lgframe)" strokeWidth="6" />
      <circle cx="256" cy="256" r="230" fill="none" stroke="#2a89d6" strokeWidth="1.5" opacity="0.5" />
      <g stroke="#5fe6ff" strokeWidth="3" strokeLinecap="round" opacity="0.85">
        <line x1="256" y1="20" x2="256" y2="38" />
        <line x1="256" y1="474" x2="256" y2="492" />
        <line x1="20" y1="256" x2="38" y2="256" />
        <line x1="474" y1="256" x2="492" y2="256" />
      </g>
    </>
  );
}
