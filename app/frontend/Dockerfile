# ──────────────────────────────────────────────────────
#  Stage 1 – Build the production bundle
# ──────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# In production, axios baseURL stays relative ("/api/...")
# so nginx can reverse-proxy to the backend container.
ENV VITE_BACKEND_URL=""
RUN npm run build


# ──────────────────────────────────────────────────────
#  Stage 2 – Serve with nginx + reverse proxy /api
# ──────────────────────────────────────────────────────
FROM nginx:1.27-alpine

# Remove default config and add our own.
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
