# 接口设计（平台后端）

本文档定义平台后端的主要 HTTP API 接口，前端通过这些接口完成登录、钱包查询、任务领取和 AI 调用等操作。与 AI 服务之间的接口仅做简要说明。

> 说明：以下为设计草案，可在实际开发中根据框架习惯微调路径与字段命名。

---

## 1. 认证与用户接口

### 1.1 注册

- `POST /api/auth/register`
- 请求体：
  - `email`（可选）
  - `phone`（可选，两者至少一个）
  - `password`
  - `code`（可选，短信或邮箱验证码）
- 响应：
  - `user`：用户基础信息
  - `token`：访问令牌（如 JWT）

说明：

- 注册成功后自动创建用户并初始化余额（含初始赠币）

### 1.2 登录

- `POST /api/auth/login`
- 请求体（根据登录方式不同略有差异）：
  - 账号密码登录：`identifier`（邮箱或手机号）、`password`
  - 验证码登录：`phone` / `email` + `code`
- 响应：
  - `user`
  - `token`

### 1.3 获取当前用户信息

- `GET /api/auth/me`
- 请求头：
  - `Authorization: Bearer <token>`
- 响应：
  - `user`：包含基础信息与当前余额快照（可选）

### 1.4 登出

- `POST /api/auth/logout`
- 逻辑：
  - 前端删除本地 Token
  - 如使用服务端 Session，可在服务端失效化

---

## 2. 钱包与交易接口

### 2.1 获取钱包概览

- `GET /api/wallet`
- 请求头：
  - `Authorization: Bearer <token>`
- 响应：
  - `balance`：当前余额
  - `currency`：币种代号（如 `GC`）
  - `updated_at`：余额最近更新时间

### 2.2 获取交易流水

- `GET /api/wallet/transactions`
- 查询参数：
  - `page`（默认 1）
  - `page_size`（默认 20）
  - `type`（可选过滤：`recharge` / `reward` / `cost`）
- 响应：
  - `items`: 交易列表，每项包含：
    - `id`
    - `amount`
    - `type`
    - `reason`
    - `created_at`
  - `total`
  - `page`
  - `page_size`

### 2.3 充值（占位接口）

- `POST /api/wallet/recharge`
- MVP 可以先不对接真实支付渠道，只做占位或内部测试充值。

请求体示例：

- `amount`：希望充值的游戏币数量

响应：

- `balance`：充值后的余额

> 真正接入支付渠道（如 Stripe / 支付宝 / 微信）时，需要引入订单表与回调处理，此处仅保留接口占位。

---

## 3. AI 调用接口

### 3.1 AI 对话（示例）

- `POST /api/ai/chat`
- 请求头：
  - `Authorization: Bearer <token>`
- 请求体示例：
  - `messages`: 聊天消息数组（遵循常见 Chat 格式）
  - `model`：可选，指定使用的模型
  - `extra`：可选，额外参数

后端处理流程：

1. 校验用户身份
2. 根据计费策略计算需要扣除的游戏币数量
3. 检查余额是否足够
4. 扣减余额并记录交易（`type=cost`）
5. 写入一条 `ai_requests` 记录
6. 调用 AI 服务的 HTTP 接口（例如 `POST /ai/chat`）
7. 将 AI 响应返回给前端，并可附带本次消耗信息

响应体示例：

- `answer`：AI 回复内容
- `usage`：调用统计数据（如 Token 数）
- `balance`：最新余额（可选）
- `transaction_id`：本次扣费流水 ID（可选）

### 3.2 其他 AI 功能占位

可预留以下接口：

- `POST /api/ai/generate`：文生文 / 文生图
- `POST /api/ai/image`：图像生成 / 编辑

实现方式与 `chat` 类似，主要差别在于计费策略与请求参数。

---

## 4. 任务与奖励接口

### 4.1 获取任务列表

- `GET /api/tasks`
- 请求头：
  - `Authorization: Bearer <token>`
- 响应：
  - `tasks`: 数组，每项包含：
    - `id`
    - `code`
    - `name`
    - `description`
    - `reward_amount`
    - `status`（`pending` / `completed` / `rewarded`）

### 4.2 领取任务奖励

- `POST /api/tasks/{task_id}/claim`
- 请求头：
  - `Authorization: Bearer <token>`
- 响应：
  - `success`：是否领取成功
  - `balance`：最新余额

后端逻辑：

1. 检查用户是否有资格领取（任务已完成但未领取）
2. 向用户发放对应游戏币奖励
3. 记录一条 `transactions`（`type=reward`）
4. 更新 `user_tasks` 状态为 `rewarded`

---

## 5. 管理后台接口（简化版）

路径可以统一加前缀 `/api/admin`。

### 5.1 管理员登录

- `POST /api/admin/login`
- 请求体：
  - `username`
  - `password`
- 响应：
  - `token`

### 5.2 查看用户列表

- `GET /api/admin/users`
- 查询参数：
  - `page`，`page_size`
  - `keyword`（按邮箱 / 手机 / 昵称模糊搜索）
- 响应：
  - 用户列表（含 `id`、`email` / `phone`、`balance`、`created_at`）

### 5.3 查看单个用户详情

- `GET /api/admin/users/{user_id}`

返回：

- 用户详细信息 + 近几条交易记录

### 5.4 给用户发放游戏币

- `POST /api/admin/users/{user_id}/grant-coins`
- 请求体：
  - `amount`：发放数量
  - `reason`：原因
- 响应：
  - `balance`：发放后的余额

逻辑：

- 写一条 `transactions`（`type=reward` 或 `adjustment`）

---

## 6. 与 AI 服务的接口（简要）

AI 服务接口由另一个项目实现，此处仅给出平台需要的调用约定示例。

### 6.1 平台调用 AI 服务：`/ai/chat`

- 方法：`POST`
- 请求体：
  - `messages`：消息数组
  - `user_id` 或 `session_id`：可选，便于 AI 服务做个性化
  - `params`：如温度、最大 Token 数等
- 响应体：
  - `answer`
  - `usage`：
    - `prompt_tokens`
    - `completion_tokens`
    - `total_tokens`

平台后端可使用 `total_tokens` 参与计费，也可以只按调用次数计费。

---

## 7. 错误码与返回格式（建议）

建议统一返回格式：

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

失败时：

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INSUFFICIENT_BALANCE",
    "message": "余额不足，请先获取更多游戏币"
  }
}
```

常见错误码建议：

- `UNAUTHORIZED`：未登录或 Token 无效
- `FORBIDDEN`：权限不足
- `VALIDATION_ERROR`：参数校验失败
- `INSUFFICIENT_BALANCE`：余额不足
- `TASK_NOT_COMPLETED`：任务尚未完成
- `TASK_ALREADY_REWARDED`：任务奖励已领取
- `INTERNAL_ERROR`：服务器内部错误

