FROM node:20-bookworm-slim

WORKDIR /app

ENV NODE_ENV=development
ENV PORT=3000
ENV PUPPETEER_SKIP_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
# The bot needs to know its own reachable origin to log itself in as
# admin before visiting a reported URL (see src/bot.ts). Since the bot
# and the app run in the same container, localhost always resolves
# correctly here -- set directly in the image rather than via
# challenge.yaml's service-level `env:` to work around a ctf-operator
# validation bug (DuplicateContainerEnv is incorrectly raised whenever
# a service defines 2+ flags together with any env: entries, since the
# uniqueness check re-inserts every env name once per flag instead of
# once overall).
ENV BOT_ORIGIN=http://localhost

RUN apt-get update \
    && apt-get install -y --no-install-recommends chromium \
    && rm -rf /var/lib/apt/lists/*

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
