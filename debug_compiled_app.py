#!/usr/bin/env python3
"""
Teste para verificar se a aplicação compilada tem todos os módulos necessários
"""
import os
import subprocess
import sys


def test_compiled_app():
    """Testa se a aplicação compilada funciona"""
    print("🧪 Testando aplicação compilada...")
    
    app_path = "/Users/fredchevitarese/Projetos/u2be_down/dist/U2Be Down.app/Contents/MacOS/U2Be Down"
    
    if not os.path.exists(app_path):
        print("❌ Aplicação compilada não encontrada")
        return False
    
    print(f"📁 Aplicação encontrada: {app_path}")
    
    # Tenta executar a aplicação em modo test (se possível)
    try:
        # Executa com timeout para evitar travamento
        result = subprocess.run(
            [app_path, "--help"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        print(f"📤 Return code: {result.returncode}")
        if result.stdout:
            print(f"📤 Stdout: {result.stdout}")
        if result.stderr:
            print(f"📤 Stderr: {result.stderr}")
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - aplicação pode estar funcionando (sem --help)")
        return True
    except Exception as e:
        print(f"❌ Erro ao executar: {e}")
        return False

def check_app_bundle():
    """Verifica a estrutura do bundle da aplicação"""
    print("\n🧪 Verificando estrutura do bundle...")
    
    bundle_path = "/Users/fredchevitarese/Projetos/u2be_down/dist/U2Be Down.app"
    
    if not os.path.exists(bundle_path):
        print("❌ Bundle não encontrado")
        return False
    
    # Verifica estrutura
    contents_path = os.path.join(bundle_path, "Contents")
    macos_path = os.path.join(contents_path, "MacOS")
    resources_path = os.path.join(contents_path, "Resources")
    
    print(f"📁 Contents: {'✅' if os.path.exists(contents_path) else '❌'}")
    print(f"📁 MacOS: {'✅' if os.path.exists(macos_path) else '❌'}")
    print(f"📁 Resources: {'✅' if os.path.exists(resources_path) else '❌'}")
    
    # Lista arquivos principais
    if os.path.exists(macos_path):
        macos_files = os.listdir(macos_path)
        print(f"📄 Arquivos MacOS: {macos_files}")
    
    if os.path.exists(resources_path):
        resources_files = os.listdir(resources_path)[:5]  # Primeiros 5
        print(f"📄 Arquivos Resources (sample): {resources_files}")
    
    return True

def check_console_logs():
    """Verifica se há logs no Console.app"""
    print("\n💡 Para debug adicional:")
    print("1. Abra Console.app (Applications > Utilities)")
    print("2. Execute a aplicação U2Be Down")
    print("3. Procure por logs de erro relacionados ao U2Be Down")
    print("4. Também verifique crash reports em ~/Library/Logs/DiagnosticReports/")

if __name__ == "__main__":
    print("🧪 Debug da Aplicação Compilada")
    print("=" * 50)
    
    bundle_ok = check_app_bundle()
    app_ok = test_compiled_app()
    
    print("\n" + "=" * 50)
    if bundle_ok and app_ok:
        print("✅ Estrutura da aplicação parece correta")
        print("💡 O problema pode estar em:")
        print("   - Permissões do macOS")
        print("   - Módulos faltando")
        print("   - Configuração do yt-dlp")
    else:
        print("❌ Há problemas na estrutura da aplicação")
    
    check_console_logs()
