# Parakeet.ai — Copy Review

## Top findings

**1. Payments aren't actually live — don't let hosted-tier copy read as a live purchase.**
The website (`website/app/page.tsx`) explicitly states *"Payments coming soon — Pro is a placeholder for now."* Even though the licensing/dashboard/metered-budget plumbing is real and shippable, there is no working checkout yet. Every hosted-tier CTA in this campaign is written as "join the cohort / hosted beta" rather than "buy Pro for $9" to avoid a bait-and-switch the moment someone clicks through. **Before publishing, confirm this is still accurate** — if Stripe has since gone live, update the ad/email/calendar copy referencing "cohort" language to real pricing.

**2. macOS is a code capability, not a shippable download claim.**
The repo only contains a Windows PyInstaller spec (`packaging/parakeet.spec` → `dist/Parakeet.exe`); there's no `.dmg`/py2app artifact anywhere (confirmed: `pynput` branches on `darwin` in the spec, but no macOS packaging target exists). Every download CTA in this campaign is scoped to "Windows" only, even though README/GUIDE describe the app as cross-platform. If a macOS build exists elsewhere and isn't in this repo, download CTAs can be widened back to "Windows & macOS."

**3. Screen-share-invisible framing needs a standing guardrail, not a one-time check.**
This is the single highest-risk feature for drifting into an interview/exam-cheating dog-whistle. Every instance across landing page, Email 3, LinkedIn, the X thread, Ad Variant 4, and the video script is scoped strictly to "demos" and "client calls" — never proximity, never eval/interview/exam language, not even as a joke. Flagged specifically in Ad Variant 4 and Day 4 of the calendar as the piece to re-check on every reuse or repurpose, since ad copy is the most likely to get remixed downstream without full context.

## Pass-through checks

- 5-second hero test passes (headline + subhead name audience, action, and mechanism).
- One primary CTA maintained per piece throughout.
- No hard-banned phrases ("game-changing," "revolutionary," "in today's competitive landscape," generic "learn more" CTAs, hollow social proof) appear anywhere.
- Ad claims (Hinglish default, keyless search, meeting copilot, screen-share invisibility) match landing page claims 1:1.
- Email subjects match body content with no bait-and-switch.
- Social proof sections are explicitly placeholder-labeled rather than pre-filled with invented numbers.
