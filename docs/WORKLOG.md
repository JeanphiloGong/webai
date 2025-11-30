# 项目工作日志（AI DApp + 游戏币系统）

本文件用于记录项目关键工作项与进度，方便团队协作与同步。  
说明：状态可在执行过程中由团队成员手动更新为「进行中 / 已完成」等。

---

## 2025-11-28 最小 MVP 原型任务（待开始）

目标：在最短时间内完成一个可演示的「AI 平台 + 链下游戏币」最小闭环原型。  
范围仅限平台侧，AI 模型由独立项目提供或先用假数据占位。

### 一、后端（FastAPI）任务

1. 基础项目与数据库
   - [x] 在 `app/backend` 下初始化 FastAPI 项目（入口 `main.py`，包含 `/health`）。
   - [x] 配置 PostgreSQL 连接（参考 `docs/DB_SCHEMA.md`，通过环境变量 `DATABASE_URL`）。
   - [x] 使用 Alembic 建立初始迁移，创建以下表：
     - [x] `users`
     - [x] `transactions`
     - [x] `ai_requests`

2. 用户基础能力
   - [x] 实现注册接口 `POST /api/auth/register`：
     - 创建用户记录（邮箱/手机号 + 密码哈希）。
     - 初始化用户 `balance` 为 0。
     - 发放「初始赠币」（例如 1000），写入一条 `transactions`（type=`reward`，reason=`signup_bonus`）。
   - [x] 实现登录接口 `POST /api/auth/login`：
     - 校验账号密码，返回 Token（JWT 或等价方案）。
   - [x] 实现当前用户接口 `GET /api/auth/me`：
     - 根据 Token 返回当前用户信息（可包含余额快照）。

3. 链下游戏币基础能力
   - [ ] 实现钱包概览接口 `GET /api/wallet`：
     - 返回当前用户余额与基本信息。
   - [ ] 实现交易流水接口 `GET /api/wallet/transactions`：
     - 按时间倒序分页返回 `transactions` 记录。
   - [ ] 封装统一的「变更余额」函数：
     - 在数据库事务中同时更新 `users.balance` 和插入 `transactions`。

4. AI 调用 + 扣费闭环
   - [ ] 在配置中预设固定价格（例如每次 AI 调用消耗 10 游戏币）。
   - [ ] 实现 `POST /api/ai/chat` 接口，流程：
     - 校验用户身份。
     - 检查余额是否 ≥ 价格，不足则返回业务错误（如 `INSUFFICIENT_BALANCE`）。
     - 使用统一变更余额函数扣除游戏币，写一条 `transactions`（type=`cost`，reason=`ai_chat`）。
     - 在 `ai_requests` 中记录一次调用记录（可简化为只记类型与状态）。
     - 调用一个简化的「假 AI 服务」（可以是本地占位逻辑：例如简单回声或固定回答），未来替换为真实 AI 项目。
     - 返回 AI 回复内容和最新余额。

5. 安全与基础风控
   - [ ] 密码使用 bcrypt 哈希存储（禁止明文）。
   - [ ] 在 `POST /api/ai/chat` 上实现简单的限频（按用户 ID 或 IP），防止明显刷接口。

### 二、前端（Svelte / SvelteKit）任务

1. 项目初始化与路由
   - [x] 在 `app/frontend` 下初始化 SvelteKit 项目（含 TypeScript）。
   - [x] 配置基础路由：
     - `/login`：登录 / 注册页面。
     - `/app/chat`：AI 对话页面。
     - `/wallet`：钱包页面。

2. 认证与全局状态
   - [ ] 实现 `/login` 页面：
     - 注册：调用 `POST /api/auth/register`。
     - 登录：调用 `POST /api/auth/login`，保存 Token。
   - [ ] 在前端维护全局状态：
     - 当前用户信息 `currentUser`。
     - 当前余额 `balance`。
     - 登录状态 `isAuthenticated`。
   - [ ] 未登录用户访问 `/app/chat` 或 `/wallet` 时，重定向到 `/login`。

3. AI 对话页面 `/app/chat`
   - [ ] 实现基本对话 UI（输入框 + 消息列表）。
   - [ ] 调用 `POST /api/ai/chat` 发送问题，展示 AI 回复。
   - [ ] 显示请求中的加载状态 / 错误提示。
   - [ ] 在成功响应后更新全局余额（从响应中获取或重新请求 `GET /api/wallet`）。
   - [ ] 当后端返回「余额不足」错误时，在页面上提示并引导用户前往钱包页面。

4. 钱包页面 `/wallet`
   - [ ] 调用 `GET /api/wallet` 显示当前余额。
   - [ ] 调用 `GET /api/wallet/transactions` 显示最近若干条流水。
   - [ ] UI 上区分收入（奖励）与支出（AI 调用）记录。

### 三、验收标准（本轮最小 MVP）

- [ ] 新用户可以在前端完成注册 / 登录。
- [ ] 注册后自动获得一笔初始游戏币，前端钱包页能看到余额和奖励流水。
- [ ] 用户在 AI 对话页发送消息时，会扣除固定数量游戏币，并得到 AI（或假 AI）的回复。
- [ ] 钱包页可以看到 AI 调用带来的扣费流水。
- [ ] 余额不足时，AI 对话接口返回明确错误，前端给出友好提示。

> 完成以上任务后，即视为「最小 MVP 原型」达成，可以用于内部演示和流程验证。后续扩展（任务系统、活动、链上部分等）参见 `docs/ROADMAP.md`。 

