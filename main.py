import argparse
import concurrent.futures
import logging
import os
import re
import shutil
from threading import Lock

from yt_dlp import YoutubeDL

from config import add_download_to_history, load_config, update_download_status

# Lock para operações thread-safe no histórico
history_lock = Lock()


def sanitize_folder_name(name):
    """Sanitiza nome de pasta removendo caracteres inválidos"""
    # Remove caracteres inválidos para nomes de arquivo/pasta
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    # Remove espaços duplos e espaços nas bordas
    name = re.sub(r"\s+", " ", name).strip()
    # Limita o tamanho do nome
    if len(name) > 100:
        name = name[:100].strip()
    return name or "Unknown"


def extract_video_info(url):
    """Extrai informações de vídeo(s) de uma URL (suporta playlists)"""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "extract_flat": True,  # Para playlists
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)

            if info_dict and "entries" in info_dict and info_dict["entries"]:
                # É uma playlist
                playlist_title = info_dict.get("title", "Unknown Playlist")
                playlist_uploader = info_dict.get("uploader", "Unknown")

                videos = []
                for entry in info_dict["entries"]:
                    if entry and "id" in entry:
                        videos.append(
                            {
                                "title": entry.get("title", "Unknown"),
                                "url": entry.get(
                                    "webpage_url",
                                    f"https://www.youtube.com/watch?v={entry['id']}",
                                ),
                                "duration": entry.get("duration", 0),
                                "uploader": entry.get("uploader", "Unknown"),
                                "playlist_title": playlist_title,
                                "playlist_uploader": playlist_uploader,
                                "is_playlist": True,
                            }
                        )
                logging.info(
                    f"Playlist detectada: '{playlist_title}' com {len(videos)} vídeos"
                )
                return videos
            else:
                # É um vídeo individual
                if info_dict:
                    title = info_dict.get("title", "Unknown")
                    return [
                        {
                            "title": title,
                            "url": url,
                            "duration": info_dict.get("duration", 0),
                            "uploader": info_dict.get("uploader", "Unknown"),
                            "is_playlist": False,
                        }
                    ]
                return []
    except Exception as e:
        logging.error(f"Erro ao extrair info de {url}: {e}")
        return []


def parse_urls_and_extract_info(urls):
    """Parse uma ou mais URLs e extrai informações de todos os vídeos"""
    if isinstance(urls, str):
        urls = [urls]

    all_videos = []
    for url in urls:
        videos = extract_video_info(url)
        all_videos.extend(videos)

    logging.info(f"Total de vídeos encontrados: {len(all_videos)}")
    return all_videos


def convert_video_to_mp3(video_path, progress_callback=None):
    """Converte vídeo para MP3 com callback de progresso"""
    try:
        # Import apenas quando necessário para evitar problemas no PyInstaller
        from moviepy.video.io.VideoFileClip import VideoFileClip
        
        if progress_callback:
            progress_callback(
                {
                    "status": "converting",
                    "phase": "conversion",
                    "percent": 80,
                    "message": "Carregando arquivo de vídeo...",
                }
            )

        video_clip = VideoFileClip(video_path)
        audio_path = os.path.splitext(video_path)[0] + ".mp3"

        if progress_callback:
            progress_callback(
                {
                    "status": "converting",
                    "phase": "conversion",
                    "percent": 90,
                    "message": "Convertendo áudio...",
                }
            )

        if video_clip.audio:
            video_clip.audio.write_audiofile(audio_path)
        video_clip.close()

        if progress_callback:
            progress_callback(
                {
                    "status": "converting",
                    "phase": "conversion",
                    "percent": 95,
                    "message": "Finalizando conversão...",
                }
            )

        print(f"Converted to MP3: {audio_path}")
        return audio_path
    except OSError as e:
        logging.error(f"MoviePy error: the file {video_path} could not be found! {e}")
        print(f"MoviePy error: the file {video_path} could not be found! {e}")
        return None


def download_single_video(
    url, output_path, convert_to_mp3=False, keep_video=False, progress_callback=None, video_info=None
):
    """Download de um único vídeo com progresso real das duas fases

    Args:
        url: URL do vídeo
        output_path: Caminho base de download
        convert_to_mp3: Se deve converter para MP3
        keep_video: Se deve manter o arquivo de vídeo original após conversão
        progress_callback: Callback para progresso
        video_info: Informações do vídeo (incluindo dados de playlist)
    """

    def enhanced_progress_hook(d):
        """Hook de progresso melhorado que considera download + conversão"""
        if progress_callback:
            if d["status"] == "downloading":
                # Fase 1: Download (0-70% do progresso total)
                if "downloaded_bytes" in d and "total_bytes" in d:
                    download_percent = (d["downloaded_bytes"] / d["total_bytes"]) * 100
                    total_percent = download_percent * 0.7  # 70% para download
                    progress_callback(
                        {
                            "status": "downloading",
                            "phase": "download",
                            "percent": total_percent,
                            "downloaded_bytes": d.get("downloaded_bytes", 0),
                            "total_bytes": d.get("total_bytes", 0),
                            "speed": d.get("speed", 0),
                        }
                    )
            elif d["status"] == "finished":
                # Download terminou, indo para conversão se necessário
                if convert_to_mp3:
                    progress_callback(
                        {
                            "status": "converting",
                            "phase": "conversion",
                            "percent": 70,  # Download completo = 70%
                            "message": "Convertendo para MP3...",
                        }
                    )
                else:
                    progress_callback({"status": "finished", "percent": 100})

    # Determina o diretório de download baseado em playlist
    final_output_path = output_path

    if video_info and video_info.get("is_playlist", False):
        # Cria subdiretório para playlist
        playlist_title = video_info.get("playlist_title", "Unknown Playlist")
        sanitized_name = sanitize_folder_name(playlist_title)
        playlist_dir = os.path.join(output_path, sanitized_name)

        # Cria o diretório se não existir
        try:
            os.makedirs(playlist_dir, exist_ok=True)
            final_output_path = playlist_dir
            logging.info(f"Criado diretório da playlist: {playlist_dir}")
        except OSError as e:
            logging.warning(f"Erro ao criar diretório da playlist: {e}")
            # Continua com diretório original em caso de erro

    # Formato com fallbacks para maior compatibilidade
    # 1. Tenta best (melhor qualidade com áudio+vídeo)
    # 2. Se falhar, tenta bestvideo+bestaudio/best (combina melhor vídeo e áudio)
    # 3. Se falhar, tenta worst (pior qualidade, mas sempre disponível)
    format_selector = "best[height<=1080]/bestvideo[height<=1080]+bestaudio/best/worst"
    
    ydl_opts = {
        "format": format_selector,
        "outtmpl": os.path.join(final_output_path, "%(title)s.%(ext)s"),
        "progress_hooks": [enhanced_progress_hook] if progress_callback else [],
        "ignoreerrors": False,  # Mudamos para False para capturar erros
        "no_warnings": False,  # Ativar warnings para debug
        "merge_output_format": "mp4",  # Força saída em MP4 quando combina formatos
    }

    try:
        logging.info(f"Iniciando download de: {url}")
        logging.info(f"Diretório de saída: {final_output_path}")

        with YoutubeDL(ydl_opts) as ydl:
            # Download do vídeo
            logging.info(f"Extraindo informações para: {url}")
            info_dict = ydl.extract_info(url, download=True)

            # Verifica se info_dict é válido
            if not info_dict:
                logging.error(f"Erro: yt-dlp retornou None para {url}")
                return False, "yt-dlp não conseguiu extrair informações do vídeo"

            logging.info(f"Informações extraídas com sucesso para: {url}")
            video_path = ydl.prepare_filename(info_dict)
            logging.info(f"Caminho preparado: {video_path}")

            # Verifica se o arquivo foi realmente baixado
            if not video_path or not os.path.exists(video_path):
                logging.error(f"Arquivo não encontrado após download: {video_path}")
                return False, f"Arquivo não foi baixado: {video_path}"

            final_path = video_path
            if convert_to_mp3:
                # Fase 2: Conversão (70-100% do progresso total)
                if progress_callback:
                    progress_callback(
                        {
                            "status": "converting",
                            "phase": "conversion",
                            "percent": 75,
                            "message": "Iniciando conversão para MP3...",
                        }
                    )

                mp3_path = convert_video_to_mp3(video_path, progress_callback)
                if mp3_path:
                    final_path = mp3_path
                    if not keep_video:  # Só remove se não quiser manter o vídeo
                        try:
                            os.remove(video_path)  # Remove vídeo original
                        except FileNotFoundError:
                            pass

                    # Conversão concluída
                    if progress_callback:
                        progress_callback(
                            {
                                "status": "finished",
                                "phase": "completed",
                                "percent": 100,
                                "message": "Conversão concluída!",
                            }
                        )

            logging.info(f"Download bem-sucedido: {final_path}")
            return True, final_path

    except Exception as e:
        error_msg = str(e)
        logging.error(f"Erro no download de {url}: {error_msg}")
        
        # Se o erro é sobre formato não disponível, tenta com formato mais básico
        if "Requested format is not available" in error_msg or "format" in error_msg.lower():
            logging.info(f"Tentando download com formato de fallback para: {url}")
            try:
                # Fallback com formato mais simples
                fallback_ydl_opts = {
                    "format": "worst",  # Formato mais básico, sempre disponível
                    "outtmpl": os.path.join(final_output_path, "%(title)s.%(ext)s"),
                    "progress_hooks": [enhanced_progress_hook] if progress_callback else [],
                    "ignoreerrors": False,
                    "no_warnings": False,
                }
                
                with YoutubeDL(fallback_ydl_opts) as ydl_fallback:
                    logging.info(f"Tentativa de fallback para: {url}")
                    info_dict = ydl_fallback.extract_info(url, download=True)
                    
                    if not info_dict:
                        return False, "Fallback: yt-dlp não conseguiu extrair informações do vídeo"
                    
                    video_path = ydl_fallback.prepare_filename(info_dict)
                    
                    if not video_path or not os.path.exists(video_path):
                        return False, f"Fallback: Arquivo não foi baixado: {video_path}"
                    
                    final_path = video_path
                    if convert_to_mp3:
                        mp3_path = convert_video_to_mp3(video_path, progress_callback)
                        if mp3_path:
                            final_path = mp3_path
                            if not keep_video:  # Só remove se não quiser manter o vídeo
                                try:
                                    os.remove(video_path)
                                except FileNotFoundError:
                                    pass
                    
                    logging.info(f"Download de fallback bem-sucedido: {final_path}")
                    return True, final_path
                    
            except Exception as fallback_error:
                logging.error(f"Erro no download de fallback de {url}: {fallback_error}")
                return False, f"Ambos os métodos falharam. Original: {error_msg}, Fallback: {str(fallback_error)}"
        
        return False, error_msg


def download_video_safe(args):
    """Wrapper thread-safe para download_single_video"""
    video_info, download_path, to_mp3, keep_video, progress_callback = args
    url = video_info["url"]
    title = video_info["title"]

    # Cria wrapper para o progress_callback que inclui a URL
    def wrapped_progress_callback(data):
        if progress_callback:
            progress_callback(url, data)

    # Thread-safe update do status
    with history_lock:
        update_download_status(url, "downloading")

    try:
        # Passa video_info para download_single_video para informações de playlist
        success, result = download_single_video(
            url, download_path, to_mp3, keep_video, wrapped_progress_callback, video_info
        )

        if success:
            with history_lock:
                update_download_status(url, "completed", file_path=result)
            logging.info(f"✅ Download concluído: {title}")
            return True
        else:
            with history_lock:
                update_download_status(url, "failed", error_msg=result)
            logging.error(f"❌ Erro no download de {title}: {result}")
            return False

    except Exception as e:
        logging.error(f"Erro no wrapper de download de {url}: {e}")
        with history_lock:
            update_download_status(url, "failed", error_msg=str(e))
        return False


def download_videos_parallel(
    videos_info, download_path, to_mp3=True, keep_video=False, max_workers=2, progress_callback=None
):
    """Download múltiplos vídeos em paralelo"""
    # Prepara os argumentos para cada download
    download_args = [
        (video_info, download_path, to_mp3, keep_video, progress_callback)
        for video_info in videos_info
    ]

    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submete todas as tarefas de download
        future_to_video = {
            executor.submit(download_video_safe, args): args[0]
            for args in download_args
        }

        # Coleta os resultados conforme ficam prontos
        for future in concurrent.futures.as_completed(future_to_video):
            video_info = future_to_video[future]
            try:
                success = future.result()
                results.append((video_info, success))
                status = "completado" if success else "falhou"
                logging.info(f"Download {status}: {video_info['title']}")
            except Exception as e:
                logging.error(f"Erro no download de {video_info['title']}: {e}")
                results.append((video_info, False))

    return results


def parse_urls_parallel(urls, max_workers=3):
    """Parse de múltiplas URLs em paralelo"""
    if isinstance(urls, str):
        urls = [urls]

    all_videos = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submete todas as tarefas de parse
        future_to_url = {executor.submit(extract_video_info, url): url for url in urls}

        # Coleta os resultados
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                videos = future.result()
                all_videos.extend(videos)
                logging.info(f"Parse completo para: {url}")
            except Exception as e:
                logging.error(f"Erro no parse de {url}: {e}")

    logging.info(f"Parse paralelo concluído: {len(all_videos)} vídeos")
    return all_videos


def set_ffmpeg_path():
    if not os.getenv("IMAGEIO_FFMPEG_EXE"):
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_path
        else:
            raise RuntimeError(
                "No ffmpeg exe could be found. Install ffmpeg on your system, "
                "or set the IMAGEIO_FFMPEG_EXE environment variable"
            )


def download_video(
    url, output_path, convert_to_mp3=False, keep_video=False, progress_callback=None
):
    """Função de download básica (compatibilidade)"""
    success, result = download_single_video(
        url, output_path, convert_to_mp3, keep_video, progress_callback
    )
    return success


def download_from_file(
    file_path,
    output_path,
    convert_to_mp3=False,
    keep_video=False,
    progress_callback=None,
):
    """Download de URLs de um arquivo"""
    with open(file_path, "r") as file:
        urls = file.readlines()

    for url in urls:
        if url.strip():
            download_video(
                url.strip(), output_path, convert_to_mp3, keep_video, progress_callback
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download YouTube videos")
    parser.add_argument("url", help="YouTube video or playlist URL")
    parser.add_argument("-o", "--output", help="Output directory", default=".")
    parser.add_argument("--mp3", action="store_true", help="Convert video to MP3")
    parser.add_argument("--keep-video", action="store_true", help="Keep video file")

    args = parser.parse_args()

    set_ffmpeg_path()
    logging.basicConfig(level=logging.INFO)

    download_video(
        args.url,
        args.output,
        convert_to_mp3=args.mp3,
        keep_video=args.keep_video,
    )
