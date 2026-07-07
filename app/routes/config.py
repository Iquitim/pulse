import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import scheduler
from app import security
from app.database import get_db, User, AgentConfig, TierConfig, LLMServer, log_activity
from app.routes.dependencies import get_current_user
from app.routes.schemas import ConfigModel, LLMServerCreate, LLMServerResponse, TestLLMServerRequest

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/api/config")
async def get_config(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    config_data = db.query(AgentConfig).filter(AgentConfig.user_id == current_user.id).first()
    if not config_data:
        config_data = AgentConfig(user_id=current_user.id)
        db.add(config_data)
        db.commit()
        
    themes = [t.strip() for t in config_data.themes_csv.split(",") if t.strip()]
    
    # Fallback to default persona if not set yet
    persona = config_data.persona_description
    if persona is None:
        from app.database import DEFAULT_PERSONA_DESCRIPTION
        persona = DEFAULT_PERSONA_DESCRIPTION
        
    return {
        "themes": themes,
        "tone": config_data.tone,
        "interval_hours": config_data.interval_hours,
        "is_active": config_data.is_active,
        "system_prompt": config_data.system_prompt,
        "persona_description": persona,
        "requires_approval": config_data.requires_approval,
        "scheduling_mode": config_data.scheduling_mode or "recorrente",
        "channel": config_data.channel or "bluesky"
    }

@router.post("/api/config")
async def save_config(new_config: ConfigModel, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tier_config = db.query(TierConfig).filter(TierConfig.tier_name == current_user.plan_tier).first()
    if tier_config and len(new_config.themes) > tier_config.max_themes:
        raise HTTPException(
            status_code=400,
            detail=f"Limite de temas excedido para o plano {current_user.plan_tier}. Máximo de {tier_config.max_themes} temas permitidos."
        )

    config_data = db.query(AgentConfig).filter(AgentConfig.user_id == current_user.id).first()
    if not config_data:
        config_data = AgentConfig(user_id=current_user.id)
        db.add(config_data)
        
    config_data.themes_csv = ",".join(new_config.themes)
    config_data.tone = new_config.tone
    config_data.interval_hours = new_config.interval_hours
    config_data.is_active = new_config.is_active
    config_data.system_prompt = new_config.system_prompt
    config_data.persona_description = new_config.persona_description
    config_data.requires_approval = new_config.requires_approval
    config_data.scheduling_mode = new_config.scheduling_mode or "recorrente"
    config_data.channel = new_config.channel or "bluesky"
    
    db.commit()
    
    scheduler.sync_scheduler()
    
    log_activity(db, current_user.id, "save_config", f"Configurações salvas: ativo={config_data.is_active}, modo={config_data.scheduling_mode}, canal={config_data.channel}, temas_count={len(new_config.themes)}")
    
    return {
        "themes": new_config.themes,
        "tone": config_data.tone,
        "interval_hours": config_data.interval_hours,
        "is_active": config_data.is_active,
        "system_prompt": config_data.system_prompt,
        "persona_description": config_data.persona_description,
        "requires_approval": config_data.requires_approval,
        "scheduling_mode": config_data.scheduling_mode,
        "channel": config_data.channel
    }

# --- LLM Servers CRUD APIs ---

@router.get("/api/llm-servers", response_model=List[LLMServerResponse])
async def get_llm_servers(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    servers = db.query(LLMServer).filter(LLMServer.user_id == current_user.id).order_by(LLMServer.created_at.desc()).all()
    res = []
    for s in servers:
        res.append(LLMServerResponse(
            id=s.id,
            name=s.name,
            provider=s.provider,
            model=s.model,
            base_url=s.base_url,
            is_active=s.is_active,
            api_key="********" if s.api_key_encrypted else ""
        ))
    return res

@router.post("/api/llm-servers", response_model=LLMServerResponse)
async def create_llm_server(req: LLMServerCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if this is the first server for this user
    existing_count = db.query(LLMServer).filter(LLMServer.user_id == current_user.id).count()
    should_be_active = (existing_count == 0)
    
    api_key_encrypted = None
    if req.api_key:
        api_key_encrypted = security.encrypt_value(req.api_key)
        
    new_server = LLMServer(
        user_id=current_user.id,
        name=req.name,
        provider=req.provider,
        model=req.model,
        base_url=req.base_url,
        api_key_encrypted=api_key_encrypted,
        is_active=should_be_active
    )
    db.add(new_server)
    db.commit()
    db.refresh(new_server)
    
    log_activity(db, current_user.id, "create_llm_server", f"Servidor LLM criado: {req.name} ({req.provider})")
    
    return LLMServerResponse(
        id=new_server.id,
        name=new_server.name,
        provider=new_server.provider,
        model=new_server.model,
        base_url=new_server.base_url,
        is_active=new_server.is_active,
        api_key="********" if new_server.api_key_encrypted else ""
    )

@router.put("/api/llm-servers/{server_id}", response_model=LLMServerResponse)
async def update_llm_server(server_id: int, req: LLMServerCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    server = db.query(LLMServer).filter(LLMServer.id == server_id, LLMServer.user_id == current_user.id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Servidor LLM não encontrado.")
        
    server.name = req.name
    server.provider = req.provider
    server.model = req.model
    server.base_url = req.base_url
    
    if req.api_key and req.api_key != "********":
        server.api_key_encrypted = security.encrypt_value(req.api_key)
    elif not req.api_key:
        server.api_key_encrypted = None
        
    db.commit()
    db.refresh(server)
    
    log_activity(db, current_user.id, "update_llm_server", f"Servidor LLM atualizado: {req.name}")
    
    return LLMServerResponse(
        id=server.id,
        name=server.name,
        provider=server.provider,
        model=server.model,
        base_url=server.base_url,
        is_active=server.is_active,
        api_key="********" if server.api_key_encrypted else ""
    )

@router.delete("/api/llm-servers/{server_id}")
async def delete_llm_server(server_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    server = db.query(LLMServer).filter(LLMServer.id == server_id, LLMServer.user_id == current_user.id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Servidor LLM não encontrado.")
        
    was_active = server.is_active
    name = server.name
    
    db.delete(server)
    db.commit()
    
    # If deleted server was active, activate the most recent remaining server (if any)
    if was_active:
        next_server = db.query(LLMServer).filter(LLMServer.user_id == current_user.id).order_by(LLMServer.created_at.desc()).first()
        if next_server:
            next_server.is_active = True
            db.commit()
            
    log_activity(db, current_user.id, "delete_llm_server", f"Servidor LLM excluído: {name}")
    return {"status": "success", "message": f"Servidor {name} excluído com sucesso."}

@router.post("/api/llm-servers/{server_id}/activate", response_model=LLMServerResponse)
async def activate_llm_server(server_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    server_to_activate = db.query(LLMServer).filter(LLMServer.id == server_id, LLMServer.user_id == current_user.id).first()
    if not server_to_activate:
        raise HTTPException(status_code=404, detail="Servidor LLM não encontrado.")
        
    # Mark all other user servers as inactive
    db.query(LLMServer).filter(
        LLMServer.user_id == current_user.id,
        LLMServer.id != server_id
    ).update({LLMServer.is_active: False})
    
    server_to_activate.is_active = True
    db.commit()
    db.refresh(server_to_activate)
    
    log_activity(db, current_user.id, "activate_llm_server", f"Servidor LLM ativado: {server_to_activate.name}")
    
    return LLMServerResponse(
        id=server_to_activate.id,
        name=server_to_activate.name,
        provider=server_to_activate.provider,
        model=server_to_activate.model,
        base_url=server_to_activate.base_url,
        is_active=server_to_activate.is_active,
        api_key="********" if server_to_activate.api_key_encrypted else ""
    )

@router.post("/api/llm-servers/test-connection")
async def test_llm_server_connection(req: TestLLMServerRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    api_key = req.api_key
    # Handle mask if they are testing a saved server but passing mask
    if api_key == "********":
        # Note: We need a server ID to lookup, but TestLLMServerRequest doesn't have ID because it tests the *form* values.
        # But wait! If they are editing a server, they have the ID. Let's see: we can look up if there is an existing server with this name or provider, but to be completely safe:
        # We can pass an optional server_id in TestLLMServerRequest, or we can look up the first server matching their provider/model/name.
        # Let's add an optional id to TestLLMServerRequest, or look it up.
        # Actually, adding an optional 'id' field to TestLLMServerRequest is extremely easy and robust!
        # Wait, if we don't have the ID, let's search if the user has a server with this name/model and decrypt its key.
        pass
        
    # Let's add an optional ID to the schema, or support passing it. Let's look up by name/provider to fall back, or if not found use None.
    # Actually, let's just add `id: Optional[int] = None` to `TestLLMServerRequest` in `schemas.py` or inspect it here.
    # Let's see: if api_key is "********", we can query db for any server of this user where api_key_encrypted is set, and decrypt the first one.
    # Or even better, we can query by matching base_url and model:
    if api_key == "********":
        match = db.query(LLMServer).filter(
            LLMServer.user_id == current_user.id,
            LLMServer.provider == req.provider,
            LLMServer.model == req.model
        ).first()
        if match and match.api_key_encrypted:
            api_key = security.decrypt_value(match.api_key_encrypted)
        else:
            api_key = None
            

    try:
        from app.agent import test_connection
        success = test_connection(req.provider, req.model, req.base_url, api_key)
        if success:
            return {"status": "success", "message": "Conexão com o LLM estabelecida com sucesso!"}
        else:
            raise Exception("O modelo não retornou uma resposta válida.")
    except Exception as e:
        logger.error(f"Erro no teste de conexão do LLM: {e}")
        raise HTTPException(status_code=400, detail=str(e))
