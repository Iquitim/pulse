from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app import config
from app import security
from app.database import get_db, User, InviteCode, AgentConfig, log_activity
from app.routes.dependencies import get_current_user
from app.routes.schemas import RegisterRequest, LoginRequest, ChangePasswordRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register")
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if not config.ALLOW_PUBLIC_REGISTRATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="O cadastro público de novos usuários está desativado nesta instância."
        )

    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Este e-mail já está cadastrado.")

    plan_tier = "free"
    code_entry = None

    if config.REQUIRE_INVITE_CODE:
        if not req.invite_code:
            raise HTTPException(status_code=400, detail="Código de convite obrigatório nesta instância.")
        
        code_entry = db.query(InviteCode).filter(
            InviteCode.code == req.invite_code,
            InviteCode.revoked_at == None
        ).first()
        
        if not code_entry:
            raise HTTPException(status_code=400, detail="Código de convite inválido ou revogado.")
            
        if code_entry.uses_count >= code_entry.max_uses:
            raise HTTPException(status_code=400, detail="Este código de convite já atingiu o limite de uso.")
        
        plan_tier = code_entry.plan_tier

    else:
        if req.invite_code:
            code_entry = db.query(InviteCode).filter(
                InviteCode.code == req.invite_code,
                InviteCode.revoked_at == None
            ).first()
            
            if not code_entry:
                raise HTTPException(status_code=400, detail="Código de convite inválido ou revogado.")
                
            if code_entry.uses_count >= code_entry.max_uses:
                raise HTTPException(status_code=400, detail="Este código de convite já atingiu o limite de uso.")
            
            plan_tier = code_entry.plan_tier

    hashed_pwd = security.hash_password(req.password)
    
    new_user = User(
        email=req.email,
        hashed_password=hashed_pwd,
        role="user",
        plan_tier=plan_tier
    )
    db.add(new_user)
    db.flush()

    if code_entry:
        code_entry.uses_count += 1
    
    default_config = AgentConfig(
        user_id=new_user.id,
        is_active=False,
        requires_approval=False,
        interval_hours=6,
        tone="informativo"
    )
    db.add(default_config)
    db.commit()
    
    log_activity(db, new_user.id, "register", f"Conta criada com sucesso com perfil de cota {plan_tier}.")

    return {"status": "success", "message": "Conta criada com sucesso."}

@router.post("/login")
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not security.verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Sua conta está inativa.")

    access_token = security.create_access_token(data={"sub": user.email})
    log_activity(db, user.id, "login", "Login realizado com sucesso.")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user.email,
            "role": user.role,
            "plan_tier": user.plan_tier,
            "must_change_password": user.must_change_password
        }
    }

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "role": current_user.role,
        "plan_tier": current_user.plan_tier,
        "must_change_password": current_user.must_change_password
    }

@router.post("/change-password")
async def change_password(req: ChangePasswordRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not security.verify_password(req.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Senha atual incorreta.")
    
    if req.new_password == req.current_password:
        raise HTTPException(status_code=400, detail="A nova senha deve ser diferente da atual.")
        
    current_user.hashed_password = security.hash_password(req.new_password)
    current_user.must_change_password = False
    db.commit()
    log_activity(db, current_user.id, "change_password", "Senha alterada com sucesso.")
    return {"status": "success", "message": "Senha alterada com sucesso."}
