#!/bin/bash

# Build script para macOS - U2Be Down
# Este script cria executáveis e pacotes para macOS

set -e  # Parar em caso de erro

echo "🍎 Build macOS - U2Be Down"
echo "========================================"

# Verificar se estamos no macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Este script deve ser executado no macOS!"
    exit 1
fi

# Verificar se estamos no diretório correto
if [ ! -f "main.py" ]; then
    echo "❌ Erro: Execute no diretório do projeto!"
    exit 1
fi

# Verificar se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado! Instale via:"
    echo "   brew install python3"
    exit 1
fi

# Instalar dependências se necessário
echo "📦 Verificando dependências..."
if ! pip3 show pyinstaller &> /dev/null; then
    echo "📥 Instalando PyInstaller..."
    pip3 install pyinstaller
fi

# Instalar dependências do projeto
if [ -f "requirements.txt" ]; then
    echo "📥 Instalando dependências do projeto..."
    pip3 install -r requirements.txt
fi

# Criar executável da GUI
echo "🔨 Compilando executável da GUI..."
python3 -m PyInstaller \
    --onefile \
    --windowed \
    --name "U2Be Down" \
    --icon "assets/icon.ico" \
    --add-data "assets:assets" \
    --osx-bundle-identifier "com.u2bedown.app" \
    gui.py

# Verificar se foi criado
if [ ! -f "dist/U2Be Down" ]; then
    echo "❌ Falha ao criar executável!"
    exit 1
fi

echo "✅ Executável criado: dist/U2Be Down"

# Criar aplicação .app
echo "📱 Criando aplicação .app..."
APP_NAME="U2Be Down.app"
APP_DIR="dist/$APP_NAME"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

# Criar estrutura do .app
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Mover executável
mv "dist/U2Be Down" "$MACOS_DIR/U2Be Down"

# Criar Info.plist
cat > "$CONTENTS_DIR/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>U2Be Down</string>
    <key>CFBundleIdentifier</key>
    <string>com.u2bedown.app</string>
    <key>CFBundleName</key>
    <string>U2Be Down</string>
    <key>CFBundleVersion</key>
    <string>1.0.2</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.2</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeExtensions</key>
            <array>
                <string>*</string>
            </array>
            <key>CFBundleTypeName</key>
            <string>URL</string>
            <key>CFBundleTypeRole</key>
            <string>Viewer</string>
            <key>LSHandlerRank</key>
            <string>Alternate</string>
        </dict>
    </array>
</dict>
</plist>
EOF

# Copiar ícone se existir
if [ -f "assets/icon.icns" ]; then
    cp "assets/icon.icns" "$RESOURCES_DIR/icon.icns"
    # Adicionar ícone ao Info.plist
    sed -i '' 's|</dict>|    <key>CFBundleIconFile</key>\
    <string>icon.icns</string>\
</dict>|' "$CONTENTS_DIR/Info.plist"
elif [ -f "assets/icon.png" ]; then
    # Converter PNG para ICNS se possível
    if command -v sips &> /dev/null; then
        echo "🖼️  Convertendo ícone PNG para ICNS..."
        sips -s format icns "assets/icon.png" --out "$RESOURCES_DIR/icon.icns"
        sed -i '' 's|</dict>|    <key>CFBundleIconFile</key>\
    <string>icon.icns</string>\
</dict>|' "$CONTENTS_DIR/Info.plist"
    fi
fi

# Tornar executável
chmod +x "$MACOS_DIR/U2Be Down"

echo "✅ Aplicação .app criada: $APP_DIR"

# Criar DMG (se possível)
if command -v hdiutil &> /dev/null; then
    echo "💿 Criando arquivo DMG..."

    DMG_NAME="U2Be-Down-macOS.dmg"
    TEMP_DMG="temp.dmg"

    # Criar DMG temporário
    hdiutil create -size 200m -fs HFS+ -volname "U2Be Down" "$TEMP_DMG"

    # Montar DMG
    hdiutil attach "$TEMP_DMG" -readwrite -mountroot /Volumes

    # Copiar aplicação
    cp -R "$APP_DIR" "/Volumes/U2Be Down/"

    # Criar link para Applications
    ln -s /Applications "/Volumes/U2Be Down/Applications"

    # Desmontar
    hdiutil detach "/Volumes/U2Be Down"

    # Converter para DMG final comprimido
    hdiutil convert "$TEMP_DMG" -format UDZO -o "dist/$DMG_NAME"

    # Limpar
    rm "$TEMP_DMG"

    echo "✅ DMG criado: dist/$DMG_NAME"
fi

# Mostrar resumo
echo ""
echo "🎉 Build concluído com sucesso!"
echo "📁 Arquivos criados:"
echo "   📱 dist/$APP_NAME"
if [ -f "dist/U2Be-Down-macOS.dmg" ]; then
    echo "   💿 dist/U2Be-Down-macOS.dmg"
fi

echo ""
echo "🚀 Para instalar:"
echo "   1. Abra o arquivo DMG (se criado) ou"
echo "   2. Arraste '$APP_NAME' para a pasta Applications"
echo ""
echo "🔒 Nota: Pode ser necessário permitir a execução em:"
echo "   Preferências do Sistema > Segurança e Privacidade"
