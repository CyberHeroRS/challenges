FROM node:20-bookworm AS web-build
WORKDIR /app/web
COPY apps/web/package*.json ./
RUN npm install
COPY apps/web/ ./
RUN npm run build

FROM node:20-bookworm AS api-build
WORKDIR /app/api
COPY apps/api/package*.json ./
RUN npm install
COPY apps/api/ ./
RUN npm run build

FROM node:20-bookworm-slim
WORKDIR /app
ENV NODE_ENV=production
COPY --from=api-build /app/api/package*.json ./api/
COPY --from=api-build /app/api/node_modules ./api/node_modules
COPY --from=api-build /app/api/dist ./api/dist
COPY --from=web-build /app/web/dist ./web-dist
WORKDIR /app/api
CMD ["node", "dist/server.js"]
