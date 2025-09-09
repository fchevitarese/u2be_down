#!/bin/bash

# U2Be Down - Gerador de Pacote .deb Profissional

set -e

echo "📦 Criando pacote .deb para U2Be Down..."

# Verificar se estamos no diretório correto
if [ ! -f "main.py" ]; then
    echo "❌ Erro: Execute no diretório do projeto!"
    exit 1
fi

# Verificar se o executável existe
if [ ! -f "dist/u2be_down" ]; then
    echo "❌ Executável não encontrado. Execute primeiro:"
    echo "   python3 simple_build.py"
    exit 1
fi

# Configurações do pacote
PACKAGE_NAME="u2be-down"
VERSION="1.0.2"
ARCHITECTURE="amd64"
MAINTAINER="U2Be Down Team <noreply@u2bedown.com>"
DESCRIPTION="YouTube Video Downloader with GUI and Music Player"

# Criar estrutura do pacote
DEB_DIR="${PACKAGE_NAME}_${VERSION}_${ARCHITECTURE}"
echo "📁 Criando estrutura em: $DEB_DIR"

# Limpar diretório anterior se existir
rm -rf "$DEB_DIR"

# Criar diretórios
mkdir -p "$DEB_DIR/DEBIAN"
mkdir -p "$DEB_DIR/opt/u2be-down"
mkdir -p "$DEB_DIR/usr/local/bin"
mkdir -p "$DEB_DIR/usr/share/applications"
mkdir -p "$DEB_DIR/usr/share/pixmaps"
mkdir -p "$DEB_DIR/usr/share/doc/u2be-down"

echo "📋 Criando arquivo de controle..."
# Arquivo control
cat > "$DEB_DIR/DEBIAN/control" << EOF
Package: $PACKAGE_NAME
Version: $VERSION
Section: multimedia
Priority: optional
Architecture: $ARCHITECTURE
Depends: ffmpeg, python3 (>= 3.8)
Suggests: youtube-dl, yt-dlp
Maintainer: $MAINTAINER
Homepage: https://github.com/fchevitarese/u2be_down
Description: $DESCRIPTION
 U2Be Down is a comprehensive YouTube video downloader with a modern GUI.
 Features include:
 .
  * Download videos and audio from YouTube
  * Convert videos to MP3 automatically
  * Built-in music player
  * Playlist support
  * Parallel downloads
  * History tracking
 .
 This package includes all necessary dependencies and provides
 both command-line and graphical interfaces.
EOF

echo "📄 Criando scripts de instalação..."
# Script pós-instalação
cat > "$DEB_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e

# Criar link simbólico
ln -sf /opt/u2be-down/u2be_down /usr/local/bin/u2be_down

# Atualizar database de aplicações
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications 2>/dev/null || true
fi

# Atualizar cache de ícones
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t /usr/share/pixmaps 2>/dev/null || true
fi

echo "🎉 U2Be Down instalado com sucesso!"
echo "📚 Execute: u2be_down --help para ver as opções"
echo "🖥️  Interface gráfica: u2be_down (sem argumentos)"
EOF

# Script pré-remoção
cat > "$DEB_DIR/DEBIAN/prerm" << 'EOF'
#!/bin/bash
set -e

# Remover link simbólico
rm -f /usr/local/bin/u2be_down

echo "🗑️  U2Be Down removido do sistema"
EOF

# Script pós-remoção
cat > "$DEB_DIR/DEBIAN/postrm" << 'EOF'
#!/bin/bash
set -e

# Atualizar databases
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications 2>/dev/null || true
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t /usr/share/pixmaps 2>/dev/null || true
fi
EOF

# Tornar scripts executáveis
chmod 755 "$DEB_DIR/DEBIAN/postinst"
chmod 755 "$DEB_DIR/DEBIAN/prerm"
chmod 755 "$DEB_DIR/DEBIAN/postrm"

echo "📂 Copiando arquivos da aplicação..."
# Copiar executável
cp "dist/u2be_down" "$DEB_DIR/opt/u2be-down/"
chmod +x "$DEB_DIR/opt/u2be-down/u2be_down"

# Copiar assets
if [ -d "assets" ]; then
    cp -r "assets" "$DEB_DIR/opt/u2be-down/"
fi

# Copiar configuração
if [ -f "config.json" ]; then
    cp "config.json" "$DEB_DIR/opt/u2be-down/"
fi

# Copiar ícone para sistema
if [ -f "assets/icon_128.png" ]; then
    cp "assets/icon_128.png" "$DEB_DIR/usr/share/pixmaps/u2be-down.png"
elif [ -f "assets/icon.png" ]; then
    cp "assets/icon.png" "$DEB_DIR/usr/share/pixmaps/u2be-down.png"
fi

echo "🖥️  Criando entrada desktop..."
# Criar desktop entry
cat > "$DEB_DIR/usr/share/applications/u2be-down.desktop" << EOF
[Desktop Entry]
Name=U2Be Down
GenericName=YouTube Downloader
Comment=Download videos and music from YouTube
Exec=u2be_down
Icon=/usr/share/pixmaps/u2be-down.png
Terminal=false
Type=Application
Categories=AudioVideo;Audio;Video;Network;
MimeType=text/uri-list;x-scheme-handler/http;x-scheme-handler/https;
Keywords=youtube;download;video;audio;mp3;converter;
StartupNotify=true
EOF

echo "📚 Criando documentação..."
# Criar documentação
cat > "$DEB_DIR/usr/share/doc/u2be-down/README.Debian" << EOF
U2Be Down para Debian/Ubuntu
=============================

Este pacote instala o U2Be Down, um downloader de vídeos do YouTube
com interface gráfica e player de música integrado.

Uso:
----

Interface Gráfica:
  u2be_down

Linha de Comando:
  u2be_down "https://youtube.com/watch?v=VIDEO_ID"
  u2be_down --help

Dependências:
-------------

O pacote requer:
- ffmpeg (para conversão de vídeo/áudio)
- python3 (já incluído na maioria das distribuições)

Problemas Conhecidos:
--------------------

Se você encontrar problemas com downloads, certifique-se de que:
1. FFmpeg está instalado: sudo apt install ffmpeg
2. Você tem conexão com a internet
3. A URL do vídeo é válida

Suporte:
--------

Para reportar bugs ou solicitar recursos:
https://github.com/fchevitarese/u2be_down/issues

EOF

# Criar changelog
cat > "$DEB_DIR/usr/share/doc/u2be-down/changelog" << EOF
u2be-down ($VERSION) unstable; urgency=medium

  * Initial Debian package release
  * YouTube video downloader with GUI
  * MP3 conversion support
  * Built-in music player
  * Playlist support
  * Parallel downloads

 -- $MAINTAINER  $(date -R)
EOF

# Comprimir changelog
gzip -9 "$DEB_DIR/usr/share/doc/u2be-down/changelog"

# Criar copyright
cat > "$DEB_DIR/usr/share/doc/u2be-down/copyright" << EOF
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: u2be-down
Source: https://github.com/fchevitarese/u2be_down

Files: *
Copyright: 2025 U2Be Down Team
License: MIT

License: MIT
 Permission is hereby granted, free of charge, to any person obtaining a
 copy of this software and associated documentation files (the "Software"),
 to deal in the Software without restriction, including without limitation
 the rights to use, copy, modify, merge, publish, distribute, sublicense,
 and/or sell copies of the Software, and to permit persons to whom the
 Software is furnished to do so, subject to the following conditions:
 .
 The above copyright notice and this permission notice shall be included
 in all copies or substantial portions of the Software.
 .
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 DEALINGS IN THE SOFTWARE.
EOF

echo "🔨 Construindo pacote .deb..."
# Construir o pacote
if command -v dpkg-deb >/dev/null 2>&1; then
    dpkg-deb --build "$DEB_DIR"

    echo ""
    echo "✅ Pacote .deb criado com sucesso!"
    echo "📦 Arquivo: ${DEB_DIR}.deb"
    echo "📏 Tamanho: $(du -h "${DEB_DIR}.deb" | cut -f1)"
    echo ""
    echo "🚀 Para instalar:"
    echo "   sudo dpkg -i ${DEB_DIR}.deb"
    echo "   sudo apt-get install -f  # Se houver dependências faltando"
    echo ""
    echo "🗑️  Para remover:"
    echo "   sudo apt remove $PACKAGE_NAME"

    # Verificar integridade do pacote
    echo "🔍 Verificando integridade do pacote..."
    if dpkg-deb --info "${DEB_DIR}.deb" >/dev/null 2>&1; then
        echo "✅ Pacote válido!"
    else
        echo "❌ Erro na verificação do pacote"
        exit 1
    fi

else
    echo "❌ dpkg-deb não encontrado. Instale com:"
    echo "   sudo apt install dpkg-dev"
    exit 1
fi

echo ""
echo "📋 Informações do pacote:"
dpkg-deb --info "${DEB_DIR}.deb"
