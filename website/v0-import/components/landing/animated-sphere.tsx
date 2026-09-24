"use client";

import { useEffect, useRef } from "react";

/** OnCUE variant: dual-ring orbit (not a solid sphere) — distinct from v0 Optimus sphere. */
export function AnimatedSphere() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const frameRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const chars = "◇◆○●·∘";
    let time = 0;

    const resize = () => {
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    resize();
    window.addEventListener("resize", resize);

    const render = () => {
      const rect = canvas.getBoundingClientRect();
      ctx.clearRect(0, 0, rect.width, rect.height);

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const baseRadius = Math.min(rect.width, rect.height) * 0.38;

      ctx.font = "11px monospace";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";

      const rings = [
        { radius: baseRadius, tilt: 0.35, speed: 0.45, count: 48 },
        { radius: baseRadius * 0.72, tilt: -0.55, speed: -0.32, count: 36 },
      ];

      rings.forEach((ring) => {
        for (let i = 0; i < ring.count; i++) {
          const angle = (i / ring.count) * Math.PI * 2 + time * ring.speed;
          const x = Math.cos(angle) * ring.radius;
          const y = Math.sin(angle) * ring.radius * Math.cos(ring.tilt);
          const z = Math.sin(angle) * ring.radius * Math.sin(ring.tilt);

          const depth = (z + ring.radius) / (ring.radius * 2);
          const alpha = 0.12 + depth * 0.55;
          const charIndex = Math.floor(depth * (chars.length - 1));

          ctx.fillStyle = `rgba(0, 0, 0, ${alpha})`;
          ctx.fillText(chars[charIndex], centerX + x, centerY + y * 0.85);
        }
      });

      time += 0.012;
      frameRef.current = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(frameRef.current);
    };
  }, []);

  return <canvas ref={canvasRef} className="w-full h-full" style={{ display: "block" }} />;
}
