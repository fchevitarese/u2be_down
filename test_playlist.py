#!/usr/bin/env python3

"""
Teste de funcionalidade de playlist
"""

import sys

sys.path.append(".")

from main import extract_video_info, parse_urls_parallel


def test_playlist_detection():
    """Testa detecção de playlist"""

    # URL de exemplo de playlist do YouTube (pequena e pública)
    playlist_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDMM"

    print("🧪 Testando detecção de playlist...")
    print(f"URL: {playlist_url}")

    # Teste 1: extract_video_info
    print("\n1️⃣ Testando extract_video_info:")
    videos = extract_video_info(playlist_url)
    print(f"   Vídeos encontrados: {len(videos)}")

    if videos:
        print(f"   Primeiro vídeo: {videos[0].get('title', 'N/A')}")
        print(f"   É playlist: {videos[0].get('is_playlist', False)}")
        if videos[0].get("is_playlist"):
            print(f"   Título da playlist: {videos[0].get('playlist_title', 'N/A')}")

    # Teste 2: parse_urls_parallel
    print("\n2️⃣ Testando parse_urls_parallel:")
    videos_parallel = parse_urls_parallel([playlist_url])
    print(f"   Vídeos encontrados: {len(videos_parallel)}")

    if videos_parallel:
        print(f"   Primeiro vídeo: {videos_parallel[0].get('title', 'N/A')}")
        print(f"   É playlist: {videos_parallel[0].get('is_playlist', False)}")

    # Teste 3: URL individual
    print("\n3️⃣ Testando URL individual:")
    single_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    videos_single = extract_video_info(single_url)
    print(f"   URL: {single_url}")
    print(f"   Vídeos encontrados: {len(videos_single)}")

    if videos_single:
        print(f"   Título: {videos_single[0].get('title', 'N/A')}")
        print(f"   É playlist: {videos_single[0].get('is_playlist', False)}")


if __name__ == "__main__":
    test_playlist_detection()
