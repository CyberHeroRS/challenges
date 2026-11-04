FROM node:20-alpine

WORKDIR /app

RUN apk add --no-cache python3 make g++

COPY package.json ./
RUN npm install --omit=dev

COPY . .

ENV NODE_ENV=production
ENV PORT=3000
ENV DB_PATH=/app/data/rooms.sqlite

RUN mkdir -p /app/data

EXPOSE 3000

CMD ["node", "server.js"]
