# 医疗大模型测试平台

一个基于 FastAPI + Vue3 的医疗大模型对话测试平台，支持多模型切换、会话管理、消息评价等功能。

## 🚀 功能特性

- **多模型支持**：支持 OpenAI GPT 系列及兼容 API 的其他大模型
- **实时对话**：基于 SSE 的流式对话体验
- **会话管理**：创建、切换、删除对话会话
- **消息评价**：对 AI 回复进行好评/差评
- **用户认证**：基于 Session 的用户登录系统
- **响应式设计**：支持桌面端和移动端

## 🛠️ 技术栈

### 后端
- **FastAPI**：现代化的 Python Web 框架
- **SQLAlchemy**：ORM 框架（默认连接本地 MySQL）
- **Pydantic**：数据验证
- **Uvicorn**：ASGI 服务端
- **Redis**：限流与缓存支持

### 前端
- **Vue 3**：渐进式 JavaScript 框架
- **TypeScript**：类型安全的 JavaScript
- **Element Plus**：Vue 3 UI 组件库
- **Pinia**：Vue 状态管理
- **Vite**：前端构建工具

### 部署
- **uv**：Python 依赖与环境管理
- **Docker / Docker Compose（可选）**：一键容器化部署

## 📦 快速开始

### 环境要求

- [uv](https://github.com/astral-sh/uv) 0.8+
- Python 3.13（由 uv 自动管理）
- Node.js 18+（前端开发）
- Docker（本地 MySQL/Redis 由 compose 启动）

> 提示：首次运行会自动在项目根目录创建 `.venv` 虚拟环境，并写入 `.python-version` 指定解释器版本。

### 启动后端（uv）

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd medicine_llm
   ```

2. **配置环境变量**
   ```bash
   cp .env.example .env
   # 按需修改 .env
   ```

3. **启动本地数据库/缓存（MySQL + Redis）**
   ```powershell
   cd C:\Programs\Project\docker-compose\database
   docker compose up -d mysql redis
   ```
   > 说明：上述目录包含统一维护的数据库 docker-compose 配置。若在 Linux/Mac，可进入该目录后执行 `docker compose up -d mysql redis`。

4. **启动后端服务（推荐使用脚本）**
   ```powershell
   .\start.ps1          # 初始化虚拟环境并同步依赖
   .\start.ps1 -InitDb  # 首次运行可额外初始化数据库表
   ```

   或者手动执行：
   ```bash
   uv venv --python 3.13
   uv sync
   uv run python backend/init_db.py  # 可选：初始化数据表
   uv run -- uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **停止后端服务**
   ```powershell
   .\stop.ps1
   ```
   或在运行窗口使用 `Ctrl+C` 结束服务。

6. **访问接口**
   - 后端 API: http://localhost:8000
   - API 文档: http://localhost:8000/docs

### 启动前端

1. **安装依赖**
   ```bash
   cd frontend
   npm install
   ```

2. **启动开发服务器**
   ```bash
   npm run dev
   ```

   默认访问地址：`http://localhost:3000`

### 使用 Docker（可选）

仍可使用仓库自带的 `docker-compose.yml` 在容器中部署：

```bash
docker compose up -d
docker compose down
```

## 📝 API 文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整 API 文档。

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
| `DATABASE_URL` | 数据库连接串，默认指向本地 docker-compose MySQL | `mysql+pymysql://fly_user:jax666@localhost:33061/flyai` |
| `DB_HOST` / `DB_PORT` / `DB_NAME` / `DB_USER` / `DB_PASSWORD` | MySQL 连接信息（未设置 `DATABASE_URL` 时自动组合） | localhost / 33061 / flyai / fly_user / jax666 |
| `REDIS_URL` | Redis 连接串，默认指向本地 docker-compose Redis | `redis://:jax666@localhost:63791/0` |
| `REDIS_HOST` / `REDIS_PORT` / `REDIS_PASSWORD` / `REDIS_DB` | Redis 参数（未显式提供 `REDIS_URL` 时使用） | localhost / 63791 / jax666 / 0 |
| `SECRET_KEY` | 应用密钥 | - |
| `OPENAI_API_KEY` | OpenAI API 密钥 | - |
| `OPENAI_BASE_URL` | OpenAI API 基础 URL | https://api.openai.com/v1 |
| `SESSION_EXPIRE_DAYS` | 会话过期时间（天） | 7 |

### 支持的模型

默认支持以下 OpenAI 模型：
- gpt-4o
- gpt-4o-mini
- gpt-4-turbo
- gpt-3.5-turbo

也支持其他兼容 OpenAI API 的服务，如：DeepSeek、阿里云百炼等。

## 🗂️ 项目结构

```
medicine_llm/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── models/         # 数据模型
│   │   ├── routers/        # API 路由
│   │   ├── services/       # 业务逻辑
│   │   ├── deps.py         # 依赖注入
│   │   ├── db.py           # 数据库配置
│   │   └── cache.py        # Redis 客户端
│   ├── main.py             # 应用入口
│   ├── init_db.py          # 初始化数据库脚本
│   └── debug_login.py      # 调试工具
├── frontend/               # 前端代码
│   └── ...
├── pyproject.toml          # Python 项目配置（uv）
├── uv.lock                 # 依赖锁定文件
├── .python-version         # 指定 Python 版本（3.13）
├── start.ps1               # 本地启动脚本（uv）
├── stop.ps1                # 本地停止脚本
└── README.md               # 项目说明
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
A: 项目启动时会自动创建数据库表；如需手动执行可运行 `uv run python backend/init_db.py`。

---

如果这个项目对你有帮助，请点个 ⭐️ 支持一下！
