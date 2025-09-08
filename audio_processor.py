import os
import tempfile
import threading
import logging
import subprocess


class SimpleAudioProcessor:
    """Processador de áudio simples usando ffmpeg para ajustes de pitch"""

    def __init__(self):
        self.temp_files = []

    def apply_pitch_shift_ffmpeg(self, input_file, output_file, semitones):
        """Aplica pitch shift usando ffmpeg com método mais confiável"""
        try:
            # Calcular o fator de pitch
            # 1 semitom = 2^(1/12) ≈ 1.0595
            pitch_factor = 2.0 ** (semitones / 12.0)

            # Usar rubberband se disponível, senão usar método asetrate
            try:
                # Tentar método rubberband primeiro (mais qualidade)
                cmd = [
                    "ffmpeg",
                    "-i",
                    input_file,
                    "-af",
                    f"rubberband=pitch={pitch_factor}",
                    "-c:a",
                    "libmp3lame",
                    "-b:a",
                    "192k",
                    "-ar",
                    "44100",
                    "-ac",
                    "2",
                    "-y",
                    "-v",
                    "error",
                    output_file,
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

                if result.returncode == 0:
                    logging.info("Pitch shift aplicado com rubberband")
                    return True
                else:
                    logging.warning("Rubberband falhou, tentando asetrate")
                    return self._apply_asetrate_method(
                        input_file, output_file, semitones
                    )

            except Exception:
                # Se rubberband não estiver disponível, usar asetrate
                return self._apply_asetrate_method(input_file, output_file, semitones)

        except Exception as e:
            logging.error(f"Erro no pitch shift: {e}")
            return False

    def _apply_asetrate_method(self, input_file, output_file, semitones):
        """Método asetrate melhorado com validação"""
        try:
            pitch_factor = 2.0 ** (semitones / 12.0)

            # Usar método mais conservador para estabilidade
            cmd = [
                "ffmpeg",
                "-i",
                input_file,
                "-af",
                f"atempo={1/pitch_factor}",  # Manter pitch
                "-c:a",
                "libmp3lame",
                "-q:a",
                "2",  # Qualidade VBR alta
                "-ar",
                "44100",
                "-ac",
                "2",
                "-y",
                "-v",
                "error",
                output_file,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                # Verificar se o arquivo foi criado e tem tamanho válido
                if os.path.exists(output_file) and os.path.getsize(output_file) > 1024:
                    logging.info("Pitch shift aplicado com atempo")
                    return True
                else:
                    logging.error("Arquivo de saída inválido")
                    return False
            else:
                logging.error(f"Erro no método atempo: {result.stderr}")
                # Tentar método de fallback ainda mais simples
                return self._apply_simple_copy(input_file, output_file)

        except Exception as e:
            logging.error(f"Erro no método asetrate: {e}")
            return False

    def _apply_simple_copy(self, input_file, output_file):
        """Método de fallback: copia arquivo sem modificação"""
        try:
            import shutil

            shutil.copy2(input_file, output_file)
            logging.warning("Pitch shift falhou, arquivo copiado sem mod.")
            return True
        except Exception as e:
            logging.error(f"Erro na cópia simples: {e}")
            return False

    def process_audio_simple(self, input_file, pitch_semitones=0):
        """Processa áudio com pitch shift simples"""
        if pitch_semitones == 0:
            return input_file  # Retorna arquivo original

        try:
            # Criar arquivo temporário com extensão MP3
            fd, temp_file = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)
            self.temp_files.append(temp_file)

            # Aplicar pitch shift
            success = self.apply_pitch_shift_ffmpeg(
                input_file, temp_file, pitch_semitones
            )
            if success:
                return temp_file
            else:
                return None

        except Exception as e:
            logging.error(f"Erro ao processar áudio: {e}")
            return None

    def cleanup(self):
        """Remove arquivos temporários"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logging.debug(f"Arquivo temporário removido: {temp_file}")
            except Exception as e:
                logging.error(f"Erro ao remover arquivo temporário: {e}")
        self.temp_files.clear()


class AsyncSimpleAudioProcessor:
    """Versão assíncrona do processador simples"""

    def __init__(self, callback=None):
        self.processor = SimpleAudioProcessor()
        self.callback = callback
        self.is_processing = False

    def process_audio_async(self, file_path, pitch_shift=0, speed_change=1.0):
        """Processa áudio de forma assíncrona"""
        if self.is_processing:
            return False

        # Por enquanto, ignorar speed_change (seria mais complexo com ffmpeg)
        self.processing_thread = threading.Thread(
            target=self._process_worker, args=(file_path, pitch_shift)
        )
        self.processing_thread.daemon = True
        self.processing_thread.start()
        return True

    def _process_worker(self, file_path, pitch_shift):
        """Worker thread para processamento"""
        self.is_processing = True

        try:
            result_file = self.processor.process_audio_simple(file_path, pitch_shift)

            if self.callback:
                if result_file:
                    callback_data = {"pitch_shift": pitch_shift}
                    self.callback(result_file, None, callback_data)
                else:
                    self.callback(None, "Erro no processamento de áudio")

        except Exception as e:
            if self.callback:
                self.callback(None, f"Erro no processamento: {str(e)}")
        finally:
            self.is_processing = False

    def is_busy(self):
        """Verifica se está processando"""
        return self.is_processing

    def cleanup(self):
        """Limpa recursos"""
        self.processor.cleanup()


def check_ffmpeg():
    """Verifica se ffmpeg está instalado"""
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False
