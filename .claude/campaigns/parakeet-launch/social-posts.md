# Parakeet.ai — Social Posts

## LinkedIn — Problem angle
Purpose: name the tab-switch tax without thought-leader cadence

> Every time you screenshot an error into ChatGPT and alt-tab back, you pay a small tax. Multiply that across coding, notes, WhatsApp, and lecture slides, and it adds up to a lot of lost flow.
>
> We built Parakeet to remove that tax at the moment it happens: one hotkey, wherever you already are — screenshot or voice, answer streams onto an overlay. No new tab.
>
> Launching soon on Windows.

*Notes: No "unpopular opinion," no engagement-bait line breaks, no hashtag stack.*

## LinkedIn — Proof/insight angle
Purpose: surface the Hinglish-first design decision as the real differentiator

> Most dictation tools assume you think in English. Parakeet's speech recognition defaults to Hinglish output — "kal ka weather check karo" transcribes and works exactly as said, not as a workaround you have to configure.
>
> It's a small design choice with a real effect: you stop translating your own thoughts before you can type them.
>
> Screen Q&A, live call-audio capture, and keyless web search are built the same way — around how people actually use their screen and their voice.

*Notes: Specific, technical claim (default output, not a setting) — supportable from the repo's STT_LANGUAGE default.*

## LinkedIn — Direct invitation angle
Purpose: clear ask, single CTA

> Parakeet is an on-screen AI copilot for Windows — one hotkey for instant screen answers, one for Hinglish dictation into any app, one for listening to a live call.
>
> Dictation and screen Q&A work free with a Groq key (also free, console.groq.com).
>
> If you're a student or early in your career and tired of alt-tabbing for a quick answer, the download link is in the comments. Genuinely want feedback from the first 100 people who try it.

*Notes: One CTA (download link in comments + explicit ask for feedback).*

## X — Standalone posts (6)
Purpose: platform-native, punchy, same voice as LinkedIn but shorter

1. "kal ka weather check karo" — said it into Parakeet, it typed exactly that into WhatsApp. No translating into English first. That's the whole pitch.
2. Ctrl+Shift+Space screenshots your screen and just answers. No new tab, no paste, no "give me a sec let me google that."
3. Built a hotkey that hears your mic AND your Zoom call at the same time and answers without you looking away. Ctrl+Shift+M, hold, ask.
4. Web search that doesn't need an API key. "Search the web for X" just works — DuckDuckGo under the hood, sources cited. Add a Tavily key later if you want.
5. The overlay doesn't show up in your screen share or recording. Not because we're hiding something — because your assistant popping up mid-demo is annoying, not a feature.
6. Pure Python. One process. No Electron. Built it that way on purpose.

*Notes: #5 stays scoped to "demo" framing — do not let future edits drift toward exam/interview implications.*

## X — Thread (10 tweets)
Purpose: walk through the product end-to-end, including honest limits

1. Most days I screenshot something into ChatGPT, alt-tab back, lose my place, alt-tab again to check the answer. Built Parakeet to kill that loop. Thread on what it actually does:
2. First hotkey: Ctrl+Shift+Space. Press it, it screenshots your screen and just answers — the error, the question, whatever's up. Zero typing to start.
3. You can keep asking by typing after — "explain more," "in Hindi" — and it still has the screen context from that first screenshot.
4. Second hotkey: hold Ctrl+Shift+D. Click into any text box — WhatsApp, ChatGPT, a search bar — speak, release. Text lands at your cursor.
5. The part I actually care about: Hinglish is the default output, not a setting you dig for. "Kal ka weather check karo" transcribes and works as typed. Most dictation tools are English-first; this one isn't.
6. Third hotkey: hold Ctrl+Shift+M during any call — Zoom, Meet, a YouTube video. It hears your mic AND the call audio together, live, and answers.
7. Web search works with zero API key setup — DuckDuckGo, cited sources, out of the box. Add a free Tavily key later if you want higher-quality results.
8. The overlay is invisible in screen shares and recordings by default on Windows. It's there for you, not for whoever you're presenting to. Toggle it off any time you want to show it — your own demo recording, for example.
9. What it doesn't do yet, because I'd rather tell you than let you find out: no autonomous clicking through websites, no file delete/move, and local doc search is filename + text match, not semantic yet.
10. Free to try today — dictation and screen Q&A work with a free Groq key (console.groq.com). Download link below. Would love to know which hotkey you reach for first.

*Notes: Tweet 8 mirrors LinkedIn/email framing exactly (demo/presentation use case) for cross-channel consistency.*
