FROM node:20-alpine
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install
COPY index.js index.html answer.html ./
EXPOSE 3000
CMD [ "npm", "start" ]
