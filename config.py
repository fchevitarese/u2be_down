import json
import logging
import os
import threading
from datetime import datetime

CONFIG_FILE = "config.json"
DOWNLOADS_HISTORY_FILE = "downloads_history.json"

# Lock para proteger acesso ao arquivo JSON
_file_lock = threading.Lock()

# Configurar logging específico para debug
debug_logger = logging.getLogger("downloads_debug")
debug_logger.setLevel(logging.DEBUG)

# Adicionar handler se ainda não existir
if not debug_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    debug_logger.addHandler(handler)


def get_default_config():
    """Retorna a configuração padrão"""
    return {
        "default_download_path": "/home/fred/Músicas/Downloads",
        "logging_enabled": True,
        "auto_convert_to_mp3": True,
        "keep_video": False,
    }


def load_config():
    """Carrega a configuração do arquivo"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as file:
                config = json.load(file)
                # Merge com config padrão para garantir que todos os campos existam
                default_config = get_default_config()
                default_config.update(config)
                return default_config
        except (json.JSONDecodeError, Exception):
            return get_default_config()
    return get_default_config()


def save_config(config):
    """Salva a configuração no arquivo"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=2, ensure_ascii=False)


def load_downloads_history():
    """Carrega o histórico de downloads do arquivo JSON"""
    with _file_lock:  # Proteger acesso ao arquivo
        if os.path.exists(DOWNLOADS_HISTORY_FILE):
            try:
                with open(DOWNLOADS_HISTORY_FILE, "r", encoding="utf-8") as file:
                    downloads = json.load(file)
                    return downloads
            except Exception as e:
                debug_logger.error(f"❌ LOAD_HISTORY: Erro ao carregar histórico: {e}")
                logging.error(f"❌ LOAD_HISTORY: Erro ao carregar histórico: {e}")

        debug_logger.info("🔍 LOAD_HISTORY: Arquivo não existe, retornando lista vazia")
        logging.info("🔍 LOAD_HISTORY: Arquivo não existe, retornando lista vazia")
        return []


def save_downloads_history(downloads):
    """Salva o histórico de downloads no arquivo JSON"""
    with _file_lock:  # Proteger acesso ao arquivo
        try:
            with open(DOWNLOADS_HISTORY_FILE, "w", encoding="utf-8") as file:
                json.dump(downloads, file, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Erro ao salvar histórico: {e}")


def add_download_to_history(title, url, file_path="", status="pending"):
    """Adiciona um download ao histórico com logs detalhados"""
    debug_logger.info(f"➕ ADD_DOWNLOAD: Adicionando '{title}' com status '{status}'")

    downloads = load_downloads_history()

    # Verifica se já existe
    existing = None
    for download in downloads:
        if download["url"] == url:
            existing = download
            break

    if existing:
        debug_logger.info(
            f"➕ ADD_DOWNLOAD: URL já existe, status atual: {existing.get('status')}"
        )
        if existing.get("status") != status:
            debug_logger.info(
                f"➕ ADD_DOWNLOAD: Atualizando status de {existing.get('status')} para {status}"
            )
            existing["status"] = status
        return

    download_entry = {
        "title": title,
        "url": url,
        "file_path": file_path,
        "status": status,
        "timestamp": datetime.now().isoformat(),
    }

    downloads.append(download_entry)
    debug_logger.info(
        f"➕ ADD_DOWNLOAD: Nova entrada adicionada. Total agora: {len(downloads)}"
    )

    save_downloads_history(downloads)


def update_download_status(url, status, file_path=None, error_msg=None):
    """Atualiza o status de um download no histórico com logs detalhados"""
    debug_logger.info(f"🔄 UPDATE_STATUS: URL={url[:50]}... Status={status}")

    downloads = load_downloads_history()
    found = False

    for download in downloads:
        if download["url"] == url:
            old_status = download.get("status", "unknown")
            download["status"] = status
            if file_path:
                download["file_path"] = file_path
            if error_msg:
                download["error_message"] = error_msg
            found = True
            debug_logger.info(f"🔄 UPDATE_STATUS: Encontrado! {old_status} → {status}")
            break

    if not found:
        debug_logger.warning(f"⚠️ UPDATE_STATUS: URL não encontrada no histórico!")

    save_downloads_history(downloads)


def clear_completed_downloads():
    """Remove downloads concluídos do histórico com logs detalhados"""
    debug_logger.info("🧹 CLEAR_COMPLETED: Iniciando limpeza de downloads concluídos")

    downloads = load_downloads_history()
    original_count = len(downloads)
    completed_count = len([d for d in downloads if d["status"] == "completed"])

    downloads = [d for d in downloads if d["status"] != "completed"]
    final_count = len(downloads)

    debug_logger.info(
        f"🧹 CLEAR_COMPLETED: {original_count} → {final_count} (removidos {completed_count} concluídos)"
    )

    save_downloads_history(downloads)
    return downloads


def clear_all_downloads():
    """Remove todos os downloads do histórico com logs detalhados"""
    debug_logger.info("🧹 CLEAR_ALL: Removendo TODOS os downloads do histórico")

    downloads = load_downloads_history()
    original_count = len(downloads)

    save_downloads_history([])

    debug_logger.info(f"🧹 CLEAR_ALL: {original_count} downloads removidos")
    return []


def clear_failed_downloads():
    """Remove downloads com falha do histórico com logs detalhados"""
    debug_logger.info("🧹 CLEAR_FAILED: Iniciando limpeza de downloads falhados")

    downloads = load_downloads_history()
    original_count = len(downloads)
    failed_count = len([d for d in downloads if d["status"] == "failed"])

    downloads = [d for d in downloads if d["status"] != "failed"]
    final_count = len(downloads)

    debug_logger.info(
        f"🧹 CLEAR_FAILED: {original_count} → {final_count} (removidos {failed_count} falhados)"
    )

    save_downloads_history(downloads)
    return downloads
