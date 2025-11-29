# 数据库表结构设计（链下版）

本文档基于「完全链下游戏币」的 MVP 场景，设计平台后端所需的核心数据库表结构。以 PostgreSQL 为例，其他关系型数据库可以做等价映射。

---

## 1. 核心表概览

MVP 阶段建议包含以下核心表：

- `users`：用户基础信息与余额
- `transactions`：游戏币交易流水
- `ai_requests`：AI 调用记录
- `tasks`：任务定义
- `user_tasks`：用户任务完成情况
- `admin_users`：后台管理员账号

后续扩展可以新增：

- `pricing_rules`：计费策略配置
- `onchain_withdrawals` / `onchain_deposits`：链上同步相关（非 MVP）

---

## 2. `users` 表

用户基础信息与余额。

示例字段：

- `id`（bigserial, PK）
- `email`（varchar, unique, nullable：允许只手机号注册）
- `phone`（varchar, unique, nullable）
- `password_hash`（varchar）—— 存储密码哈希（如 bcrypt）
- `nickname`（varchar, nullable）
- `avatar_url`（varchar, nullable）
- `balance`（bigint, default 0）—— 当前游戏币余额（以最小单位计）
- `is_active`（boolean, default true）
- `created_at`（timestamptz, default now()）
- `updated_at`（timestamptz, default now()）

说明：

- 余额使用整数型，避免浮点误差
- 如未来希望支持多种虚拟币，可拆分为 `user_balances` 表

---

## 3. `transactions` 表

记录所有游戏币变动，作为账本。

示例字段：

- `id`（bigserial, PK）
- `user_id`（bigint, FK -> users.id）
- `amount`（bigint）—— 正数为收入，负数为支出
- `type`（varchar）—— `recharge` / `reward` / `cost` / `adjustment` 等
- `reason`（varchar, nullable）—— 简要说明，例如「注册赠币」「AI 调用」
- `related_ai_request_id`（bigint, FK -> ai_requests.id, nullable）
- `meta`（jsonb, nullable）—— 扩展信息，如活动 ID、任务 ID
- `created_at`（timestamptz, default now()）

索引建议：

- `idx_transactions_user_created_at`（user_id, created_at DESC）

---

## 4. `ai_requests` 表

记录每次 AI 调用的请求与结果摘要，便于统计与问题排查。

示例字段：

- `id`（bigserial, PK）
- `user_id`（bigint, FK -> users.id）
- `request_type`（varchar）—— `chat` / `generate` / `image` 等
- `input_preview`（text）—— 请求内容的截断版本（例如前 200 字）
- `output_preview`（text, nullable）—— 响应内容截断版
- `usage`（jsonb, nullable）—— 用于记录 Token 数等；
- `status`（varchar）—— `success` / `failed` / `timeout` 等
- `error_message`（text, nullable）
- `created_at`（timestamptz, default now()）

注意隐私与合规要求，可以考虑：

- 对敏感内容做脱敏或不落库
+- 提供数据清理 / 匿名化工具（后续）

---

## 5. `tasks` 表

任务配置表，用于定义任务和奖励。

示例字段：

- `id`（bigserial, PK）
- `code`（varchar, unique）—— 任务唯一编码，例如 `FIRST_AI_CALL`
- `name`（varchar）—— 展示名称
- `description`（text）—— 任务说明
- `reward_amount`（bigint）—— 完成奖励的游戏币数量
- `is_active`（boolean, default true）
- `created_at`（timestamptz, default now()）
- `updated_at`（timestamptz, default now()）

任务逻辑可以在代码中实现，或通过更多字段（如条件表达式）实现更灵活的配置（后续扩展）。

---

## 6. `user_tasks` 表

记录用户的任务状态。

示例字段：

- `id`（bigserial, PK）
- `user_id`（bigint, FK -> users.id）
- `task_id`（bigint, FK -> tasks.id）
- `status`（varchar）—— `pending` / `completed` / `rewarded`
- `progress`（jsonb, nullable）—— 可用于记录进度数据，如完成次数
- `completed_at`（timestamptz, nullable）
- `rewarded_at`（timestamptz, nullable）
- `created_at`（timestamptz, default now()）
- `updated_at`（timestamptz, default now()）

业务规则示例：

- 某任务只能领取一次奖励，则需保证 `rewarded` 记录唯一
- 每次任务状态变化都更新 `updated_at`

---

## 7. `admin_users` 表

后台管理员账号。

示例字段：

- `id`（bigserial, PK）
- `username`（varchar, unique）
- `password_hash`（varchar）
- `role`（varchar）—— 例如 `super_admin` / `operator`
- `is_active`（boolean, default true）
- `created_at`（timestamptz, default now()）
- `updated_at`（timestamptz, default now()）

后续可扩展权限控制表，例如 `admin_roles` / `admin_permissions`。

---

## 8. 计费配置（可选，非 MVP 必需）

如果希望不通过硬编码来控制价格，可以增加：

- `pricing_rules` 表
  - `id`
  - `code`（如 `AI_CHAT_BASIC`）
  - `name`
  - `price_per_call`（bigint）
  - `price_per_token`（bigint, nullable）
  - `is_active`

平台后端在扣费时根据不同调用场景选择对应规则。

---

## 9. 迁移与演进建议

- 使用数据库迁移工具管理表结构（如 Alembic / Django Migrations / Prisma Migrate 等）
- 所有与游戏币相关的变更保持向后兼容，避免破坏旧流水记录
- 对于未来引入链上模式：
  - 可以新增 `wallets` 表存储链上地址
  - 新增链上相关记录表，而不是直接改动现有 `transactions` 语义

