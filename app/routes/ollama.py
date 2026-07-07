import logging
import threading
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import security
from app import ollama_installer
from app.database import get_db, User, LLMServer, log_activity
from app.routes.dependencies import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# Global pull progress storage
# key: (host, model) -> dict
pull_progress = {}

class PullRequest(BaseModel):
    host: str
    model: str

class StartRequest(BaseModel):
    model: Optional[str] = None

# Helper to normalize Ollama URLs from OpenAI to native API
def normalize_host(host_url: str) -> str:
    if not host_url:
        return "http://localhost:11434"
    # Remove trailing /v1 or /v1/ if they exist
    url = host_url.strip()
    if url.endswith("/v1/"):
        url = url[:-4]
    elif url.endswith("/v1"):
        url = url[:-3]
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    return url

@router.get("/api/ollama/diagnostic")
async def get_ollama_diagnostic(current_user: User = Depends(get_current_user)):
    try:
        return ollama_installer.get_hardware_report()
    except Exception as e:
        logger.error(f"Erro ao obter diagnóstico de hardware: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/api/ollama/status")
async def get_ollama_status(current_user: User = Depends(get_current_user)):
    try:
        # Check standard running local instance
        if ollama_installer.check_local_ollama_running():
            return {
                "status": "running",
                "type": "system",
                "embedded_installed": ollama_installer.is_embedded_installed()
            }
        
        # Check embedded running instance
        embedded_pid = ollama_installer.get_running_embedded_pid()
        if embedded_pid:
            return {
                "status": "running",
                "type": "embedded",
                "embedded_installed": True
            }
            
        # Check if embedded is downloaded but stopped
        if ollama_installer.is_embedded_installed():
            return {
                "status": "stopped",
                "type": "none",
                "embedded_installed": True
            }
            
        return {
            "status": "not_installed",
            "type": "none",
            "embedded_installed": False
        }
    except Exception as e:
        logger.error(f"Erro ao verificar status do Ollama: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/ollama/install")
async def install_ollama(current_user: User = Depends(get_current_user)):
    state = ollama_installer.get_install_state()
    if state["status"] in ("downloading", "extracting"):
        return {"status": "busy", "message": "Instalação já está em andamento."}
        
    success = ollama_installer.start_install()
    if success:
        return {"status": "started", "message": "Instalação do Ollama iniciada."}
    else:
        raise HTTPException(status_code=400, detail="Não foi possível iniciar a instalação.")

@router.get("/api/ollama/install-progress")
async def get_install_progress(current_user: User = Depends(get_current_user)):
    return ollama_installer.get_install_state()

@router.post("/api/ollama/start")
async def start_ollama(req: StartRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        success = ollama_installer.start_embedded_ollama()
        if not success:
            raise HTTPException(status_code=400, detail="Falha ao iniciar o serviço embutido do Ollama.")
            
        # Auto-configure LLM Server in database
        # Determine default model to configure (from request or diagnostic default)
        default_model = req.model
        if not default_model:
            diag = ollama_installer.get_hardware_report()
            default_model = diag.get("recommended_model", "phi3:3.8b")

        # Check if Ollama Server is already configured
        existing_server = db.query(LLMServer).filter(
            LLMServer.user_id == current_user.id,
            LLMServer.provider == "ollama",
            LLMServer.base_url.like("%localhost:11434%")
        ).first()

        if not existing_server:
            # Create new server entry
            # Deactivate all other user servers
            db.query(LLMServer).filter(LLMServer.user_id == current_user.id).update({LLMServer.is_active: False})
            
            new_server = LLMServer(
                user_id=current_user.id,
                name="Ollama Embutido (Local)",
                provider="ollama",
                model=default_model,
                base_url="http://localhost:11434/v1",
                is_active=True
            )
            db.add(new_server)
            db.commit()
            log_activity(db, current_user.id, "start_embedded_ollama", f"Ollama embutido iniciado e ativado. Modelo padrão: {default_model}")
        else:
            # Activate existing server entry
            db.query(LLMServer).filter(LLMServer.user_id == current_user.id).update({LLMServer.is_active: False})
            existing_server.is_active = True
            existing_server.model = default_model
            db.commit()
            log_activity(db, current_user.id, "start_embedded_ollama", f"Ollama embutido reativado. Modelo padrão: {default_model}")

        return {"status": "success", "message": f"Ollama embutido rodando com modelo {default_model}."}
    except Exception as e:
        logger.error(f"Erro ao iniciar Ollama: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/ollama/stop")
async def stop_ollama(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    success = ollama_installer.stop_embedded_ollama()
    if success:
        log_activity(db, current_user.id, "stop_embedded_ollama", "Serviço Ollama embutido parado pelo usuário.")
        return {"status": "success", "message": "Ollama embutido parado com sucesso."}
    else:
        raise HTTPException(status_code=400, detail="Não foi possível parar o serviço (talvez não esteja rodando).")

@router.get("/api/ollama/models")
async def get_ollama_models(host: Optional[str] = None, current_user: User = Depends(get_current_user)):
    from ollama import Client
    normalized_host = normalize_host(host)
    try:
        client = Client(host=normalized_host)
        models_data = client.list()
        # Parse model names robustly supporting both dicts and class objects
        models_list = []
        models = []
        if hasattr(models_data, 'models'):
            models = models_data.models
        elif isinstance(models_data, dict):
            models = models_data.get("models", [])
            
        for m in models:
            name = None
            if hasattr(m, 'model'):
                name = m.model
            elif hasattr(m, 'name'):
                name = m.name
            elif isinstance(m, dict):
                name = m.get("model") or m.get("name")
                
            if name:
                models_list.append(name)
                
        return {"status": "success", "models": models_list}
    except Exception as e:
        logger.error(f"Erro ao conectar com Ollama no host {normalized_host}: {e}")
        raise HTTPException(status_code=400, detail=f"Não foi possível conectar com o Ollama em {normalized_host}. Certifique-se de que o serviço está rodando.")

def _pull_model_thread(host: str, model: str):
    from ollama import Client
    global pull_progress
    key = (host, model)
    try:
        client = Client(host=host)
        pull_progress[key] = {
            "status": "Iniciando transferência...",
            "completed": 0,
            "total": 0,
            "percentage": 0,
            "done": False,
            "error": None
        }
        
        for response in client.pull(model=model, stream=True):
            status = response.get("status", "")
            completed = response.get("completed") or 0
            total = response.get("total") or 0
            percentage = int((completed / total) * 100) if total > 0 else 0
            
            pull_progress[key] = {
                "status": status,
                "completed": completed,
                "total": total,
                "percentage": percentage,
                "done": False,
                "error": None
            }
            
        pull_progress[key] = {
            "status": "Modelo baixado com sucesso!",
            "completed": 0,
            "total": 0,
            "percentage": 100,
            "done": True,
            "error": None
        }
    except Exception as e:
        logger.error(f"Erro ao fazer pull de {model} em {host}: {e}")
        pull_progress[key] = {
            "status": "Falhou",
            "completed": 0,
            "total": 0,
            "percentage": 0,
            "done": True,
            "error": str(e)
        }

@router.post("/api/ollama/pull")
async def pull_model(req: PullRequest, current_user: User = Depends(get_current_user)):
    normalized_host = normalize_host(req.host)
    key = (normalized_host, req.model)
    
    # Check if download is already running
    if key in pull_progress and not pull_progress[key]["done"]:
        return {"status": "busy", "message": f"Download do modelo {req.model} já está em andamento."}
        
    # Start thread
    thread = threading.Thread(target=_pull_model_thread, args=(normalized_host, req.model), daemon=True)
    thread.start()
    return {"status": "started", "message": f"Iniciando download do modelo {req.model}."}

@router.get("/api/ollama/pull-progress")
async def get_pull_progress(host: str, model: str, current_user: User = Depends(get_current_user)):
    normalized_host = normalize_host(host)
    key = (normalized_host, model)
    if key in pull_progress:
        return pull_progress[key]
    return {
        "status": "idle",
        "completed": 0,
        "total": 0,
        "percentage": 0,
        "done": False,
        "error": None
    }
