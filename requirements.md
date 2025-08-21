# AI Model Tester（需求文档）

## 1. 目标

做一个最小但顺手的“大模型测试台”：

* 前端：Vue 3（Vite、Pinia、Vue Router、Element Plus）
* 后端：FastAPI（Uvicorn）、SQLAlchemy（不使用 Alembic）
* 数据库：MySQL（docker compose，utf8mb4）
* 流：SSE（Server-Sent Events）流式回复
* 认证：**简易登录**（用户名 + 密码哈希），**Cookie Session**（无 JWT）
* 模型选择：`qwen3` / `llama3` / `gemma` / `deepseek` / `kimi`
* 每条回答可**评价**（好/差 + 文字描述）
* `.env`：**BASE\_URL** + **API\_KEY**（通过网关按 `model` 参数转发）

---

## 2. 环境变量（.env）

```
BASE_URL=https://your-gateway.example.com
API_KEY=key

# Backend
APP_HOST=0.0.0.0
APP_PORT=8000

# DB
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ai_chat
DB_USER=chatuser
DB_PASSWORD=chatpass

# Session
SESSION_SECRET=change_me_32_chars
SESSION_EXPIRE_DAYS=7
```

> 说明
>
> * **BASE\_URL**/**API\_KEY**：统一中转地址与 Key；实际模型通过传参 `model` 选择。
> * 只要网关支持不同 `model` 值即可调用不同大模型。

---

## 3. Docker Compose（MySQL）

`docker-compose.yml`

```yaml
version: "3.9"
services:
  db:
    image: mysql:8.0
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: lianyi656
      MYSQL_DATABASE: ai_chat
      MYSQL_USER: chatuser
      MYSQL_PASSWORD: chatpass
    ports:
      - "3306:3306"
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    volumes:
      - ./mysql_data:/var/lib/mysql
```

---

## 4. 数据库结构（初始化 SQL）

> 不用 Alembic，项目启动时若表不存在则创建；或手动执行以下 SQL。

```sql
CREATE DATABASE IF NOT EXISTS ai_chat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ai_chat;

CREATE TABLE IF NOT EXISTS users (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(64) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS conversations (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  title VARCHAR(255) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS messages (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  conv_id BIGINT NOT NULL,
  role ENUM('user','assistant','system') NOT NULL,
  content LONGTEXT NOT NULL,
  model VARCHAR(64) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  rating TINYINT NULL,                 -- 1=好评, 0=差评, NULL=未评
  rating_comment VARCHAR(1000) NULL,   -- 评价文字
  FOREIGN KEY (conv_id) REFERENCES conversations(id) ON DELETE CASCADE,
  INDEX idx_conv_id (conv_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS sessions (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  session_id CHAR(36) NOT NULL UNIQUE,   -- UUID
  user_id BIGINT NOT NULL,
  expires_at DATETIME NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;
```

---

## 5. 后端设计（FastAPI）

### 5.1 依赖

```
fastapi
uvicorn
python-dotenv
pydantic
sqlalchemy
pymysql
bcrypt
itsdangerous        # 可选，用于额外签名 session 值
```

### 5.2 会话与认证

* 登录：校验用户名/密码（bcrypt），创建 `sessions` 记录（UUID + 过期时间），写入 **HttpOnly Cookie**（如：`sid`）。
* 中间件：读取 `sid` → 校验数据库有效且未过期 → 注入 `current_user`。
* 登出：删除 `sessions` 记录 + 清空 Cookie。

### 5.3 模型调用（统一 BASE\_URL / API\_KEY）

* 请求体：`{ model, messages, stream=true }`
* 转发到 `.env` 的 `BASE_URL`，Header `Authorization: Bearer ${API_KEY}`
* **SSE**：逐块转发给前端
* 请求超时、错误码、速率限制（可选简单 sleep / 节流）

### 5.4 API 设计

```
POST   /api/auth/login           # 登录（返回 Set-Cookie: sid=...）
POST   /api/auth/logout          # 登出（清 Cookie）
GET    /api/auth/me              # 当前用户

GET    /api/models               # 返回可选模型列表

POST   /api/conversations        # 新建会话（title 可用首条用户问题前 20 字）
GET    /api/conversations        # 列出我的会话（最近 50）
GET    /api/conversations/{id}   # 拉取会话及消息
DELETE /api/conversations/{id}   # 删除会话

POST   /api/chat/stream          # SSE 流式聊天（body: conv_id, model, prompt, system_prompt?）
POST   /api/messages/{id}/rate   # 对消息评价（body: rating(0/1), comment?）
```

### 5.5 SSE 返回格式（示例）

服务端以 `text/event-stream` 逐条发送：

```
event: chunk
data: {"delta":"你好", "message_id":123}

event: chunk
data: {"delta":"，请问…", "message_id":123}

event: done
data: {"message_id":123, "full": "你好，请问…"}
```

后端在 `done` 事件时把最终完整回答写入 `messages` 表（role=assistant），并持久化 `model`。

---

## 6. 前端设计（Vue 3）

### 6.1 页面

* `/login` 登录页（用户名 + 密码；成功后跳 `/chat`）
* `/chat`

  * 左侧：会话列表（新建会话按钮）
  * 右侧：聊天区（模型下拉、系统提示词输入框（默认值可编辑）、消息区（流式）、输入框、发送）
  * 每条 **assistant** 消息有“评价”按钮 → 弹出 `对话框` 输入评价（好/差 + 文本）

### 6.2 状态（Pinia）

* `authStore`: user、isAuthed、me()
* `chatStore`: conversations、currentConv、messages、currentModel、systemPrompt
* SSE 连接状态（isStreaming）

### 6.3 调用流程

1. 进入 `/chat` → 拉取会话列表 → 若无会话则「新建会话」
2. 选择模型 → 输入问题 → 调用 `/api/chat/stream`（SSE）
3. 流式展示 → 结束后把新消息附加到当前会话
4. 用户点击“评价”→ POST `/api/messages/{id}/rate`

---

## 7. 默认可选模型

固定返回（后端硬编码或从配置加载）：

```json
["qwen3", "llama3", "gemma", "deepseek", "kimi"]
```

---

## 8. 默认系统提示词（可编辑）

> 初始在前端提供一个默认值，发送时一起传给后端；后端将其作为第一条 `system` 消息注入请求。

```
你是一位医学学习辅助助手。你的目标是帮助医学生提升问诊能力：
- 先理解患者主诉和现病史，提示遗漏的关键信息
- 指出提问策略的问题并给出更优方案
- 遵循循证医学与常见指南，表达清晰、可执行
- 如不确定，明确说出不确定点并给出可能方向
```

---

## 9. 安全与简化

* 登录只做**单次登录 + Cookie Session**（无注册/刷新）。
* 密码必须 **bcrypt** 存储。
* Cookie：`HttpOnly; Secure(生产); SameSite=Lax`。
* 简单防刷：对 `/api/chat/stream` 做最小限度节流（例如每用户每 2s 一次）。
* 禁止跨用户访问：所有查询按 `user_id` 限制。

---

## 10. 启动步骤（本地）

1. 启动 MySQL

```
docker compose up -d
```

2. 创建 `.env`（见上）
3. 初始化数据库（启动时自动建表；或手动执行 SQL）
4. 启动后端

```
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

5. 启动前端

```
pnpm install
pnpm dev
```

---

## 11. 接口示例

### 登录

`POST /api/auth/login`

```json
{ "username": "demo", "password": "your_password" }
```

* 成功：Set-Cookie: `sid=...`；body：`{ "id": 1, "username": "demo" }`

### 获取模型列表

`GET /api/models` → `["qwen3","llama3","gemma","deepseek","kimi"]`

### 新建会话

`POST /api/conversations`

```json
{ "title": "心内科问诊练习" }
```

### 流式聊天

`POST /api/chat/stream`（SSE）

```json
{
  "conv_id": 123,
  "model": "qwen3",
  "system_prompt": "（可选，前端传）",
  "prompt": "患者男，45岁，胸痛2小时..."
}
```

### 消息评价

`POST /api/messages/456/rate`

```json
{ "rating": 1, "comment": "反馈很专业，建议清晰" }
```

---

## 12. 目录结构建议

```
project/
  frontend/
    src/
      stores/
      pages/
        Login.vue
        Chat.vue
      components/
        MessageItem.vue
        RateDialog.vue
      utils/sse.ts
    vite.config.ts
  backend/
    app/
      main.py
      deps.py        # 会话校验中间件/依赖
      db.py          # SQLAlchemy engine/session + init tables
      models.py      # SQLAlchemy models
      schemas.py     # Pydantic
      routers/
        auth.py
        conversations.py
        chat.py
        messages.py
      services/
        chat_gateway.py  # BASE_URL + API_KEY 调用封装（SSE）
        session.py       # 创建/校验/清理 session
        crypto.py        # bcrypt 封装
    .env
  docker-compose.yml
  README.md
```

---

## 13. 备注

* 没有 JWT / Alembic；**小项目就用 Cookie 会话 + 启动时自动建表**最轻。
* 未来若要多人多权限，再考虑 JWT 或 OAuth。
* 如果网关返回 OpenAI 风格流（`data: {...}` + `data: [DONE]`），后端需做一次轻转换为统一 SSE 事件。
