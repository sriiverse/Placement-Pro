# ─── Stage 1: Build the React/Vite app ───────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency manifests first (leverages Docker layer caching)
COPY package.json package-lock.json ./
RUN npm ci --silent

# Receive VITE_API_URL as a build-time argument so the correct API URL
# gets baked into the production bundle.
ARG VITE_API_URL=http://localhost:5000/api
ENV VITE_API_URL=${VITE_API_URL}

# Copy the rest of the source and build
COPY . .
RUN npm run build

# ─── Stage 2: Serve with nginx ────────────────────────────────────────────────
FROM nginx:1.25-alpine AS production

# Remove the default nginx welcome page
RUN rm -rf /usr/share/nginx/html/*

# Copy our built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx config that handles React Router (SPA) correctly
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
