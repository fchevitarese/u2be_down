# 🎵 Funcionalidades de Playlist - U2Be Down

Este documento detalha como utilizar as funcionalidades avançadas de playlist do U2Be Down.

## 🎯 Como Funciona

O U2Be Down possui **detecção automática** de playlists do YouTube, processando todos os vídeos automaticamente sem configuração adicional.

### ✅ URLs Suportadas

#### 📋 Playlists Completas
```
https://www.youtube.com/playlist?list=PLxxxxxx
https://www.youtube.com/watch?v=VIDEO_ID&list=PLxxxxxx
```

#### 🎵 Mixes e Radio
```
https://www.youtube.com/watch?v=VIDEO_ID&list=RDMM    # Mix personalizado
https://www.youtube.com/watch?v=VIDEO_ID&list=RD      # Radio baseado no vídeo
```

#### 📺 Playlists de Canal
```
https://www.youtube.com/watch?v=VIDEO_ID&list=UU...   # Uploads do canal
https://www.youtube.com/watch?v=VIDEO_ID&list=PL...   # Playlist pública
```

## 🖥️ Usando na GUI

### 1. Parse de URLs (Recomendado)

1. **Cole a URL da playlist** na área de texto principal
2. **Clique em "Parse URLs"** (não "Download Agora")
3. **Aguarde o processamento** - verá todos os vídeos sendo listados
4. **Verifique a lista** de downloads detectados
5. **Clique em "Download Agora"** para baixar todos

```
📝 Área de texto:
https://www.youtube.com/playlist?list=PLxxxxxx

🔍 Clique "Parse URLs" primeiro ← IMPORTANTE!
```

### 2. Download Direto (Alternativo)

1. **Cole a URL da playlist**
2. **Configure as opções** (MP3, diretório, etc.)
3. **Clique em "Download Agora"**
4. **Aguarde** - processará automaticamente todos os vídeos

## 📁 Organização Automática

### Estrutura de Pastas

O U2Be Down organiza automaticamente por playlist:

```
downloads/
├── My Mix/                    ← Nome da playlist
│   ├── Música 1.mp3
│   ├── Música 2.mp3
│   └── ...
├── Playlist Favoritas/        ← Outra playlist
│   ├── Video 1.mp3
│   └── ...
└── vídeo_individual.mp3       ← Vídeos únicos na raiz
```

### 🏷️ Metadados Preservados

Para cada vídeo de playlist, são preservados:
- ✅ **Título da playlist**
- ✅ **Criador da playlist**
- ✅ **Título do vídeo**
- ✅ **Canal original**
- ✅ **Duração**
- ✅ **Organização automática**

## 💻 Linha de Comando

### Downloads Básicos
```bash
# Playlist completa
python3 main.py "https://www.youtube.com/playlist?list=PLxxxxxx"

# Com conversão para MP3
python3 main.py --mp3 "https://www.youtube.com/playlist?list=PLxxxxxx"

# Diretório personalizado
python3 main.py -o "/caminho/downloads" "URL_PLAYLIST"
```

### Múltiplas URLs
```bash
# Arquivo com URLs (uma por linha)
python3 main.py -f urls.txt

# Múltiplas na linha de comando
python3 main.py "URL1" "URL2" "URL3"
```

## ⚡ Processamento Paralelo

### Como Funciona
- **3 workers simultâneos** por padrão
- **Parse paralelo** de URLs diferentes
- **Download paralelo** de múltiplos vídeos
- **Processamento otimizado** para playlists grandes

### Configuração
```python
# No código (config.py)
"max_parallel_downloads": 3,    # Downloads simultâneos
"max_parse_workers": 3,         # Parse simultâneo
```

## 🔧 Solução de Problemas

### ❌ "Playlist não detectada"

**Possíveis causas:**
1. **URL incorreta** - verifique se contém `list=`
2. **Playlist privada** - deve ser pública ou não listada
3. **Playlist vazia** - sem vídeos disponíveis
4. **Região bloqueada** - alguns vídeos podem não estar disponíveis

**Solução:**
```bash
# Teste a URL manualmente
python3 test_playlist.py  # Modifique a URL no arquivo
```

### ❌ "Poucos vídeos detectados"

**Possíveis causas:**
1. **Mix dinâmico** - playlists de "Mix" variam em tamanho
2. **Vídeos privados** - removidos ou privados na playlist
3. **Limite de região** - alguns vídeos não disponíveis

**Verificação:**
- Abra a playlist no navegador
- Conte quantos vídeos estão realmente disponíveis
- Compare com o resultado do U2Be Down

### ❌ "Download lento"

**Otimizações:**
1. **Reduza workers paralelos** se internet for lenta
2. **Use SSD** para downloads (não HD mecânico)
3. **Feche outros programas** que usam internet
4. **Configure qualidade menor** se necessário

## 📊 Recursos Avançados

### 🎛️ Player Interno
- ✅ **Reproduz playlists completas**
- ✅ **Controles de pitch/velocidade**
- ✅ **Navegação entre faixas**
- ✅ **Shuffle e repeat**

### 📈 Histórico e Progresso
- ✅ **Acompanha download** de cada vídeo
- ✅ **Retoma downloads** interrompidos
- ✅ **Histórico completo** de atividades
- ✅ **Limpeza automática** de concluídos

### 🔄 Atualizações Automáticas
- ✅ **Detecta novos vídeos** em playlists conhecidas
- ✅ **Evita downloads duplicados**
- ✅ **Organização consistente**

## 💡 Dicas de Uso

### 🚀 Para Playlists Grandes (100+ vídeos)
1. **Use "Parse URLs" primeiro** - para visualizar tudo
2. **Configure diretório com espaço** suficiente
3. **Deixe rodar durante a noite** para playlists muito grandes
4. **Monitore o progresso** na aba Downloads

### 🎵 Para Mixes Musicais
1. **URLs com `RDMM`** geram playlists personalizadas
2. **Tamanho varia** (50-200 músicas típico)
3. **Qualidade alta** - ideal para coleções
4. **Organização automática** por gênero/artista

### 📺 Para Canais/Creators
1. **Use URLs de uploads** (`UU...`) para canal completo
2. **Playlists públicas** (`PL...`) para coleções específicas
3. **Configurações de qualidade** importantes para vídeos longos

## 🆘 Suporte

Se as funcionalidades de playlist não estiverem funcionando como esperado:

1. **Verifique os logs** no terminal/console
2. **Teste com playlist pequena** primeiro (5-10 vídeos)
3. **Use `test_playlist.py`** para debug
4. **Reporte problemas** com URL específica e logs

### Debug Manual
```bash
# Ativar logs detalhados
python3 gui.py --debug

# Teste específico
python3 test_playlist.py  # Modifique URL de teste
```

---

📝 **Última atualização:** Setembro 2025
🔗 **Versão:** 1.0.2+
📋 **Funcionalidades testadas:** Playlists públicas, Mixes, Radio, URLs individuais
