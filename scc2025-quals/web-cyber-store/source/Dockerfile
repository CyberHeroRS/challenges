FROM surnet/alpine-wkhtmltopdf:3.21.2-0.12.6-small as wkhtmltopdf
FROM node:20-alpine

RUN apk add --no-cache \
  libstdc++ \
  libx11 \
  libxrender \
  libxext \
  libssl3 \
  ca-certificates \
  fontconfig \
  freetype \
  ttf-droid \
  ttf-freefont \
  ttf-liberation

COPY --from=wkhtmltopdf /bin/wkhtmltopdf /bin/

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install

COPY data/ ./data/
COPY src/ ./src/
COPY views ./views/

COPY entrypoint.sh /

EXPOSE 3000

CMD ["/entrypoint.sh"]
