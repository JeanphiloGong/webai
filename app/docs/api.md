# 身份认证 API 文档

- 基础地址：`http://localhost:8010`
- 认证方式：`Authorization: Bearer <token>`（注册或登录接口返回的 `token` 字段）

## 接口列表

### 1) 注册用户
- `POST /api/auth/register`
- 请求体（`application/json`）：
  ```json
  {
    "email": "user@example.com",  // email 和 phone 至少提供一个
    "phone": "13800000000",
    "password": "your-password",
    "code": "可选验证码"
  }
  ```
- 成功响应：
  ```json
  {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "phone": "13800000000",
      "balance": 1000,
      "is_activate": true
    },
    "token": "<jwt_token>"
  }
  ```
- 典型错误：400 邮箱/手机号已注册或未提供联系方式。
- 示例 curl：
  ```bash
  curl -X POST \
    'http://localhost:8010/api/auth/register' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
      "email": "user@example.com",
      "phone": "13800000000",
      "password": "your-password",
      "code": "123456"
    }'
  ```

### 2) 用户登录
- `POST /api/auth/login`
- 请求体（`application/json`）：
  ```json
  {
    "identifier": "user@example.com 或 13800000000",
    "password": "your-password"
  }
  ```
- 成功响应：
  ```json
  {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "phone": "13800000000",
      "balance": 1000,
      "is_activate": true
    },
    "token": "<jwt_token>"
  }
  ```
- 典型错误：401 帐号或密码错误；400 用户被禁用。
- 示例 curl：
  ```bash
  curl -X POST \
    'http://localhost:8010/api/auth/login' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
      "identifier": "user@example.com",
      "password": "your-password"
    }'
  ```

### 3) 获取当前用户信息
- `GET /api/auth/me`
- 需要在请求头携带 `Authorization: Bearer <token>`。
- 成功响应：
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "phone": "13800000000",
    "balance": 1000,
    "is_activate": true
  }
  ```
- 典型错误：401 未提供或无效的 token。
- 示例 curl（替换 `<jwt_token>`）：
  ```bash
  curl -X GET \
    'http://localhost:8010/api/auth/me' \
    -H 'accept: application/json' \
    -H 'Authorization: Bearer <jwt_token>'
  ```

## 使用提示
- 先调用注册或登录获取 `token`，再将其放入后续请求的 `Authorization` 头部。
- 如果在 FastAPI 文档界面测试，点击右上角 “Authorize”，输入 `Bearer <token>` 后再调用需要鉴权的接口。
