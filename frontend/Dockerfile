FROM node:22-alpine

WORKDIR /app

ENV NG_CLI_ANALYTICS=false \
    npm_config_cache=/tmp/.npm \
    npm_config_update_notifier=false

RUN mkdir -p /app/node_modules /app/.angular && \
    chown -R 1000:1000 /app

USER 1000:1000

COPY --chown=1000:1000 package*.json ./
RUN npm ci --no-audit --no-fund

EXPOSE 4200

CMD ["sh", "-c", "npm install --no-audit --no-fund && npx ng serve --host 0.0.0.0 --port 4200 --poll 2000"]