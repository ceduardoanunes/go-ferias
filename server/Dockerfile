FROM node:20-slim
WORKDIR /app

# openssl: o Prisma precisa para detectar o engine correto (evita erro em alpine)
RUN apt-get update -y && apt-get install -y openssl && rm -rf /var/lib/apt/lists/*

COPY package*.json ./
RUN npm install

COPY prisma ./prisma
RUN npx prisma generate

COPY src ./src

EXPOSE 3000
# cria/atualiza as tabelas a partir do schema, roda o seed e sobe a API
CMD ["sh", "-c", "npx prisma db push --skip-generate && node prisma/seed.js && node src/index.js"]
