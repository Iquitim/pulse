import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db, User, TierConfig, AuditLog, InviteCode, log_activity, SystemSetting
from app.routes.dependencies import get_current_user, get_admin_user
from app.routes.schemas import UpdatePlanRequest, TierConfigUpdate, InviteCodeCreate
from app import security

logger = logging.getLogger(__name__)

router = APIRouter()

# --- Audit Logs for Normal Users ---

@router.get("/api/audit-logs")
async def get_audit_logs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logs = db.query(AuditLog).filter(AuditLog.user_id == current_user.id).order_by(AuditLog.timestamp.desc()).limit(50).all()
    return [
        {
            "id": l.id,
            "action": l.action,
            "details": l.details,
            "timestamp": l.timestamp.isoformat()
        } for l in logs
    ]

# --- Administrative Endpoints (Admin Required) ---

@router.get("/api/admin/users")
async def admin_get_users(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "plan_tier": u.plan_tier,
            "created_at": u.created_at.isoformat()
        } for u in users
    ]

@router.patch("/api/admin/users/{id}")
async def admin_toggle_user_status(id: int, status_active: bool, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Você não pode desativar seu próprio usuário administrador.")
        
    user.is_active = status_active
    db.commit()
    log_activity(db, admin.id, "admin_toggle_user_status", f"Admin alterou status do usuário {user.email} para {'ativo' if status_active else 'inativo'}.")
    return {"status": "success", "message": f"Status do usuário updated."}

@router.delete("/api/admin/users/{user_id}")
async def admin_delete_user(user_id: int, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Você não pode excluir seu próprio usuário administrador.")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    email = user.email
    db.delete(user)
    db.commit()
    log_activity(db, admin.id, "admin_delete_user", f"Admin excluiu permanentemente o usuário {email}.")
    return {"status": "success", "message": "Usuário excluído com sucesso."}

@router.put("/api/admin/users/{user_id}/plan")
async def admin_update_user_plan(user_id: int, req: UpdatePlanRequest, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    if req.plan_tier not in ("free", "pro", "desk"):
        raise HTTPException(status_code=400, detail="Plano inválido.")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    old_plan = user.plan_tier
    user.plan_tier = req.plan_tier
    db.commit()
    log_activity(db, admin.id, "admin_change_user_plan", f"Admin alterou plano do usuário {user.email} de {old_plan} para {req.plan_tier}")
    return {"status": "success", "message": f"Plano do usuário atualizado para {req.plan_tier}."}

@router.get("/api/admin/tier-configs")
async def admin_get_tier_configs(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    configs = db.query(TierConfig).all()
    return [
        {
            "tier_name": c.tier_name,
            "max_themes": c.max_themes,
            "max_accounts": c.max_accounts,
            "max_calendar_items": c.max_calendar_items,
            "daily_post_limit": c.daily_post_limit
        } for c in configs
    ]

@router.put("/api/admin/tier-configs/{tier_name}")
async def admin_update_tier_configs(tier_name: str, req: TierConfigUpdate, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    config_entry = db.query(TierConfig).filter(TierConfig.tier_name == tier_name).first()
    if not config_entry:
        raise HTTPException(status_code=404, detail="Configuração de tier não encontrada.")
    
    config_entry.max_themes = req.max_themes
    config_entry.max_accounts = req.max_accounts
    config_entry.max_calendar_items = req.max_calendar_items
    config_entry.daily_post_limit = req.daily_post_limit
    
    db.commit()
    log_activity(db, admin.id, "admin_update_tier_configs", f"Admin atualizou limites do tier {tier_name}: temas={req.max_themes}, contas={req.max_accounts}, itens={req.max_calendar_items}, posts_diarios={req.daily_post_limit}")
    return {"status": "success", "message": f"Configurações do plano {tier_name} atualizadas."}

@router.get("/api/admin/users/{user_id}/audit-logs")
async def admin_get_user_audit_logs(user_id: int, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    
    logs = db.query(AuditLog).filter(AuditLog.user_id == user_id).order_by(AuditLog.timestamp.desc()).limit(100).all()
    return [
        {
            "id": l.id,
            "action": l.action,
            "details": l.details,
            "timestamp": l.timestamp.isoformat()
        } for l in logs
    ]

@router.get("/api/admin/invite-codes")
async def admin_get_invite_codes(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    codes = db.query(InviteCode).all()
    return [
        {
            "id": c.id,
            "code": c.code,
            "plan_tier": c.plan_tier,
            "max_uses": c.max_uses,
            "uses_count": c.uses_count,
            "created_at": c.created_at.isoformat(),
            "revoked": c.revoked_at is not None
        } for c in codes
    ]

@router.post("/api/admin/invite-codes")
async def admin_create_invite_code(req: InviteCodeCreate, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    existing = db.query(InviteCode).filter(InviteCode.code == req.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Este código de convite já existe.")
        
    new_code = InviteCode(
        code=req.code,
        plan_tier=req.plan_tier,
        max_uses=req.max_uses
    )
    db.add(new_code)
    db.commit()
    return {"status": "success", "code": new_code.code}

@router.delete("/api/admin/invite-codes/{id}")
async def admin_revoke_invite_code(id: int, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    code_entry = db.query(InviteCode).filter(InviteCode.id == id).first()
    if not code_entry:
        raise HTTPException(status_code=404, detail="Código de convite não encontrado.")
        
    code_entry.revoked_at = datetime.utcnow()
    db.commit()
    return {"status": "success", "message": "Código de convite revogado."}

@router.get("/api/admin/global-settings")
async def admin_get_global_settings(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    client_id_setting = db.query(SystemSetting).filter(SystemSetting.key == "twitter_client_id").first()
    client_secret_setting = db.query(SystemSetting).filter(SystemSetting.key == "twitter_client_secret").first()
    
    return {
        "twitter_client_id": client_id_setting.value if client_id_setting else "",
        "twitter_client_secret_configured": bool(client_secret_setting and client_secret_setting.value)
    }

@router.put("/api/admin/global-settings")
async def admin_update_global_settings(
    req: dict,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    twitter_client_id = req.get("twitter_client_id", "").strip()
    twitter_client_secret = req.get("twitter_client_secret", "").strip()
    
    id_setting = db.query(SystemSetting).filter(SystemSetting.key == "twitter_client_id").first()
    if not id_setting:
        id_setting = SystemSetting(key="twitter_client_id", value=twitter_client_id)
        db.add(id_setting)
    else:
        id_setting.value = twitter_client_id
        
    if twitter_client_secret and twitter_client_secret != "__UNCHANGED__":
        encrypted_secret = security.encrypt_value(twitter_client_secret)
        secret_setting = db.query(SystemSetting).filter(SystemSetting.key == "twitter_client_secret").first()
        if not secret_setting:
            secret_setting = SystemSetting(key="twitter_client_secret", value=encrypted_secret)
            db.add(secret_setting)
        else:
            secret_setting.value = encrypted_secret
            
    db.commit()
    log_activity(db, admin.id, "admin_update_global_settings", "Admin atualizou as credenciais globais da API do Twitter.")
    return {"status": "success", "message": "Configurações globais atualizadas com sucesso."}
