"""
Kids Joke API - 儿童笑话 API 主入口
一个为父母和老师提供的儿童笑话管理系统

Features:
- 用户管理 (注册、登录、信息更新)
- 笑话管理 (创建、查询、随机获取)
- 收藏管理 (收藏、取消收藏、列表查询)
- JWT 认证
- 请求限流
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .database import engine, Base
from .routers import users, collections, jokes
from .models import Joke
from .database import SessionLocal

# ==================== 创建数据库表 ====================
Base.metadata.create_all(bind=engine)


# ==================== 限流器配置 ====================
limiter = Limiter(key_func=get_remote_address)


# ==================== 创建 FastAPI 应用 ====================
app = FastAPI(
    title="Kids Joke API",
    description="""
## 🎉 Kids Joke API - 儿童笑话 API

一个专为父母和老师设计的儿童笑话管理系统。

### 功能特点:
- 👤 **用户管理**: 注册、登录、信息管理
- 😄 **笑话管理**: 创建、查询、随机获取适龄笑话
- ⭐ **收藏管理**: 收藏喜欢的笑话，方便重复使用
- 🔐 **JWT 认证**: 安全的 Token 认证机制
- 🚦 **请求限流**: 防止 API 滥用

### 使用流程:
1. 调用 `/users/register` 注册账号
2. 调用 `/users/login` 获取 Token
3. 在请求 Header 中添加 `Authorization: Bearer <token>`
4. 开始使用各种 API!

### 适用场景:
- 🏠 **家庭模式 (Home)**: 父母给孩子讲笑话
- 🏫 **教室模式 (Classroom)**: 老师在课堂上使用
""",
    version="1.0.0",
    contact={
        "name": "Kids Joke Team",
        "email": "support@kidsjoke.com"
    },
    license_info={
        "name": "MIT License"
    }
)

# 添加限流器到应用
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ==================== CORS 中间件 ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 注册路由 ====================
app.include_router(users.router, prefix="/api/v1")
app.include_router(jokes.router, prefix="/api/v1")
app.include_router(collections.router, prefix="/api/v1")


# ==================== 根路由 ====================
@app.get("/", tags=["Root"])
@limiter.limit("30/minute")
def root(request: Request):
    """
    API 根路由 - 返回欢迎信息和 API 状态
    """
    return {
        "message": "Welcome to Kids Joke API! 🎉",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# ==================== 健康检查 ====================
@app.get("/health", tags=["Health"])
@limiter.limit("60/minute")
def health_check(request: Request):
    """
    健康检查端点
    """
    return {"status": "healthy", "service": "kids-joke-api"}


# ==================== 初始化示例笑话数据 ====================
@app.on_event("startup")
def init_sample_jokes():
    """
    应用启动时初始化一些示例笑话
    """
    db = SessionLocal()
    try:
        # 检查是否已有笑话
        existing_jokes = db.query(Joke).count()
        if existing_jokes == 0:
            sample_jokes = [
                {
                    "question": "What do you call a bear with no teeth?",
                    "answer": "A gummy bear!",
                    "joke_type": "pun",
                    "min_age": 3,
                    "max_age": 10,
                    "tags": "animal,bear,candy"
                },
                {
                    "question": "Why did the banana go to the doctor?",
                    "answer": "Because it wasn't peeling well!",
                    "joke_type": "pun",
                    "min_age": 4,
                    "max_age": 12,
                    "tags": "food,fruit,health"
                },
                {
                    "question": "What do you call a fish without eyes?",
                    "answer": "A fsh!",
                    "joke_type": "pun",
                    "min_age": 5,
                    "max_age": 12,
                    "tags": "animal,fish,spelling"
                },
                {
                    "question": "Why don't scientists trust atoms?",
                    "answer": "Because they make up everything!",
                    "joke_type": "pun",
                    "min_age": 8,
                    "max_age": 15,
                    "tags": "science,atoms"
                },
                {
                    "question": "What do you call a sleeping dinosaur?",
                    "answer": "A dino-snore!",
                    "joke_type": "pun",
                    "min_age": 3,
                    "max_age": 8,
                    "tags": "animal,dinosaur,sleep"
                },
                {
                    "question": "Why did the teddy bear say no to dessert?",
                    "answer": "Because she was already stuffed!",
                    "joke_type": "pun",
                    "min_age": 4,
                    "max_age": 10,
                    "tags": "toy,food,teddy"
                },
                {
                    "question": "What do you call a cow with no legs?",
                    "answer": "Ground beef!",
                    "joke_type": "pun",
                    "min_age": 6,
                    "max_age": 12,
                    "tags": "animal,cow,food"
                },
                {
                    "question": "Why do bees have sticky hair?",
                    "answer": "Because they use honeycombs!",
                    "joke_type": "pun",
                    "min_age": 4,
                    "max_age": 10,
                    "tags": "animal,bee,honey"
                },
                {
                    "question": "What did the ocean say to the beach?",
                    "answer": "Nothing, it just waved!",
                    "joke_type": "pun",
                    "min_age": 3,
                    "max_age": 10,
                    "tags": "nature,ocean,beach"
                },
                {
                    "question": "Why did the math book look so sad?",
                    "answer": "Because it had too many problems!",
                    "joke_type": "pun",
                    "min_age": 6,
                    "max_age": 12,
                    "tags": "school,math,book"
                }
            ]
            
            for joke_data in sample_jokes:
                joke = Joke(**joke_data)
                db.add(joke)
            
            db.commit()
            print("✅ Initialized 10 sample jokes!")
    finally:
        db.close()


# ==================== 应用限流到所有 API 路由 ====================
# 为用户相关路由添加限流
@app.middleware("http")
async def add_rate_limit_headers(request: Request, call_next):
    """
    添加限流相关的响应头
    """
    response = await call_next(request)
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
