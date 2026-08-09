from app.agent import _detect_ai_cliches

def test_detect_ai_cliches_clean_human_text():
    human_post = "Hoje testei a migração de um banco SQLite para Postgres no ecossistema Python. A diferença de velocidade em queries complexas foi nítida."
    score = _detect_ai_cliches(human_post)
    assert score <= 5

def test_detect_ai_cliches_high_score_cliche():
    ai_cliche_post = "Desvende a jornada incrível e descubra como impulsionar seu potencial redefinindo o futuro digital! 🚀✨🔥 #ia #tech #futuro"
    score = _detect_ai_cliches(ai_cliche_post)
    assert score > 30

def test_detect_ai_cliches_excessive_emojis():
    text_with_many_emojis = "Post normal com muitos emojis 🎉😀🔥🚀💡✨"
    score = _detect_ai_cliches(text_with_many_emojis)
    assert score > 0
