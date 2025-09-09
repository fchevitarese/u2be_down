#!/bin/bash

# U2Be Down - Gerador Universal de Instaladores
# Cria todos os tipos de instalador para Linux

set -e

echo "🚀 U2Be Down - Gerador Universal de Instaladores"
echo "================================================"

# Verificar se estamos no diretório correto
if [ ! -f "main.py" ]; then
    echo "❌ Erro: Execute no diretório do projeto!"
    exit 1
fi

# Função para verificar comandos
check_command() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "❌ $1 não encontrado. Instale com: sudo apt install $2"
        return 1
    fi
    return 0
}

# Verificar dependências básicas
echo "🔍 Verificando dependências..."
missing_deps=0

if ! check_command "dpkg-deb" "dpkg-dev"; then
    missing_deps=1
fi

if ! check_command "wget" "wget"; then
    missing_deps=1
fi

if [ $missing_deps -eq 1 ]; then
    echo ""
    echo "📦 Instale as dependências com:"
    echo "   sudo apt update"
    echo "   sudo apt install dpkg-dev wget"
    exit 1
fi

# Verificar se o executável existe
if [ ! -f "dist/u2be_down" ]; then
    echo "🔨 Executável não encontrado. Criando..."
    if [ -f "simple_build.py" ]; then
        python3 simple_build.py
    else
        echo "❌ Erro: simple_build.py não encontrado!"
        exit 1
    fi
fi

echo "✅ Dependências OK!"
echo ""

# Menu de opções
echo "📋 Escolha o tipo de instalador:"
echo "1) Pacote .deb (Debian/Ubuntu)"
echo "2) AppImage (Universal Linux)"
echo "3) Ambos (.deb + AppImage)"
echo "4) Tar.gz (Portável)"
echo "5) Todos os formatos"
echo ""
read -p "Selecione uma opção (1-5): " choice

case $choice in
    1)
        echo "📦 Criando pacote .deb..."
        ./create_deb.sh
        ;;
    2)
        echo "🚀 Criando AppImage..."
        ./create_appimage.sh
        ;;
    3)
        echo "📦 Criando pacote .deb..."
        ./create_deb.sh
        echo ""
        echo "🚀 Criando AppImage..."
        ./create_appimage.sh
        ;;
    4)
        echo "📦 Criando arquivo tar.gz..."
        create_tarball
        ;;
    5)
        echo "🎯 Criando todos os formatos..."

        echo "📦 1/3 - Criando pacote .deb..."
        ./create_deb.sh
        echo ""

        echo "🚀 2/3 - Criando AppImage..."
        ./create_appimage.sh
        echo ""

        echo "📦 3/3 - Criando arquivo tar.gz..."
        create_tarball
        ;;
    *)
        echo "❌ Opção inválida!"
        exit 1
        ;;
esac

# Função para criar tarball
create_tarball() {
    echo "📦 Criando arquivo tar.gz portável..."

    TAR_DIR="u2be-down-portable"
    rm -rf "$TAR_DIR"
    mkdir -p "$TAR_DIR"

    # Copiar arquivos
    cp "dist/u2be_down" "$TAR_DIR/"

    if [ -d "assets" ]; then
        cp -r "assets" "$TAR_DIR/"
    fi

    if [ -f "config.json" ]; then
        cp "config.json" "$TAR_DIR/"
    fi

    # Criar script de execução
    cat > "$TAR_DIR/run.sh" << 'EOF'
#!/bin/bash
# Script de execução para U2Be Down

# Obter diretório do script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Executar aplicação
cd "$DIR"
./u2be_down "$@"
EOF

    chmod +x "$TAR_DIR/run.sh"
    chmod +x "$TAR_DIR/u2be_down"

    # Criar README
    cat > "$TAR_DIR/README.txt" << EOF
U2Be Down - YouTube Downloader
==============================

Este é um pacote portável do U2Be Down.

Para executar:
1. Extraia este arquivo em qualquer diretório
2. Execute: ./u2be_down
   ou: ./run.sh

Dependências:
- FFmpeg deve estar instalado no sistema
- Para instalar: sudo apt install ffmpeg

Uso:
- Interface gráfica: ./u2be_down
- Linha de comando: ./u2be_down "https://youtube.com/watch?v=VIDEO_ID"
- Ajuda: ./u2be_down --help

Versão: 1.0.2
Site: https://github.com/fchevitarese/u2be_down
EOF

    # Criar tarball
    tar -czf "u2be-down-1.0.2-linux-portable.tar.gz" "$TAR_DIR"

    echo "✅ Tarball criado: u2be-down-1.0.2-linux-portable.tar.gz"
    echo "📏 Tamanho: $(du -h "u2be-down-1.0.2-linux-portable.tar.gz" | cut -f1)"

    # Limpar
    rm -rf "$TAR_DIR"
}

echo ""
echo "🎉 Instaladores criados com sucesso!"
echo ""
echo "📁 Arquivos gerados:"
ls -la *.deb *.AppImage *.tar.gz 2>/dev/null || echo "   (conforme selecionado)"

echo ""
echo "📋 Como usar:"

if [ -f *.deb ]; then
    echo "📦 Pacote .deb:"
    echo "   sudo dpkg -i u2be-down_*.deb"
    echo "   sudo apt-get install -f  # Se necessário"
fi

if [ -f *.AppImage ]; then
    echo "🚀 AppImage:"
    echo "   chmod +x U2Be_Down-*.AppImage"
    echo "   ./U2Be_Down-*.AppImage"
fi

if [ -f *.tar.gz ]; then
    echo "📦 Tar.gz:"
    echo "   tar -xzf u2be-down-*-portable.tar.gz"
    echo "   cd u2be-down-portable && ./u2be_down"
fi

echo ""
echo "✨ Pronto para distribuição!"
