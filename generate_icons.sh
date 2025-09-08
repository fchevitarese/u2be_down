#!/bin/bash

# Script para criar ícones em múltiplos formatos
# Gera .ico para Windows e .icns para macOS a partir do PNG

echo "🎨 Gerando ícones para múltiplas plataformas..."

if [ ! -f "assets/icon.png" ]; then
    echo "❌ Arquivo assets/icon.png não encontrado!"
    exit 1
fi

echo "📁 Criando diretório temporário..."
mkdir -p temp_icons

# Gerar diferentes tamanhos
sizes=(16 32 48 64 128 256 512 1024)

echo "🔄 Gerando tamanhos..."
for size in "${sizes[@]}"; do
    convert "assets/icon.png" -resize "${size}x${size}" "temp_icons/icon_${size}.png"
    echo "   ✓ ${size}x${size}"
done

# Gerar .ico para Windows (se não existir)
if [ ! -f "assets/icon.ico" ] || [ "assets/icon.png" -nt "assets/icon.ico" ]; then
    echo "🪟 Gerando ícone .ico para Windows..."
    convert temp_icons/icon_16.png temp_icons/icon_32.png temp_icons/icon_48.png temp_icons/icon_64.png temp_icons/icon_128.png temp_icons/icon_256.png "assets/icon.ico"
    echo "   ✓ assets/icon.ico criado"
fi

# Gerar .icns para macOS
echo "🍎 Gerando ícone .icns para macOS..."

# Criar estrutura iconset
iconset_dir="temp_icons/icon.iconset"
mkdir -p "$iconset_dir"

# Copiar imagens com nomes corretos para iconset
cp temp_icons/icon_16.png "$iconset_dir/icon_16x16.png"
cp temp_icons/icon_32.png "$iconset_dir/icon_16x16@2x.png"
cp temp_icons/icon_32.png "$iconset_dir/icon_32x32.png"
cp temp_icons/icon_64.png "$iconset_dir/icon_32x32@2x.png"
cp temp_icons/icon_128.png "$iconset_dir/icon_128x128.png"
cp temp_icons/icon_256.png "$iconset_dir/icon_128x128@2x.png"
cp temp_icons/icon_256.png "$iconset_dir/icon_256x256.png"
cp temp_icons/icon_512.png "$iconset_dir/icon_256x256@2x.png"
cp temp_icons/icon_512.png "$iconset_dir/icon_512x512.png"
cp temp_icons/icon_1024.png "$iconset_dir/icon_512x512@2x.png"

# Gerar .icns usando iconutil (macOS) ou ImageMagick
if command -v iconutil >/dev/null 2>&1; then
    iconutil -c icns "$iconset_dir" -o "assets/icon.icns"
    echo "   ✓ assets/icon.icns criado com iconutil"
elif command -v convert >/dev/null 2>&1; then
    # Fallback para ImageMagick em outros sistemas
    convert temp_icons/icon_*.png "assets/icon.icns"
    echo "   ✓ assets/icon.icns criado com ImageMagick"
else
    echo "   ⚠️  iconutil e convert não disponíveis - .icns não criado"
fi

# Limpar arquivos temporários
echo "🧹 Limpando arquivos temporários..."
rm -rf temp_icons

echo "✅ Ícones gerados com sucesso!"
echo "📁 Arquivos criados:"
[ -f "assets/icon.ico" ] && echo "   🪟 assets/icon.ico (Windows)"
[ -f "assets/icon.icns" ] && echo "   🍎 assets/icon.icns (macOS)"
[ -f "assets/icon_128.png" ] && echo "   🐧 assets/icon_128.png (Linux)"
