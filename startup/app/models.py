"""
Database Models - 数据库模型
定义用户、笑话、收藏的数据表结构
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class User(Base):
    """
    用户表 - 存储用户信息
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # 用户基本信息
    username = Column(String(100), nullable=True)
    address = Column(String(500), nullable=True)
    
    # 孩子年龄 (例如: 5, 8, 10)
    child_age = Column(Integer, nullable=True)
    
    # 默认模式: "home" (家庭模式) 或 "classroom" (教室模式)
    default_mode = Column(String(20), default="home")
    
    # 是否启用效果 (EFFECTS on/off)
    effects_enabled = Column(Boolean, default=True)
    
    # 账户状态
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联收藏
    collections = relationship("Collection", back_populates="user")


class Joke(Base):
    """
    笑话表 - 存储笑话内容
    """
    __tablename__ = "jokes"

    id = Column(Integer, primary_key=True, index=True)
    
    # 笑话内容 (问答式)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    
    # 笑话类型: "pun" (双关语), "knock_knock" (敲门笑话), "riddle" (谜语) 等
    joke_type = Column(String(50), default="pun")
    
    # 适合年龄范围
    min_age = Column(Integer, default=3)
    max_age = Column(Integer, default=12)
    
    # 标签 (用逗号分隔，如 "animal,food,school")
    tags = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联收藏
    collections = relationship("Collection", back_populates="joke")


class Collection(Base):
    """
    收藏表 - 用户收藏的笑话
    """
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joke_id = Column(Integer, ForeignKey("jokes.id"), nullable=False)
    
    # 收藏时间
    collected_at = Column(DateTime, default=datetime.utcnow)
    
    # 用户备注 (可选)
    note = Column(String(500), nullable=True)

    # 关联
    user = relationship("User", back_populates="collections")
    joke = relationship("Joke", back_populates="collections")
