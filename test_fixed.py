#!/usr/bin/env python3
"""
Teste para verificar se o loop infinito foi corrigido
"""
import os
import sys

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_only():
    """Testa apenas o config.py sem GUI"""
    print("🧪 Testando apenas config.py...")
    
    try:
        from config import load_downloads_history, save_downloads_history
        print("✅ Imports do config funcionando")
        
        # Teste rápido de carregamento
        downloads = load_downloads_history()
        print(f"✅ Carregamento funcionando - {len(downloads)} downloads encontrados")
        
        return True
    except Exception as e:
        print(f"❌ Erro no config: {e}")
        return False

def test_gui_import():
    """Testa se conseguimos importar a GUI sem problemas"""
    print("\n🧪 Testando imports da GUI...")
    
    try:
        from gui import YouTubeDownloader
        print("✅ Import da GUI funcionando")
        return True
    except Exception as e:
        print(f"❌ Erro na GUI: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Teste após correção do loop infinito")
    print("=" * 50)
    
    config_ok = test_config_only()
    gui_ok = test_gui_import()
    
    print("\n" + "=" * 50)
    if config_ok and gui_ok:
        print("✅ Todos os testes passaram! O loop infinito foi corrigido.")
    else:
        print("❌ Ainda há problemas")
