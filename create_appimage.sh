#!/bin/bash

# U2Be Down - Gerador de AppImage

set -e

echo "🚀 Criando AppImage para U2Be Down..."

# Verificar dependências
if ! command -v wget >/dev/null 2>&1; then
    echo "❌ wget não encontrado. Instale com: sudo apt install wget"
    exit 1
fi

# Verificar se o executável existe
if [ ! -f "dist/u2be_down" ]; then
    echo "❌ Executável não encontrado. Execute primeiro:"
    echo "   python3 simple_build.py"
    exit 1
fi

# Configurações
APP_NAME="U2Be_Down"
APP_DIR="U2Be_Down.AppDir"
VERSION="1.0.2"

# Limpar diretório anterior
rm -rf "$APP_DIR"
rm -f "${APP_NAME}-*.AppImage"

echo "📁 Criando estrutura AppDir..."
# Criar estrutura AppDir
mkdir -p "$APP_DIR/usr/bin"
mkdir -p "$APP_DIR/usr/share/applications"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$APP_DIR/usr/share/metainfo"

echo "📂 Copiando arquivos da aplicação..."
# Copiar executável
cp "dist/u2be_down" "$APP_DIR/usr/bin/"
chmod +x "$APP_DIR/usr/bin/u2be_down"

# Copiar assets
if [ -d "assets" ]; then
    mkdir -p "$APP_DIR/usr/share/u2be-down"
    cp -r "assets" "$APP_DIR/usr/share/u2be-down/"
fi

# Copiar configuração
if [ -f "config.json" ]; then
    cp "config.json" "$APP_DIR/usr/share/u2be-down/"
fi

echo "🎨 Configurando ícones..."
# Copiar ícone
if [ -f "assets/icon.png" ]; then
    cp "assets/icon.png" "$APP_DIR/usr/share/icons/hicolor/256x256/apps/u2be-down.png"
    cp "assets/icon.png" "$APP_DIR/u2be-down.png"  # Ícone principal do AppImage
fi

echo "🖥️  Criando desktop entry..."
# Criar .desktop file
cat > "$APP_DIR/u2be-down.desktop" << EOF
[Desktop Entry]
Name=U2Be Down
GenericName=YouTube Downloader
Comment=Download videos and music from YouTube
Exec=u2be_down
Icon=u2be-down
Terminal=false
Type=Application
Categories=AudioVideo;Audio;Video;Network;
MimeType=text/uri-list;x-scheme-handler/http;x-scheme-handler/https;
Keywords=youtube;download;video;audio;mp3;converter;
StartupNotify=true
X-AppImage-Version=$VERSION
EOF

# Copiar para usr/share/applications também
cp "$APP_DIR/u2be-down.desktop" "$APP_DIR/usr/share/applications/"

echo "📋 Criando metainfo..."
# Criar arquivo metainfo (AppStream)
cat > "$APP_DIR/usr/share/metainfo/u2be-down.appdata.xml" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>u2be-down</id>
  <metadata_license>MIT</metadata_license>
  <project_license>MIT</project_license>
  <name>U2Be Down</name>
  <summary>YouTube Video Downloader with Music Player</summary>
  <description>
    <p>
      U2Be Down is a comprehensive YouTube video downloader with a modern graphical interface.
      It allows you to download videos and convert them to MP3 format automatically.
    </p>
    <p>Features:</p>
    <ul>
      <li>Download videos and audio from YouTube</li>
      <li>Automatic MP3 conversion</li>
      <li>Built-in music player</li>
      <li>Playlist support</li>
      <li>Parallel downloads for faster performance</li>
      <li>Download history tracking</li>
      <li>Clean and intuitive interface</li>
    </ul>
  </description>
  <categories>
    <category>AudioVideo</category>
    <category>Audio</category>
    <category>Video</category>
  </categories>
  <url type="homepage">https://github.com/fchevitarese/u2be_down</url>
  <url type="bugtracker">https://github.com/fchevitarese/u2be_down/issues</url>
  <screenshots>
    <screenshot type="default">
      <caption>Main interface</caption>
    </screenshot>
  </screenshots>
  <releases>
    <release version="$VERSION" date="$(date +%Y-%m-%d)">
      <description>
        <p>Initial AppImage release with full functionality</p>
      </description>
    </release>
  </releases>
</component>
EOF

echo "🔧 Criando script AppRun..."
# Criar AppRun script
cat > "$APP_DIR/AppRun" << 'EOF'
#!/bin/bash

# AppRun script para U2Be Down

# Obter diretório do AppImage
HERE="$(dirname "$(readlink -f "${0}")")"

# Configurar variáveis de ambiente
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
export XDG_DATA_DIRS="${HERE}/usr/share:${XDG_DATA_DIRS}"

# Configurar caminho para assets
export U2BE_DOWN_ASSETS_PATH="${HERE}/usr/share/u2be-down/assets"

# Se config.json existe no AppImage, copiar para ~/.config se não existir
CONFIG_DIR="$HOME/.config/u2be-down"
if [ ! -d "$CONFIG_DIR" ]; then
    mkdir -p "$CONFIG_DIR"
fi

if [ -f "${HERE}/usr/share/u2be-down/config.json" ] && [ ! -f "$CONFIG_DIR/config.json" ]; then
    cp "${HERE}/usr/share/u2be-down/config.json" "$CONFIG_DIR/"
fi

# Executar aplicação
cd "$CONFIG_DIR"
exec "${HERE}/usr/bin/u2be_down" "$@"
EOF

chmod +x "$APP_DIR/AppRun"

echo "📥 Baixando appimagetool..."
# Baixar appimagetool se não existir
APPIMAGETOOL="appimagetool-x86_64.AppImage"
if [ ! -f "$APPIMAGETOOL" ]; then
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/$APPIMAGETOOL"
    chmod +x "$APPIMAGETOOL"
fi

echo "🔨 Criando AppImage..."
# Criar AppImage
"./$APPIMAGETOOL" "$APP_DIR" "${APP_NAME}-${VERSION}-x86_64.AppImage"

if [ -f "${APP_NAME}-${VERSION}-x86_64.AppImage" ]; then
    echo ""
    echo "✅ AppImage criado com sucesso!"
    echo "📦 Arquivo: ${APP_NAME}-${VERSION}-x86_64.AppImage"
    echo "📏 Tamanho: $(du -h "${APP_NAME}-${VERSION}-x86_64.AppImage" | cut -f1)"
    echo ""
    echo "🚀 Para executar:"
    echo "   chmod +x ${APP_NAME}-${VERSION}-x86_64.AppImage"
    echo "   ./${APP_NAME}-${VERSION}-x86_64.AppImage"
    echo ""
    echo "📱 Para integrar ao sistema:"
    echo "   Mova o arquivo para ~/Applications/"
    echo "   Ou execute uma vez para integração automática"
    
    # Tornar executável
    chmod +x "${APP_NAME}-${VERSION}-x86_64.AppImage"
    
    echo ""
    echo "🔍 Testando AppImage..."
    if "./${APP_NAME}-${VERSION}-x86_64.AppImage" --help >/dev/null 2>&1; then
        echo "✅ AppImage funcional!"
    else
        echo "⚠️  AppImage criado, mas pode ter problemas"
    fi
    
else
    echo "❌ Erro ao criar AppImage"
    exit 1
fi

echo ""
echo "🧹 Limpando arquivos temporários..."
rm -rf "$APP_DIR"

echo "🎉 AppImage pronto para distribuição!"
