#!/usr/bin/env python3
"""
Script para gerar instaladores para Windows e Linux
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path


def run_command(cmd, shell=False):
    """Executa um comando e retorna o resultado"""
    try:
        result = subprocess.run(
            cmd, shell=shell, check=True, capture_output=True, text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def install_dependencies():
    """Instala dependências necessárias para o build"""
    print("Instalando dependências...")

    # Instalar PyInstaller
    success, output = run_command(
        [sys.executable, "-m", "pip", "install", "pyinstaller"]
    )
    if not success:
        print(f"Erro ao instalar PyInstaller: {output}")
        return False

    # Instalar dependências do projeto
    success, output = run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    )
    if not success:
        print(f"Erro ao instalar dependências: {output}")
        return False

    print("Dependências instaladas com sucesso!")
    return True


def create_spec_file():
    """Cria arquivo .spec para PyInstaller"""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('config.json', '.'),
    ],
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='u2be_down',
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

    print("Arquivo .spec criado!")


def build_executable():
    """Compila o executável usando PyInstaller"""
    print("Compilando executável...")

    success, output = run_command(["pyinstaller", "--clean", "u2be_down.spec"])
    if not success:
        print(f"Erro ao compilar: {output}")
        return False

    print("Executável compilado com sucesso!")
    return True


def create_windows_installer():
    """Cria instalador para Windows"""
    print("Criando instalador para Windows...")

    # Criar script NSIS
    nsis_script = """
!include "MUI2.nsh"

Name "U2Be Down"
OutFile "U2BeDown_Installer.exe"
InstallDir "$PROGRAMFILES\\U2BeDown"
InstallDirRegKey HKCU "Software\\U2BeDown" ""
RequestExecutionLevel admin

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Section "U2Be Down" SecMain
    SetOutPath "$INSTDIR"
    File /r "dist\\u2be_down.exe"
    File "config.json"
    File /nonfatal /r "assets"

    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\\U2Be Down"
    CreateShortcut "$SMPROGRAMS\\U2Be Down\\U2Be Down.lnk" "$INSTDIR\\u2be_down.exe"
    CreateShortcut "$DESKTOP\\U2Be Down.lnk" "$INSTDIR\\u2be_down.exe"

    ; Registry entries
    WriteRegStr HKCU "Software\\U2BeDown" "" $INSTDIR
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\u2be_down.exe"
    Delete "$INSTDIR\\config.json"
    RMDir /r "$INSTDIR\\assets"
    Delete "$INSTDIR\\Uninstall.exe"
    RMDir "$INSTDIR"

    Delete "$SMPROGRAMS\\U2Be Down\\U2Be Down.lnk"
    RMDir "$SMPROGRAMS\\U2Be Down"
    Delete "$DESKTOP\\U2Be Down.lnk"

    DeleteRegKey /ifempty HKCU "Software\\U2BeDown"
SectionEnd
"""

    with open("installer.nsi", "w") as f:
        f.write(nsis_script)

    # Criar arquivo de licença simples
    license_content = """MIT License

Copyright (c) 2025 U2Be Down

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

    with open("LICENSE", "w") as f:
        f.write(license_content)

    print("Script NSIS criado! Para compilar o instalador Windows:")
    print("1. Instale NSIS (https://nsis.sourceforge.io/)")
    print("2. Execute: makensis installer.nsi")


def create_linux_installer():
    """Cria instalador para Linux"""
    print("Criando instalador para Linux...")

    # Criar script de instalação
    install_script = """#!/bin/bash

# U2Be Down - Linux Installer

set -e

INSTALL_DIR="/opt/u2be_down"
BIN_DIR="/usr/local/bin"
DESKTOP_DIR="/usr/share/applications"

echo "Installing U2Be Down..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Create installation directory
mkdir -p "$INSTALL_DIR"

# Copy files
cp dist/u2be_down "$INSTALL_DIR/"
cp config.json "$INSTALL_DIR/"
if [ -d "assets" ]; then
    cp -r assets "$INSTALL_DIR/"
fi

# Make executable
chmod +x "$INSTALL_DIR/u2be_down"

# Create symlink
ln -sf "$INSTALL_DIR/u2be_down" "$BIN_DIR/u2be_down"

# Create desktop entry
cat > "$DESKTOP_DIR/u2be_down.desktop" << EOF
[Desktop Entry]
Name=U2Be Down
Comment=YouTube Video Downloader
Exec=$INSTALL_DIR/u2be_down
Icon=$INSTALL_DIR/assets/icon.png
Terminal=false
Type=Application
Categories=AudioVideo;Network;
EOF

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR"
fi

echo "U2Be Down installed successfully!"
echo "You can run it from terminal with: u2be_down"
echo "Or find it in your applications menu."
"""

    with open("install_linux.sh", "w") as f:
        f.write(install_script)

    os.chmod("install_linux.sh", 0o755)

    # Criar script de desinstalação
    uninstall_script = """#!/bin/bash

# U2Be Down - Linux Uninstaller

set -e

INSTALL_DIR="/opt/u2be_down"
BIN_DIR="/usr/local/bin"
DESKTOP_DIR="/usr/share/applications"

echo "Uninstalling U2Be Down..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Remove files
rm -rf "$INSTALL_DIR"
rm -f "$BIN_DIR/u2be_down"
rm -f "$DESKTOP_DIR/u2be_down.desktop"

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR"
fi

echo "U2Be Down uninstalled successfully!"
"""

    with open("uninstall_linux.sh", "w") as f:
        f.write(uninstall_script)

    os.chmod("uninstall_linux.sh", 0o755)

    print("Scripts de instalação Linux criados!")


def create_deb_package():
    """Cria pacote .deb para Debian/Ubuntu"""
    print("Criando pacote .deb...")

    # Criar estrutura do pacote
    os.makedirs("debian_package/DEBIAN", exist_ok=True)
    os.makedirs("debian_package/opt/u2be_down", exist_ok=True)
    os.makedirs("debian_package/usr/local/bin", exist_ok=True)
    os.makedirs("debian_package/usr/share/applications", exist_ok=True)

    # Arquivo control
    control_content = """Package: u2be-down
Version: 1.0.0
Section: multimedia
Priority: optional
Architecture: amd64
Depends: python3, ffmpeg
Maintainer: U2Be Down Team <noreply@example.com>
Description: YouTube Video Downloader
 A simple and efficient YouTube video downloader with GUI support.
 Supports downloading individual videos and playlists.
"""

    with open("debian_package/DEBIAN/control", "w") as f:
        f.write(control_content)

    # Script pós-instalação
    postinst_content = """#!/bin/bash
ln -sf /opt/u2be_down/u2be_down /usr/local/bin/u2be_down
update-desktop-database /usr/share/applications 2>/dev/null || true
"""

    with open("debian_package/DEBIAN/postinst", "w") as f:
        f.write(postinst_content)

    os.chmod("debian_package/DEBIAN/postinst", 0o755)

    # Script pré-remoção
    prerm_content = """#!/bin/bash
rm -f /usr/local/bin/u2be_down
"""

    with open("debian_package/DEBIAN/prerm", "w") as f:
        f.write(prerm_content)

    os.chmod("debian_package/DEBIAN/prerm", 0o755)

    print("Estrutura do pacote .deb criada!")


def main():
    """Função principal"""
    print("=== U2Be Down - Gerador de Instaladores ===")
    print(f"Sistema operacional: {platform.system()}")
    print(f"Arquitetura: {platform.machine()}")

    # Verificar se estamos no diretório correto
    if not os.path.exists("main.py"):
        print("Erro: Execute este script no diretório do projeto!")
        sys.exit(1)

    # Instalar dependências
    if not install_dependencies():
        sys.exit(1)

    # Criar arquivo .spec
    create_spec_file()

    # Compilar executável
    if not build_executable():
        sys.exit(1)

    # Criar instaladores específicos da plataforma
    if platform.system() == "Windows":
        create_windows_installer()
    elif platform.system() == "Linux":
        create_linux_installer()
        create_deb_package()

    print("\n=== Build concluído! ===")
    print("Arquivos gerados:")
    print("- dist/u2be_down (executável)")

    if platform.system() == "Windows":
        print("- installer.nsi (script NSIS)")
        print("- LICENSE (arquivo de licença)")
    elif platform.system() == "Linux":
        print("- install_linux.sh (instalador Linux)")
        print("- uninstall_linux.sh (desinstalador Linux)")
        print("- debian_package/ (estrutura do pacote .deb)")


if __name__ == "__main__":
    main()
