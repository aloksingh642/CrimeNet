from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from ..database import get_db
from ..schemas.auth import LoginRequest, Token, UserCreate, UserResponse
from ..security.auth import authenticate_user, create_access_token, get_password_hash, get_current_active_user, get_user_by_username
from ..models.user import User
from ..config import settings
from ..services.audit_service import log_audit

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value if hasattr(user.role, 'value') else str(user.role)},
        expires_delta=access_token_expires
    )
    
    log_audit(db, user.id, user.username, "LOGIN", "USER", user.id, "User logged in")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role)
        }
    }

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    # Only ADMIN can register new users, but allow first user creation
    existing_users = db.query(User).count()
    if existing_users > 0:
        # Check admin
        role_val = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        if role_val != "ADMIN":
            raise HTTPException(status_code=403, detail="Only ADMIN can create users")
    
    existing = get_user_by_username(db, user_data.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed,
        full_name=user_data.full_name,
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    log_audit(db, current_user.id if existing_users > 0 else new_user.id, new_user.username, "USER_CREATED", "USER", new_user.id, f"Created user {new_user.username}")
    
    return new_user

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    role_val = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_val not in ["ADMIN", "INVESTIGATOR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    users = db.query(User).all()
    return users
