# Build no macOS - U2Be Down

Este guia explica como compilar o U2Be Down no macOS.

## Pré-requisitos

### 1. Python 3.8+
```bash
# Via Homebrew (recomendado)
brew install python3

# Ou via site oficial
# https://www.python.org/downloads/macos/
```

### 2. Xcode Command Line Tools
```bash
xcode-select --install
```

### 3. Homebrew (opcional, mas recomendado)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## Instalação das Dependências

### 1. Clonar o repositório
```bash
git clone https://github.com/fchevitarese/u2be_down.git
cd u2be_down
```

### 2. Criar ambiente virtual (recomendado)
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
pip install pyinstaller
```

### 4. Instalar FFmpeg
```bash
# Via Homebrew
brew install ffmpeg

# Ou via MacPorts
sudo port install ffmpeg
```

## Build da Aplicação

### Build Automático (Recomendado)
```bash
chmod +x build_macos.sh
./build_macos.sh
```

Este script irá:
- ✅ Verificar dependências
- 🔨 Compilar o executável
- 📱 Criar aplicação .app
- 💿 Gerar arquivo DMG (se possível)
- 🖼️ Converter ícones automaticamente

### Build Manual

#### 1. Executável simples
```bash
pyinstaller --onefile --windowed \
    --name "U2Be Down" \
    --icon "assets/icon.icns" \
    --add-data "assets:assets" \
    --osx-bundle-identifier "com.u2bedown.app" \
    gui.py
```

#### 2. Aplicação .app completa
```bash
pyinstaller --onedir --windowed \
    --name "U2Be Down" \
    --icon "assets/icon.icns" \
    --add-data "assets:assets" \
    --osx-bundle-identifier "com.u2bedown.app" \
    gui.py
```

## Arquivos Gerados

Após o build, você encontrará:

```
dist/
├── U2Be Down.app/          # Aplicação macOS
└── U2Be-Down-macOS.dmg     # Instalador DMG (se criado)
```

## Instalação

### Via DMG
1. Abra o arquivo `U2Be-Down-macOS.dmg`
2. Arraste "U2Be Down.app" para a pasta Applications
3. Ejete o DMG

### Via .app
1. Copie `U2Be Down.app` para `/Applications/`
2. Abra o Launchpad e procure por "U2Be Down"

## Solução de Problemas

### Erro de Segurança
Se aparecer "não é possível abrir porque é de um desenvolvedor não identificado":

1. **Método 1**: Botão direito → Abrir → Abrir
2. **Método 2**:
   ```bash
   sudo xattr -rd com.apple.quarantine "/Applications/U2Be Down.app"
   ```
3. **Método 3**: Preferências do Sistema → Segurança e Privacidade → Permitir

### Dependências em falta

#### Qt/PyQt5
```bash
pip install PyQt5
# Se houver problemas:
brew install qt5
pip install --no-cache-dir PyQt5
```

#### FFmpeg não encontrado
```bash
brew install ffmpeg
# Verificar instalação:
ffmpeg -version
```

### Erro de ícone
Se o ícone não aparecer:
```bash
# Regerar ícones
./generate_icons.sh

# Limpar cache de ícones
sudo find /private/var/folders -name com.apple.dock.iconcache -delete
killall Dock
```

## Recursos Específicos do macOS

### Integração com o Sistema
- ✅ Ícone nativo no Dock
- ✅ Entrada no Launchpad
- ✅ Notificações nativas
- ✅ Suporte a arquivos via drag & drop

### Otimizações
- Aplicação otimizada para Retina Display
- Suporte completo ao Dark Mode
- Integração com Spotlight (busca)

## Desenvolvimento

### Executar em modo de desenvolvimento
```bash
python3 gui.py
```

### Testar mudanças rapidamente
```bash
# Build rápido para testes
pyinstaller gui.py --onefile --windowed
```

### Debug
```bash
# Executar com logs detalhados
./dist/U2Be\ Down --debug
```

## CI/CD Automático

O build para macOS também está configurado no GitHub Actions. A cada push ou tag, será gerado automaticamente:
- `u2be_down-macos-app` (aplicação .app)
- `u2be_down-macos-dmg` (instalador DMG)

## Suporte

Para problemas específicos do macOS:
1. Verifique os logs em Console.app
2. Teste em modo de desenvolvimento primeiro
3. Verifique permissões de arquivo/pasta
4. Confirme versão do macOS (mínimo: 10.15 Catalina)

## Versões Testadas

- ✅ macOS Monterey (12.x)
- ✅ macOS Big Sur (11.x)
- ✅ macOS Catalina (10.15)
- ⚠️ macOS Mojave (10.14) - Pode funcionar mas não testado
