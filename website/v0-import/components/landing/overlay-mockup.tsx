/** OnCUE overlay preview for marketing hero — matches desktop HUD styling. */
export function OverlayMockup() {
  return (
    <div className="w-full max-w-sm rounded-2xl border border-emerald-500/30 bg-[#12121a]/95 p-4 shadow-2xl backdrop-blur-sm">
      <div className="mb-3 flex items-center gap-2 border-b border-white/10 pb-2">
        <span className="text-xs font-bold tracking-wide text-emerald-400">● OnCUE</span>
        <span className="ml-auto font-mono text-[10px] text-white/40">Ctrl+Shift+Space</span>
      </div>
      <p className="text-sm text-indigo-200/90">summarize this chart for my standup</p>
      <div className="mt-3 rounded-lg border border-white/10 bg-[#0c0c14] p-3 text-sm leading-relaxed text-zinc-200">
        <p>
          <span className="text-emerald-300">Weekly signups dipped 18%</span> after Tuesday — mostly
          mobile onboarding. Completion at step 3 (verify phone) fell from 72% → 51%.
        </p>
        <p className="mt-2 text-white/55">
          Suggest: shorten OTP flow or add WhatsApp login for India traffic.
        </p>
      </div>
    </div>
  );
}
