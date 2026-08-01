"use client";

import { useEffect, useRef, useState } from "react";
import { OverlayMockup } from "./overlay-mockup";

const useCases = [
  {
    id: "debug",
    label: "Debug faster",
    tag: "Developers",
    title: "Ask about the error on screen",
    description:
      "Stack trace in VS Code? Press Ctrl+Shift+Space, ask what broke, and get a fix without alt-tabbing to a browser tab.",
    hotkey: "Ctrl+Shift+Space",
    question: "why is this TypeError happening on line 42?",
    answer: (
      <>
        <p>
          <span className="text-white font-medium">user.profile</span> is undefined — the API
          returned null for guests. Add optional chaining:{" "}
          <code className="font-mono text-xs text-white/80">user?.profile?.name</code>
        </p>
      </>
    ),
    backdrop: (
      <div className="absolute inset-0 bg-[#1e1e1e] p-4 font-mono text-[10px] text-green-400/80 leading-relaxed">
        <div className="text-red-400">TypeError: Cannot read properties of undefined</div>
        <div className="text-white/40 mt-2">at renderProfile (App.tsx:42)</div>
      </div>
    ),
  },
  {
    id: "dictate",
    label: "Dictate naturally",
    tag: "Students & chat",
    title: "Hinglish into any text field",
    description:
      "Hold Ctrl+Shift+D and speak the way you actually talk. Text lands in WhatsApp, Gmail, or Notion — Roman Hindi supported.",
    hotkey: "Ctrl+Shift+D",
    question: "yaar meeting kal 4 baje shift ho gayi",
    answer: (
      <p className="text-white/70 italic text-xs">→ pasted into WhatsApp</p>
    ),
    backdrop: (
      <div className="absolute inset-0 bg-[#0b141a] p-4">
        <div className="ml-auto max-w-[70%] rounded-lg bg-[#005c4b] px-3 py-2 text-xs text-white/90">
          yaar meeting kal 4 baje shift ho gayi
        </div>
      </div>
    ),
  },
  {
    id: "standup",
    label: "Standups & charts",
    tag: "Analytics",
    title: "Summarize what you're looking at",
    description:
      "Dashboard open in a meeting? Ask OnCUE to explain the dip, suggest next steps, and talk through it on the overlay.",
    hotkey: "Ctrl+Shift+Space",
    question: "summarize this chart for my standup",
    answer: (
      <>
        <p>
          <span className="text-white font-medium">Weekly signups dipped 18%</span> after Tuesday.
          Suggest shortening the OTP step for mobile users.
        </p>
      </>
    ),
    backdrop: (
      <div className="absolute inset-0 bg-white p-4">
        <div className="h-full rounded border border-foreground/10 flex items-end gap-1 px-2 pb-2">
          {[40, 65, 55, 30, 48, 70, 62].map((h, i) => (
            <div key={i} className="flex-1 bg-foreground/20 rounded-t" style={{ height: `${h}%` }} />
          ))}
        </div>
      </div>
    ),
  },
  {
    id: "exam",
    label: "Study with your notes",
    tag: "Exam prep",
    title: "Answers grounded in your PDFs",
    description:
      "Upload notes in the dashboard. OnCUE cites your documents via RAG instead of generic web answers.",
    hotkey: "Ctrl+Shift+H",
    question: "explain Krebs cycle from my notes",
    answer: (
      <p>
        Per your <span className="text-white font-medium">bio-chapter-7.pdf</span>: the cycle oxidizes
        acetyl-CoA to CO₂, producing NADH and FADH₂ for the electron transport chain…
      </p>
    ),
    backdrop: (
      <div className="absolute inset-0 bg-[#fafafa] p-4 text-[10px] text-foreground/70">
        <div className="font-display text-sm text-foreground mb-2">bio-chapter-7.pdf</div>
        <p>The citric acid cycle begins when acetyl-CoA…</p>
      </div>
    ),
  },
  {
    id: "demo",
    label: "Invisible on share",
    tag: "Demos & calls",
    title: "Clients never see your buddy",
    description:
      "Toggle “Hide from screen sharing” before Zoom or Meet. You get answers; your audience only sees your deck.",
    hotkey: "Settings",
    question: "what should I say about Q3 pipeline?",
    answer: (
      <p>
        Lead with the <span className="text-white font-medium">enterprise pilot</span> — 3 logos in
        legal, $420k weighted pipeline. De-risk the timeline objection upfront.
      </p>
    ),
    backdrop: (
      <div className="absolute inset-0 bg-[#2d2d30] flex items-center justify-center">
        <div className="text-white/30 text-xs font-mono">Zoom — Screen Share Active</div>
      </div>
    ),
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
              {current.backdrop}
              <div className="absolute bottom-4 right-4 w-[min(100%,280px)] scale-95 origin-bottom-right">
                <OverlayMockup
                  hotkey={current.hotkey}
                  question={current.question}
                  answer={current.answer}
                />
              </div>
            </div>
            <p className="mt-3 text-center text-xs font-mono text-muted-foreground">
              Simulated screen + OnCUE overlay
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
