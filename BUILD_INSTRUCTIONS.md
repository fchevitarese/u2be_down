# Build Instructions - U2Be Down

Este documento fornece instruções para criar instaladores do U2Be Down para Windows e Linux.

## Pré-requisitos

### Geral
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git (opcional, para controle de versão)

### Linux
- Distribuições suportadas: Ubuntu, Debian, CentOS, Fedora, etc.
- Dependências do sistema: `python3-dev`, `build-essential`
- Para criar pacotes .deb: `dpkg-deb`

### Windows
- Windows 7 ou superior
- Para criar instalador: [NSIS (Nullsoft Scriptable Install System)](https://nsis.sourceforge.io/)

## Instruções de Build

### Método 1: Scripts Automáticos (Recomendado)

#### Linux
```bash
# Tornar o script executável (primeira vez)
chmod +x build_linux.sh

# Executar o build
./build_linux.sh
```

#### Windows
```cmd
REM Executar o script de build
build_windows.bat
```

### Método 2: Usando Makefile

```bash
# Ver todas as opções disponíveis
make help

# Limpar arquivos de build anteriores
make clean

# Instalar dependências
make install-deps

# Build para Linux
make build-linux

# Build para Windows (executar no Windows)
make build-windows

# Build para plataforma atual
make build-all
```

### Método 3: Python Script (Avançado)

```bash
# Executar o script de build Python
python3 build_installer.py
```

## Arquivos Gerados

### Linux
- `dist/u2be_down` - Executável standalone
- `installer/` - Diretório com arquivos de instalação
  - `install.sh` - Script de instalação
  - `uninstall.sh` - Script de desinstalação
- `u2be_down_linux.tar.gz` - Arquivo portável
- `u2be-down_1.0.0_amd64.deb` - Pacote Debian (se dpkg-deb disponível)

### Windows
- `dist/u2be_down.exe` - Executável standalone
- `installer/` - Diretório com arquivos de instalação
- `installer.nsi` - Script do NSIS para criar instalador
- `U2BeDown_Setup.exe` - Instalador final (após compilar NSIS)

## Como Instalar

### Linux

#### Método 1: Usando o script de instalação
```bash
# Extrair o arquivo
tar -xzf u2be_down_linux.tar.gz

# Instalar (requer sudo)
sudo ./install.sh
```

#### Método 2: Usando pacote .deb (Ubuntu/Debian)
```bash
sudo dpkg -i u2be-down_1.0.0_amd64.deb
sudo apt-get install -f  # Resolver dependências se necessário
```

#### Método 3: Executável portável
```bash
# Extrair e executar diretamente
tar -xzf u2be_down_linux.tar.gz
./u2be_down
```

### Windows

#### Método 1: Usando o instalador
1. Execute `U2BeDown_Setup.exe`
2. Siga as instruções do assistente de instalação

#### Método 2: Executável portável
1. Copie `u2be_down.exe` para qualquer diretório
2. Execute diretamente

## Como Desinstalar

### Linux
```bash
# Se instalado via script
sudo ./uninstall.sh

# Se instalado via .deb
sudo apt remove u2be-down
```

### Windows
- Use "Adicionar ou Remover Programas" no Painel de Controle
- Ou execute o desinstalador em `Arquivos de Programas\U2BeDown\Uninstall.exe`

## Dependências do Sistema

### Linux
O aplicativo requer as seguintes dependências:
- `python3` (geralmente já instalado)
- `ffmpeg` (para processamento de vídeo/áudio)

Instalar ffmpeg:
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# CentOS/RHEL/Fedora
sudo dnf install ffmpeg  # ou sudo yum install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

### Windows
- O FFmpeg é incluído no instalador ou deve ser instalado separadamente
- Instruções detalhadas estão no README.md principal

## Solução de Problemas

### Erro: "Python not found"
- Certifique-se de que Python 3.8+ está instalado
- Verifique se o Python está no PATH do sistema

### Erro: "Permission denied" (Linux)
- Use `sudo` para instalação
- Verifique permissões dos scripts: `chmod +x build_linux.sh`

### Erro: "Module not found"
- Execute: `pip install -r requirements.txt`
- Certifique-se de estar usando o ambiente Python correto

### Erro: "PyInstaller failed"
- Instale/atualize PyInstaller: `pip install --upgrade pyinstaller`
- Limpe arquivos anteriores: `make clean`

### Erro: "NSIS not found" (Windows)
1. Baixe e instale NSIS de https://nsis.sourceforge.io/
2. Adicione NSIS ao PATH do sistema
3. Recompile com: `makensis installer.nsi`

## Estrutura do Projeto

```
u2be_down/
├── main.py                 # Arquivo principal
├── requirements.txt        # Dependências Python
├── config.json            # Configurações
├── assets/                 # Recursos (ícones, etc.)
├── build_linux.sh         # Script de build Linux
├── build_windows.bat      # Script de build Windows
├── build_installer.py     # Script Python de build
├── Makefile               # Automação de build
└── BUILD_INSTRUCTIONS.md  # Este arquivo
```

## Customização

### Modificar informações do instalador
Edite as variáveis no início dos scripts de build:
- Nome do aplicativo
- Versão
- Autor/Empresa
- Ícone da aplicação

### Adicionar dependências
1. Adicione ao `requirements.txt`
2. Atualize a seção `hiddenimports` nos scripts de build
3. Recompile

### Modificar estrutura de instalação
Edite os scripts `install.sh` e `installer.nsi` conforme necessário.

## Contribuição

Para contribuir com melhorias nos scripts de build:
1. Faça fork do repositório
2. Crie uma branch para sua funcionalidade
3. Teste em ambas as plataformas
4. Submeta um pull request

## Suporte

Para problemas relacionados ao build, abra uma issue no repositório do GitHub com:
- Sistema operacional e versão
- Versão do Python
- Logs completos do erro
- Passos para reproduzir o problema
