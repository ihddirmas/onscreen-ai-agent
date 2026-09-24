"use client";

import { useEffect, useRef, useState } from "react";
import { HOTKEYS } from "@/lib/oncue-brand";

export function HotkeysSection() {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setIsVisible(true);
      },
      { threshold: 0.1 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  return (
    <section id="hotkeys" ref={ref} className="relative py-24 lg:py-32 border-t border-foreground/10">
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12">
        <div className="mb-16 lg:mb-24">
          <span className="inline-flex items-center gap-3 text-sm font-mono text-muted-foreground mb-6">
            <span className="w-8 h-px bg-foreground/30" />
            Hotkeys
          </span>
          <h2
            className={`text-4xl lg:text-6xl font-display tracking-tight transition-all duration-700 ${
              isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
            }`}
          >
            Five shortcuts.
            <br />
            <span className="text-muted-foreground">Zero alt-tab.</span>
          </h2>
          <p className="mt-6 text-lg text-muted-foreground max-w-2xl">
            Global hotkeys work over any window — customize every binding in the desktop app under
            Settings → Behavior.
          </p>
        </div>

        <div className="grid gap-px bg-foreground/10 md:grid-cols-2 lg:grid-cols-3">
          {HOTKEYS.map((hk, i) => (
            <div
              key={hk.keys}
              className={`group bg-background p-8 lg:p-10 hover-lift transition-all duration-500 ${
                isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"
              }`}
              style={{ transitionDelay: `${i * 80}ms` }}
            >
              <span className="font-mono text-xs text-muted-foreground block mb-4">
                {String(i + 1).padStart(2, "0")}
              </span>
              <kbd className="inline-block font-mono text-xs px-3 py-1.5 border border-foreground/20 bg-foreground/[0.03] mb-4">
                {hk.keys}
              </kbd>
              <h3 className="font-display text-2xl mb-2 group-hover:translate-x-1 transition-transform duration-300">
                {hk.title}
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{hk.description}</p>
            </div>
          ))}
          <div
            className={`bg-foreground text-background p-8 lg:p-10 md:col-span-2 lg:col-span-1 flex flex-col justify-center transition-all duration-500 ${
              isVisible ? "opacity-100" : "opacity-0"
            }`}
            style={{ transitionDelay: "400ms" }}
          >
            <span className="font-mono text-xs tracking-widest text-background/50 uppercase mb-4">
              Tray app
            </span>
            <p className="font-display text-2xl lg:text-3xl leading-snug">
              Always one hotkey away.
            </p>
            <p className="mt-4 text-sm text-background/60 leading-relaxed">
              Hide from screen sharing before Zoom or Meet — your viewers won&apos;t see the overlay.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
