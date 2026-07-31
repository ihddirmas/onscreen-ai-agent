# Evidence Templates — Gemini XPRIZE Submission

> Fill in all sections with real data. Attach screenshots/exports where noted. Judges may request additional documentation.

---

## 1. Revenue

### Total revenue (arms-length third-party customers)

| Metric | Value |
|---|---|
| **Total revenue (USD)** | `[PLACEHOLDER]` |
| **Currency** | USD |
| **Period** | May 1 – August 17, 2026 |
| **Payment processors** | Stripe, Razorpay |

### Revenue by month

| Month | Revenue (USD) | Notes |
|---|---|---|
| May 2026 | `[PLACEHOLDER]` | |
| June 2026 | `[PLACEHOLDER]` | |
| July 2026 | `[PLACEHOLDER]` | |
| August 2026 | `[PLACEHOLDER]` | (partial month through submission) |

### Related-party revenue (report separately)

| Source | Amount (USD) | Relationship | Notes |
|---|---|---|---|
| `[PLACEHOLDER: e.g. friend who paid]` | `[PLACEHOLDER]` | `[friend/family/pre-existing]` | `[explanation]` |
| **Related-party total** | `[PLACEHOLDER]` | | |

### Arms-length revenue (excluding related-party)

**Arms-length total:** `[PLACEHOLDER: total minus related-party]`

### Evidence to attach
- [ ] Stripe dashboard export (Payments → Export)
- [ ] Razorpay settlement report
- [ ] Bank statement showing deposits (redact account numbers)
- [ ] Screenshot of Stripe/Razorpay revenue chart

---

## 2. Expenses

### Total expenses

| Metric | Value |
|---|---|
| **Total expenses (USD)** | `[PLACEHOLDER]` |
| **Period** | May 1 – August 17, 2026 |

### Expense breakdown

| Category | Amount (USD) | Description |
|---|---|---|
| Hosting (Cloud Run) | `[PLACEHOLDER]` | LiteLLM proxy |
| Hosting (Vercel) | `[PLACEHOLDER]` | Website |
| Hosting (Railway) | `[PLACEHOLDER]` | Webapp + Redis |
| Hosting (Supabase) | `[PLACEHOLDER]` | Database, auth, storage |
| AI API usage | `[PLACEHOLDER]` | Groq (free), Gemini, optional Claude/GPT |
| Domain | `[PLACEHOLDER]` | oncue.ai or similar |
| Marketing | `[PLACEHOLDER]` | See §3 |
| Other | `[PLACEHOLDER]` | `[description]` |
| **Total** | `[PLACEHOLDER]` | |

### Evidence to attach
- [ ] Cloud Console billing export
- [ ] Vercel/Railway/Supabase invoices
- [ ] Google AI Studio / Gemini API billing
- [ ] Domain registrar receipt

---

## 3. Marketing and customer acquisition spend

| Metric | Value |
|---|---|
| **Total marketing spend (USD)** | `[PLACEHOLDER: $0 if none]` |

### Breakdown (if any)

| Channel | Spend (USD) | Result |
|---|---|---|
| `[e.g. Reddit ads]` | `[PLACEHOLDER]` | `[X signups]` |
| `[e.g. Twitter/X]` | `[PLACEHOLDER]` | `[Y impressions]` |
| Organic (time only) | $0 | `[Z signups from Reddit posts, etc.]` |

> **Note:** Must be disclosed even if zero.

---

## 4. Simple P&L

| Line item | Amount (USD) |
|---|---|
| **Revenue (arms-length)** | `[PLACEHOLDER]` |
| Related-party revenue | `[PLACEHOLDER]` |
| **Total revenue** | `[PLACEHOLDER]` |
| | |
| Hosting | `[PLACEHOLDER]` |
| AI API costs | `[PLACEHOLDER]` |
| Marketing | `[PLACEHOLDER]` |
| Other expenses | `[PLACEHOLDER]` |
| **Total expenses** | `[PLACEHOLDER]` |
| | |
| **Net (revenue − expenses)** | `[PLACEHOLDER]` |

---

## 5. Users

### User count

| Metric | Value |
|---|---|
| **Total registered users** | `[PLACEHOLDER]` |
| **Active users (used app ≥1 session)** | `[PLACEHOLDER]` |
| **Paying users** | `[PLACEHOLDER]` |

### User breakdown

| Segment | Count | Description |
|---|---|---|
| Students (college/university) | `[PLACEHOLDER]` | `[e.g. CS students in India]` |
| Early-career developers | `[PLACEHOLDER]` | `[e.g. 0-3 YOE]` |
| Other | `[PLACEHOLDER]` | `[description]` |

### Testimonials (with user consent)

**Testimonial 1:**
> "[PLACEHOLDER: quote]"
> — `[First name]`, `[role/location]`

**Testimonial 2:**
> "[PLACEHOLDER: quote]"
> — `[First name]`, `[role/location]`

### Customer contact info (for judge verification)

> Users must be aware their information is being shared.

| Name | Email | Phone | Relationship | Consent |
|---|---|---|---|---|
| `[PLACEHOLDER]` | `[PLACEHOLDER]` | `[PLACEHOLDER]` | Paying customer | Yes |
| `[PLACEHOLDER]` | `[PLACEHOLDER]` | `[PLACEHOLDER]` | Free user | Yes |
| `[PLACEHOLDER]` | `[PLACEHOLDER]` | `[PLACEHOLDER]` | Paying customer | Yes |

---

## 6. Corporate ID (if organization entrant)

| Field | Value |
|---|---|
| Organization name | `[PLACEHOLDER]` |
| Corporate ID / registration number | `[PLACEHOLDER]` |
| Country of incorporation | `[PLACEHOLDER]` |
| Document | `[Attach certificate of incorporation]` |

---

## 7. How to export evidence from OnCUE stack

### Stripe
1. dashboard.stripe.com → Payments → Export → CSV
2. Screenshot: Home → Gross volume chart (May–Aug)

### Razorpay
1. dashboard.razorpay.com → Transactions → Download
2. Screenshot: Analytics → Revenue

### Supabase (users)
```sql
SELECT count(*) FROM profiles;
SELECT count(*) FROM profiles WHERE tier = 'pro';
SELECT count(*) FROM usage_ledger WHERE event_type = 'session_start';
```

### LiteLLM (API spend)
```bash
curl "$LITELLM_URL/spend/logs" -H "Authorization: Bearer $LITELLM_MASTER_KEY"
```

### Google Cloud (hosting costs)
1. console.cloud.google.com → Billing → Reports
2. Filter: Cloud Run, May–Aug 2026

### Gemini API
1. aistudio.google.com → Usage (or Cloud Console → APIs → Generative Language API)
