import logging
from typing import List
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db, User, EditorialItem, TierConfig, log_activity
from app.routes.dependencies import get_current_user
from app.routes.schemas import EditorialItemCreate, EditorialItemResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/calendar", tags=["calendar"])

@router.get("", response_model=List[EditorialItemResponse])
async def get_calendar(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(EditorialItem).filter(EditorialItem.user_id == current_user.id).order_by(EditorialItem.scheduled_date.asc()).all()
    return items

@router.post("", response_model=EditorialItemResponse)
async def create_calendar_item(req: EditorialItemCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sched_dt = req.scheduled_date
    if sched_dt.tzinfo is not None:
        sched_utc = sched_dt.astimezone(timezone.utc).replace(tzinfo=None)
    else:
        sched_utc = sched_dt
        
    if sched_utc < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Não é possível agendar postagens no passado.")

    calendar_count = db.query(EditorialItem).filter(EditorialItem.user_id == current_user.id).count()
    tier_config = db.query(TierConfig).filter(TierConfig.tier_name == current_user.plan_tier).first()
    if tier_config and calendar_count >= tier_config.max_calendar_items:
        raise HTTPException(
            status_code=400,
            detail=f"Limite de itens no calendário excedido para o plano {current_user.plan_tier}. Máximo de {tier_config.max_calendar_items} posts permitidos."
        )

    theme_val = req.theme
    if req.is_manual and (not theme_val or theme_val == "Uso Manual"):
        theme_val = f"Manual: {req.manual_content[:30]}..." if req.manual_content else "Uso Manual"

    new_item = EditorialItem(
        user_id=current_user.id,
        theme=theme_val,
        scheduled_date=req.scheduled_date,
        status="planejado",
        objective=req.objective,
        cta=req.cta,
        channel=req.channel,
        is_manual=req.is_manual,
        manual_content=req.manual_content
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    log_activity(db, current_user.id, "create_calendar_item", f"Item agendado no calendário: Tema={theme_val}, Canal={req.channel}, Data={req.scheduled_date.isoformat()}, Manual={req.is_manual}")
    return new_item

@router.put("/{item_id}", response_model=EditorialItemResponse)
async def update_calendar_item(item_id: int, req: EditorialItemCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sched_dt = req.scheduled_date
    if sched_dt.tzinfo is not None:
        sched_utc = sched_dt.astimezone(timezone.utc).replace(tzinfo=None)
    else:
        sched_utc = sched_dt
        
    if sched_utc < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Não é possível agendar postagens no passado.")

    item = db.query(EditorialItem).filter(
        EditorialItem.id == item_id,
        EditorialItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item do calendário não encontrado.")
        
    old_theme = item.theme
    theme_val = req.theme
    if req.is_manual and (not theme_val or theme_val == "Uso Manual"):
        theme_val = f"Manual: {req.manual_content[:30]}..." if req.manual_content else "Uso Manual"

    item.theme = theme_val
    item.scheduled_date = req.scheduled_date
    item.objective = req.objective
    item.cta = req.cta
    item.channel = req.channel
    item.is_manual = req.is_manual
    item.manual_content = req.manual_content
    
    db.commit()
    db.refresh(item)
    log_activity(db, current_user.id, "update_calendar_item", f"Item do calendário ID {item_id} atualizado. Tema anterior={old_theme}, Novo Tema={req.theme}, Canal={req.channel}, Data={req.scheduled_date.isoformat()}, Manual={req.is_manual}")
    return item

@router.delete("/{item_id}")
async def delete_calendar_item(item_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(EditorialItem).filter(
        EditorialItem.id == item_id,
        EditorialItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item do calendário não encontrado.")
        
    theme = item.theme
    db.delete(item)
    db.commit()
    log_activity(db, current_user.id, "delete_calendar_item", f"Item do calendário ID {item_id} removido (Tema={theme}).")
    return {"status": "success", "message": "Item do calendário removido com sucesso."}
