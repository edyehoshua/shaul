FROM node:24-slim AS builder
WORKDIR /usr/src/app
COPY package.json .
COPY package-lock.json* .
COPY .npmrc .
RUN npm ci

FROM node:24-slim
WORKDIR /usr/src/app
RUN apt-get update \
  && apt-get install -y --no-install-recommends python3 \
  && rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/src/app/ /usr/src/app/
COPY . .
CMD ["npm", "start"]
