from datetime import datetime
import random
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.database import get_db_session, AgentConfig, User, SocialAccount, log_failed_post, log_successful_post, log_draft_post, EditorialItem, PostHistory
from app import agent
from app.social.registry import get_social_network_client

logger = logging.getLogger(__name__)

# Inicializa o agendador em segundo plano
scheduler = BackgroundScheduler()

def run_automated_post(user_id: int):
    logger.info(f"Executando tarefa agendada de postagem automática para o usuário {user_id}...")
    
    with get_db_session() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            logger.warning(f"Postagem cancelada para {user_id}: Usuário inexistente ou inativo no sistema.")
            return
            
        from app.database import check_daily_post_limit
        if not check_daily_post_limit(db, user_id):
            logger.warning(f"Postagem cancelada para o usuário {user_id}: limite diário excedido.")
            log_failed_post(db, user_id, "Agendamento falhou: Limite diário de postagens excedido.", "N/A", "informativo")
            return
            
        config_data = user.agent_config
        if not config_data or not config_data.is_active or config_data.scheduling_mode != "recorrente":
            logger.warning(f"Postagem cancelada para {user_id}: Agente desativado ou modo não é recorrente.")
            return
            
        themes = [t.strip() for t in config_data.themes_csv.split(",") if t.strip()]
        tone = config_data.tone or "informativo"
        system_prompt = config_data.system_prompt
        requires_approval = config_data.requires_approval
        
        if not themes:
            logger.warning(f"Postagem cancelada para o usuário {user_id}: nenhum tema configurado.")
            log_failed_post(db, user_id, "Agendamento falhou: Nenhum tema cadastrado para gerar o post.", "N/A", tone)
            return
            
        # Busca contas conectadas e ativas do usuário para a plataforma selecionada
        selected_channel = config_data.channel or "bluesky"
        social_accounts = db.query(SocialAccount).filter(
            SocialAccount.user_id == user_id,
            SocialAccount.platform == selected_channel,
            SocialAccount.is_connected == True
        ).all()
        
        if not social_accounts:
            logger.warning(f"Postagem cancelada para o usuário {user_id}: nenhuma conta de {selected_channel} conectada.")
            log_failed_post(db, user_id, f"Agendamento falhou: Nenhuma conta de {selected_channel} ativa e conectada.", "N/A", tone)
            return

        theme = random.choice(themes)
        logger.info(f"Tema escolhido aleatoriamente para o usuário {user_id}: {theme}")
        
        try:
            # Gera o conteúdo do post com a IA
            content = agent.generate_post_content(theme, tone, system_prompt, config_data=config_data)
            logger.info(f"Conteúdo gerado via LangChain para o usuário {user_id}: '{content}'")
            
            # Avalia a qualidade do post gerado
            quality_score = None
            try:
                analysis = agent.analyze_post_quality(content, tone, config_data=config_data)
                quality_score = analysis.get("score_geral")
            except Exception as qa_err:
                logger.error(f"Erro ao avaliar qualidade do post gerado automaticamente: {qa_err}")

            if requires_approval:
                logger.info(f"Modo de aprovação ativo para o usuário {user_id}. Salvando como rascunho...")
                # Cria PostHistory do rascunho com o score de qualidade pré-calculado
                new_draft = PostHistory(
                    user_id=user_id,
                    status="draft",
                    theme=theme,
                    tone=tone,
                    content=content,
                    quality_score=quality_score
                )
                db.add(new_draft)
                db.commit()
                log_activity = db.query(User).first() # Avoid direct DB import loop helper
                from app.database import log_activity as db_log_activity
                db_log_activity(db, user_id, "post_draft_created", f"Rascunho criado. Tema: {theme}")
            else:
                # Publica em todas as contas sociais ativas conectadas pelo usuário
                for account in social_accounts:
                    try:
                        client = get_social_network_client(account.platform, account.encrypted_credentials)
                        resp = client.publish(content)
                        logger.info(f"Post publicado com sucesso no {account.platform} para o usuário {user_id}.")
                        log_successful_post(
                            db,
                            user_id,
                            content,
                            theme,
                            tone,
                            uri=resp.get("uri"),
                            cid=resp.get("cid"),
                            social_account_id=account.id,
                            quality_score=quality_score
                        )
                    except Exception as inner_err:
                        logger.error(f"Erro ao publicar no {account.platform} para {user_id}: {inner_err}")
                        log_failed_post(db, user_id, f"Falha ao publicar no {account.platform}: {inner_err}", theme, tone)
        except Exception as e:
            logger.error(f"Erro durante a postagem automática do usuário {user_id}: {e}")
            log_failed_post(db, user_id, str(e), theme, tone)

def check_due_editorial_posts():
    logger.info("Verificando posts do calendário editorial agendados para publicação...")
    
    with get_db_session() as db:
        # Busca itens do calendário pendentes e cuja data de agendamento já passou
        due_items = db.query(EditorialItem).filter(
            EditorialItem.status == "planejado",
            EditorialItem.scheduled_date <= datetime.utcnow()
        ).all()
        
        if not due_items:
            return
            
        logger.info(f"Encontrados {len(due_items)} posts planejados para publicação agora.")
        
        for item in due_items:
            try:
                user = db.query(User).filter(User.id == item.user_id).first()
                if not user or not user.is_active:
                    logger.warning(f"Item {item.id} ignorado: Usuário inativo ou inexistente.")
                    item.status = "falhou"
                    continue
                
                from app.database import check_daily_post_limit
                if not check_daily_post_limit(db, user.id):
                    logger.warning(f"Item {item.id} ignorado: Limite diário de posts excedido para o usuário {user.id}.")
                    log_failed_post(db, user.id, "Calendário falhou: Limite diário de postagens excedido.", item.theme)
                    item.status = "falhou"
                    continue
                
                config_data = user.agent_config
                if not config_data or not config_data.is_active or config_data.scheduling_mode != "personalizado":
                    logger.warning(f"Item {item.id} ignorado: Agente desativado ou modo não é personalizado.")
                    item.status = "falhou"
                    continue
                
                # Busca as contas conectadas do usuário para o canal específico do item
                social_accounts = db.query(SocialAccount).filter(
                    SocialAccount.user_id == user.id,
                    SocialAccount.platform == item.channel,
                    SocialAccount.is_connected == True
                ).all()
                
                if not social_accounts:
                    logger.warning(f"Item {item.id} ignorado: Nenhuma conta conectada para o canal {item.channel}.")
                    log_failed_post(db, user.id, f"Calendário falhou: nenhuma conta conectada para {item.channel}", item.theme)
                    item.status = "falhou"
                    continue
                
                # Prepara o prompt customizado
                tone = config_data.tone or "informativo"
                system_prompt = config_data.system_prompt or ""
                
                if item.is_manual:
                    content = item.manual_content or ""
                    logger.info(f"Usando conteúdo manual para item planejado {item.id}: '{content}'")
                    quality_score = None
                    try:
                        analysis = agent.analyze_post_quality(content, tone, config_data=config_data)
                        quality_score = analysis.get("score_geral")
                    except Exception as qa_err:
                        logger.error(f"Erro ao avaliar qualidade do post manual: {qa_err}")
                else:
                    # Se houver objetivo ou CTA, alimentamos a IA com estas informações adicionais
                    prompt_context = system_prompt
                    if item.objective or item.cta:
                        prompt_context += "\n\nDiretrizes de negócio para este post específico:"
                        if item.objective:
                            prompt_context += f"\n* Objetivo do post: {item.objective}"
                        if item.cta:
                            prompt_context += f"\n* Call to Action (CTA): {item.cta}"
                    
                    # Gera o conteúdo do post
                    content = agent.generate_post_content(item.theme, tone, prompt_context, config_data=config_data)
                    logger.info(f"Conteúdo gerado para item planejado {item.id}: '{content}'")
                    
                    # Avalia a qualidade do post gerado
                    quality_score = None
                    try:
                        analysis = agent.analyze_post_quality(content, tone, config_data=config_data)
                        quality_score = analysis.get("score_geral")
                    except Exception as qa_err:
                        logger.error(f"Erro ao avaliar qualidade do post do calendário: {qa_err}")

                # Se exigir aprovação manual, salva como rascunho
                if config_data.requires_approval:
                    new_post = PostHistory(
                        user_id=user.id,
                        status="draft",
                        theme=item.theme,
                        tone=tone,
                        content=content,
                        quality_score=quality_score
                    )
                    db.add(new_post)
                    db.flush()
                    
                    item.status = "em_producao"
                    item.post_history_id = new_post.id
                    logger.info(f"Item {item.id} salvo como rascunho com sucesso.")
                    from app.database import log_activity
                    log_activity(db, user.id, "post_draft_created", f"Rascunho criado a partir do calendário. Tema: {item.theme}")
                else:
                    # Publica em todas as contas conectadas deste canal
                    for account in social_accounts:
                        try:
                            client = get_social_network_client(account.platform, account.encrypted_credentials)
                            resp = client.publish(content)
                            
                            new_post = PostHistory(
                                user_id=user.id,
                                social_account_id=account.id,
                                status="success",
                                theme=item.theme,
                                tone=tone,
                                content=content,
                                uri=resp.get("uri"),
                                cid=resp.get("cid"),
                                quality_score=quality_score
                            )
                            db.add(new_post)
                            db.flush()
                            
                            item.status = "publicado"
                            item.post_history_id = new_post.id
                            
                            # Salva o arquivo markdown local
                            from app.database import save_post_to_markdown
                            save_post_to_markdown(content, item.theme, tone, user_id=user.id)
                            logger.info(f"Item {item.id} publicado com sucesso no {account.platform}.")
                            from app.database import log_activity
                            log_activity(db, user.id, "post_published", f"Post publicado a partir do calendário. Tema: {item.theme}")
                        except Exception as inner_err:
                            logger.error(f"Erro ao publicar item {item.id} no {account.platform}: {inner_err}")
                            log_failed_post(db, user.id, f"Falha ao publicar no {account.platform}: {inner_err}", item.theme, tone)
                            item.status = "falhou"
            except Exception as e:
                logger.error(f"Falha ao processar item do calendário {item.id}: {e}")
                item.status = "falhou"
                
        db.commit()

def sync_scheduler():
    # Garante que o job global do calendário está ativo
    if not scheduler.get_job("check_due_editorial_posts"):
        scheduler.add_job(
            check_due_editorial_posts,
            "interval",
            minutes=1,
            id="check_due_editorial_posts"
        )
        logger.info("Registrado job global do calendário check_due_editorial_posts.")

    # Sincroniza as configurações de agentes ativos com o scheduler em memória
    with get_db_session() as db:
        active_configs = db.query(AgentConfig).filter(
            AgentConfig.is_active == True,
            AgentConfig.scheduling_mode == "recorrente"
        ).all()
        
        active_user_ids = {cfg.user_id for cfg in active_configs}
        
        # Recupera todos os jobs correntes
        existing_jobs = scheduler.get_jobs()
        existing_job_ids = {job.id for job in existing_jobs}
        
        # Remove jobs obsoletos ou com intervalo modificado
        for job_id in existing_job_ids:
            if not job_id.startswith("posting_job_"):
                continue
            try:
                user_id = int(job_id.split("_")[-1])
            except ValueError:
                continue
                
            should_remove = False
            if user_id not in active_user_ids:
                should_remove = True
            else:
                cfg = next((c for c in active_configs if c.user_id == user_id), None)
                job = scheduler.get_job(job_id)
                if cfg and job:
                    interval_hours = cfg.interval_hours
                    job_interval_seconds = job.trigger.interval.total_seconds()
                    if int(job_interval_seconds) != interval_hours * 3600:
                        should_remove = True
            
            if should_remove:
                try:
                    scheduler.remove_job(job_id)
                    logger.info(f"Removido job obsoleto: {job_id}")
                except Exception as e:
                    logger.error(f"Erro ao remover job {job_id}: {e}")

        # Registra novos jobs para usuários ativados no modo recorrente
        for cfg in active_configs:
            job_id = f"posting_job_{cfg.user_id}"
            if not scheduler.get_job(job_id):
                user = db.query(User).filter(User.id == cfg.user_id).first()
                if user and user.is_active:
                    scheduler.add_job(
                        run_automated_post,
                        "interval",
                        hours=cfg.interval_hours,
                        id=job_id,
                        args=[cfg.user_id]
                    )
                    logger.info(f"Registrado job {job_id} com recorrência de {cfg.interval_hours} horas.")

