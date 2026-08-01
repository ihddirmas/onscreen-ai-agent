"use client";

import Link from "next/link";
import { ArrowRight, Check } from "lucide-react";

const plans = [
  {
    name: "Free",
    description: "For trying hosted mode",
    price: 0,
    features: [
      "On-screen AI overlay",
      "Voice + screenshot answers",
      "~$1 hosted credits / month",
      "1 reference document",
    ],
    cta: "Start free",
    href: "/login",
    popular: false,
  },
  {
    name: "Pro",
    description: "For daily power users",
    price: 9,
    features: [
      "Everything in Free",
      "~$15 hosted credits / month",
      "Unlimited reference documents",
      "Claude, GPT & Gemini models",
    ],
    cta: "Get Pro",
    href: "/login",
    popular: true,
  },
];

export function PricingSection() {
  return (
    <section id="pricing" className="relative py-32 lg:py-40 border-t border-foreground/10">
      <div className="max-w-7xl mx-auto px-6 lg:px-12">
        <div className="max-w-3xl mb-20">
          <span className="font-mono text-xs tracking-widest text-muted-foreground uppercase block mb-6">
            Pricing
          </span>
          <h2 className="font-display text-5xl md:text-6xl lg:text-7xl tracking-tight text-foreground mb-6">
            Simple, transparent
            <br />
            <span className="text-stroke">pricing</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-xl">
            Start free with hosted models. Upgrade when you need Claude, GPT, or Gemini.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-px bg-foreground/10 max-w-4xl mx-auto">
          {plans.map((plan, idx) => (
            <div
              key={plan.name}
              className={`relative p-8 lg:p-12 bg-background ${
                plan.popular ? "md:-my-4 md:py-12 lg:py-16 border-2 border-[#34d399]" : ""
              }`}
            >
              {plan.popular && (
                <span className="absolute -top-3 left-8 px-3 py-1 bg-[#059669] text-white text-xs font-mono uppercase tracking-widest">
                  Most popular
                </span>
              )}

              <div className="mb-8">
                <span className="font-mono text-xs text-muted-foreground">
                  {String(idx + 1).padStart(2, "0")}
                </span>
                <h3 className="font-display text-3xl text-foreground mt-2">{plan.name}</h3>
                <p className="text-sm text-muted-foreground mt-2">{plan.description}</p>
              </div>

              <div className="mb-8 pb-8 border-b border-foreground/10">
                <div className="flex items-baseline gap-2">
                  <span className="font-display text-5xl lg:text-6xl text-foreground">
                    ${plan.price}
                  </span>
                  <span className="text-muted-foreground">/month</span>
                </div>
              </div>

              <ul className="space-y-4 mb-10">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3">
                    <Check className="w-4 h-4 text-[#059669] mt-0.5 shrink-0" />
                    <span className="text-sm text-muted-foreground">{feature}</span>
                  </li>
                ))}
              </ul>

              <Link
                href={plan.href}
                className={`w-full py-4 flex items-center justify-center gap-2 text-sm font-medium transition-all group ${
                  plan.popular
                    ? "bg-[#059669] text-white hover:bg-[#10b981]"
                    : "border border-foreground/20 text-foreground hover:border-[#34d399]/50 hover:bg-[#34d399]/5"
                }`}
              >
                {plan.cta}
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
              </Link>
            </div>
          ))}
        </div>

        <p className="mt-12 text-center text-sm text-muted-foreground">
          No API key required for hosted trial · Bring your own key anytime in Settings
        </p>
      </div>
    </section>
  );
}
