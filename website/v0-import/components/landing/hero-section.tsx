"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import { AnimatedSphere } from "./animated-sphere";
import { HeroOverlayMockup } from "./overlay-mockup";
import { BTN_PRIMARY, SECTION_LINE } from "@/lib/oncue-brand";

const words = ["ask", "dictate", "explain", "ship"];

const marqueeStats = [
  { value: "100% free", label: "to start — no card needed", tag: "TRIAL" },
  { value: "1 hotkey", label: "replaces the alt-tab cycle", tag: "FLOW" },
  { value: "Hinglish", label: "dictation at your cursor", tag: "VOICE" },
  { value: "Private", label: "invisible on screen share", tag: "DEMOS" },
];

export function HeroSection() {
  const [isVisible, setIsVisible] = useState(false);
  const [wordIndex, setWordIndex] = useState(0);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setWordIndex((prev) => (prev + 1) % words.length);
    }, 3200);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="relative min-h-screen flex flex-col justify-center overflow-hidden">
      <div className="absolute right-0 top-1/2 -translate-y-1/2 w-[600px] h-[600px] lg:w-[800px] lg:h-[800px] opacity-35 pointer-events-none">
        <AnimatedSphere />
      </div>

      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-25">
        {[...Array(6)].map((_, i) => (
          <div
            key={`h-${i}`}
            className="absolute h-px bg-foreground/10"
            style={{ top: `${16.66 * (i + 1)}%`, left: 0, right: 0 }}
          />
        ))}
      </div>

      <div className="relative z-10 max-w-[1400px] mx-auto px-6 lg:px-12 py-32 lg:py-40">
        <div
          className={`mb-8 transition-all duration-700 ${
            isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
          }`}
        >
          <span className="inline-flex items-center gap-3 text-sm font-mono text-muted-foreground">
            <span className={`w-8 h-px ${SECTION_LINE}`} />
            An AI buddy on your desktop
          </span>
        </div>

        <div className="mb-12">
          <h1
            className={`text-[clamp(2.75rem,11vw,9rem)] font-display leading-[0.92] tracking-tight transition-all duration-1000 ${
              isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
            }`}
          >
            <span className="block text-muted-foreground text-[0.55em] mb-2">Press a hotkey.</span>
            <span className="block">Then </span>
            <span className="relative inline-block">
              <span key={wordIndex} className="inline-flex">
                {words[wordIndex].split("").map((char, i) => (
                  <span
                    key={`${wordIndex}-${i}`}
                    className="inline-block animate-word-rise"
                    style={{ animationDelay: `${i * 40}ms` }}
                  >
                    {char}
                  </span>
                ))}
              </span>
              <span className="absolute -bottom-1 left-0 right-0 h-2 bg-foreground/10 line-reveal" />
            </span>
            <span className="text-muted-foreground">.</span>
          </h1>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 lg:gap-24 items-end">
          <div>
            <p
              className={`text-xl lg:text-2xl text-muted-foreground leading-relaxed max-w-xl transition-all duration-700 delay-200 ${
                isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
              }`}
            >
              OnCUE lives on your desktop — it sees what you see, answers about anything on screen,
              dictates in Hinglish, and stays invisible when you screen-share.
            </p>

            <div
              className={`flex flex-col sm:flex-row items-start gap-4 mt-10 transition-all duration-700 delay-300 ${
                isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
              }`}
            >
              <Button asChild size="lg" className={`${BTN_PRIMARY} px-8 h-14 text-base group`}>
                <Link href="/login">
                  Start free
                  <ArrowRight className="w-4 h-4 ml-2 transition-transform group-hover:translate-x-1" />
                </Link>
              </Button>
              <Button
                asChild
                size="lg"
                variant="outline"
                className="h-14 px-8 text-base rounded-full border-foreground/20 hover:bg-foreground/5"
              >
                <a href="#use-cases">See use cases</a>
              </Button>
            </div>
            <p className="mt-6 text-sm font-mono text-muted-foreground">
              Windows & Linux · No API key for hosted trial
            </p>
          </div>

          <div
            className={`mt-10 lg:mt-0 transition-all duration-700 delay-400 ${
              isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"
            }`}
          >
            <HeroOverlayMockup />
          </div>
        </div>
      </div>

      <div
        className={`absolute bottom-24 left-0 right-0 transition-all duration-700 delay-500 ${
          isVisible ? "opacity-100" : "opacity-0"
        }`}
      >
        <div className="flex gap-16 marquee-reverse whitespace-nowrap">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="flex gap-16">
              {marqueeStats.map((stat) => (
                <div key={`${stat.tag}-${i}`} className="flex items-baseline gap-4">
                  <span className="text-4xl lg:text-5xl font-display">{stat.value}</span>
                  <span className="text-sm text-muted-foreground">
                    {stat.label}
                    <span className="block font-mono text-xs mt-1">{stat.tag}</span>
                  </span>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
