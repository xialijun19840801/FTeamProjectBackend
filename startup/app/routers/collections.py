"""
Collections API Router - 收藏管理 API
用户收藏笑话的增删查功能
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models import User, Joke, Collection
from ..schemas import (
    CollectionCreate,
    CollectionResponse,
    CollectionListResponse,
    MessageResponse
)
from ..auth import get_current_user

router = APIRouter(prefix="/collections", tags=["Collections - 收藏管理"])


# ==================== 收藏笑话 ====================

@router.post("", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
def collect_joke(
    collection_data: CollectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    收藏一个笑话
    
    - **joke_id**: 要收藏的笑话ID
    - **note**: 收藏备注 (可选)
    """
    # 检查笑话是否存在
    joke = db.query(Joke).filter(Joke.id == collection_data.joke_id).first()
    if not joke:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Joke not found"
        )
    
    # 检查是否已收藏
    existing_collection = db.query(Collection).filter(
        Collection.user_id == current_user.id,
        Collection.joke_id == collection_data.joke_id
    ).first()
    
    if existing_collection:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Joke already collected"
        )
    
    # 创建收藏
    new_collection = Collection(
        user_id=current_user.id,
        joke_id=collection_data.joke_id,
        note=collection_data.note
    )
    
    db.add(new_collection)
    db.commit()
    db.refresh(new_collection)
    
    return new_collection


# ==================== 获取收藏列表 ====================

@router.get("", response_model=CollectionListResponse)
def get_collections(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的最大记录数"),
    joke_type: Optional[str] = Query(None, description="按笑话类型筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的收藏列表
    
    支持分页和筛选:
    - **skip**: 跳过的记录数 (默认 0)
    - **limit**: 返回的最大记录数 (默认 20，最大 100)
    - **joke_type**: 按笑话类型筛选 (可选)
    """
    query = db.query(Collection).filter(Collection.user_id == current_user.id)
    
    # 如果指定了笑话类型，进行筛选
    if joke_type:
        query = query.join(Joke).filter(Joke.joke_type == joke_type)
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    collections = query.order_by(Collection.collected_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "collections": collections
    }


# ==================== 获取单个收藏 ====================

@router.get("/{collection_id}", response_model=CollectionResponse)
def get_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定收藏的详情
    
    - **collection_id**: 收藏ID
    """
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.user_id == current_user.id
    ).first()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    return collection


# ==================== 更新收藏备注 ====================

@router.put("/{collection_id}", response_model=CollectionResponse)
def update_collection(
    collection_id: int,
    note: str = Query(..., max_length=500, description="新的备注内容"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新收藏的备注
    
    - **collection_id**: 收藏ID
    - **note**: 新的备注内容
    """
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.user_id == current_user.id
    ).first()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    collection.note = note
    db.commit()
    db.refresh(collection)
    
    return collection


# ==================== 取消收藏 ====================

@router.delete("/{collection_id}", response_model=MessageResponse)
def remove_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取消收藏 (删除收藏记录)
    
    - **collection_id**: 收藏ID
    """
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.user_id == current_user.id
    ).first()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    
    db.delete(collection)
    db.commit()
    
    return {"message": "Collection removed successfully", "success": True}


# ==================== 通过笑话ID取消收藏 ====================

@router.delete("/joke/{joke_id}", response_model=MessageResponse)
def remove_collection_by_joke(
    joke_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    通过笑话ID取消收藏
    
    - **joke_id**: 笑话ID
    """
    collection = db.query(Collection).filter(
        Collection.joke_id == joke_id,
        Collection.user_id == current_user.id
    ).first()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found for this joke"
        )
    
    db.delete(collection)
    db.commit()
    
    return {"message": "Collection removed successfully", "success": True}
