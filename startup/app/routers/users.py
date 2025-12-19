"""
Users API Router - 用户管理 API
包含用户注册、登录、信息查询和更新
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from ..database import get_db
from ..models import User
from ..schemas import (
    UserCreate, 
    UserUpdate, 
    UserResponse, 
    Token, 
    LoginRequest,
    MessageResponse
)
from ..auth import (
    get_password_hash, 
    authenticate_user, 
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/users", tags=["Users - 用户管理"])


# ==================== 用户注册 ====================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册
    
    - **email**: 邮箱地址 (唯一)
    - **password**: 密码 (至少6位)
    - **username**: 用户名 (可选)
    - **address**: 地址 (可选)
    - **child_age**: 孩子年龄 1-18 (可选)
    - **default_mode**: 默认模式 home/classroom (可选，默认 home)
    - **effects_enabled**: 是否启用效果 (可选，默认 true)
    """
    # 检查邮箱是否已存在
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 创建新用户
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        username=user_data.username,
        address=user_data.address,
        child_age=user_data.child_age,
        default_mode=user_data.default_mode or "home",
        effects_enabled=user_data.effects_enabled if user_data.effects_enabled is not None else True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


# ==================== 用户登录 ====================

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录，获取 JWT Token
    
    - **email**: 邮箱地址
    - **password**: 密码
    
    返回 access_token，在后续请求的 Header 中使用:
    ```
    Authorization: Bearer <access_token>
    ```
    """
    user = authenticate_user(db, login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


# ==================== 获取当前用户信息 ====================

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户的信息
    
    需要在 Header 中提供 JWT Token:
    ```
    Authorization: Bearer <access_token>
    ```
    """
    return current_user


# ==================== 获取指定用户信息 ====================

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定用户的信息 (需要认证)
    
    - **user_id**: 用户ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


# ==================== 更新用户信息 ====================

@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新当前用户的信息
    
    可更新字段:
    - **username**: 用户名
    - **address**: 地址
    - **child_age**: 孩子年龄
    - **default_mode**: 默认模式 (home/classroom)
    - **effects_enabled**: 是否启用效果
    """
    update_data = user_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


# ==================== 删除用户 ====================

@router.delete("/me", response_model=MessageResponse)
def delete_current_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除当前用户账号
    
    ⚠️ 此操作不可逆！
    """
    db.delete(current_user)
    db.commit()
    
    return {"message": "User deleted successfully", "success": True}
