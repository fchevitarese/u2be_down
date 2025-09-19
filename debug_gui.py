#!/usr/bin/env python3

"""
Script de depuração para o U2Be Down
Este script cria logs detalhados para diagnosticar problemas de inicialização
"""

import logging
import sys
import traceback
from datetime import datetime


def setup_debug_logging():
    """Configura logging detalhado para debug"""
    log_file = f"/tmp/u2be_down_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("U2BeDownDebug")
    logger.info(f"=== DEBUG SESSION STARTED ===")
    logger.info(f"Log file: {log_file}")
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    
    return logger, log_file

def test_imports(logger):
    """Testa imports críticos um por um"""
    imports_to_test = [
        ("os", "import os"),
        ("sys", "import sys"),
        ("PyQt5.QtWidgets", "from PyQt5.QtWidgets import QApplication"),
        ("yt_dlp", "from yt_dlp import YoutubeDL"),
        ("config", "from config import load_config"),
        ("main (sem moviepy)", "import main"),
    ]
    
    for name, import_stmt in imports_to_test:
        try:
            logger.info(f"Testando import: {name}")
            exec(import_stmt)
            logger.info(f"✅ Import {name} OK")
        except Exception as e:
            logger.error(f"❌ Import {name} FALHOU: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")

def test_gui_init(logger):
    """Testa inicialização da GUI"""
    try:
        logger.info("Testando inicialização da GUI...")
        from PyQt5.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            logger.info("✅ QApplication criado com sucesso")
        else:
            logger.info("✅ QApplication já existe")
            
        return app
        
    except Exception as e:
        logger.error(f"❌ Falha na inicialização da GUI: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None

def main():
    """Função principal de debug"""
    logger, log_file = setup_debug_logging()
    
    try:
        # Testar imports
        test_imports(logger)
        
        # Testar GUI
        app = test_gui_init(logger)
        
        if app:
            logger.info("Tentando importar e inicializar GUI principal...")
            from gui import YouTubeDownloader
            
            window = YouTubeDownloader()
            window.show()
            
            logger.info("✅ GUI inicializada com sucesso!")
            logger.info("Iniciando loop de eventos...")
            
            sys.exit(app.exec_())
        else:
            logger.error("❌ Não foi possível inicializar a aplicação")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ ERRO CRÍTICO: {e}")
        logger.error(f"Traceback completo: {traceback.format_exc()}")
        print(f"\n\n=== ERRO CRÍTICO ===")
        print(f"Veja o log completo em: {log_file}")
        print(f"Erro: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
