import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app import agent
from app.database import get_db, User, Idea, PostHistory, AgentConfig, log_activity
from app.routes.dependencies import get_current_user
from app.routes.schemas import IdeaCreate, IdeaUpdate, IdeaResponse, AnalyzeQualityRequest

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/api/ideas", response_model=List[IdeaResponse])
async def get_ideas(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Idea).filter(Idea.user_id == current_user.id).order_by(Idea.created_at.desc()).all()

@router.post("/api/ideas", response_model=IdeaResponse)
async def create_idea(req: IdeaCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_idea = Idea(
        user_id=current_user.id,
        title=req.title,
        description=req.description,
        channel=req.channel,
        status="pending"
    )
    db.add(new_idea)
    db.commit()
    db.refresh(new_idea)
    log_activity(db, current_user.id, "create_idea", f"Ideia criada: {req.title}")
    return new_idea

@router.put("/api/ideas/{idea_id}", response_model=IdeaResponse)
async def update_idea(idea_id: int, req: IdeaUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.id == idea_id, Idea.user_id == current_user.id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Ideia não encontrada.")
    
    if req.title is not None:
        idea.title = req.title
    if req.description is not None:
        idea.description = req.description
    if req.status is not None:
        idea.status = req.status
    if req.channel is not None:
        idea.channel = req.channel
        
    db.commit()
    db.refresh(idea)
    log_activity(db, current_user.id, "update_idea", f"Ideia atualizada ID {idea_id}: status={idea.status}")
    return idea

@router.delete("/api/ideas/{idea_id}")
async def delete_idea(idea_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.id == idea_id, Idea.user_id == current_user.id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Ideia não encontrada.")
    
    title = idea.title
    db.delete(idea)
    db.commit()
    log_activity(db, current_user.id, "delete_idea", f"Ideia ID {idea_id} excluída (Título={title}).")
    return {"status": "success", "message": "Ideia excluída com sucesso."}

@router.post("/api/analyze-quality")
async def analyze_quality(req: AnalyzeQualityRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        config_data = db.query(AgentConfig).filter(AgentConfig.user_id == current_user.id).first()
        analysis = agent.analyze_post_quality(req.content, req.tone, config_data=config_data)
        return analysis
    except Exception as e:
        logger.error(f"Erro ao analisar qualidade do post para {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/metrics/insights")
async def get_metrics_insights(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    posts = db.query(PostHistory).filter(
        PostHistory.user_id == current_user.id,
        PostHistory.status == "success"
    ).order_by(PostHistory.timestamp.desc()).limit(30).all()
    
    posts_data = []
    for p in posts:
        posts_data.append({
            "content": p.content,
            "theme": p.theme,
            "likes": p.likes or 0,
            "reposts": p.reposts or 0,
            "replies": p.replies or 0
        })
        
    try:
        config_data = db.query(AgentConfig).filter(AgentConfig.user_id == current_user.id).first()
        insights = agent.generate_metrics_insights(posts_data, config_data=config_data)
        return insights
    except Exception as e:
        logger.error(f"Erro ao gerar insights de métricas para {current_user.id}: {e}")
        return {
            "insight_text": "Cadastre e ative um Servidor de Inteligência Artificial (LLM) nas Configurações para que o Pulse possa gerar insights automáticos sobre suas publicações.",
            "sugestoes": [
                "Configure o seu primeiro servidor na aba de Configurações",
                "Adicione redes sociais ativas para ver o engajamento",
                "Gere rascunhos na aba de Editor"
            ]
        }

