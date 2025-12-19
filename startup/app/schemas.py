"""
Pydantic Schemas - 请求和响应的数据结构
用于数据验证和序列化
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ==================== 用户相关 Schema ====================

class UserCreate(BaseModel):
    """创建用户的请求体"""
    email: EmailStr
    password: str = Field(..., min_length=6, description="密码至少6位")
    username: Optional[str] = None
    address: Optional[str] = None
    child_age: Optional[int] = Field(None, ge=1, le=18, description="孩子年龄 1-18")
    default_mode: Optional[str] = Field("home", pattern="^(home|classroom)$")
    effects_enabled: Optional[bool] = True


class UserUpdate(BaseModel):
    """更新用户的请求体"""
    username: Optional[str] = None
    address: Optional[str] = None
    child_age: Optional[int] = Field(None, ge=1, le=18)
    default_mode: Optional[str] = Field(None, pattern="^(home|classroom)$")
    effects_enabled: Optional[bool] = None


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    email: str
    username: Optional[str]
    address: Optional[str]
    child_age: Optional[int]
    default_mode: str
    effects_enabled: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 认证相关 Schema ====================

class Token(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token 数据"""
    email: Optional[str] = None


class LoginRequest(BaseModel):
    """登录请求"""
    email: EmailStr
    password: str


# ==================== 笑话相关 Schema ====================

class JokeCreate(BaseModel):
    """创建笑话的请求体"""
    question: str = Field(..., min_length=5, description="笑话问题部分")
    answer: str = Field(..., min_length=1, description="笑话答案部分")
    joke_type: Optional[str] = "pun"
    min_age: Optional[int] = Field(3, ge=1, le=18)
    max_age: Optional[int] = Field(12, ge=1, le=18)
    tags: Optional[str] = None


class JokeResponse(BaseModel):
    """笑话响应"""
    id: int
    question: str
    answer: str
    joke_type: str
    min_age: int
    max_age: int
    tags: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 收藏相关 Schema ====================

class CollectionCreate(BaseModel):
    """收藏笑话的请求体"""
    joke_id: int
    note: Optional[str] = Field(None, max_length=500, description="收藏备注")


class CollectionResponse(BaseModel):
    """收藏响应"""
    id: int
    user_id: int
    joke_id: int
    collected_at: datetime
    note: Optional[str]
    joke: JokeResponse  # 包含笑话详情

    class Config:
        from_attributes = True


class CollectionListResponse(BaseModel):
    """收藏列表响应"""
    total: int
    collections: List[CollectionResponse]


# ==================== 通用响应 Schema ====================

class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str
    success: bool = True
