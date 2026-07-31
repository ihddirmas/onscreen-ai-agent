# Demo Video Outline — OnCUE.ai (≤ 3 minutes)

> Record on a **real Windows machine** with screen capture. Upload to YouTube as **public**. No copyrighted music.

**Target length:** 2:45 (leaves buffer under the 3:00 judge cutoff)

---

## 0:00–0:10 | Hook

**Visual:** Student sees a code error. Starts to screenshot → alt-tab to ChatGPT → paste → wait.

**On-screen text:** "Screenshot. Alt-tab. Paste. Wait."

**VO:** "This is how most students get an AI answer. OnCUE skips all of it."

---

## 0:10–0:25 | Screen Q&A (AI agent live)

**Visual:** Same error. User presses `Ctrl+Shift+Space`. Overlay streams an answer referencing the error on screen.

**On-screen text:** `Ctrl+Shift+Space` — instant screen Q&A

**VO:** "One hotkey. The AI agent reads your screen, decides what to do, and answers — without leaving your app."

**Show:** Agent deciding to answer directly (or using a tool). This demonstrates AI-native operations.

---

## 0:25–0:40 | Hinglish dictation

**Visual:** User clicks into WhatsApp Web. Holds `Ctrl+Shift+D`. Speaks: "kal ka weather check karo". Text appears typed.

**On-screen text:** `Ctrl+Shift+D` — Hinglish dictation, by default

**VO:** "Speak in Hinglish — however you actually talk. No translating into English first."

---

## 0:40–0:55 | Document RAG + Gemini persona

**Visual:** Quick cut to web dashboard. Upload a PDF. Show "ready" status. Cut back to desktop — ask a question about the uploaded doc. Agent cites the document.

**On-screen text:** Upload docs → Gemini builds your persona → AI answers from YOUR materials

**VO:** "Upload your study notes. Gemini summarizes who you are. Now every answer is grounded in your own content."

**This section proves:** Gemini API call in production + real AI workflow.

---

## 0:55–1:10 | Voice + meeting copilot

**Visual:** User on a video call (or simulated). Holds `Ctrl+Shift+V`, asks a question aloud. Overlay answers.

**On-screen text:** `Ctrl+Shift+V` — hears your mic + system audio

**VO:** "On a call, hold one key. It hears you and the call audio together."

---

## 1:10–1:20 | AI runs the business

**Visual:** Quick montage:
- Supabase dashboard showing `usage_ledger` rows
- Google Cloud Run service with request logs
- LiteLLM spend meter on user dashboard

**On-screen text:** AI in production — agent logs, usage tracking, Cloud Run

**VO:** "Every session is logged. Inference runs on Google Cloud. This isn't a demo — it's production."

---

## 1:20–1:35 | Hosted mode (no API keys)

**Visual:** Settings screen showing Hosted provider + license key. Signup flow on website → key auto-configured.

**On-screen text:** Sign up free — no API keys needed

**VO:** "Users sign up, get a key, and start. We handle the models, the billing, and the infrastructure."

---

## 1:35–1:50 | Real business

**Visual:** Stripe/Razorpay dashboard (blur sensitive numbers) OR pricing page + "X paying users"

**On-screen text:** `[PLACEHOLDER: $X revenue | Y users]`

**VO:** "Real users. Real revenue. Built in 90 days with AI running the product."

---

## 1:50–2:00 | CTA

**Visual:** OnCUE tray icon. Website URL. Download button.

**On-screen text:** oncue.ai — Download free for Windows

**VO:** "OnCUE. Skip the alt-tab tax."

---

## Production notes

- **No stock footage** — real screen recordings only
- **No copyrighted music** — voiceover only or royalty-free ambient
- **Turn off screen-share hiding** for recording (Settings → disable WDA_EXCLUDEFROMCAPTURE) so the overlay is visible
- **Show AI making decisions** — don't just show static text appearing; show the agent thinking/tool-calling if possible
- **Mention Gemini + Cloud Run** explicitly in the RAG section (judges check for this)
- **Practice once with a timer** — 2:45 target

## Equipment

- Windows 10/11 PC
- OBS Studio or built-in screen recorder
- Decent microphone for VO (or record VO separately and sync)
- Test all hotkeys before recording — no fumbling on camera
