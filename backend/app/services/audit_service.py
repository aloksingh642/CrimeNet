from sqlalchemy.orm import Session
from ..models.audit import AuditLog
from datetime import datetime

def log_audit(db: Session, user_id: int, username: str, action: str, resource_type: str = None, resource_id: str = None, details: str = None, ip_address: str = None):
    try:
        audit = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            details=details,
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()
    except Exception as e:
        print(f"Audit log failed: {e}")
        db.rollback()
