FROM node:20-bookworm-slim

WORKDIR /app

COPY . .

ENV NODE_ENV=production
ENV PORT=4545

EXPOSE 4545

CMD ["node", "server.js"]
