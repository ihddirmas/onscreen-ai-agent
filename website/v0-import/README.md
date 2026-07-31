# v0 import staging (Optimus / shadcn export)

Paste the **entire unzipped v0 project** here, keeping this layout:

```text
website/v0-import/
├── app/
├── components/
├── hooks/
├── lib/
├── public/
├── styles/
├── components.json
├── next.config.mjs
├── package.json
├── postcss.config.mjs
├── tsconfig.json
└── .gitignore
```

**Skip:** `node_modules/`, `.next/`, `pnpm-lock.yaml` (we use npm in `website/`).

**Do not paste** `.env` files — keep `website/.env.local`.

When done, message: **"v0-import is ready — integrate"**.

Integration plan:
- v0 `app/page.tsx`, `components/`, `styles/` → marketing landing
- **Keep** `website/app/api/`, `dashboard/`, `login/` (OnCUE product)
- Merge `package.json` deps + shadcn `components.json`
- CTAs → `/login`, `/dashboard`, `/download`
