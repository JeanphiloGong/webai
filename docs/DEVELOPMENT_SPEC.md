# 开发规范与实施流程（团队版）

本文档用于统一本项目团队的技术选型、目录结构和开发流程，所有成员在实现 MVP 及后续迭代时应遵循本规范。

本规范围绕「AI 平台 + 链下游戏币 + 可扩展 Web3 能力」的目标，结合已有设计文档：

- 架构：`docs/ARCHITECTURE.md`
- 功能：`docs/PLATFORM_DESIGN.md`
- 游戏币：`docs/TOKEN_DESIGN.md`
- 数据库：`docs/DB_SCHEMA.md`
- 接口：`docs/API_DESIGN.md`
- 前端：`docs/FRONTEND_SPEC.md`
- 安全：`docs/SECURITY_RISK_CONTROL.md`
- 路线图：`docs/ROADMAP.md`

---

## 1. 统一技术栈规范

### 1.1 前端

- 框架：**Svelte（推荐使用 SvelteKit）**
- 构建工具：**Vite（SvelteKit 默认集成）**
- 语言：**TypeScript**
- 路由：SvelteKit 路由（基于文件系统）
- 网络请求：`fetch` 或 `axios` 封装
- 样式：**TailwindCSS**

> 说明：当前前端统一使用 Svelte 技术栈。如果未来需要更换为 Vue / React 等，可保持后端 API 协议不变，前端自由重写。

### 1.2 平台后端（本仓库）

- 语言：**Python 3.10+**
- Web 框架：**FastAPI**
- ORM：**SQLAlchemy**
- 数据库迁移：**Alembic**
- HTTP 客户端：**httpx**（用于调用外部 AI 服务）
- 密码哈希：**passlib[bcrypt]**
- 配置管理：**python-dotenv** 或等价方案

### 1.3 数据库

- 生产环境：**PostgreSQL**
  - 所有正式环境必须使用 Postgres
  - 表结构设计以 `docs/DB_SCHEMA.md` 为准
- 本地开发：
  - 推荐使用本地 Postgres，与生产保持一致
  - 仅在个人实验时可使用 SQLite，但迁移必须与 Postgres 对齐

### 1.4 AI 服务（独立项目）

- 不在本仓库内实现，但约定：
  - 使用 HTTP 接口供平台调用
  - 接口约定参考 `docs/API_DESIGN.md` 中「与 AI 服务的接口」部分

---

## 2. 目录结构规范

项目根目录主要结构约定如下（已有或推荐）：

- `README.md`：项目总览与文档索引
- `AGENTS.md`：AI Agent 行为规范（不可随意修改）
- `docs/`：所有设计与规范文档
- `app/backend/`：平台后端代码（FastAPI）
- `app/frontend/`：前端 Web 应用代码（Svelte / SvelteKit）

要求：

- 后端所有业务逻辑放在 `app/backend` 下，不在根目录散落脚本
- 前端所有页面、组件、状态管理放在 `app/frontend` 下
- 新增文档统一放在 `docs/` 目录中，并在 `README.md` 或本文件中补充索引

---

## 3. 新成员环境初始化流程

### 3.1 克隆仓库

- 从代码托管平台克隆本仓库到本地。

### 3.2 安装基础工具

- 必备：
  - Python 3.10+
  - Node.js 18+（Svelte/SvelteKit 推荐）
  - PostgreSQL（本地或远程可访问实例）

---

## 4. 后端环境初始化（FastAPI）

在 `app/backend` 目录中：

1. 创建虚拟环境（示例）  
   `python -m venv .venv`
2. 激活虚拟环境  
   - macOS / Linux：`source .venv/bin/activate`  
   - Windows：`.venv\Scripts\activate`
3. 安装依赖（最低集合）  
   `pip install fastapi uvicorn[standard] sqlalchemy psycopg2-binary alembic python-dotenv passlib[bcrypt] httpx`
4. 配置数据库连接  
   - 创建 `.env` 文件（不提交到仓库），包含例如：  
     - `DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/ai_dapp`  
     - `AI_SERVICE_BASE_URL=http://localhost:9000`（示例）
5. 运行开发服务器（入口名称可根据实际代码调整）  
   `uvicorn main:app --reload`

> 后端的模块划分、接口定义、表结构必须与 `docs/ARCHITECTURE.md`、`docs/API_DESIGN.md`、`docs/DB_SCHEMA.md` 保持一致。

---

## 5. 数据库与迁移流程

所有环境的数据库结构通过 Alembic 迁移维护：

1. 初始化 Alembic（仅一次）  
   在 `app/backend` 中运行：`alembic init migrations`
2. 根据 `docs/DB_SCHEMA.md` 定义 ORM 模型（`users`、`transactions`、`ai_requests` 等）。
3. 生成迁移脚本：`alembic revision --autogenerate -m "init schema"`
4. 应用迁移：`alembic upgrade head`

新增 / 修改表结构时：

- 先更新相关设计文档（`DB_SCHEMA.md`）
- 再修改 ORM 模型
- 最后通过 Alembic 生成并应用迁移

---

## 6. 后端模块与实现顺序（MVP）

所有后端开发以 `docs/API_DESIGN.md` 和 `docs/DB_SCHEMA.md` 为依据，建议按以下顺序实施：

### 6.1 阶段 1：基础骨架与数据库

- 创建 FastAPI 应用骨架（`main.py`）
- 实现数据库连接与基础 ORM 设置（如 `database.py`）
- 使用 Alembic 创建初始迁移，包含：
  - `users`
  - `transactions`
  - `ai_requests`

### 6.2 阶段 2：认证与用户系统

实现接口：

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

约定：

- 注册成功时初始化用户 `balance` 并发放初始赠币，写入 `transactions`
- 密码使用 bcrypt 哈希存储
- 使用 JWT 或等价 Token 机制实现认证中间件

### 6.3 阶段 3：链下钱包与交易流水

实现接口：

- `GET /api/wallet`
- `GET /api/wallet/transactions`

实现原则：

- 更新余额与写入交易流水必须在单一数据库事务内完成
- 封装统一的「变更余额」函数，所有扣费 / 奖励均通过此函数调用

### 6.4 阶段 4：任务与奖励（基础版）

基于 `tasks` 和 `user_tasks`：

- 实现：
  - `GET /api/tasks`
  - `POST /api/tasks/{task_id}/claim`
- 内置任务示例：
  - 注册任务
  - 首次成功使用 AI
  - 每日首次登录任务

### 6.5 阶段 5：AI 调用入口与扣费

关键接口：

- `POST /api/ai/chat`

统一流程：

1. 校验用户身份
2. 根据计费策略计算本次调用所需游戏币（初期可为固定值）
3. 检查余额是否足够
4. 扣费（事务内更新 `users.balance`，写一条 `transactions`）
5. 记录 `ai_requests`
6. 调用外部 AI 服务（`AI_SERVICE_BASE_URL`）
7. 返回 AI 响应，以及本次调用的 `usage` 和最新 `balance`（可选）

### 6.6 阶段 6：简化版管理后台接口

实现接口：

- `POST /api/admin/login`
- `GET /api/admin/users`
- `GET /api/admin/users/{user_id}`
- `POST /api/admin/users/{user_id}/grant-coins`

要求：

- 管理员发币 / 调整余额必须通过统一的余额变更函数
- 所有操作记录原因，便于审计

---

## 7. 前端实现顺序（Svelte / SvelteKit，MVP）

所有前端开发以 `docs/FRONTEND_SPEC.md` 和 `docs/API_DESIGN.md` 为依据。

建议使用 **SvelteKit** 放在 `app/frontend` 下：

### 7.1 阶段 1：项目初始化与路由

1. 在 `app/frontend` 目录使用官方脚手架创建 SvelteKit 项目（命令可参考官方文档）。  
2. 配置基础路由（基于文件系统）：
   - `/login`
   - `/app/chat`
   - `/wallet`
   - `/tasks`
3. 引入 TailwindCSS，用于快速构建 UI。

### 7.2 阶段 2：认证与全局状态

- 实现登录 / 注册页面（`/login`）
- 调用后端：
  - `POST /api/auth/register`
  - `POST /api/auth/login`
  - `GET /api/auth/me`
- 前端维护全局状态：
  - 当前用户 `currentUser`
  - 当前余额 `balance`
  - 登录状态 `isAuthenticated`
- 未登录用户访问受保护路由（chat / wallet / tasks）时重定向到 `/login`。

### 7.3 阶段 3：AI 对话页（`/app/chat`）

功能：

- 显示对话消息列表
- 发送消息，调用 `POST /api/ai/chat`
- 显示加载状态、错误提示（如余额不足）
- 更新全局余额状态

### 7.4 阶段 4：钱包页（`/wallet`）

功能：

- 调用 `GET /api/wallet` 展示当前余额
- 调用 `GET /api/wallet/transactions` 展示流水列表

UI 建议：

- 明确区分收入 / 支出
- 支持分页或滚动加载

### 7.5 阶段 5：任务页（`/tasks`）

功能：

- 调用 `GET /api/tasks` 获取任务与状态
- 支持点击领取任务奖励（`POST /api/tasks/{task_id}/claim`）
- 提供跳转入口（如「去聊天」跳转 `/app/chat`）

### 7.6 阶段 6：基础管理后台（可选）

- 如与主前端同项目，可在 `/admin` 下提供后台入口
- 功能：
  - 管理员登录
  - 用户列表与详情
  - 手动发放游戏币界面

---

## 8. 错误处理与返回格式约定

后端接口建议统一使用 `docs/API_DESIGN.md` 中的响应格式：

- 成功：

```json
{
  "success": true,
  "data": { },
  "error": null
}
```

- 失败：

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误说明"
  }
}
```

常用错误码：

- `UNAUTHORIZED`：未登录 / Token 无效
- `FORBIDDEN`：权限不足
- `VALIDATION_ERROR`：参数校验失败
- `INSUFFICIENT_BALANCE`：余额不足
- `TASK_NOT_COMPLETED`：任务未完成无法领取奖励
- `TASK_ALREADY_REWARDED`：任务奖励已领取
- `INTERNAL_ERROR`：服务器内部错误

前端在封装请求时：

- 对 `UNAUTHORIZED` 自动跳转登录页
- 对业务错误（如 `INSUFFICIENT_BALANCE`）给出明确提示，并引导去任务 / 充值

---

## 9. 安全与风控最低要求（MVP）

所有实现必须至少满足 `docs/SECURITY_RISK_CONTROL.md` 中的 MVP 基线：

- 密码使用安全哈希存储（禁止明文）
- 余额与交易变更在事务内保证一致性
- AI 调用接口具备基础限频机制（按用户 ID / IP）
- 管理员发币操作有详细日志（操作人、时间、原因）

---

## 10. 文档与代码的关系

- 新功能或重要改动，应先更新或补充相关设计文档：
  - 数据库变更 → 更新 `docs/DB_SCHEMA.md`
  - 接口变更 → 更新 `docs/API_DESIGN.md`
  - 前端交互变更 → 更新 `docs/FRONTEND_SPEC.md`
- 文档与实现不一致时，以「先更新文档，再修改代码」为原则，避免长期偏离。

本规范作为团队统一的「落地手册」，在实际执行中如有合理调整需求，应在讨论后同步修订本文件。

