# ---- Dev image (used by docker-compose; command overridden to `npm run dev`) ----
# For production, use Dockerfile.prod (multi-stage standalone build).
FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
