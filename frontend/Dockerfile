# 多阶段构建
# 第一阶段：构建阶段
FROM node:18-alpine as build-stage

WORKDIR /app

# 安装pnpm
RUN npm install -g pnpm

# 复制package文件
COPY package*.json ./
COPY pnpm-lock.yaml* ./

# 安装依赖
RUN pnpm install --frozen-lockfile

# 复制源代码
COPY . .

# 构建应用
RUN pnpm run build

# 第二阶段：生产阶段
FROM nginx:alpine as production-stage

# 复制构建产物
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]

# 开发环境的Dockerfile
FROM node:18-alpine as dev-stage

WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装所有依赖（包括开发依赖）
RUN npm install

# 复制源代码
COPY . .

# 暴露端口
EXPOSE 3000

# 启动开发服务器
CMD ["npm", "run", "dev"]