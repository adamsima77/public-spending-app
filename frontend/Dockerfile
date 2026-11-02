FROM node:22-alpine AS base
WORKDIR /app

FROM base AS dev

RUN mkdir -p /app/node_modules /app/.angular \
    && chown -R node:node /app
EXPOSE 4200
CMD ["sh", "-c", "npm install && npx ng serve --host 0.0.0.0 --port 4200"]
