# ==============================================================================
# Stage 1 — Build the React app
# ==============================================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first (layer cache-friendly)
COPY package.json package-lock.json ./
RUN npm ci --silent

# Copy source and build
COPY . .
RUN npm run build


# ==============================================================================
# Stage 2 — Serve with nginx
# ==============================================================================
FROM nginx:1.27-alpine

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx template (uses envsubst for runtime env vars)
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template

# Copy built React app
COPY --from=builder /app/dist /usr/share/nginx/html

# nginx runs as root by default; expose port
EXPOSE 80

# Use envsubst to render the template at container start (built-in nginx image feature)
# ENV vars BACKEND_SCHEME and BACKEND_HOST are injected by docker-compose
CMD ["nginx", "-g", "daemon off;"]
