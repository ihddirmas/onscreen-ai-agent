"use client";

import Image from "next/image";
import { useEffect, useRef, useState } from "react";

const useCases = [
  {
    id: "debug",
    label: "Debug faster",
    tag: "Developers",
    title: "Ask about the error on screen",
    description:
      "Stack trace in VS Code? Press Ctrl+Shift+Space, ask what broke, and get a fix without alt-tabbing to a browser tab.",
    image: "/screenshots/use-case-debug.png",
    alt: "OnCUE overlay explaining a TypeError in VS Code",
  },
  {
    id: "dictate",
    label: "Dictate naturally",
    tag: "Students & chat",
    title: "Hinglish into any text field",
    description:
      "Hold Ctrl+Shift+D and speak the way you actually talk. Text lands in WhatsApp, Gmail, or Notion — Roman Hindi supported.",
    image: "/screenshots/use-case-dictate.png",
    alt: "OnCUE dictation overlay over a chat app",
  },
  {
    id: "standup",
    label: "Standups & charts",
    tag: "Analytics",
    title: "Summarize what you're looking at",
    description:
      "Dashboard open in a meeting? Ask OnCUE to explain the dip, suggest next steps, and talk through it on the overlay.",
    image: "/screenshots/use-case-standup.png",
    alt: "OnCUE summarizing a weekly signups chart for a standup",
  },
  {
    id: "exam",
    label: "Study with your notes",
    tag: "Exam prep",
    title: "Answers grounded in your PDFs",
    description:
      "Upload notes in the dashboard. OnCUE cites your documents via RAG instead of generic web answers.",
    image: "/screenshots/use-case-exam.png",
    alt: "OnCUE answering an exam question from uploaded PDF notes",
  },
  {
    id: "demo",
    label: "Invisible on share",
    tag: "Demos & calls",
    title: "Clients never see your buddy",
    description:
      "Toggle “Hide from screen sharing” before Zoom or Meet. You get answers; your audience only sees your deck.",
    image: "/screenshots/use-case-demo.png",
    alt: "OnCUE overlay during a Zoom screen share — visible only to you",
  },
];

export function UseCasesSection() {
  const [active, setActive] = useState(0);
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

  const current = useCases[active];

  return (
    <section id="use-cases" ref={ref} className="relative py-32 lg:py-40 border-t border-foreground/10">
      <div className="max-w-7xl mx-auto px-6 lg:px-12">
        <div className="max-w-3xl mb-16">
          <span className="font-mono text-xs tracking-widest text-muted-foreground uppercase block mb-6">
            Use cases
          </span>
          <h2
            className={`font-display text-5xl md:text-6xl tracking-tight transition-all duration-700 ${
              isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
            }`}
          >
            Your desktop buddy
            <br />
            <span className="text-stroke">in the wild</span>
          </h2>
          <p className="mt-6 text-lg text-muted-foreground max-w-xl">
            Same frontier models as everyone else — OnCUE breaks them out of browser tabs. Press a
            hotkey, ask about what you see, dictate, or study from your docs.
          </p>
        </div>

        <div className="flex flex-wrap gap-2 mb-12">
          {useCases.map((uc, i) => (
            <button
              key={uc.id}
              onClick={() => setActive(i)}
              className={`px-4 py-2 text-sm font-mono border transition-all duration-300 ${
                active === i
                  ? "bg-foreground text-background border-foreground"
                  : "border-foreground/20 text-muted-foreground hover:border-foreground/40 hover:text-foreground"
              }`}
            >
              {uc.label}
            </button>
          ))}
        </div>

        <div
          className={`grid lg:grid-cols-2 gap-12 lg:gap-20 items-center transition-all duration-500 ${
            isVisible ? "opacity-100" : "opacity-0"
          }`}
        >
          <div>
            <span className="font-mono text-xs text-muted-foreground uppercase tracking-widest">
              {current.tag}
            </span>
            <h3 className="font-display text-3xl lg:text-4xl mt-3 mb-4">{current.title}</h3>
            <p className="text-lg text-muted-foreground leading-relaxed">{current.description}</p>
          </div>

          <div className="relative">
            <div className="relative aspect-[4/3] rounded-xl border border-foreground/10 overflow-hidden bg-background shadow-lg">
              <Image
                key={current.image}
                src={current.image}
                alt={current.alt}
                fill
                className="object-cover object-center transition-opacity duration-300"
                sizes="(max-width: 1024px) 100vw, 50vw"
                priority={active === 0}
              />
            </div>
            <p className="mt-3 text-center text-xs font-mono text-muted-foreground">
              Real OnCUE desktop overlay · captured from Qt UI
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
