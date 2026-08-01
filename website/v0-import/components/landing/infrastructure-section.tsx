"use client";

import { useEffect, useState, useRef } from "react";

const locations = [
  { city: "LiteLLM proxy", region: "Hosted backend", latency: "~400ms TTFT" },
  { city: "Usage API", region: "Trial & billing", latency: "session check" },
  { city: "RAG service", region: "Your documents", latency: "grounded answers" },
  { city: "Groq STT", region: "Speech (cloud)", latency: "Hinglish dictation" },
  { city: "Local Whisper", region: "Offline STT", latency: "private mode" },
  { city: "Desktop overlay", region: "Tray + hotkeys", latency: "<1s to first token" },
];

export function InfrastructureSection() {
  const [isVisible, setIsVisible] = useState(false);
  const [activeLocation, setActiveLocation] = useState(0);
  const sectionRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setIsVisible(true);
      },
      { threshold: 0.1 }
    );

    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveLocation((prev) => (prev + 1) % locations.length);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section ref={sectionRef} className="relative py-24 lg:py-32 overflow-hidden">
      <div className="max-w-[1400px] mx-auto px-6 lg:px-12">
        <div className="grid lg:grid-cols-2 gap-16 lg:gap-24 items-center">
          {/* Left: Content */}
          <div
            className={`transition-all duration-700 ${
              isVisible ? "opacity-100 translate-x-0" : "opacity-0 -translate-x-8"
            }`}
          >
            <span className="inline-flex items-center gap-3 text-sm font-mono text-muted-foreground mb-6">
              <span className="w-8 h-px bg-foreground/30" />
              Infrastructure
            </span>
            <h2 className="text-4xl lg:text-6xl font-display tracking-tight mb-8">
              Hosted stack,
              <br />
              one click.
            </h2>
            <p className="text-xl text-muted-foreground leading-relaxed mb-12">
              Sign in on the dashboard → <strong>Open OnCUE app</strong> sends your license key,
              usage API, RAG URL, and LiteLLM backend via <code className="font-mono text-sm">oncue://connect</code>.
              Or bring your own Groq / Claude / GPT / Gemini keys.
            </p>

            <div className="grid grid-cols-3 gap-8">
              <div>
                <div className="text-4xl lg:text-5xl font-display mb-2">5</div>
                <div className="text-sm text-muted-foreground">Global hotkeys</div>
              </div>
              <div>
                <div className="text-4xl lg:text-5xl font-display mb-2">BYO</div>
                <div className="text-sm text-muted-foreground">Or hosted trial</div>
              </div>
              <div>
                <div className="text-4xl lg:text-5xl font-display mb-2">RAG</div>
                <div className="text-sm text-muted-foreground">Your documents</div>
              </div>
            </div>
          </div>

          {/* Right: Location list */}
          <div
            className={`transition-all duration-700 delay-200 ${
              isVisible ? "opacity-100 translate-x-0" : "opacity-0 translate-x-8"
            }`}
          >
            <div className="border border-foreground/10">
              {/* Header */}
              <div className="px-6 py-4 border-b border-foreground/10 flex items-center justify-between">
                <span className="text-sm font-mono text-muted-foreground">Edge Network</span>
                <span className="flex items-center gap-2 text-xs font-mono text-green-600">
                  <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  All operational
                </span>
              </div>

              {/* Locations */}
              <div>
                {locations.map((location, index) => (
                  <div
                    key={location.city}
                    className={`px-6 py-5 border-b border-foreground/5 last:border-b-0 flex items-center justify-between transition-all duration-300 ${
                      activeLocation === index ? "bg-foreground/[0.02]" : ""
                    }`}
                  >
                    <div className="flex items-center gap-4">
                      <span 
                        className={`w-2 h-2 rounded-full transition-colors duration-300 ${
                          activeLocation === index ? "bg-foreground" : "bg-foreground/20"
                        }`}
                      />
                      <div>
                        <div className="font-medium">{location.city}</div>
                        <div className="text-sm text-muted-foreground">{location.region}</div>
                      </div>
                    </div>
                    <span className="font-mono text-sm text-muted-foreground">{location.latency}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
