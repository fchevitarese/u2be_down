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

# Verificar se o arquivo .spec existe
if [ ! -f "U2Be Down.spec" ]; then
    echo "❌ Arquivo 'U2Be Down.spec' não encontrado!"
    exit 1
fi

# Limpar builds anteriores
echo "🧹 Limpando builds anteriores..."
rm -rf build/ dist/

# Criar executável da GUI usando o arquivo .spec
echo "🔨 Compilando executável da GUI com arquivo .spec..."
python3 -m PyInstaller "U2Be Down.spec"

# Verificar se foi criado
if [ ! -d "dist/U2Be Down.app" ]; then
    echo "❌ Falha ao criar aplicação!"
    exit 1
fi

echo "✅ Aplicação criada: dist/U2Be Down.app"

APP_NAME="U2Be Down.app"
APP_DIR="dist/$APP_NAME"

# Verificar se a aplicação foi criada corretamente
if [ ! -d "$APP_DIR" ]; then
    echo "❌ Aplicação .app não foi criada corretamente!"
    exit 1
fi

echo "✅ Aplicação .app finalizada: $APP_DIR"

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
