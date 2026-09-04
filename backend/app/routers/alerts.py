from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.alert import Alert
from app.models.user import User
from app.schemas.schemas import AlertResponse, AlertUpdateRequest

router = APIRouter(tags=["alerts"])


@router.get("/alerts", response_model=List[AlertResponse])
def list_alerts(
    status: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Alert).filter(Alert.user_id == current_user.id)
    if status:
        q = q.filter(Alert.status == status)
    if risk_level:
        q = q.filter(Alert.risk_level == risk_level)
    return q.order_by(Alert.created_at.desc()).limit(limit).all()


@router.post("/alerts/{alert_id}/action", response_model=AlertResponse)
def act_on_alert(
    alert_id: int,
    payload: AlertUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = db.query(Alert).filter(
        Alert.id == alert_id, Alert.user_id == current_user.id
    ).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")
    alert.status = payload.status
    alert.action_taken_by = current_user.email
    alert.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)
    return alert
