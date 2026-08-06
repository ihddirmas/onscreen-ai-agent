"use client";

import { useEffect, useRef } from "react";

/** OnCUE variant: wireframe cube (not filled tetrahedron). */
export function AnimatedTetrahedron() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const frameRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const chars = "│─┌┐└┘";
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

    const vertices = [
      { x: -1, y: -1, z: -1 },
      { x: 1, y: -1, z: -1 },
      { x: 1, y: 1, z: -1 },
      { x: -1, y: 1, z: -1 },
      { x: -1, y: -1, z: 1 },
      { x: 1, y: -1, z: 1 },
      { x: 1, y: 1, z: 1 },
      { x: -1, y: 1, z: 1 },
    ];

    const edges = [
      [0, 1], [1, 2], [2, 3], [3, 0],
      [4, 5], [5, 6], [6, 7], [7, 4],
      [0, 4], [1, 5], [2, 6], [3, 7],
    ];

    const rotate = (
      point: { x: number; y: number; z: number },
      ax: number,
      ay: number,
      az: number
    ) => {
      let { x, y, z } = point;
      let cos = Math.cos(ay);
      let sin = Math.sin(ay);
      x = x * cos - z * sin;
      z = x * sin + z * cos;

      cos = Math.cos(ax);
      sin = Math.sin(ax);
      const ny = y * cos - z * sin;
      z = y * sin + z * cos;
      y = ny;

      cos = Math.cos(az);
      sin = Math.sin(az);
      const nx = x * cos - y * sin;
      y = x * sin + y * cos;
      x = nx;

      return { x, y, z };
    };

    const render = () => {
      const rect = canvas.getBoundingClientRect();
      ctx.clearRect(0, 0, rect.width, rect.height);

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const scale = Math.min(rect.width, rect.height) * 0.32;

      ctx.font = "16px monospace";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";

      const points: { x: number; y: number; z: number; char: string }[] = [];

      edges.forEach(([i, j]) => {
        const v1 = vertices[i];
        const v2 = vertices[j];
        for (let t = 0; t <= 1; t += 0.08) {
          const raw = {
            x: v1.x + (v2.x - v1.x) * t,
            y: v1.y + (v2.y - v1.y) * t,
            z: v1.z + (v2.z - v1.z) * t,
          };
          const point = rotate(raw, time * 0.35, time * 0.5, time * 0.15);
          const depth = (point.z + 2) / 4;
          const charIndex = Math.floor(depth * (chars.length - 1));
          points.push({
            x: centerX + point.x * scale,
            y: centerY - point.y * scale,
            z: point.z,
            char: chars[charIndex],
          });
        }
      });

      points.sort((a, b) => a.z - b.z);
      points.forEach((point) => {
        const alpha = 0.2 + (point.z + 1.5) * 0.35;
        ctx.fillStyle = `rgba(0, 0, 0, ${Math.min(alpha, 0.85)})`;
        ctx.fillText(point.char, point.x, point.y);
      });

      time += 0.018;
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
