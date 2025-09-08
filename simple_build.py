#!/usr/bin/env python3
"""
Build Simples - U2Be Down
Versão simplificada para gerar apenas o executável
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path


def run_cmd(cmd):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, str(e)


def main():
    print("🔨 Build Simples - U2Be Down")
    print("=" * 40)
    
    # Verificar se estamos no diretório correto
    if not Path('main.py').exists():
        print("❌ main.py não encontrado!")
        print("Execute no diretório do projeto.")
        return False
    
    print("📦 Instalando PyInstaller...")
    success, _ = run_cmd("pip install pyinstaller")
    if not success:
        print("❌ Erro ao instalar PyInstaller")
        return False
    
    print("📦 Instalando dependências...")
    success, _ = run_cmd("pip install -r requirements.txt")
    if not success:
        print("⚠️  Aviso: Algumas dependências podem ter falhado")
    
    print("🔨 Criando executável...")
    
    # Comando PyInstaller básico
    cmd = [
        "pyinstaller",
        "--onefile",
        "--console", 
        "--name=u2be_down",
        "main.py"
    ]
    
    # Adicionar dados se existirem
    if Path('config.json').exists():
        cmd.extend(["--add-data", "config.json:."])
    
    if Path('assets').exists():
        cmd.extend(["--add-data", "assets:assets"])
    
    # Executar PyInstaller
    success, output = run_cmd(" ".join(cmd))
    if not success:
        print(f"❌ Erro no build: {output}")
        return False
    
    # Verificar se o executável foi criado
    if platform.system() == "Windows":
        exe_path = Path("dist/u2be_down.exe")
    else:
        exe_path = Path("dist/u2be_down")
    
    if exe_path.exists():
        print(f"✅ Executável criado: {exe_path}")
        print(f"📏 Tamanho: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
        
        # Criar diretório de release
        release_dir = Path("release")
        release_dir.mkdir(exist_ok=True)
        
        # Copiar executável
        shutil.copy2(exe_path, release_dir / exe_path.name)
        
        # Copiar arquivos adicionais
        if Path('config.json').exists():
            shutil.copy2('config.json', release_dir)
        
        if Path('assets').exists():
            shutil.copytree('assets', release_dir / 'assets', dirs_exist_ok=True)
        
        print(f"📁 Arquivos copiados para: {release_dir}")
        print("\n🎉 Build concluído com sucesso!")
        return True
    else:
        print("❌ Executável não encontrado")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
