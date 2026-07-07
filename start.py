import os
import sys
import subprocess
import secrets
import base64
import shutil

# Script de Inicialização Universal e Agnóstica para o Pulse
# Funciona de forma idêntica no Windows, macOS e Linux.

def main():
    print("=" * 80)
    print("         🚀 Inicializador Universal de Instância do Pulse 🚀")
    print("=" * 80)

    # 1. Determinar caminhos de executáveis com base no OS
    is_windows = os.name == 'nt'
    venv_dir = "venv"

    if is_windows:
        python_bin = os.path.join(venv_dir, "Scripts", "python.exe")
        pip_bin = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        python_bin = os.path.join(venv_dir, "bin", "python")
        pip_bin = os.path.join(venv_dir, "bin", "pip")

    # 2. Criar Virtualenv caso não exista
    if not os.path.exists(venv_dir):
        print("[1/4] Criando ambiente virtual Python (venv)...")
        try:
            subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
            print("✓ Ambiente virtual criado com sucesso.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao criar ambiente virtual: {e}")
            sys.exit(1)
    else:
        print("[✓] Ambiente virtual detectado.")

    # 3. Instalar/atualizar dependências
    print("[2/4] Instalando dependências (requirements.txt)...")
    try:
        subprocess.run([pip_bin, "install", "--upgrade", "pip"], check=True)
        subprocess.run([pip_bin, "install", "-r", "requirements.txt"], check=True)
        print("✓ Dependências instaladas com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        sys.exit(1)

    # 4. Configurar arquivo .env de forma segura
    if not os.path.exists(".env"):
        print("[3/4] Arquivo .env não encontrado. Gerando a partir do .env.example...")
        if os.path.exists(".env.example"):
            try:
                shutil.copy(".env.example", ".env")
                
                # Gerar chaves seguras dinamicamente usando módulos padrões do Python
                jwt_key = secrets.token_hex(32)
                # Chave Base64 compatível com Fernet
                fernet_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
                
                with open(".env", "r", encoding="utf-8") as f:
                    content = f.read()
                
                content = content.replace("your_secure_random_jwt_secret_key_minimum_32_chars", jwt_key)
                content = content.replace("your_fernet_encryption_key_base64_format", fernet_key)
                
                with open(".env", "w", encoding="utf-8") as f:
                    f.write(content)
                
                print("✓ Arquivo .env configurado com chaves geradas automaticamente.")
            except Exception as e:
                print(f"❌ Erro ao configurar o .env: {e}")
                sys.exit(1)
        else:
            print("⚠️ Alerta: Arquivo .env.example não foi encontrado para cópia inicial.")
    else:
        print("[✓] Arquivo .env detectado.")

    # 5. Exibir credenciais padrão
    print("=" * 80)
    print("🔑 CREDENCIAIS PADRÃO DE PRIMEIRO ACESSO:")
    print("   E-mail: admin@pulse.com")
    print("   Senha:  admin123")
    print("   Código de Convite: PULSE-OPEN-SOURCE")
    print("   Acesse o painel em: http://localhost:8000")
    print("=" * 80)

    # 6. Iniciar o servidor FastAPI
    print("[4/4] Iniciando servidor do Pulse...")
    try:
        # Roda o app.py do projeto usando o interpretador do venv
        subprocess.run([python_bin, "app.py"])
    except KeyboardInterrupt:
        print("\nServidor finalizado pelo usuário.")
    except Exception as e:
        print(f"❌ Erro ao iniciar o servidor: {e}")

if __name__ == "__main__":
    main()
