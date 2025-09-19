#!/usr/bin/env python3

"""
Script de diagnóstico básico para identificar problemas de importação
"""

import sys
import traceback


def test_basic_imports():
    """Testa imports básicos do projeto"""
    print("🔍 Testando imports básicos...")
    
    tests = [
        ("os", "import os"),
        ("sys", "import sys"),
        ("PyQt5", "import PyQt5"),
        ("PyQt5.QtWidgets", "from PyQt5.QtWidgets import QApplication"),
        ("yt_dlp", "import yt_dlp"),
        ("config", "import config"),
    ]
    
    results = []
    
    for name, import_stmt in tests:
        try:
            print(f"  Testando {name}...", end=" ")
            exec(import_stmt)
            print("✅ OK")
            results.append((name, True, None))
        except Exception as e:
            print(f"❌ ERRO: {e}")
            results.append((name, False, str(e)))
    
    return results

def test_main_import():
    """Testa import do main.py"""
    print("\n🔍 Testando import do main.py...")
    try:
        import main
        print("✅ main.py importado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao importar main.py: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_gui_import():
    """Testa import do gui.py"""
    print("\n🔍 Testando import do gui.py...")
    try:
        import gui
        print("✅ gui.py importado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao importar gui.py: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    print("🚀 Diagnóstico U2Be Down")
    print("========================")
    print(f"Python: {sys.version}")
    print(f"Platform: {sys.platform}")
    print()
    
    # Testar imports básicos
    basic_results = test_basic_imports()
    
    # Testar main
    main_ok = test_main_import()
    
    # Testar GUI apenas se main estiver OK
    if main_ok:
        gui_ok = test_gui_import()
    else:
        gui_ok = False
        print("\n⚠️  Pulando teste da GUI devido a erro no main.py")
    
    # Resumo
    print("\n📋 RESUMO DO DIAGNÓSTICO")
    print("=" * 40)
    
    failed_imports = [name for name, success, _ in basic_results if not success]
    
    if failed_imports:
        print(f"❌ Imports básicos falharam: {', '.join(failed_imports)}")
    else:
        print("✅ Todos os imports básicos funcionando")
    
    if main_ok:
        print("✅ main.py OK")
    else:
        print("❌ main.py com problemas")
    
    if gui_ok:
        print("✅ gui.py OK")
    else:
        print("❌ gui.py com problemas")
    
    if all([len(failed_imports) == 0, main_ok, gui_ok]):
        print("\n🎉 DIAGNÓSTICO: Todas as importações funcionando!")
        print("   O problema pode estar na inicialização da GUI ou multiprocessing.")
    else:
        print("\n🔧 DIAGNÓSTICO: Problemas de importação identificados.")
        print("   Resolva os imports antes de compilar.")

if __name__ == "__main__":
    main()
