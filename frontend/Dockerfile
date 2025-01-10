FROM node:alpine

WORKDIR /app

COPY package*.json ./

# Установка зависимостей
RUN npm ci

# Логирование результата
RUN echo "Dependencies installed:"
RUN ls -l node_modules

COPY . .

RUN npm run build
CMD cp -r build result_build