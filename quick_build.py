#!/usr/bin/env python3
"""
Quick Installer Builder for U2Be Down
Script simplificado para gerar instaladores
"""

import os
import sys
import subprocess
import platform
import tempfile
import shutil
from pathlib import Path


def run_command(cmd, cwd=None):
    """Execute command and return success status"""
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True, cwd=cwd
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def check_dependencies():
    """Check if required tools are available"""
    print("🔍 Verificando dependências...")

    # Check Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é necessário")
        return False

    # Check pip
    success, _ = run_command("pip --version")
    if not success:
        success, _ = run_command("pip3 --version")
        if not success:
            print("❌ pip não encontrado")
            return False

    print("✅ Dependências básicas OK")
    return True


def install_build_deps():
    """Install build dependencies"""
    print("📦 Instalando dependências de build...")

    commands = [
        "pip install --upgrade pip",
        "pip install pyinstaller",
        "pip install -r requirements.txt",
    ]

    for cmd in commands:
        print(f"  Executando: {cmd}")
        success, output = run_command(cmd)
        if not success:
            print(f"❌ Erro: {output}")
            return False

    print("✅ Dependências instaladas")
    return True


def create_pyinstaller_spec():
    """Create PyInstaller spec file"""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

# Collect assets
assets_data = []
if os.path.exists('assets'):
    assets_data.append(('assets', 'assets'))
if os.path.exists('config.json'):
    assets_data.append(('config.json', '.'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=assets_data,
    hiddenimports=[
        'PIL._tkinter_finder',
        'moviepy.video.io.ffmpeg_tools',
        'moviepy.audio.io.ffmpeg_audiowriter',
        'pygame',
        'mutagen',
        'librosa',
        'soundfile',
        'scipy',
        'numpy',
        'imageio_ffmpeg',
        'concurrent.futures',
        'threading',
        'queue',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Determine executable extension
exe_name = 'u2be_down'
if os.name == 'nt':
    exe_name += '.exe'

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=exe_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""

    with open("u2be_down.spec", "w") as f:
        f.write(spec_content)

    return True


def build_executable():
    """Build executable with PyInstaller"""
    print("🔨 Compilando executável...")

    success, output = run_command("pyinstaller --clean u2be_down.spec")
    if not success:
        print(f"❌ Erro na compilação: {output}")
        return False

    # Check if executable was created
    exe_name = "u2be_down.exe" if platform.system() == "Windows" else "u2be_down"
    exe_path = Path("dist") / exe_name

    if not exe_path.exists():
        print(f"❌ Executável não encontrado: {exe_path}")
        return False

    print(f"✅ Executável criado: {exe_path}")
    return True


def create_linux_package():
    """Create Linux installation package"""
    print("📦 Criando pacote Linux...")

    # Create package directory
    pkg_dir = Path("package_linux")
    pkg_dir.mkdir(exist_ok=True)

    # Copy executable
    shutil.copy2("dist/u2be_down", pkg_dir / "u2be_down")

    # Copy config if exists
    if Path("config.json").exists():
        shutil.copy2("config.json", pkg_dir / "config.json")

    # Copy assets if exists
    if Path("assets").exists():
        shutil.copytree("assets", pkg_dir / "assets", dirs_exist_ok=True)

    # Create install script
    install_script = """#!/bin/bash
set -e

INSTALL_DIR="/opt/u2be_down"
BIN_DIR="/usr/local/bin"
SCRIPT_DIR="$(dirname "$0")"

echo "Instalando U2Be Down..."

if [ "$EUID" -ne 0 ]; then
    echo "Por favor, execute como root (use sudo)"
    exit 1
fi

mkdir -p "$INSTALL_DIR"
cp "$SCRIPT_DIR/u2be_down" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/u2be_down"

if [ -f "$SCRIPT_DIR/config.json" ]; then
    cp "$SCRIPT_DIR/config.json" "$INSTALL_DIR/"
fi

if [ -d "$SCRIPT_DIR/assets" ]; then
    cp -r "$SCRIPT_DIR/assets" "$INSTALL_DIR/"
fi

ln -sf "$INSTALL_DIR/u2be_down" "$BIN_DIR/u2be_down"

echo "✅ U2Be Down instalado com sucesso!"
echo "Execute: u2be_down"
"""

    with open(pkg_dir / "install.sh", "w") as f:
        f.write(install_script)

    os.chmod(pkg_dir / "install.sh", 0o755)

    # Create uninstall script
    uninstall_script = """#!/bin/bash
set -e

INSTALL_DIR="/opt/u2be_down"
BIN_DIR="/usr/local/bin"

echo "Removendo U2Be Down..."

if [ "$EUID" -ne 0 ]; then
    echo "Por favor, execute como root (use sudo)"
    exit 1
fi

rm -rf "$INSTALL_DIR"
rm -f "$BIN_DIR/u2be_down"

echo "✅ U2Be Down removido com sucesso!"
"""

    with open(pkg_dir / "uninstall.sh", "w") as f:
        f.write(uninstall_script)

    os.chmod(pkg_dir / "uninstall.sh", 0o755)

    # Create tar.gz
    success, _ = run_command(f"tar -czf u2be_down_linux.tar.gz -C {pkg_dir} .")
    if success:
        print("✅ Arquivo u2be_down_linux.tar.gz criado")

    return True


def create_windows_package():
    """Create Windows installation package"""
    print("📦 Criando pacote Windows...")

    # Create package directory
    pkg_dir = Path("package_windows")
    pkg_dir.mkdir(exist_ok=True)

    # Copy executable
    shutil.copy2("dist/u2be_down.exe", pkg_dir / "u2be_down.exe")

    # Copy config if exists
    if Path("config.json").exists():
        shutil.copy2("config.json", pkg_dir / "config.json")

    # Copy assets if exists
    if Path("assets").exists():
        shutil.copytree("assets", pkg_dir / "assets", dirs_exist_ok=True)

    # Create batch installer
    install_bat = """@echo off
echo Instalando U2Be Down...

set INSTALL_DIR=%PROGRAMFILES%\\U2BeDown
mkdir "%INSTALL_DIR%" 2>nul

copy "%~dp0u2be_down.exe" "%INSTALL_DIR%\\" >nul
if exist "%~dp0config.json" copy "%~dp0config.json" "%INSTALL_DIR%\\" >nul
if exist "%~dp0assets" xcopy "%~dp0assets" "%INSTALL_DIR%\\assets\\" /E /I /Q >nul

echo.
echo ✅ U2Be Down instalado em: %INSTALL_DIR%
echo.
echo Para executar, abra o Prompt de Comando e digite:
echo "%INSTALL_DIR%\\u2be_down.exe"
echo.
pause
"""

    with open(pkg_dir / "install.bat", "w") as f:
        f.write(install_bat)

    # Create zip file
    try:
        import zipfile

        with zipfile.ZipFile(
            "u2be_down_windows.zip", "w", zipfile.ZIP_DEFLATED
        ) as zipf:
            for file_path in pkg_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(pkg_dir)
                    zipf.write(file_path, arcname)

        print("✅ Arquivo u2be_down_windows.zip criado")
    except Exception as e:
        print(f"⚠️  Erro ao criar ZIP: {e}")

    return True


def main():
    """Main function"""
    print("🚀 U2Be Down - Gerador de Instalador Rápido")
    print("=" * 50)

    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Erro: main.py não encontrado")
        print("Execute este script no diretório do projeto!")
        sys.exit(1)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Install build dependencies
    if not install_build_deps():
        sys.exit(1)

    # Create spec file
    print("📝 Criando arquivo de configuração...")
    if not create_pyinstaller_spec():
        sys.exit(1)

    # Build executable
    if not build_executable():
        sys.exit(1)

    # Create platform-specific package
    current_platform = platform.system()

    if current_platform == "Linux":
        create_linux_package()
        print("\n🎉 Build Linux concluído!")
        print("📁 Arquivos gerados:")
        print("   - dist/u2be_down (executável)")
        print("   - package_linux/ (arquivos de instalação)")
        print("   - u2be_down_linux.tar.gz (pacote completo)")
        print("\n📖 Para instalar:")
        print("   tar -xzf u2be_down_linux.tar.gz")
        print("   sudo ./install.sh")

    elif current_platform == "Windows":
        create_windows_package()
        print("\n🎉 Build Windows concluído!")
        print("📁 Arquivos gerados:")
        print("   - dist/u2be_down.exe (executável)")
        print("   - package_windows/ (arquivos de instalação)")
        print("   - u2be_down_windows.zip (pacote completo)")
        print("\n📖 Para instalar:")
        print("   Extraia o ZIP e execute install.bat")

    else:
        print(f"\n⚠️  Plataforma {current_platform} não suportada diretamente")
        print("Executável criado em dist/")

    print("\n✨ Processo concluído com sucesso!")


if __name__ == "__main__":
    main()
