ARG NODE_VERSION=18

### Frontend build
FROM node:${NODE_VERSION} AS frontend_build

COPY frontend/package.json /app/
COPY frontend/package-lock.json /app/

WORKDIR /app
RUN npm install --legacy-peer-deps

COPY frontend/ /app/

### Backend build
FROM node:${NODE_VERSION} AS backend_build

COPY backend/package.json /app/
COPY backend/package-lock.json /app/

WORKDIR /app
RUN npm install

COPY backend/ /app/

### Final image
FROM node:${NODE_VERSION}

COPY --from=frontend_build /app /app/frontend
COPY --from=backend_build /app /app/backend

COPY start.sh /app/

WORKDIR /app
RUN chmod +x start.sh
CMD ["./start.sh"]
