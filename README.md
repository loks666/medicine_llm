# 医疗大模型测试平台

一个基于 FastAPI + Vue3 的医疗大模型对话测试平台，支持多模型切换、会话管理、消息评价等功能。

## 🚀 功能特性

- **多模型支持**: 支持 OpenAI GPT 系列及兼容 API 的其他大模型
- **实时对话**: 基于 SSE 的流式对话体验
- **会话管理**: 创建、切换、删除对话会话
- **消息评价**: 对 AI 回复进行好评/差评
- **用户认证**: 基于 Session 的用户登录系统
- **响应式设计**: 支持桌面端和移动端
- **Docker 部署**: 一键容器化部署

## 🛠️ 技术栈

### 后端
- **FastAPI**: 现代化的 Python Web 框架
- **MySQL**: 主数据库
- **Redis**: 缓存和会话存储
- **SQLAlchemy**: ORM 框架
- **Pydantic**: 数据验证
- **Uvicorn**: ASGI 服务器

### 前端
- **Vue 3**: 渐进式 JavaScript 框架
- **TypeScript**: 类型安全的 JavaScript
- **Element Plus**: Vue 3 UI 组件库
- **Pinia**: Vue 状态管理
- **Vue Router**: 路由管理
- **Vite**: 前端构建工具

### 部署
- **Docker**: 容器化部署
- **Docker Compose**: 多容器编排
- **Nginx**: 反向代理和静态文件服务

## 📦 快速开始

### 环境要求

- Docker 和 Docker Compose
- Node.js 18+ (本地开发)
- Python 3.11+ (本地开发)

### 使用 Docker Compose 部署（推荐）

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd medicine_llm
   ```

2. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，设置你的 OpenAI API Key 等配置
   ```

3. **启动服务**
   ```bash
   # Windows PowerShell (推荐)
   .\start.ps1
   
   # 或者直接使用 docker-compose
   docker-compose up -d
   ```

4. **访问应用**
   - 前端: http://localhost:3001
   - 后端 API: http://localhost:8000
   - API 文档: http://localhost:8000/docs

5. **停止服务**
   ```bash
   # Windows PowerShell
   .\stop.ps1
   
   # 或者直接使用 docker-compose
   docker-compose down
   ```

### 本地开发

#### 后端开发

1. **进入后端目录**
   ```bash
   cd backend
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```bash
   cp ../.env.example .env
   # 编辑 .env 文件
   ```

5. **启动数据库**
   ```bash
   docker-compose up -d mysql redis
   ```

6. **运行后端**
   ```bash
   uvicorn app.main:app --reload
   ```

#### 前端开发

1. **进入前端目录**
   ```bash
   cd frontend
   ```

2. **安装依赖**
   ```bash
   npm install
   ```

3. **启动开发服务器**
   ```bash
   npm run dev
   ```

## 📝 API 文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的 API 文档。

### 主要 API 端点

- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/me` - 获取当前用户信息
- `GET /api/conversations` - 获取会话列表
- `POST /api/conversations` - 创建新会话
- `GET /api/conversations/{id}` - 获取会话详情
- `DELETE /api/conversations/{id}` - 删除会话
- `POST /api/chat/stream` - 流式聊天
- `GET /api/chat/models` - 获取可用模型
- `POST /api/messages/{id}/rate` - 评价消息

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | MySQL 数据库连接 | - |
| `REDIS_URL` | Redis 连接 | - |
| `SECRET_KEY` | 应用密钥 | - |
| `OPENAI_API_KEY` | OpenAI API 密钥 | - |
| `OPENAI_BASE_URL` | OpenAI API 基础 URL | https://api.openai.com/v1 |
| `DEBUG` | 调试模式 | false |
| `SESSION_EXPIRE_HOURS` | 会话过期时间（小时） | 24 |

### 支持的模型

默认支持以下 OpenAI 模型：
- gpt-4o
- gpt-4o-mini
- gpt-4-turbo
- gpt-3.5-turbo

也支持其他兼容 OpenAI API 的服务，如：
- DeepSeek
- 阿里云百炼
- 其他兼容服务

## 🗂️ 项目结构

```
medical_llm/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── models/         # 数据模型
│   │   ├── routers/        # API 路由
│   │   ├── services/       # 业务逻辑
│   │   ├── database.py     # 数据库配置
│   │   └── main.py         # 应用入口
│   ├── requirements.txt    # Python 依赖
│   └── Dockerfile         # 后端 Docker 配置
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # Vue 组件
│   │   ├── pages/         # 页面组件
│   │   ├── stores/        # Pinia 状态管理
│   │   ├── router/        # 路由配置
│   │   ├── types/         # TypeScript 类型
│   │   └── utils/         # 工具函数
│   ├── package.json       # Node.js 依赖
│   └── Dockerfile        # 前端 Docker 配置
├── docker-compose.yml     # Docker Compose 配置
├── .env.example          # 环境变量模板
└── README.md            # 项目说明
```

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 常见问题

### Q: 如何更换 AI 模型？
A: 在 `.env` 文件中修改 `OPENAI_BASE_URL` 和 `OPENAI_API_KEY`，支持任何兼容 OpenAI API 的服务。

### Q: 如何自定义可用模型列表？
A: 修改 `backend/app/routers/chat.py` 中的 `get_models` 函数。

### Q: 数据库迁移怎么处理？
A: 项目启动时会自动创建数据库表，无需手动迁移。

### Q: 如何配置 HTTPS？
A: 在生产环境中，建议使用 Nginx 或云服务商的负载均衡器配置 SSL 证书。

---

⭐ 如果这个项目对你有帮助，请给个 Star！
