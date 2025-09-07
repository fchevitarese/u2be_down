#!/usr/bin/env python3
"""Teste da função de parse sem a GUI"""

from main import parse_urls_and_extract_info
from config import add_download_to_history, load_downloads_history


def test_parse():
    print("=== Teste da função parse_urls_and_extract_info ===")

    # Teste com uma URL simples
    test_url = "https://www.youtube.com/watch?v=3JZ_D3ELwOQ"
    print(f"\nTestando com URL: {test_url}")

    try:
        videos = parse_urls_and_extract_info(test_url)
        print(f"Encontrados {len(videos)} vídeos:")

        for i, video in enumerate(videos):
            print(f"{i+1}. {video['title']}")
            print(f"   URL: {video['url']}")
            print(f"   Duração: {video.get('duration', 'Desconhecida')} segundos")

            # Adiciona ao histórico com status "pending"
            add_download_to_history(video["title"], video["url"], "", "pending")
            print("   ✓ Adicionado ao histórico com status 'pending'")
            print()

        print("=== Histórico de Downloads ===")
        history = load_downloads_history()
        print(f"Total de itens no histórico: {len(history)}")

        pending_items = [item for item in history if item.get("status") == "pending"]
        print(f"Itens pendentes: {len(pending_items)}")

        for item in pending_items[-3:]:  # Mostra os últimos 3 itens pendentes
            print(f"- {item['title']} [{item['status']}]")

    except Exception as e:
        print(f"Erro: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_parse()
