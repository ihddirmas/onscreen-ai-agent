# v0-import — marketing design system

Full v0 export used as the **visual source** for the OnCUE website landing page.

## Layout

```
v0-import/
├── app/              # Reference Next app (not served directly)
├── components/
│   ├── landing/      # Page sections — imported by website/app/page.tsx
│   └── ui/           # shadcn-style primitives (Button, etc.)
├── hooks/
├── lib/              # cn() and shared utils
├── public/
└── styles/
```

## How the main site uses this

- **`website/app/page.tsx`** imports landing sections via `@/components/landing/*`
- **`website/tsconfig.json`** resolves `@/*` → `v0-import/*` first, then `website/*`
- **`website/app/globals.css`** includes Tailwind v4 tokens aligned with `v0-import/app/globals.css`

Edit landing copy and layout in `components/landing/`. Dashboard, login, and API routes stay under `website/app/`.

## Local preview

```bash
cd website && npm install && npm run dev
```
