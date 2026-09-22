FROM node:20-slim
WORKDIR /app/server

# openssl: o Prisma precisa para detectar o engine correto (evita erro em alpine)
RUN apt-get update -y && apt-get install -y openssl && rm -rf /var/lib/apt/lists/*

COPY server/package*.json ./
RUN npm install

COPY server/prisma ./prisma
RUN npx prisma generate

COPY server/src ./src

# Frontend (arquivo único, raiz do repo). Copiado pra dentro da imagem de
# propósito — NÃO é bind mount: assim o front nunca fica numa versão à
# frente do banco/API, os dois só mudam juntos, no mesmo build.
COPY index.html /app/index.html

EXPOSE 3000
# aplica as migrations, roda o seed e sobe a API
CMD ["sh", "-c", "npx prisma migrate deploy && node prisma/seed.js && node src/index.js"]
