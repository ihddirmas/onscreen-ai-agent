# Product Evidence — AI Running in Production

Judges want proof that AI is live, making decisions, and operating continuously — not a slide deck or localhost demo. This guide shows how to collect evidence from the OnCUE stack.

---

## 1. Agent execution logs (desktop)

Every desktop session reports to the `usage_ledger` table in Supabase.

### Export session data
```sql
-- Total sessions
SELECT count(*) AS total_sessions
FROM usage_ledger
WHERE event_type = 'session_start';

-- Sessions by day (last 30 days)
SELECT date_trunc('day', created_at) AS day, count(*) AS sessions
FROM usage_ledger
WHERE event_type = 'session_start'
GROUP BY 1
ORDER BY 1 DESC;

-- Inference events with model used
SELECT model_used, count(*) AS calls, sum(tokens_in) AS tokens_in, sum(tokens_out) AS tokens_out
FROM usage_ledger
WHERE event_type = 'inference'
GROUP BY 1
ORDER BY 2 DESC;

-- Recent sessions (redact user_id for submission)
SELECT created_at, event_type, model_used, tokens_in, tokens_out, cost_usd, tier
FROM usage_ledger
ORDER BY created_at DESC
LIMIT 50;
```

### Screenshot to include
- Supabase Table Editor → `usage_ledger` with recent rows visible
- Dashboard credit meter showing non-zero usage

---

## 2. LiteLLM proxy logs (inference routing)

The LiteLLM proxy on Cloud Run logs every API request.

### Via API
```bash
# Total spend across all keys
curl "$LITELLM_URL/global/spend/report" \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY"

# Per-key spend
curl "$LITELLM_URL/key/info?key=USER_KEY" \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY"
```

### Via Google Cloud Console
1. Cloud Run → `oncue-litellm` → Logs
2. Filter: `oncue-persona` or `oncue-default` or `oncue-gemini`
3. Screenshot showing request volume over multiple days

---

## 3. Gemini API usage

The `oncue-persona` model calls Gemini 2.5 Flash on every document upload.

### Verify a Gemini call happened
1. Upload a test PDF on the dashboard
2. Check Supabase `profiles.persona` — should update with a summary
3. Check LiteLLM logs for `oncue-persona` request
4. Check Google AI Studio → Usage for `gemini-2.5-flash` request count

### Screenshot to include
- Google AI Studio usage dashboard showing Gemini requests during hackathon period
- OR Cloud Console → APIs & Services → Generative Language API → Metrics

---

## 4. Document RAG pipeline

Proves AI processes user documents autonomously.

### Verify
```sql
-- Documents uploaded
SELECT count(*) AS docs, count(*) FILTER (WHERE status = 'ready') AS ready
FROM documents;

-- Chunks embedded
SELECT count(*) AS chunks FROM doc_chunks;
```

### Screenshot
- Dashboard showing uploaded documents with "ready" status
- Supabase `doc_chunks` table with embedding vectors

---

## 5. Payment events (business operations)

```sql
SELECT event_type, provider, count(*) AS events
FROM payment_events
GROUP BY 1, 2;

SELECT * FROM payment_events ORDER BY created_at DESC LIMIT 10;
```

### Screenshot
- Stripe dashboard with payment count
- `payment_events` table in Supabase

---

## 6. Cloud Run uptime (continuous production)

### Screenshot
- Cloud Run → `oncue-litellm` → Metrics → Request count over 7+ days
- Shows the service is running continuously, not just deployed for the video

---

## 7. Example agent session (redacted)

Include 1–2 redacted examples showing AI making decisions:

```
Session: 2026-07-28 14:32 UTC
User tier: pro
Model: oncue-default

User action: Ctrl+Shift+Space on VS Code with Python ImportError
Agent decision: Answer directly from screenshot (no tool needed)
Response: "You're missing the `requests` module. Run `pip install requests` in your terminal."
Tokens: 1,240 in / 89 out
Cost: $0.00 (Groq free tier)
```

```
Session: 2026-07-29 09:15 UTC
User tier: free
Model: oncue-default

User action: Voice command "mere notes se yeh topic explain karo"
Agent decision: Called search_my_documents("topic name")
RAG results: 3 chunks from uploaded lecture-notes.pdf
Response: [grounded answer citing user's own notes]
```

---

## 8. Evidence package checklist

Attach these to your Devpost submission or keep ready for judge requests:

- [ ] `usage_ledger` export (CSV or screenshot)
- [ ] LiteLLM spend report
- [ ] Gemini API usage screenshot
- [ ] Cloud Run request metrics (7-day chart)
- [ ] 1–2 redacted agent session examples
- [ ] Document upload → persona update screenshot
- [ ] Payment events table or Stripe export
