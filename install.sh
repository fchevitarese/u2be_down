#!/bin/bash
# Instalador do U2Be Down v2.0
# Script de instalação para macOS

set -e

echo "🚀 Instalador do U2Be Down v2.0"
echo "================================="

# Verificar se estamos no diretório correto
if [ ! -d "dist" ]; then
    echo "❌ Erro: Execute este script no diretório do projeto U2Be Down"
    exit 1
fi

# Verificar se a aplicação foi compilada
if [ ! -d "dist/U2Be Down.app" ]; then
    echo "❌ Erro: Aplicação não encontrada. Execute primeiro:"
    echo "   python3 -m PyInstaller 'U2Be Down.spec' --noconfirm"
    exit 1
fi

# Definir diretório de instalação
INSTALL_DIR="/Applications"
APP_NAME="U2Be Down.app"

echo "📁 Diretório de instalação: $INSTALL_DIR"

# Verificar permissões
if [ ! -w "$INSTALL_DIR" ]; then
    echo "⚠️  Necessário permissão de administrador para instalar em $INSTALL_DIR"
    sudo_prefix="sudo"
else
    sudo_prefix=""
fi

# Remover versão anterior se existir
if [ -d "$INSTALL_DIR/$APP_NAME" ]; then
    echo "🗑️  Removendo versão anterior..."
    $sudo_prefix rm -rf "$INSTALL_DIR/$APP_NAME"
fi

# Copiar nova versão
echo "📦 Instalando U2Be Down..."
$sudo_prefix cp -R "dist/$APP_NAME" "$INSTALL_DIR/"

# Verificar instalação
if [ -d "$INSTALL_DIR/$APP_NAME" ]; then
    echo "✅ Instalação concluída com sucesso!"
    echo ""
    echo "🎉 U2Be Down v2.0 foi instalado em:"
    echo "   $INSTALL_DIR/$APP_NAME"
    echo ""
    echo "📝 Para usar:"
    echo "   1. Abra o Launchpad ou vá para Applications"
    echo "   2. Procure por 'U2Be Down'"
    echo "   3. Clique para abrir"
    echo ""
    echo "🔧 Recursos da v2.0:"
    echo "   ✅ Downloads do YouTube funcionando"
    echo "   ✅ Conversão automática para MP3"
    echo "   ✅ Opção para manter vídeo original"
    echo "   ✅ Interface melhorada"
    echo "   ✅ Player de música integrado"
    echo ""
    echo "📂 Local padrão dos downloads: ~/Music"
    echo ""
    
    # Tentar abrir a aplicação
    read -p "🚀 Deseja abrir o U2Be Down agora? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        open "$INSTALL_DIR/$APP_NAME"
        echo "🎵 U2Be Down está sendo aberto..."
    fi
else
    echo "❌ Erro na instalação!"
    exit 1
fi
