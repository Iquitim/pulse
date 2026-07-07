import logging
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app import config
from app import database

logger = logging.getLogger(__name__)

def get_llm(config_data: Optional[database.AgentConfig], temperature: float = 0.7):
    provider = "gemini"
    model = "gemini-2.5-flash-lite"
    base_url = None
    api_key = None
    
    if config_data:
        from app.database import get_db_session, LLMServer
        
        user_id = None
        try:
            user_id = config_data.user_id
        except Exception:
            user_id = config_data.__dict__.get("user_id")
            
        active_server_found = False
        try:
            with get_db_session() as db:
                active_server = db.query(LLMServer).filter(
                    LLMServer.user_id == user_id,
                    LLMServer.is_active == True
                ).first()
                if active_server:
                    active_server_found = True
                    provider = active_server.provider
                    model = active_server.model
                    base_url = active_server.base_url
                    if active_server.api_key_encrypted:
                        from app.security import decrypt_value
                        try:
                            api_key = decrypt_value(active_server.api_key_encrypted)
                        except Exception as e:
                            logger.error(f"Erro ao decifrar chave de API do LLM do servidor ativo: {e}")
        except Exception as e:
            logger.error(f"Erro ao buscar servidor LLM ativo no banco de dados: {e}")
            
        if not active_server_found:
            raise ValueError("Nenhum servidor LLM ativo está configurado. Por favor, adicione e ative um servidor nas Configurações.")

    if provider == "gemini":
        if not api_key:
            raise ValueError("Chave de API do Gemini (GOOGLE_API_KEY) não foi configurada.")
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=temperature
        )
    elif provider in ("ollama", "openai_compatible"):
        from langchain_openai import ChatOpenAI
        if provider == "ollama":
            if not base_url:
                base_url = "http://localhost:11434/v1"
            if not api_key:
                api_key = "ollama"
                
        if not base_url:
            raise ValueError("Base URL do provedor OpenAI/Compatível é obrigatória.")
        if not api_key:
            raise ValueError("API Key do provedor OpenAI/Compatível é obrigatória.")
            
        return ChatOpenAI(
            model=model or "llama3",
            api_key=api_key,
            base_url=base_url,
            temperature=temperature
        )
    else:
        raise ValueError(f"Provedor '{provider}' desconhecido.")

def test_connection(provider: str, model: str, base_url: Optional[str], api_key: Optional[str]) -> bool:
    if provider == "gemini":
        if not api_key:
            raise ValueError("Chave de API do Gemini não fornecida.")
        llm = ChatGoogleGenerativeAI(
            model=model or "gemini-2.5-flash-lite",
            google_api_key=api_key,
            temperature=0.1
        )
    elif provider in ("ollama", "openai_compatible"):
        from langchain_openai import ChatOpenAI
        if provider == "ollama":
            if not base_url:
                base_url = "http://localhost:11434/v1"
            if not api_key:
                api_key = "ollama"
                
        if not base_url:
            raise ValueError("Base URL do provedor OpenAI/Compatível é obrigatória.")
        if not api_key:
            raise ValueError("API Key do provedor OpenAI/Compatível é obrigatória.")
            
        llm = ChatOpenAI(
            model=model or "llama3",
            api_key=api_key,
            base_url=base_url,
            temperature=0.1
        )
    else:
        raise ValueError(f"Provedor '{provider}' desconhecido.")
        
    res = llm.invoke("Responda com a palavra OK")
    return bool(res.content and len(res.content.strip()) > 0)

def generate_post_content(theme: str, tone: str, system_prompt: Optional[str] = None, idea_text: Optional[str] = None, config_data: Optional[database.AgentConfig] = None) -> str:
    persona = ""
    if config_data:
        persona = getattr(config_data, "persona_description", None) or database.DEFAULT_PERSONA_DESCRIPTION
        if not system_prompt:
            system_prompt = config_data.system_prompt
    else:
        if not system_prompt:
            system_prompt = database.DEFAULT_SYSTEM_PROMPT
        persona = getattr(database, "DEFAULT_PERSONA_DESCRIPTION", "")

    full_prompt = system_prompt or ""
    if persona:
        full_prompt += f"\n\nPersona (quem você representa):\n{persona}"

    llm = get_llm(config_data, temperature=0.7)
    
    if idea_text:
        original_theme = theme
        theme = f"a seguinte ideia bruta: '{idea_text}'"
        if original_theme and original_theme != "Geral" and original_theme != "random":
            theme += f" (relacionada ao tema '{original_theme}')"
        human_text = f"Escreva o post curto com base na ideia bruta fornecida, utilizando o tom '{tone}'."
    else:
        human_text = "Gere o post sobre o tema '{theme}' no tom '{tone}'."

    prompt = ChatPromptTemplate.from_messages([
        ("system", full_prompt),
        ("human", human_text)
    ])
    
    chain = prompt | llm | StrOutputParser()
    content = chain.invoke({"theme": theme, "tone": tone})
    
    clean_content = content.strip().strip('"').strip("'")
    if len(clean_content) > 280:
        clean_content = clean_content[:277] + "..."
        
    return clean_content

def _detect_ai_cliches(content: str) -> int:
    """
    Detecta clichês típicos de texto gerado por IA em português.
    Retorna uma pontuação de 0 (parece humano) a 100 (parece IA genérica).
    """
    import re
    text = content.lower()
    
    # Lista de palavras/expressões fortemente associadas a textos genéricos de IA
    ai_cliches = [
        r'\bdesvende\b', r'\bdesvendando\b', r'\bdesvendar\b',
        r'\brevolucion[aá]\w*\b', r'\btransformador\w*\b',
        r'\bjornada\b', r'\bimpulsion[ae]\w*\b', r'\balavanc[ae]\w*\b',
        r'\bpotencializ[ae]\w*\b', r'\bmaximiz[ae]\w*\b',
        r'\bincrível\b', r'\bincríveis\b',
        r'\bdescubra\s+como\b', r'\bvocê\s+sabia\s+que\b',
        r'\bimersão\b', r'\bimersivo\b',
        r'\bexplorando\b', r'\bexplore\s+o\b',
        r'\bnão\s+perca\b', r'\bnão\s+fique\s+de\s+fora\b',
        r'\bo\s+futuro\s+é\s+agora\b', r'\bo\s+poder\s+d[aoe]\b',
        r'\bgaranta\s+já\b', r'\btransform[ae]\w*\s+su[as]\b',
        r'\bredefin\w+\b', r'\binov[aá]\w+\b',
        r'\bvem\s+comigo\b', r'\bvem\s+conferir\b',
        r'\bsaiba\s+mais\b', r'\bconfira\s+agora\b',
        r'\bestá\s+pronto\b', r'\bestão\s+prontos\b',
        r'\bchave\s+para\s+o\s+sucesso\b', r'\bsegredo[s]?\s+(para|do|da)\b',
        r'\bpasso\s+a\s+passo\b', r'\bdicas\s+(imperdíveis|essenciais|valiosas)\b',
        r'\bmundo\s+(digital|corporativo|dos\s+negócios)\b',
        r'\bera\s+(digital|da\s+ia|da\s+inteligência)\b',
        r'\b(game|divisor)\s+(changer|de\s+águas)\b',
        r'\b(muito\s+)?mais\s+do\s+que\b',
    ]
    
    matches = 0
    for pattern in ai_cliches:
        found = re.findall(pattern, text)
        matches += len(found)
    
    # Contagem de emojis excessivos (3+ é sinal de IA genérica)
    emoji_count = len(re.findall(r'[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF]', content))
    if emoji_count >= 4:
        matches += 2
    elif emoji_count >= 3:
        matches += 1
    
    # Contagem de hashtags excessivas (3+ hashtags em post curto)
    hashtag_count = len(re.findall(r'#\w+', content))
    if hashtag_count >= 3:
        matches += 2
    elif hashtag_count >= 2:
        matches += 1
    
    # Escala: 0 matches = 0, 1 = 15, 2 = 35, 3 = 55, 4 = 70, 5+ = 85-100
    if matches == 0:
        return 5
    elif matches == 1:
        return 20
    elif matches == 2:
        return 40
    elif matches == 3:
        return 60
    elif matches == 4:
        return 75
    else:
        return min(100, 80 + (matches - 5) * 5)


def analyze_post_quality(content: str, tone: str, config_data: Optional[database.AgentConfig] = None) -> dict:
    llm = get_llm(config_data, temperature=0.3)
    
    system_msg = """Você é um avaliador de posts para redes sociais.
Avalie o post com notas de 0 a 100 para cada critério abaixo.

Retorne APENAS um JSON válido com esta estrutura exata, sem texto adicional:
{{
  "clareza": 80,
  "gancho": 75,
  "especificidade": 70,
  "tom": 85,
  "cta": 60,
  "sugestoes": [
    "Primeira recomendação de melhoria específica para o texto analisado",
    "Segunda recomendação de melhoria específica para o texto analisado"
  ]
}}

Critérios:
- clareza: Nota de 0 a 100 indicando se o texto é fácil de ler e entender.
- gancho: Nota de 0 a 100 indicando se a primeira frase prende a atenção.
- especificidade: Nota de 0 a 100 indicando se traz exemplos ou pontos concretos.
- tom: Nota de 0 a 100 indicando se está no tom '{tone}'.
- cta: Nota de 0 a 100 indicando se tem um convite natural para interação.
- sugestoes: Array contendo exatamente 2 sugestões personalizadas, práticas e reais de melhoria baseadas no texto fornecido. ATENÇÃO: Você DEVE gerar sugestões reais para o post do usuário, nunca repita ou use placeholders genéricos ou os textos do exemplo.
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        ("human", "Post para avaliar:\n\n{content}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    result_str = chain.invoke({"content": content, "tone": tone})
    
    # Limpar possíveis artefatos do LLM
    result_str = result_str.replace("```json", "").replace("```", "").strip()
    # Extrair apenas o JSON (tudo entre { e })
    import re
    json_match = re.search(r'\{[^{}]*\}', result_str, re.DOTALL)
    if json_match:
        result_str = json_match.group(0)
    
    try:
        import json
        data = json.loads(result_str)
        
        clareza = max(0, min(100, float(data.get("clareza", 50))))
        gancho = max(0, min(100, float(data.get("gancho", 50))))
        especificidade = max(0, min(100, float(data.get("especificidade", 50))))
        tom = max(0, min(100, float(data.get("tom", 50))))
        cta = max(0, min(100, float(data.get("cta", 50))))
        
        # Calcular 'generico' no backend via detecção de clichês,
        # pois modelos pequenos (ex: qwen2:1.5b) não conseguem avaliar isso.
        generico = _detect_ai_cliches(content)
        data["generico"] = generico
        
        # Média base dos atributos positivos
        base_score = (clareza + gancho + especificidade + tom + cta) / 5.0
        
        # Penalização proporcional ao fator genérico
        penalty_factor = 1.0 - (generico / 100.0)
        calculated_score = base_score * penalty_factor
        
        data["score_geral"] = max(0, min(100, int(round(calculated_score))))
        return data
    except Exception as e:
        logger.error(f"Erro ao analisar JSON de qualidade do post: {e}. Output bruto: {result_str}")
        generico = _detect_ai_cliches(content)
        base_fallback = 50
        penalty = 1.0 - (generico / 100.0)
        return {
            "clareza": 50,
            "gancho": 50,
            "especificidade": 50,
            "tom": 50,
            "generico": generico,
            "cta": 50,
            "score_geral": max(0, int(round(base_fallback * penalty))),
            "sugestoes": ["Não foi possível concluir a análise estruturada da IA. Tente novamente."]
        }

def generate_metrics_insights(posts_data: list, config_data: Optional[database.AgentConfig] = None) -> dict:
    llm = get_llm(config_data, temperature=0.4)
    
    formatted_posts = ""
    for idx, p in enumerate(posts_data):
        formatted_posts += f"Post {idx+1}:\n- Conteúdo: {p['content']}\n- Tema: {p['theme']}\n- Engajamento (Curtidas: {p['likes']}, Reposts: {p['reposts']}, Respostas: {p['replies']})\n\n"
        
    system_msg = """Você é um estrategista de mídias sociais e analista de conteúdo por IA.
Você receberá uma lista de posts recentes publicados pelo usuário com suas respectivas métricas de engajamento.
Sua tarefa é analisar os dados, correlacionar os temas e formular uma síntese de insights de desempenho com sugestões de novas publicações.

Retorne APENAS um JSON válido e estrito com a seguinte estrutura, sem explicações adicionais, sem blocos de código ```json e sem markdown:
{{
  "insight_text": "Sua análise detalhada em português descrevendo quais temas performaram melhor e o porquê (ex: 'Posts sobre Inteligência Artificial geraram 2x mais curtidas do que postagens genéricas de carreira...').",
  "sugestoes": [
    "Variação de Post 1 sobre o tema vencedor...",
    "Variação de Post 2 sobre o tema vencedor...",
    "Variação de Post 3 sobre o tema vencedor..."
  ]
}}
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        ("human", "Aqui estão os posts publicados e suas métricas:\n\n{formatted_posts}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    result_str = chain.invoke({"formatted_posts": formatted_posts})
    
    result_str = result_str.replace("```json", "").replace("```", "").strip()
    
    try:
        import json
        return json.loads(result_str)
    except Exception as e:
        logger.error(f"Erro ao analisar JSON de insights de métricas: {e}. Output bruto: {result_str}")
        return {
            "insight_text": "Nenhum histórico suficiente de engajamento detectado para formular insights analíticos ainda. Continue postando para alimentar a IA!",
            "sugestoes": [
                "Publique mais posts com CTAs de engajamento na aba de Calendário.",
                "Varie os temas cadastrados nas Configurações para testar o interesse da audiência.",
                "Experimente diferentes tons de voz (ex: corporativo vs informal) no Editor."
            ]
        }
