import { useEffect, useRef } from 'react';
import { usePrefersReducedMotion } from '../motion';
import './Background.css';

/** Ambient deep-space backdrop: a slow-drifting nebula gradient (pure CSS)
 * behind a twinkling starfield (canvas, since per-pixel twinkle isn't
 * practical in CSS/DOM). Both are inert to pointer events and sit behind
 * everything else. Under prefers-reduced-motion the nebula's drift keyframe
 * is disabled in CSS and the starfield renders once, statically, with no
 * animation loop at all. */
export default function Background() {
  const canvasRef = useRef(null);
  const reduced = usePrefersReducedMotion();

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    let stars = [];
    let raf = null;

    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      const count = Math.min(160, Math.round((window.innerWidth * window.innerHeight) / 9000));
      stars = Array.from({ length: count }, () => ({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        z: Math.random() * 0.8 + 0.2,
        t: Math.random() * Math.PI * 2,
      }));
      drawFrame(false); // always paint at least one frame, even when reduced
    }

    function drawFrame(animate) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (const s of stars) {
        let tw = 1;
        if (animate) {
          s.t += 0.02 * s.z;
          tw = 0.5 + 0.5 * Math.sin(s.t);
          s.y += 0.06 * s.z;
          if (s.y > canvas.height) s.y = 0;
        }
        ctx.globalAlpha = (0.25 + 0.75 * tw) * s.z;
        ctx.fillStyle = s.z > 0.75 ? '#bcd6ff' : '#6f86c0';
        const r = s.z * 1.5;
        ctx.fillRect(s.x, s.y, r, r);
      }
      ctx.globalAlpha = 1;
    }

    function loop() {
      drawFrame(true);
      raf = requestAnimationFrame(loop);
    }

    resize();
    window.addEventListener('resize', resize);
    if (!reduced) raf = requestAnimationFrame(loop);

    return () => {
      window.removeEventListener('resize', resize);
      if (raf) cancelAnimationFrame(raf);
    };
  }, [reduced]);

  return (
    <>
      <div className="bg-nebula" aria-hidden="true" />
      <canvas ref={canvasRef} className="bg-stars" aria-hidden="true" />
    </>
  );
}
