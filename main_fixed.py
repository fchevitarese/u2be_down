import argparse
import logging
import os
import shutil
import concurrent.futures
from threading import Lock

from moviepy.editor import VideoFileClip
from yt_dlp import YoutubeDL
from config import load_config, add_download_to_history, update_download_status

# Lock para operações thread-safe no histórico
history_lock = Lock()


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
                            }
                        )
                logging.info(f"Playlist detectada com {len(videos)} vídeos")
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
    url, output_path, convert_to_mp3=False, progress_callback=None
):
    """Download de um único vídeo com progresso real das duas fases"""

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

    ydl_opts = {
        "format": "best",
        "outtmpl": os.path.join(output_path, "%(title)s.%(ext)s"),
        "progress_hooks": [enhanced_progress_hook] if progress_callback else [],
        "ignoreerrors": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            # Download do vídeo
            info_dict = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info_dict)

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
        logging.error(f"Erro no download de {url}: {e}")
        return False, str(e)


def download_video_safe(args):
    """Wrapper thread-safe para download_single_video"""
    video_info, download_path, to_mp3, progress_callback = args
    url = video_info["url"]
    title = video_info["title"]

    # Thread-safe update do status
    with history_lock:
        update_download_status(url, "downloading")

    try:
        # Callback de progresso thread-safe
        def safe_progress_callback(data):
            if progress_callback:
                progress_callback(url, data)

        success, result = download_single_video(
            url,
            download_path,
            convert_to_mp3=to_mp3,
            progress_callback=safe_progress_callback,
        )

        # Thread-safe update do status
        with history_lock:
            if success:
                update_download_status(url, "completed", result)
                logging.info(f"✅ Download concluído: {title}")
            else:
                update_download_status(url, "failed", error_msg=result)
                logging.error(f"❌ Download falhou: {title} - {result}")

        return success

    except Exception as e:
        logging.error(f"Erro no wrapper de download de {url}: {e}")
        with history_lock:
            update_download_status(url, "failed", error_msg=str(e))
        return False


def download_videos_parallel(
    videos_info, download_path, to_mp3=True, max_workers=2, progress_callback=None
):
    """Download múltiplos vídeos em paralelo"""
    # Prepara os argumentos para cada download
    download_args = [
        (video_info, download_path, to_mp3, progress_callback)
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
        url, output_path, convert_to_mp3, progress_callback
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
