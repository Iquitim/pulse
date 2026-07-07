import os
import logging
from typing import Optional
from fastapi import Request, HTTPException, Depends, Header, status
from sqlalchemy.orm import Session
from app.database import get_db, User
from app import security

logger = logging.getLogger(__name__)

async def get_current_user(request: Request, authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autorizado. Token de acesso ausente ou inválido."
        )
    token = authorization.split(" ")[1]
    payload = security.verify_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão expirada ou token inválido."
        )
    user_email = payload["sub"]
    user = db.query(User).filter(User.email == user_email).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário desativado ou inexistente."
        )
        
    if user.must_change_password:
        if not (request.url.path == "/api/auth/change-password" or request.url.path == "/api/auth/me"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Alteração de senha obrigatória."
            )
    return user

async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem executar esta ação."
        )
    return current_user
