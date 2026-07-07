# Guia de Contribuição — Pulse

Agradecemos o seu interesse em contribuir para o **Pulse**! Este é um projeto de código aberto mantido pela comunidade e para a comunidade. Toda ajuda com reporte de bugs, novas funcionalidades, melhorias na interface ou criação de novos conectores de redes sociais é muito bem-vinda.

---

## 🚀 Como Configurar o Ambiente de Desenvolvimento

Para começar a contribuir localmente:

1. **Faça um Fork do repositório** e clone-o em sua máquina local.
2. **Crie um ambiente virtual** com Python 3.12 (ou superior):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Instale as dependências** de desenvolvimento:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure seu arquivo de ambiente**:
   - Copie o arquivo `.env.example` para `.env`.
   - Adicione suas credenciais do Gemini (Google AI) e configure as chaves de teste.
5. **Rode o servidor localmente**:
   - Execute o script `app.py`:
     ```bash
     python app.py
     ```
   - O painel estará disponível em [http://localhost:8000](http://localhost:8000).

---

## 🔌 Como Contribuir com Novos Conectores Sociais

A arquitetura de integração do Pulse foi projetada para ser modular e extensível. Se você quer adicionar suporte a uma nova rede social (ex: Mastodon, Threads, etc.), siga estes passos:

### 1. Criar a classe do Conector
Crie um novo arquivo no diretório `app/social/` (ex: `app/social/mastodon.py`) herdando da classe base `BaseSocialNetwork` (em `app/social/base.py`) e implemente os métodos obrigatórios:

```python
from app.social.base import BaseSocialNetwork

class MastodonConnector(BaseSocialNetwork):
    def connect(self) -> bool:
        """
        Estabelece a conexão com a rede social usando as credenciais decifradas.
        Retorna True se a conexão for bem-sucedida, False caso contrário.
        """
        # Exemplo: inicializar cliente Mastodon
        pass

    def post(self, content: str) -> bool:
        """
        Envia uma publicação de texto.
        Retorna True se publicado com sucesso, False em caso de falha.
        """
        # Exemplo: fazer postagem na API do Mastodon
        pass
```

### 2. Registrar o Conector no Registry
Abra o arquivo `app/social/registry.py` e registre a sua nova rede social no dicionário `SOCIAL_NETWORK_REGISTRY`:

```python
from app.social.mastodon import MastodonConnector

SOCIAL_NETWORK_REGISTRY = {
    "bluesky": BlueskyConnector,
    "twitter": TwitterConnector,
    "threads": ThreadsConnector,
    "mastodon": MastodonConnector,  # Seu novo conector aqui
}
```

### 3. Interface de Credenciais
No componente `templates/components/tab_config.html`, adicione a seção de formulário correspondente para salvar as credenciais e habilitar o novo canal no painel de conexões de contas sociais.

---

## 🤝 Processo de Pull Request

1. Crie uma branch para a sua feature ou correção (`git checkout -b feature/minha-melhoria`).
2. Faça commit de suas alterações com mensagens claras e objetivas.
3. Certifique-se de que os testes locais estão passando e de que o código segue as diretrizes do projeto.
4. Abra um Pull Request detalhando o que foi feito, as motivações da mudança e como o revisor pode testá-la.
