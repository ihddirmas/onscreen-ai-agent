import type { ReactNode } from "react";
import { ONCUE } from "@/lib/oncue-brand";

type OverlayMockupProps = {
  hotkey?: string;
  question: string;
  answer: ReactNode;
  className?: string;
};

/** Monochrome desktop HUD preview — matches oncue/ui/theme.py */
export function OverlayMockup({
  hotkey = "Ctrl+Shift+Space",
  question,
  answer,
  className = "",
}: OverlayMockupProps) {
  return (
    <div
      className={`w-full max-w-sm rounded-2xl border border-white/25 bg-[#12121a]/95 p-4 shadow-2xl backdrop-blur-sm ${className}`}
    >
      <div className="mb-3 flex items-center gap-2 border-b border-white/10 pb-2">
        <span className="text-xs font-bold tracking-wide text-white/90">● OnCUE</span>
        <span className="ml-auto font-mono text-[10px] text-white/40">{hotkey}</span>
      </div>
      <p className="text-sm text-indigo-200/90">{question}</p>
      <div
        className="mt-3 rounded-lg border border-white/10 bg-[#0c0c14] p-3 text-sm leading-relaxed"
        style={{ color: ONCUE.hudText }}
      >
        {answer}
      </div>
    </div>
  );
}

/** Default hero mockup */
export function HeroOverlayMockup() {
  return (
    <OverlayMockup
      question="summarize this chart for my standup"
      answer={
        <>
          <p>
            <span className="text-white font-medium">Weekly signups dipped 18%</span> after Tuesday
            — mostly mobile onboarding. Completion at step 3 (verify phone) fell from 72% → 51%.
          </p>
          <p className="mt-2" style={{ color: ONCUE.hudMuted }}>
            Suggest: shorten OTP flow or add WhatsApp login for India traffic.
          </p>
        </>
      }
    />
  );
}
