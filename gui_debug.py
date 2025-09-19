#!/usr/bin/env python3
"""
Versão debug da GUI para identificar onde está o problema
"""
import logging
import os
import sys

# Configurar logging para mostrar debug info
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication

from gui import YouTubeDownloader


class DebugYouTubeDownloader(YouTubeDownloader):
    """Versão debug do downloader com logs extras"""
    
    def start_download(self):
        """Versão debug do start_download com logs extras"""
        print("🐛 DEBUG: start_download chamado!")
        
        urls_text = self.url_text.toPlainText().strip()
        print(f"🐛 DEBUG: URLs inseridas: '{urls_text}'")
        
        if not urls_text:
            print("🐛 DEBUG: Nenhuma URL inserida - mostrando warning")
            return super().start_download()

        output_path = self.path_label.text()
        print(f"🐛 DEBUG: Caminho de download: '{output_path}'")
        
        if not output_path:
            print("🐛 DEBUG: Nenhum caminho selecionado - mostrando warning")
            return super().start_download()

        urls = [url.strip() for url in urls_text.split("\n") if url.strip()]
        print(f"🐛 DEBUG: URLs processadas: {urls}")

        print("🐛 DEBUG: Iniciando parse thread...")
        return super().start_download()

    def on_parse_finished_for_download(self, videos):
        """Versão debug do callback"""
        print(f"🐛 DEBUG: Parse terminou! {len(videos)} vídeos encontrados:")
        for i, video in enumerate(videos):
            print(f"   {i+1}. {video.get('title', 'N/A')}")
        
        return super().on_parse_finished_for_download(videos)

    def on_parse_error_for_download(self, error_msg):
        """Versão debug do callback de erro"""
        print(f"🐛 DEBUG: Erro no parse: {error_msg}")
        return super().on_parse_error_for_download(error_msg)

if __name__ == "__main__":
    print("🐛 Iniciando GUI em modo DEBUG")
    print("=" * 50)
    print("📝 Instruções:")
    print("1. Cole um link do YouTube na caixa de texto")
    print("2. Verifique se há uma pasta selecionada")
    print("3. Clique em 'Iniciar Download'")
    print("4. Observe os logs de debug aqui no terminal")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    window = DebugYouTubeDownloader()
    window.show()
    sys.exit(app.exec_())
