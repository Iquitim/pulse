import os
import platform
import subprocess
import shutil
import urllib.request
import threading
import time
import logging
import psutil

logger = logging.getLogger(__name__)

# Base directory for storing binaries
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = os.path.join(BASE_DIR, "bin")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Ensure folders exist
os.makedirs(BIN_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Portability releases of Ollama (v0.30.10)
OLLAMA_RELEASES = {
    "Linux": "https://github.com/ollama/ollama/releases/download/v0.30.10/ollama-linux-amd64.tar.zst",
    "Darwin": "https://github.com/ollama/ollama/releases/download/v0.30.10/ollama-darwin.tgz",
    "Windows": "https://github.com/ollama/ollama/releases/download/v0.30.10/ollama-windows-amd64.zip"
}

# Global install state
install_state = {
    "status": "idle",  # idle, downloading, extracting, completed, failed
    "downloaded_bytes": 0,
    "total_bytes": 0,
    "percentage": 0,
    "error": None
}

# Thread reference
_install_thread = None
_ollama_process = None

def get_install_state():
    return install_state

def detect_nvidia_gpu():
    nvidia_smi = shutil.which("nvidia-smi")
    if not nvidia_smi:
        return None
    try:
        res = subprocess.run(
            [nvidia_smi, "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            timeout=5
        )
        lines = res.stdout.strip().split("\n")
        if lines and lines[0]:
            parts = lines[0].split(",")
            gpu_name = parts[0].strip()
            vram_mb = float(parts[1].strip())
            return {"name": gpu_name, "vram_gb": round(vram_mb / 1024, 1)}
    except Exception as e:
        logger.error(f"Erro ao consultar nvidia-smi: {e}")
    return None

def detect_apple_silicon():
    return platform.system() == "Darwin" and platform.machine() == "arm64"

def get_hardware_report():
    system_os = platform.system()
    ram_gb = round(psutil.virtual_memory().total / (1024**3), 1)
    cpu_cores = psutil.cpu_count(logical=True)
    disk_free_gb = round(shutil.disk_usage(BASE_DIR).free / (1024**3), 1)

    gpu = detect_nvidia_gpu()
    is_mac_m1 = detect_apple_silicon()

    # Determine system tier
    if is_mac_m1:
        if ram_gb >= 16:
            tier = "Ultra"
            reason = "Apple Silicon com Memória Unificada ideal."
        else:
            tier = "High"
            reason = "Apple Silicon de 8GB. Excelente performance de GPU, mas RAM restrita."
    elif gpu:
        if gpu["vram_gb"] >= 8 and ram_gb >= 16:
            tier = "Ultra"
            reason = f"GPU dedicada NVIDIA {gpu['name']} com {gpu['vram_gb']}GB VRAM e RAM abundante."
        elif gpu["vram_gb"] >= 6:
            tier = "High"
            reason = f"GPU dedicada NVIDIA {gpu['name']} com {gpu['vram_gb']}GB VRAM."
        else:
            tier = "Mid"
            reason = f"GPU NVIDIA de entrada {gpu['name']} com {gpu['vram_gb']}GB VRAM."
    else:
        if ram_gb >= 16:
            tier = "Mid"
            reason = "Execução por CPU. Memória RAM ideal para rodar modelos leves."
        elif ram_gb >= 8:
            tier = "Low"
            reason = "Execução por CPU com RAM básica. Recomenda-se modelos ultraleves."
        else:
            tier = "Critico"
            reason = "Memória RAM extremamente baixa para IA local (menos de 8GB)."

    # Assess model compatibility
    models = [
        {
            "id": "qwen2:1.5b",
            "name": "Qwen 2 (1.5B)",
            "size": "900 MB",
            "required_ram": 4,
            "status": "excellent" if tier in ("Ultra", "High", "Mid") else "good",
            "status_label": "Excelente" if tier in ("Ultra", "High", "Mid") else "Bom",
            "speed_label": "🚀 Ultrarrápido (>30 tokens/s)" if tier in ("Ultra", "High") else "⚡ Rápido (~15 tokens/s)" if tier == "Mid" else "⚠️ Aceitável (~5-8 tokens/s)"
        },
        {
            "id": "phi3:3.8b",
            "name": "Phi 3 (3.8B)",
            "size": "2.2 GB",
            "required_ram": 6,
            "status": "excellent" if tier in ("Ultra", "High") else "good" if tier == "Mid" else "slow" if tier == "Low" else "unsupported",
            "status_label": "Excelente" if tier in ("Ultra", "High") else "Bom" if tier == "Mid" else "Lento" if tier == "Low" else "Não recomendado",
            "speed_label": "🚀 Ultrarrápido (>20 tokens/s)" if tier in ("Ultra", "High") else "⚡ Rápido (~5-10 tokens/s)" if tier == "Mid" else "⚠️ Lento (~2-4 tokens/s)" if tier == "Low" else "❌ Risco de travamento"
        },
        {
            "id": "llama3:latest",
            "name": "Llama 3 (8B)",
            "size": "4.7 GB",
            "required_ram": 12,
            "status": "excellent" if tier in ("Ultra", "High") else "slow" if tier == "Mid" else "unsupported",
            "status_label": "Excelente" if tier in ("Ultra", "High") else "Lento" if tier == "Mid" else "Incompatível",
            "speed_label": "🚀 Excelente (>15 tokens/s)" if tier in ("Ultra", "High") else "⚠️ Lento (~1-3 tokens/s)" if tier == "Mid" else "❌ Incompatível (Lentidão extrema)"
        },
        {
            "id": "gemma2:latest",
            "name": "Gemma 2 (9B)",
            "size": "5.5 GB",
            "required_ram": 14,
            "status": "excellent" if tier in ("Ultra", "High") else "slow" if tier == "Mid" else "unsupported",
            "status_label": "Excelente" if tier in ("Ultra", "High") else "Lento" if tier == "Mid" else "Incompatível",
            "speed_label": "🚀 Excelente (>12 tokens/s)" if tier in ("Ultra", "High") else "⚠️ Lento (~1-2 tokens/s)" if tier == "Mid" else "❌ Incompatível (Lentidão extrema)"
        }
    ]

    # Select best model recommendation
    if tier == "Ultra":
        recommended_model = "llama3:latest"
        recommended_reason = "Seu computador suporta perfeitamente o Llama 3 (8B) com aceleração gráfica."
    elif tier == "High":
        recommended_model = "phi3:3.8b"
        recommended_reason = "Seu setup tem excelente GPU mas RAM restrita, o Phi 3 (3.8B) rodará de forma impecável."
    elif tier == "Mid":
        recommended_model = "phi3:3.8b"
        recommended_reason = "Sem aceleração gráfica ideal. O Phi 3 em CPU apresenta ótimo equilíbrio de qualidade."
    else:
        recommended_model = "qwen2:1.5b"
        recommended_reason = "Recursos de RAM modestos. O modelo Qwen 2 (1.5B) é superleve e rápido."

    return {
        "os": system_os,
        "ram_gb": ram_gb,
        "cpu_cores": cpu_cores,
        "disk_free_gb": disk_free_gb,
        "gpu": gpu,
        "apple_silicon": is_mac_m1,
        "tier": tier,
        "reason": reason,
        "models": models,
        "recommended_model": recommended_model,
        "recommended_reason": recommended_reason
    }

def check_local_ollama_running(url="http://localhost:11434"):
    import requests
    try:
        res = requests.get(url, timeout=2)
        return res.status_code == 200 or "Ollama is running" in res.text
    except Exception:
        return False

def _download_and_extract_thread():
    global install_state
    system_os = platform.system()
    if system_os not in OLLAMA_RELEASES:
        install_state["status"] = "failed"
        install_state["error"] = f"Sistema operacional {system_os} não é suportado pelo instalador portátil."
        return

    release_url = OLLAMA_RELEASES[system_os]
    ext = ".tar.zst" if system_os == "Linux" else (".tgz" if system_os == "Darwin" else ".zip")
    archive_path = os.path.join(BIN_DIR, f"ollama_archive{ext}")
    extract_dest = os.path.join(BIN_DIR, "ollama_extracted")

    try:
        # Step 1: Download
        install_state["status"] = "downloading"
        install_state["downloaded_bytes"] = 0
        install_state["percentage"] = 0
        logger.info(f"Iniciando download do Ollama portátil: {release_url}")

        req = urllib.request.Request(release_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            install_state["total_bytes"] = int(response.headers.get('content-length', 0))
            bytes_downloaded = 0
            chunk_size = 512 * 1024  # 512 KB chunks
            
            with open(archive_path, "wb") as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    bytes_downloaded += len(chunk)
                    install_state["downloaded_bytes"] = bytes_downloaded
                    if install_state["total_bytes"] > 0:
                        install_state["percentage"] = int((bytes_downloaded / install_state["total_bytes"]) * 100)
                    else:
                        install_state["percentage"] = 0

        logger.info("Download concluído com sucesso. Iniciando extração...")
        install_state["status"] = "extracting"

        # Step 2: Extract
        os.makedirs(extract_dest, exist_ok=True)

        if ext == ".zip":
            import zipfile
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dest)
        elif ext == ".tgz":
            import tarfile
            with tarfile.open(archive_path, 'r:gz') as tar_ref:
                tar_ref.extractall(extract_dest)
        elif ext == ".tar.zst":
            # For Linux, zstandard is not in standard library, so we invoke native system tar since we verified it is present.
            tar_cmd = ["tar", "--zstd", "-xf", archive_path, "-C", extract_dest]
            res = subprocess.run(tar_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode != 0:
                raise Exception(f"Erro ao extrair tar.zst via terminal: {res.stderr}")

        # Remove archive to save space
        if os.path.exists(archive_path):
            os.remove(archive_path)

        # Grant execution permissions for Linux/macOS
        if system_os in ("Linux", "Darwin"):
            binary_path = get_embedded_binary_path()
            if binary_path and os.path.exists(binary_path):
                os.chmod(binary_path, 0o755)

        logger.info("Extração concluída com sucesso.")
        install_state["status"] = "completed"
        install_state["percentage"] = 100

    except Exception as e:
        logger.error(f"Erro na instalação do Ollama portátil: {e}")
        install_state["status"] = "failed"
        install_state["error"] = str(e)

def start_install():
    global _install_thread, install_state
    if install_state["status"] == "downloading" or install_state["status"] == "extracting":
        return False
    install_state = {
        "status": "idle",
        "downloaded_bytes": 0,
        "total_bytes": 0,
        "percentage": 0,
        "error": None
    }
    _install_thread = threading.Thread(target=_download_and_extract_thread, daemon=True)
    _install_thread.start()
    return True

def get_embedded_binary_path():
    system_os = platform.system()
    extract_dest = os.path.join(BIN_DIR, "ollama_extracted")
    if system_os == "Windows":
        return os.path.join(extract_dest, "ollama.exe")
    elif system_os == "Darwin":
        # On macOS, it extracts to Ollamaapp structure or direct binary
        # Let's check typical binary path or search for 'ollama' executable inside.
        direct = os.path.join(extract_dest, "ollama")
        if os.path.exists(direct):
            return direct
        # In case it extracts Ollama.app
        app_bin = os.path.join(extract_dest, "Ollama.app", "Contents", "Resources", "ollama")
        if os.path.exists(app_bin):
            return app_bin
        return direct
    else:  # Linux
        # Typical tar.zst structure contains bin/ollama
        return os.path.join(extract_dest, "bin", "ollama")

def is_embedded_installed():
    binary = get_embedded_binary_path()
    return binary is not None and os.path.exists(binary)

def get_pid_file_path():
    return os.path.join(BIN_DIR, "ollama.pid")

def get_running_embedded_pid():
    pid_file = get_pid_file_path()
    if os.path.exists(pid_file):
        try:
            with open(pid_file, "r") as f:
                pid = int(f.read().strip())
                # Check if process is still running and is indeed ollama
                if psutil.pid_exists(pid):
                    proc = psutil.Process(pid)
                    if "ollama" in proc.name().lower():
                        return pid
        except Exception:
            pass
    return None

def start_embedded_ollama():
    global _ollama_process
    if check_local_ollama_running():
        logger.info("Ollama local já está rodando. Nenhuma necessidade de iniciar versão embutida.")
        return True

    binary = get_embedded_binary_path()
    if not binary or not os.path.exists(binary):
        logger.error("Binário do Ollama embutido não encontrado para execução.")
        return False

    running_pid = get_running_embedded_pid()
    if running_pid:
        logger.info(f"Ollama embutido já está rodando no processo PID: {running_pid}")
        return True

    log_file_path = os.path.join(LOGS_DIR, "ollama.log")
    logger.info(f"Iniciando Ollama embutido a partir de {binary} (Logs em {log_file_path})")

    try:
        log_file = open(log_file_path, "a")
        
        # Configure model storage folder locally in workspace
        env = os.environ.copy()
        env["OLLAMA_MODELS"] = os.path.join(BASE_DIR, "models")
        os.makedirs(env["OLLAMA_MODELS"], exist_ok=True)
        
        # Start server subprocess
        _ollama_process = subprocess.Popen(
            [binary, "serve"],
            stdout=log_file,
            stderr=log_file,
            env=env,
            start_new_session=True  # Separate process group so it lives on
        )
        
        # Write PID to file
        with open(get_pid_file_path(), "w") as f:
            f.write(str(_ollama_process.pid))

        # Wait for startup (up to 5 seconds)
        for _ in range(10):
            time.sleep(0.5)
            if check_local_ollama_running():
                logger.info("Ollama embutido iniciado e respondendo na porta 11434!")
                return True
        
        logger.warning("Ollama embutido iniciado, mas não respondeu na porta no tempo limite.")
        return False
    except Exception as e:
        logger.error(f"Erro ao iniciar processo Ollama: {e}")
        return False

def stop_embedded_ollama():
    global _ollama_process
    pid = get_running_embedded_pid()
    if not pid:
        logger.info("Nenhuma instância ativa do Ollama embutido encontrada para encerrar.")
        return False

    logger.info(f"Encerrando Ollama embutido no PID {pid}...")
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        # Wait up to 3 seconds for clean exit
        for _ in range(6):
            time.sleep(0.5)
            if not psutil.pid_exists(pid):
                break
        else:
            proc.kill()
        
        # Clean PID file
        pid_file = get_pid_file_path()
        if os.path.exists(pid_file):
            os.remove(pid_file)
            
        logger.info("Ollama embutido encerrado.")
        return True
    except Exception as e:
        logger.error(f"Erro ao parar processo Ollama: {e}")
        return False
