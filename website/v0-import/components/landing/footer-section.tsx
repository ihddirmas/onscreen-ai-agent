"use client";

import Link from "next/link";
import { AnimatedWave } from "./animated-wave";

const footerLinks = {
  Product: [
    { name: "Features", href: "#features" },
    { name: "Hotkeys", href: "#hotkeys" },
    { name: "How it works", href: "#how-it-works" },
    { name: "Pricing", href: "#pricing" },
    { name: "Download", href: "/download" },
  ],
  Account: [
    { name: "Sign in", href: "/login" },
    { name: "Dashboard", href: "/dashboard" },
  ],
};

export function FooterSection() {
  return (
    <footer className="relative border-t border-foreground/10">
      <div className="absolute inset-0 h-64 opacity-20 pointer-events-none overflow-hidden">
        <AnimatedWave />
      </div>

      <div className="relative z-10 max-w-[1400px] mx-auto px-6 lg:px-12">
        <div className="py-16 lg:py-24">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-12 lg:gap-8">
            <div className="col-span-2 md:col-span-2">
              <Link href="/" className="font-display text-3xl tracking-tight flex items-center gap-2">
                <span className="text-[#34d399]">●</span>
                OnCUE
              </Link>
              <p className="mt-4 text-sm text-muted-foreground max-w-sm leading-relaxed">
                Your on-screen AI assistant — screenshot Q&A, Hinglish dictation, and
                document-grounded answers without leaving your workflow.
              </p>
            </div>

            {Object.entries(footerLinks).map(([category, links]) => (
              <div key={category}>
                <h4 className="font-mono text-xs uppercase tracking-widest text-muted-foreground mb-4">
                  {category}
                </h4>
                <ul className="space-y-3">
                  {links.map((link) => (
                    <li key={link.name}>
                      <Link
                        href={link.href}
                        className="text-sm text-foreground/70 hover:text-foreground transition-colors"
                      >
                        {link.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <div className="py-8 border-t border-foreground/10 flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-sm text-muted-foreground">© {new Date().getFullYear()} OnCUE</p>
          <p className="text-xs font-mono text-muted-foreground">
            Ctrl+Shift+Space · Ctrl+Shift+D · Ctrl+Shift+H
          </p>
        </div>
      </div>
    </footer>
  );
}
