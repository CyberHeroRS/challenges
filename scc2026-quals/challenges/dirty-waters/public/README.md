# ThreadBoard

ThreadBoard is a small forum-style web CTF challenge.

## Core idea

- Backend: TypeScript + Express
- Frontend: React
- Main vulnerability: server-side prototype pollution in config import
- Secondary bug surface: self-XSS in profile name preview (`innerHTML`)

## Intended prototype pollution chain

1. Abuse login/logout CSRF.
2. Sign in as any normal user.
3. Intercept a normal theme sync request to `/api/settings/import` and tamper nested config keys.
4. Access `/api/mod/logs/export` and retrieve the archive value (flag) by satisfying inherited moderator checks.

## Vulnerable areas

- Prototype pollution entry point:
  - `apps/api/src/store.ts` (`applyThemePatch`)
  - `apps/api/src/server.ts` (`POST /api/settings/import`)
- Flag gate:
  - `apps/api/src/store.ts` (`readModeratorArchive`)
  - `apps/api/src/server.ts` (`GET /api/mod/logs/export`)
- Self-XSS preview sink:
  - `apps/web/public/profile-preview.js`

The preview helper writes attacker-controlled display name content into `innerHTML`.

## Features

- login and register
- logout via `GET`
- forum post feed
- settings page with editable profile and normal-looking theme sync controls
- report page that queues a URL for moderator review later

## Seeded users

- `admin` / value from `ADMIN_PASSWORD`
- `guest` / `guestpass123`

## Local dev

### API

```bash
cd apps/api
npm install
npm run dev
```

### Web

```bash
cd apps/web
npm install
npm run dev
```

## Docker

```bash
docker compose up --build
```

The site is served on `http://localhost:3000`.
