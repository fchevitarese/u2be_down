#!/usr/bin/env python3
"""
Teste específico para debug de URL parsing
"""
import os
import sys

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_url_parsing():
    """Testa o parsing de uma URL específica"""
    print("🧪 Testando parsing de URL...")
    
    # URL de teste - vamos usar uma URL simples do YouTube
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - sempre funciona!
    
    try:
        from main import extract_video_info
        print(f"📝 Testando URL: {test_url}")
        
        videos = extract_video_info(test_url)
        
        if videos:
            print(f"✅ Parse funcionou! Encontrados {len(videos)} vídeos:")
            for i, video in enumerate(videos[:3]):  # Mostrar apenas os primeiros 3
                print(f"   {i+1}. {video.get('title', 'N/A')} - {video.get('uploader', 'N/A')}")
            return True
        else:
            print("❌ Parse não retornou vídeos")
            return False
            
    except Exception as e:
        print(f"❌ Erro no parsing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_parse_parallel():
    """Testa a função de parsing paralelo"""
    print("\n🧪 Testando parsing paralelo...")
    
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=ZbZSe6N_BXs"  # PHP não é melhor que Python
    ]
    
    try:
        from main import parse_urls_parallel
        print(f"📝 Testando {len(test_urls)} URLs em paralelo...")
        
        videos = parse_urls_parallel(test_urls, max_workers=2)
        
        if videos:
            print(f"✅ Parse paralelo funcionou! Total: {len(videos)} vídeos")
            return True
        else:
            print("❌ Parse paralelo não retornou vídeos")
            return False
            
    except Exception as e:
        print(f"❌ Erro no parsing paralelo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Teste de Debug - URL Parsing")
    print("=" * 50)
    
    single_ok = test_url_parsing()
    parallel_ok = test_parse_parallel()
    
    print("\n" + "=" * 50)
    if single_ok and parallel_ok:
        print("✅ Parsing está funcionando! O problema deve estar na interface.")
        print("\n💡 Sugestões:")
        print("   1. Verifique se você está clicando no botão correto")
        print("   2. Verifique se há uma pasta de download selecionada")
        print("   3. Verifique se há erro no console da GUI")
    else:
        print("❌ Há problemas no parsing de URLs")
