FROM node:latest

WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev

COPY . .

ENV NODE_ENV=production
ENV PORT=1337

EXPOSE 1337

CMD ["npm", "start"]
