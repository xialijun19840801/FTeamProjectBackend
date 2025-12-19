# Kids Joke API 🎉

一个专为父母和老师设计的儿童笑话 API 服务。

## 功能特点

- 👤 **用户管理**: 注册、登录、信息管理
- 😄 **笑话管理**: 创建、查询、随机获取适龄笑话
- ⭐ **收藏管理**: 收藏喜欢的笑话，方便重复使用
- 🔐 **JWT 认证**: 安全的 Token 认证机制
- 🚦 **请求限流**: 防止 API 滥用 (30次/分钟)

## 快速开始

### 1. 安装依赖

```bash
cd startup
pip install -r requirements.txt
```

### 2. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 接口说明

### 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **认证方式**: JWT Bearer Token
- **限流**: 30 次请求/分钟

### 用户管理 API

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| POST | `/users/register` | 用户注册 | ❌ |
| POST | `/users/login` | 用户登录 | ❌ |
| GET | `/users/me` | 获取当前用户信息 | ✅ |
| PUT | `/users/me` | 更新当前用户信息 | ✅ |
| DELETE | `/users/me` | 删除当前用户 | ✅ |
| GET | `/users/{user_id}` | 获取指定用户信息 | ✅ |

### 笑话管理 API

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| POST | `/jokes` | 创建笑话 | ❌ |
| GET | `/jokes` | 获取笑话列表 | ❌ |
| GET | `/jokes/{joke_id}` | 获取指定笑话 | ❌ |
| GET | `/jokes/random/one` | 获取随机笑话 | ❌ |
| DELETE | `/jokes/{joke_id}` | 删除笑话 | ❌ |

### 收藏管理 API

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| POST | `/collections` | 收藏笑话 | ✅ |
| GET | `/collections` | 获取收藏列表 | ✅ |
| GET | `/collections/{collection_id}` | 获取收藏详情 | ✅ |
| PUT | `/collections/{collection_id}` | 更新收藏备注 | ✅ |
| DELETE | `/collections/{collection_id}` | 取消收藏 | ✅ |
| DELETE | `/collections/joke/{joke_id}` | 通过笑话ID取消收藏 | ✅ |

## 使用示例

### 1. 用户注册

```bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "parent@example.com",
    "password": "123456",
    "username": "John",
    "child_age": 6,
    "default_mode": "home",
    "effects_enabled": true
  }'
```

**响应示例:**
```json
{
  "id": 1,
  "email": "parent@example.com",
  "username": "John",
  "address": null,
  "child_age": 6,
  "default_mode": "home",
  "effects_enabled": true,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### 2. 用户登录

```bash
curl -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "parent@example.com",
    "password": "123456"
  }'
```

**响应示例:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. 获取随机笑话

```bash
curl -X GET "http://localhost:8000/api/v1/jokes/random/one?age=6"
```

**响应示例:**
```json
{
  "id": 1,
  "question": "What do you call a bear with no teeth?",
  "answer": "A gummy bear!",
  "joke_type": "pun",
  "min_age": 3,
  "max_age": 10,
  "tags": "animal,bear,candy",
  "created_at": "2024-01-15T10:00:00"
}
```

### 4. 收藏笑话 (需要认证)

```bash
curl -X POST "http://localhost:8000/api/v1/collections" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "joke_id": 1,
    "note": "My kid loves this one!"
  }'
```

**响应示例:**
```json
{
  "id": 1,
  "user_id": 1,
  "joke_id": 1,
  "collected_at": "2024-01-15T10:35:00",
  "note": "My kid loves this one!",
  "joke": {
    "id": 1,
    "question": "What do you call a bear with no teeth?",
    "answer": "A gummy bear!",
    "joke_type": "pun",
    "min_age": 3,
    "max_age": 10,
    "tags": "animal,bear,candy",
    "created_at": "2024-01-15T10:00:00"
  }
}
```

### 5. 获取收藏列表 (需要认证)

```bash
curl -X GET "http://localhost:8000/api/v1/collections?limit=10" \
  -H "Authorization: Bearer <your_token>"
```

**响应示例:**
```json
{
  "total": 1,
  "collections": [
    {
      "id": 1,
      "user_id": 1,
      "joke_id": 1,
      "collected_at": "2024-01-15T10:35:00",
      "note": "My kid loves this one!",
      "joke": {
        "id": 1,
        "question": "What do you call a bear with no teeth?",
        "answer": "A gummy bear!",
        "joke_type": "pun",
        "min_age": 3,
        "max_age": 10,
        "tags": "animal,bear,candy",
        "created_at": "2024-01-15T10:00:00"
      }
    }
  ]
}
```

## 数据模型

### User (用户)

| 字段 | 类型 | 描述 |
|------|------|------|
| id | int | 用户ID |
| email | string | 邮箱 (唯一) |
| username | string | 用户名 |
| address | string | 地址 |
| child_age | int | 孩子年龄 (1-18) |
| default_mode | string | 默认模式 (home/classroom) |
| effects_enabled | bool | 是否启用效果 |

### Joke (笑话)

| 字段 | 类型 | 描述 |
|------|------|------|
| id | int | 笑话ID |
| question | string | 笑话问题部分 |
| answer | string | 笑话答案部分 |
| joke_type | string | 笑话类型 (pun, knock_knock, riddle) |
| min_age | int | 最小适合年龄 |
| max_age | int | 最大适合年龄 |
| tags | string | 标签 (逗号分隔) |

### Collection (收藏)

| 字段 | 类型 | 描述 |
|------|------|------|
| id | int | 收藏ID |
| user_id | int | 用户ID |
| joke_id | int | 笑话ID |
| collected_at | datetime | 收藏时间 |
| note | string | 备注 |

## 错误码说明

| HTTP 状态码 | 描述 |
|-------------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 / Token 无效 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 429 | 请求过于频繁 (限流) |
| 500 | 服务器内部错误 |

## 技术栈

- **框架**: FastAPI
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **认证**: JWT (python-jose)
- **密码加密**: bcrypt (passlib)
- **限流**: slowapi
- **ORM**: SQLAlchemy

## 项目结构

```
startup/
├── app/
│   ├── __init__.py          # 包初始化
│   ├── main.py              # FastAPI 主入口
│   ├── database.py          # 数据库配置
│   ├── models.py            # 数据模型
│   ├── schemas.py           # Pydantic Schema
│   ├── auth.py              # JWT 认证模块
│   └── routers/
│       ├── __init__.py
│       ├── users.py         # 用户 API
│       ├── jokes.py         # 笑话 API
│       └── collections.py   # 收藏 API
├── requirements.txt         # 依赖列表
├── README.md               # 说明文档
└── kids_joke.db            # SQLite 数据库 (自动生成)
```

## License

MIT License
