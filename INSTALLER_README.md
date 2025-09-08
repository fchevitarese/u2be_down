# 📦 Geradores de Instalador - U2Be Down

Este projeto inclui vários scripts para criar instaladores para Windows e Linux.

## 🚀 Opções de Build (da mais simples para a mais avançada)

### 1. Build Simples (Recomendado para teste)
```bash
python3 simple_build.py
```
- Cria apenas o executável
- Mais rápido e simples
- Ideal para testar se tudo funciona

### 2. Build com Scripts de Shell
```bash
# Linux
./build_linux.sh

# Windows
build_windows.bat
```
- Cria executável + instaladores
- Inclui scripts de instalação/desinstalação
- Cria pacotes .deb e .tar.gz (Linux)

### 3. Build Avançado
```bash
python3 quick_build.py
```
- Verificação automática de dependências
- Criação de pacotes completos
- Mais opcões de customização

### 4. Usando Makefile
```bash
make build-linux    # Para Linux
make build-all       # Para plataforma atual
make clean          # Limpar arquivos de build
```

## 📋 Pré-requisitos

### Todos os métodos precisam:
- Python 3.8+
- pip (gerenciador de pacotes Python)

### Para Linux:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip ffmpeg

# Fedora/CentOS
sudo dnf install python3 python3-pip ffmpeg

# Arch Linux
sudo pacman -S python python-pip ffmpeg
```

### Para Windows:
- Baixar Python do [python.org](https://python.org)
- Instalar FFmpeg conforme instruções no README.md

## 🎯 Qual método usar?

| Método | Quando usar |
|--------|-------------|
| `simple_build.py` | Primeira vez, para testar |
| `build_linux.sh` | Build completo Linux |
| `build_windows.bat` | Build completo Windows |
| `quick_build.py` | Automação máxima |
| `Makefile` | Desenvolvimento contínuo |

## 📁 Arquivos Gerados

### Linux
- `dist/u2be_down` - Executável
- `u2be_down_linux.tar.gz` - Pacote portável
- `u2be-down_1.0.0_amd64.deb` - Pacote Debian
- Scripts `install.sh` e `uninstall.sh`

### Windows
- `dist/u2be_down.exe` - Executável
- `u2be_down_windows.zip` - Pacote portável
- `installer.nsi` - Script para NSIS
- `U2BeDown_Setup.exe` - Instalador (após compilar NSIS)

## 🔧 Instalação

### Linux - Método 1 (Pacote .deb)
```bash
sudo dpkg -i u2be-down_1.0.0_amd64.deb
```

### Linux - Método 2 (Script)
```bash
tar -xzf u2be_down_linux.tar.gz
sudo ./install.sh
```

### Linux - Método 3 (Portável)
```bash
tar -xzf u2be_down_linux.tar.gz
./u2be_down
```

### Windows - Método 1 (Instalador)
1. Execute `U2BeDown_Setup.exe`
2. Siga o assistente

### Windows - Método 2 (Portável)
1. Extraia `u2be_down_windows.zip`
2. Execute `u2be_down.exe`

## ❌ Solução de Problemas

### "Python não encontrado"
```bash
# Verificar se Python está instalado
python3 --version

# Se não estiver, instalar:
# Ubuntu/Debian: sudo apt install python3
# Fedora: sudo dnf install python3
# Windows: baixar de python.org
```

### "pip não encontrado"
```bash
# Linux
sudo apt install python3-pip  # Ubuntu/Debian
sudo dnf install python3-pip  # Fedora

# Windows: pip vem com Python
```

### "PyInstaller failed"
```bash
# Limpar cache e tentar novamente
rm -rf build/ dist/ __pycache__/
pip install --upgrade pyinstaller
python3 simple_build.py
```

### "Permission denied" (Linux)
```bash
# Dar permissão aos scripts
chmod +x *.sh *.py

# Para instalação
sudo ./install.sh
```

### FFmpeg não encontrado
```bash
# Linux
sudo apt install ffmpeg        # Ubuntu/Debian
sudo dnf install ffmpeg        # Fedora
sudo pacman -S ffmpeg          # Arch

# Windows: ver README.md para instruções detalhadas
```

## 🔄 Processo de Build Automatizado

Para criar instaladores para ambas as plataformas:

1. **No Linux:**
```bash
./build_linux.sh
```

2. **No Windows:**
```cmd
build_windows.bat
```

3. **Criar instalador Windows (após executar build_windows.bat):**
   - Instalar NSIS
   - Clicar com botão direito em `installer.nsi`
   - Selecionar "Compile NSIS Script"

## 📊 Comparação dos Métodos

| Característica | simple_build | build_linux.sh | quick_build.py |
|----------------|--------------|-----------------|----------------|
| Velocidade | ⚡⚡⚡ | ⚡⚡ | ⚡ |
| Simplicidade | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| Recursos | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Instaladores | ❌ | ✅ | ✅ |
| Auto-checagem | ❌ | ⭐ | ⭐⭐⭐ |

## 🚀 Começar Rapidamente

```bash
# 1. Clone o repositório
git clone <seu-repo>
cd u2be_down

# 2. Build simples (para testar)
python3 simple_build.py

# 3. Se funcionou, fazer build completo
./build_linux.sh    # Linux
# ou
build_windows.bat   # Windows
```

## 📞 Suporte

Se encontrar problemas:

1. Verifique os pré-requisitos
2. Execute `simple_build.py` primeiro
3. Verifique os logs de erro
4. Consulte a seção de solução de problemas
5. Abra uma issue no GitHub

---

**💡 Dica:** Comece sempre com `simple_build.py` para verificar se tudo está funcionando antes de usar os métodos mais avançados!
