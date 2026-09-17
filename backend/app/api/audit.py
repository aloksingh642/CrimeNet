from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models.audit import AuditLog
from ..models.user import User
from ..security.auth import get_current_active_user

router = APIRouter(prefix="/api/audit-logs", tags=["audit"])

@router.get("")
def list_audit_logs(
    limit: int = Query(100, ge=1, le=500),
    action: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    role_val = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_val not in ["ADMIN", "INVESTIGATOR"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return logs

@router.get("/stats")
def audit_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    from sqlalchemy import func
    
    total = db.query(AuditLog).count()
    by_action = db.query(AuditLog.action, func.count(AuditLog.id)).group_by(AuditLog.action).all()
    
    return {
        "total": total,
        "by_action": [{"action": action, "count": count} for action, count in by_action]
    }
