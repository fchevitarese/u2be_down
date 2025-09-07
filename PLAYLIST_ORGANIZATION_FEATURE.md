# 📁 Funcionalidade de Organização por Playlists

## 🎯 Objetivo
Organizar automaticamente os downloads em diretórios específicos quando o download for de uma playlist do YouTube.

## ✨ Funcionalidades Implementadas

### 1. **Detecção Automática de Playlists**
- O sistema agora identifica automaticamente quando uma URL é de uma playlist
- Extrai o nome da playlist e informações dos vídeos contidos
- Marca cada vídeo com informações sobre sua playlist de origem

### 2. **Criação Automática de Diretórios**
- Quando uma playlist é detectada, o sistema cria automaticamente um subdiretório
- Nome do diretório baseado no título da playlist
- Sanitização automática para remover caracteres inválidos

### 3. **Interface Visual Melhorada**
- Downloads de playlists mostram `[📁 Nome da Playlist]` no título
- Facilita identificação visual de conteúdo de playlists
- Mantém organização clara na interface

## 🔧 Implementação Técnica

### **Modificações Principais:**

#### `main.py`:
1. **Nova função `sanitize_folder_name()`**:
   ```python
   def sanitize_folder_name(name):
       # Remove caracteres inválidos: <>:"/\|?*
       # Remove espaços duplos e limita tamanho
       # Retorna nome seguro para diretório
   ```

2. **`extract_video_info()` aprimorada**:
   ```python
   # Agora detecta playlists e adiciona:
   {
       "playlist_title": "Nome da Playlist",
       "playlist_uploader": "Canal",
       "is_playlist": True
   }
   ```

3. **`download_single_video()` modificada**:
   ```python
   # Recebe video_info com dados da playlist
   # Cria diretório baseado no nome da playlist
   # Faz download no diretório específico
   ```

#### `gui.py`:
1. **Exibição melhorada de títulos**:
   ```python
   # Mostra: "Nome do Vídeo [📁 Nome da Playlist]"
   display_title = f"{title} [📁 {playlist_title}]"
   ```

## 📂 Estrutura de Diretórios Resultante

### **Antes** (downloads individuais):
```
📁 Downloads/
├── Video 1.mp3
├── Video 2.mp3
└── Video 3.mp3
```

### **Depois** (com playlists):
```
📁 Downloads/
├── Video Individual.mp3
├── 📁 Minha Playlist Favorita/
│   ├── Video 1 da Playlist.mp3
│   ├── Video 2 da Playlist.mp3
│   └── Video 3 da Playlist.mp3
└── 📁 Outra Playlist/
    ├── Video A.mp3
    └── Video B.mp3
```

## 🎮 Como Usar

### **1. Download de Playlist**:
1. Cole a URL da playlist no campo de URL
2. Clique em "Analisar URLs"
3. O sistema detectará automaticamente que é uma playlist
4. Títulos aparecerão como: `"Video X [📁 Nome da Playlist]"`
5. Clique em "Download" - arquivos serão salvos na pasta da playlist

### **2. Exemplos de URLs de Playlist**:
```
https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxx
https://youtube.com/watch?v=ABC123&list=PLxxxxxxxxxxxxxx
```

## 🔍 Funcionalidades de Sanitização

### **Caracteres Removidos**:
- `< > : " / \ | ? *` (caracteres inválidos para nomes de pasta)
- Espaços duplos são convertidos em espaços únicos
- Espaços nas bordas são removidos

### **Exemplos**:
```
Entrada: "My Awesome<>: Playlist|?*"
Saída:   "My Awesome Playlist"

Entrada: "  Nome   com    Espaços  "
Saída:   "Nome com Espaços"

Entrada: "Nome Muito Longo Que Excede o Limite..."
Saída:   "Nome Muito Longo Que Excede o Lim" (truncado em 100 chars)
```

## ⚡ Benefícios

### **Organização**:
- ✅ Separação clara entre downloads individuais e de playlists
- ✅ Facilita localização de arquivos específicos
- ✅ Mantém contexto original da playlist

### **Usabilidade**:
- ✅ Processo totalmente automático
- ✅ Não interfere com downloads individuais
- ✅ Interface visual clara para identificação

### **Compatibilidade**:
- ✅ Mantém compatibilidade com downloads individuais
- ✅ Sistema de fallback em caso de erro na criação de diretório
- ✅ Funciona com todas as funcionalidades existentes

## 🚀 Próximos Passos Sugeridos

1. **Configuração Opcional**: Permitir ao usuário desabilitar organização por playlist
2. **Nomenclatura Customizada**: Templates para nomes de diretórios
3. **Subpastas por Uploader**: Organizar também por canal do criador
4. **Limpeza de Diretórios Vazios**: Remover pastas vazias automaticamente

---

## 📊 Status da Implementação

- [x] ✅ Detecção automática de playlists
- [x] ✅ Criação de diretórios sanitizados
- [x] ✅ Download organizado por playlist
- [x] ✅ Interface visual atualizada
- [x] ✅ Compatibilidade com sistema existente
- [x] ✅ Testes básicos realizados

**Funcionalidade 100% implementada e pronta para uso!** 🎉
