"""
Jokes API Router - 笑话管理 API
笑话的增删查功能 (用于管理和测试)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from ..database import get_db
from ..models import Joke
from ..schemas import JokeCreate, JokeResponse, MessageResponse
from ..auth import get_current_user

router = APIRouter(prefix="/jokes", tags=["Jokes - 笑话管理"])


# ==================== 创建笑话 ====================

@router.post("", response_model=JokeResponse, status_code=status.HTTP_201_CREATED)
def create_joke(
    joke_data: JokeCreate,
    db: Session = Depends(get_db)
):
    """
    创建一个新笑话
    
    - **question**: 笑话问题部分
    - **answer**: 笑话答案部分
    - **joke_type**: 笑话类型 (pun, knock_knock, riddle 等)
    - **min_age**: 最小适合年龄
    - **max_age**: 最大适合年龄
    - **tags**: 标签 (逗号分隔)
    """
    new_joke = Joke(
        question=joke_data.question,
        answer=joke_data.answer,
        joke_type=joke_data.joke_type or "pun",
        min_age=joke_data.min_age or 3,
        max_age=joke_data.max_age or 12,
        tags=joke_data.tags
    )
    
    db.add(new_joke)
    db.commit()
    db.refresh(new_joke)
    
    return new_joke


# ==================== 获取笑话列表 ====================

@router.get("", response_model=List[JokeResponse])
def get_jokes(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的最大记录数"),
    joke_type: Optional[str] = Query(None, description="按笑话类型筛选"),
    age: Optional[int] = Query(None, ge=1, le=18, description="按适合年龄筛选"),
    db: Session = Depends(get_db)
):
    """
    获取笑话列表
    
    支持分页和筛选:
    - **skip**: 跳过的记录数 (默认 0)
    - **limit**: 返回的最大记录数 (默认 20)
    - **joke_type**: 按笑话类型筛选
    - **age**: 按适合年龄筛选
    """
    query = db.query(Joke)
    
    if joke_type:
        query = query.filter(Joke.joke_type == joke_type)
    
    if age:
        query = query.filter(Joke.min_age <= age, Joke.max_age >= age)
    
    jokes = query.offset(skip).limit(limit).all()
    
    return jokes


# ==================== 获取单个笑话 ====================

@router.get("/{joke_id}", response_model=JokeResponse)
def get_joke(joke_id: int, db: Session = Depends(get_db)):
    """
    获取指定笑话的详情
    
    - **joke_id**: 笑话ID
    """
    joke = db.query(Joke).filter(Joke.id == joke_id).first()
    
    if not joke:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Joke not found"
        )
    
    return joke


# ==================== 获取随机笑话 ====================

@router.get("/random/one", response_model=JokeResponse)
def get_random_joke(
    age: Optional[int] = Query(None, ge=1, le=18, description="按适合年龄筛选"),
    joke_type: Optional[str] = Query(None, description="按笑话类型筛选"),
    db: Session = Depends(get_db)
):
    """
    获取一个随机笑话
    
    - **age**: 按适合年龄筛选 (可选)
    - **joke_type**: 按笑话类型筛选 (可选)
    """
    from sqlalchemy.sql.expression import func
    
    query = db.query(Joke)
    
    if age:
        query = query.filter(Joke.min_age <= age, Joke.max_age >= age)
    
    if joke_type:
        query = query.filter(Joke.joke_type == joke_type)
    
    joke = query.order_by(func.random()).first()
    
    if not joke:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No jokes found matching the criteria"
        )
    
    return joke


# ==================== 删除笑话 ====================

@router.delete("/{joke_id}", response_model=MessageResponse)
def delete_joke(joke_id: int, db: Session = Depends(get_db)):
    """
    删除指定笑话
    
    - **joke_id**: 笑话ID
    """
    joke = db.query(Joke).filter(Joke.id == joke_id).first()
    
    if not joke:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Joke not found"
        )
    
    db.delete(joke)
    db.commit()
    
    return {"message": "Joke deleted successfully", "success": True}
