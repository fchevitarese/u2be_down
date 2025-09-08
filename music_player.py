import os
import random
from pathlib import Path
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSlider,
    QListWidget,
    QListWidgetItem,
    QGroupBox,
    QSplitter,
    QMessageBox,
    QFileDialog,
    QSpinBox,
)
from PyQt5.QtGui import QFont
import pygame
from mutagen.mp3 import MP3
import logging
from audio_processor import AsyncSimpleAudioProcessor, check_ffmpeg


class MusicPlayer(QWidget):
    """Player de música interno com controles completos"""

    def __init__(self, downloads_path="downloads"):
        super().__init__()

        # Verificar se ffmpeg está disponível
        self.ffmpeg_available = check_ffmpeg()
        if not self.ffmpeg_available:
            warning_msg = "FFmpeg não encontrado. " "Controles de pitch desabilitados."
            logging.warning(warning_msg)

        self.downloads_path = downloads_path
        self.current_song = None
        self.current_index = 0
        self.playlist = []
        self.is_playing = False
        self.is_paused = False
        self.position = 0
        self.duration = 0
        self.volume = 0.7
        self.shuffle_mode = False
        self.repeat_mode = False

        # Controles de pitch e velocidade
        self.current_pitch = 0  # Em semitons
        self.current_speed = 1.0
        self.processed_file = None
        self.has_processed_audio = False  # Para controlar botão salvar

        # Processador de áudio
        self.audio_processor = AsyncSimpleAudioProcessor(self.on_audio_processed)

        # Inicializar pygame mixer
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)

        self.init_ui()
        self.load_music_library()

        # Timer para atualizar posição da música
        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self.update_position)
        self.position_timer.start(1000)  # Atualiza a cada segundo

    def init_ui(self):
        """Inicializa a interface do player"""
        layout = QVBoxLayout()

        # Título do player
        title_label = QLabel("🎵 Player Interno")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Splitter principal
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Painel esquerdo - Biblioteca de músicas
        library_widget = QWidget()
        library_layout = QVBoxLayout()

        library_group = QGroupBox("📚 Biblioteca de Músicas")
        library_group_layout = QVBoxLayout()

        # Botões da biblioteca
        library_buttons = QHBoxLayout()

        self.refresh_library_btn = QPushButton("🔄 Atualizar")
        self.refresh_library_btn.clicked.connect(self.load_music_library)
        library_buttons.addWidget(self.refresh_library_btn)

        self.add_folder_btn = QPushButton("📁 Adicionar Pasta")
        self.add_folder_btn.clicked.connect(self.add_music_folder)
        library_buttons.addWidget(self.add_folder_btn)

        library_buttons.addStretch()
        library_group_layout.addLayout(library_buttons)

        # Lista de músicas
        self.music_list = QListWidget()
        self.music_list.itemDoubleClicked.connect(self.play_selected_song)
        library_group_layout.addWidget(self.music_list)

        library_group.setLayout(library_group_layout)
        library_layout.addWidget(library_group)
        library_widget.setLayout(library_layout)

        # Painel direito - Controles do player
        player_widget = QWidget()
        player_layout = QVBoxLayout()

        # Informações da música atual
        current_song_group = QGroupBox("🎧 Reproduzindo Agora")
        current_song_layout = QVBoxLayout()

        self.current_song_label = QLabel("Nenhuma música selecionada")
        self.current_song_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        current_song_font = QFont()
        current_song_font.setPointSize(12)
        current_song_font.setBold(True)
        self.current_song_label.setFont(current_song_font)
        current_song_layout.addWidget(self.current_song_label)

        self.current_artist_label = QLabel("")
        self.current_artist_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        current_song_layout.addWidget(self.current_artist_label)

        current_song_group.setLayout(current_song_layout)
        player_layout.addWidget(current_song_group)

        # Barra de progresso
        progress_layout = QVBoxLayout()

        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setMinimum(0)
        self.progress_slider.setMaximum(100)
        self.progress_slider.sliderPressed.connect(self.on_seek_start)
        self.progress_slider.sliderReleased.connect(self.on_seek_end)
        progress_layout.addWidget(self.progress_slider)

        # Tempo atual / duração
        time_layout = QHBoxLayout()
        self.current_time_label = QLabel("00:00")
        self.duration_label = QLabel("00:00")
        time_layout.addWidget(self.current_time_label)
        time_layout.addStretch()
        time_layout.addWidget(self.duration_label)
        progress_layout.addLayout(time_layout)

        player_layout.addLayout(progress_layout)

        # Controles principais
        controls_layout = QHBoxLayout()

        self.shuffle_btn = QPushButton("🔀")
        self.shuffle_btn.setCheckable(True)
        self.shuffle_btn.clicked.connect(self.toggle_shuffle)
        self.shuffle_btn.setToolTip("Modo Aleatório")
        controls_layout.addWidget(self.shuffle_btn)

        self.previous_btn = QPushButton("⏮️")
        self.previous_btn.clicked.connect(self.previous_song)
        controls_layout.addWidget(self.previous_btn)

        self.play_pause_btn = QPushButton("▶️")
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        controls_layout.addWidget(self.play_pause_btn)

        self.stop_btn = QPushButton("⏹️")
        self.stop_btn.clicked.connect(self.stop_music)
        controls_layout.addWidget(self.stop_btn)

        self.next_btn = QPushButton("⏭️")
        self.next_btn.clicked.connect(self.next_song)
        controls_layout.addWidget(self.next_btn)

        self.repeat_btn = QPushButton("🔁")
        self.repeat_btn.setCheckable(True)
        self.repeat_btn.clicked.connect(self.toggle_repeat)
        self.repeat_btn.setToolTip("Modo Repetir")
        controls_layout.addWidget(self.repeat_btn)

        player_layout.addLayout(controls_layout)

        # Controle de volume
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("🔊"))

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(int(self.volume * 100))
        self.volume_slider.valueChanged.connect(self.change_volume)
        volume_layout.addWidget(self.volume_slider)

        self.volume_label = QLabel("70%")
        volume_layout.addWidget(self.volume_label)

        player_layout.addLayout(volume_layout)

        # Controles de Pitch (Tonalidade)
        pitch_group = QGroupBox("🎼 Controles de Tonalidade")
        pitch_layout = QVBoxLayout()

        # Botões de pitch preset
        pitch_buttons_layout = QHBoxLayout()

        self.pitch_down_octave_btn = QPushButton("-12")
        self.pitch_down_octave_btn.clicked.connect(lambda: self.adjust_pitch(-12))
        self.pitch_down_octave_btn.setToolTip("1 oitava abaixo")
        pitch_buttons_layout.addWidget(self.pitch_down_octave_btn)

        self.pitch_down_btn = QPushButton("-1")
        self.pitch_down_btn.clicked.connect(lambda: self.adjust_pitch(-1))
        self.pitch_down_btn.setToolTip("1 semitom abaixo")
        pitch_buttons_layout.addWidget(self.pitch_down_btn)

        self.pitch_reset_btn = QPushButton("0")
        self.pitch_reset_btn.clicked.connect(lambda: self.adjust_pitch(0, reset=True))
        self.pitch_reset_btn.setToolTip("Tom original")
        pitch_buttons_layout.addWidget(self.pitch_reset_btn)

        self.pitch_up_btn = QPushButton("+1")
        self.pitch_up_btn.clicked.connect(lambda: self.adjust_pitch(+1))
        self.pitch_up_btn.setToolTip("1 semitom acima")
        pitch_buttons_layout.addWidget(self.pitch_up_btn)

        self.pitch_up_octave_btn = QPushButton("+12")
        self.pitch_up_octave_btn.clicked.connect(lambda: self.adjust_pitch(+12))
        self.pitch_up_octave_btn.setToolTip("1 oitava acima")
        pitch_buttons_layout.addWidget(self.pitch_up_octave_btn)

        pitch_layout.addLayout(pitch_buttons_layout)

        # Slider de pitch fino
        pitch_slider_layout = QHBoxLayout()
        pitch_slider_layout.addWidget(QLabel("-12"))

        self.pitch_slider = QSlider(Qt.Orientation.Horizontal)
        self.pitch_slider.setMinimum(-12)
        self.pitch_slider.setMaximum(12)
        self.pitch_slider.setValue(0)
        self.pitch_slider.valueChanged.connect(self.on_pitch_slider_change)
        pitch_slider_layout.addWidget(self.pitch_slider)

        pitch_slider_layout.addWidget(QLabel("+12"))

        self.pitch_value_label = QLabel("0 semitons")
        self.pitch_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pitch_slider_layout.addWidget(self.pitch_value_label)

        pitch_layout.addLayout(pitch_slider_layout)

        # Controles de velocidade
        speed_layout = QHBoxLayout()

        self.speed_slow_btn = QPushButton("0.8x")
        self.speed_slow_btn.clicked.connect(lambda: self.adjust_speed(0.8))
        self.speed_slow_btn.setToolTip("Mais lento")
        speed_layout.addWidget(self.speed_slow_btn)

        self.speed_normal_btn = QPushButton("1.0x")
        self.speed_normal_btn.clicked.connect(lambda: self.adjust_speed(1.0))
        self.speed_normal_btn.setToolTip("Velocidade normal")
        speed_layout.addWidget(self.speed_normal_btn)

        self.speed_fast_btn = QPushButton("1.2x")
        self.speed_fast_btn.clicked.connect(lambda: self.adjust_speed(1.2))
        self.speed_fast_btn.setToolTip("Mais rápido")
        speed_layout.addWidget(self.speed_fast_btn)

        speed_layout.addWidget(QLabel("🏃"))

        pitch_layout.addLayout(speed_layout)

        # Botão para salvar versão processada
        save_layout = QHBoxLayout()

        self.save_processed_btn = QPushButton("💾 Salvar Tom Atual")
        self.save_processed_btn.clicked.connect(self.save_processed_version)
        self.save_processed_btn.setToolTip("Salvar música com o tom atual")
        self.save_processed_btn.setEnabled(False)  # Desabilitado por padrão
        save_layout.addWidget(self.save_processed_btn)

        save_layout.addStretch()

        pitch_layout.addLayout(save_layout)

        pitch_group.setLayout(pitch_layout)

        # Desabilitar controles se ffmpeg não estiver disponível
        if not self.ffmpeg_available:
            pitch_group.setEnabled(False)
            pitch_group.setToolTip("FFmpeg necessário para controles de pitch")

        player_layout.addWidget(pitch_group)

        player_layout.addStretch()
        player_widget.setLayout(player_layout)

        # Adicionar widgets ao splitter
        splitter.addWidget(library_widget)
        splitter.addWidget(player_widget)
        splitter.setSizes([400, 300])

        layout.addWidget(splitter)
        self.setLayout(layout)

    def load_music_library(self):
        """Carrega a biblioteca de músicas da pasta downloads"""
        self.music_list.clear()
        self.playlist.clear()

        if not os.path.exists(self.downloads_path):
            logging.warning(f"Pasta {self.downloads_path} não encontrada")
            return

        supported_formats = [".mp3", ".wav", ".ogg", ".m4a"]

        for file_path in Path(self.downloads_path).rglob("*"):
            if file_path.suffix.lower() in supported_formats:
                self.playlist.append(str(file_path))

                # Tentar extrair metadados
                display_name = file_path.stem
                artist = ""

                try:
                    if file_path.suffix.lower() == ".mp3":
                        audio = MP3(str(file_path))
                        if audio.tags:
                            title = audio.tags.get("TIT2")
                            artist_tag = audio.tags.get("TPE1")
                            if title:
                                display_name = str(title)
                            if artist_tag:
                                artist = str(artist_tag)
                except Exception as e:
                    logging.debug(f"Erro ao ler metadados de {file_path}: {e}")

                # Criar item da lista
                item = QListWidgetItem()
                if artist:
                    item.setText(f"{display_name} - {artist}")
                else:
                    item.setText(display_name)

                item.setData(Qt.ItemDataRole.UserRole, str(file_path))
                self.music_list.addItem(item)

        logging.info(f"Carregadas {len(self.playlist)} músicas na biblioteca")

    def add_music_folder(self):
        """Adiciona uma pasta externa à biblioteca"""
        folder = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Músicas")
        if folder:
            # Adicionar músicas da pasta selecionada
            supported_formats = [".mp3", ".wav", ".ogg", ".m4a"]

            for file_path in Path(folder).rglob("*"):
                if file_path.suffix.lower() in supported_formats:
                    if str(file_path) not in self.playlist:
                        self.playlist.append(str(file_path))

                        # Criar item da lista
                        item = QListWidgetItem()
                        item.setText(file_path.stem)
                        item.setData(Qt.ItemDataRole.UserRole, str(file_path))
                        self.music_list.addItem(item)

    def play_selected_song(self, item):
        """Reproduz a música selecionada"""
        file_path = item.data(Qt.ItemDataRole.UserRole)
        self.current_index = self.playlist.index(file_path)
        self.play_song(file_path)

    def play_song(self, file_path):
        """Reproduz uma música específica"""
        try:
            if self.is_playing:
                pygame.mixer.music.stop()

            # Limpar estado de processamento anterior
            self.cleanup_processed_file()
            self.has_processed_audio = False
            self.save_processed_btn.setEnabled(False)
            self.current_pitch = 0
            self.pitch_slider.setValue(0)
            self.update_pitch_display()

            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()

            self.current_song = file_path
            self.is_playing = True
            self.is_paused = False
            self.position = 0

            # Atualizar interface
            self.play_pause_btn.setText("⏸️")
            song_name = Path(file_path).stem
            self.current_song_label.setText(song_name)

            # Tentar obter duração
            try:
                if file_path.lower().endswith(".mp3"):
                    audio = MP3(file_path)
                    self.duration = int(audio.info.length)
                    self.duration_label.setText(self.format_time(self.duration))
                else:
                    self.duration = 0
                    self.duration_label.setText("--:--")
            except:
                self.duration = 0
                self.duration_label.setText("--:--")

            # Destacar música atual na lista
            for i in range(self.music_list.count()):
                item = self.music_list.item(i)
                if item and item.data(Qt.ItemDataRole.UserRole) == file_path:
                    self.music_list.setCurrentItem(item)
                    break

            logging.info(f"Reproduzindo: {song_name}")

        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao reproduzir música: {str(e)}")
            logging.error(f"Erro ao reproduzir {file_path}: {e}")

    def toggle_play_pause(self):
        """Alterna entre play e pause"""
        if not self.current_song:
            if self.playlist:
                self.play_song(self.playlist[0])
                self.current_index = 0
            return

        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.play_pause_btn.setText("▶️")
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.play_pause_btn.setText("⏸️")
        else:
            self.play_song(self.current_song)

    def stop_music(self):
        """Para a reprodução"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.position = 0
        self.play_pause_btn.setText("▶️")
        self.current_time_label.setText("00:00")
        self.progress_slider.setValue(0)

    def next_song(self):
        """Próxima música"""
        if not self.playlist:
            return

        if self.shuffle_mode:
            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist)

        self.play_song(self.playlist[self.current_index])

    def previous_song(self):
        """Música anterior"""
        if not self.playlist:
            return

        if self.shuffle_mode:
            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_index = (self.current_index - 1) % len(self.playlist)

        self.play_song(self.playlist[self.current_index])

    def toggle_shuffle(self):
        """Alterna modo aleatório"""
        self.shuffle_mode = self.shuffle_btn.isChecked()
        if self.shuffle_mode:
            self.shuffle_btn.setText("🔀")
            self.shuffle_btn.setStyleSheet("background-color: #4CAF50;")
        else:
            self.shuffle_btn.setText("🔀")
            self.shuffle_btn.setStyleSheet("")

    def toggle_repeat(self):
        """Alterna modo repetir"""
        self.repeat_mode = self.repeat_btn.isChecked()
        if self.repeat_mode:
            self.repeat_btn.setText("🔁")
            self.repeat_btn.setStyleSheet("background-color: #4CAF50;")
        else:
            self.repeat_btn.setText("🔁")
            self.repeat_btn.setStyleSheet("")

    def change_volume(self, value):
        """Altera o volume"""
        self.volume = value / 100.0
        pygame.mixer.music.set_volume(self.volume)
        self.volume_label.setText(f"{value}%")

    def update_position(self):
        """Atualiza a posição da música"""
        if self.is_playing and not self.is_paused:
            # Verificar se a música acabou
            # Mas não considerar como acabou se estamos processando áudio
            music_not_busy = not pygame.mixer.music.get_busy()
            processor_not_busy = not self.audio_processor.is_busy()
            if music_not_busy and processor_not_busy:
                if self.repeat_mode:
                    self.play_song(self.current_song)
                else:
                    self.next_song()
                return

            # Atualizar posição (aproximação) - só se não processando
            if not self.audio_processor.is_busy():
                self.position += 1
                time_text = self.format_time(self.position)
                self.current_time_label.setText(time_text)

                if self.duration > 0:
                    progress = int((self.position / self.duration) * 100)
                    self.progress_slider.setValue(progress)

    def on_seek_start(self):
        """Início do seek"""
        self.seeking = True

    def on_seek_end(self):
        """Fim do seek - implementação básica"""
        self.seeking = False
        if self.duration > 0:
            seek_position = (self.progress_slider.value() / 100.0) * self.duration
            self.position = int(seek_position)
            # Nota: pygame não suporta seek nativo, então reiniciamos a música
            # Em uma implementação mais avançada, usaríamos uma biblioteca como VLC

    def format_time(self, seconds):
        """Formata tempo em mm:ss"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def adjust_pitch(self, semitones, reset=False):
        """Ajusta o pitch da música atual"""
        if not self.current_song or not self.ffmpeg_available:
            return

        if reset:
            self.current_pitch = 0
        else:
            self.current_pitch += semitones

        # Limitar pitch entre -12 e +12 semitons
        self.current_pitch = max(-12, min(12, self.current_pitch))

        # Atualizar interface
        self.pitch_slider.setValue(self.current_pitch)
        self.update_pitch_display()

        # Processar áudio se há mudança de pitch
        if self.current_pitch != 0:
            self.process_current_song()
        else:
            # Voltar ao arquivo original
            self.cleanup_processed_file()
            self.has_processed_audio = False
            self.save_processed_btn.setEnabled(False)

    def on_pitch_slider_change(self, value):
        """Callback para mudança no slider de pitch"""
        if not self.ffmpeg_available:
            return

        self.current_pitch = value
        self.update_pitch_display()

        # Processar áudio com delay para evitar processamento excessivo
        if hasattr(self, "pitch_timer"):
            self.pitch_timer.stop()

        self.pitch_timer = QTimer()
        self.pitch_timer.timeout.connect(self.apply_pitch_from_slider)
        self.pitch_timer.setSingleShot(True)
        self.pitch_timer.start(500)  # 500ms delay

    def apply_pitch_from_slider(self):
        """Aplica pitch após delay do slider"""
        if self.current_pitch != 0:
            self.process_current_song()
        else:
            self.cleanup_processed_file()
            self.has_processed_audio = False
            self.save_processed_btn.setEnabled(False)

    def adjust_speed(self, speed):
        """Ajusta a velocidade da música (simplificado)"""
        if not self.current_song:
            return

        # No processador simples, não temos controle de velocidade
        # Apenas destacar o botão para feedback visual
        for btn in [self.speed_slow_btn, self.speed_normal_btn, self.speed_fast_btn]:
            btn.setStyleSheet("")

        if speed == 0.8:
            self.speed_slow_btn.setStyleSheet("background-color: #4CAF50;")
        elif speed == 1.0:
            self.speed_normal_btn.setStyleSheet("background-color: #4CAF50;")
        elif speed == 1.2:
            self.speed_fast_btn.setStyleSheet("background-color: #4CAF50;")

        logging.info(f"Controle de velocidade: {speed}x (visual apenas)")

    def update_pitch_display(self):
        """Atualiza o display do valor de pitch"""
        if self.current_pitch == 0:
            self.pitch_value_label.setText("Tom original")
        elif self.current_pitch > 0:
            self.pitch_value_label.setText(f"+{self.current_pitch} semitons")
        else:
            self.pitch_value_label.setText(f"{self.current_pitch} semitons")

    def process_current_song(self):
        """Processa a música atual com pitch"""
        if not self.current_song:
            logging.debug("process_current_song: Nenhuma música selecionada")
            return

        if self.audio_processor.is_busy():
            debug_msg = "process_current_song: Processador ocupado, ignorando"
            logging.debug(debug_msg)
            return

        logging.info(
            f"Iniciando processamento: {self.current_song} "
            f"com pitch {self.current_pitch}"
        )

        # Pausar música atual se estiver tocando
        was_playing = self.is_playing and not self.is_paused
        if was_playing:
            pygame.mixer.music.pause()
            logging.debug("Música pausada para processamento")

        # Processar áudio de forma assíncrona (apenas pitch)
        self.audio_processor.process_audio_async(
            self.current_song, pitch_shift=self.current_pitch
        )

        logging.info(f"Processando áudio: pitch={self.current_pitch}")

    def on_audio_processed(self, output_path, error, info=None):
        """Callback chamado quando áudio é processado"""
        if error:
            error_msg = f"Erro ao processar áudio: {error}"
            QMessageBox.warning(self, "Erro", error_msg)
            return

        if output_path:
            # Limpar arquivo anterior
            self.cleanup_processed_file()
            self.processed_file = output_path

            # Habilitar botão salvar
            self.has_processed_audio = True
            self.save_processed_btn.setEnabled(True)

            # Carregar áudio processado
            try:
                pygame.mixer.music.load(output_path)
                pygame.mixer.music.play()

                self.is_playing = True
                self.is_paused = False
                self.play_pause_btn.setText("⏸️")

                logging.info(f"Áudio processado carregado: {output_path}")

            except Exception as e:
                error_msg = f"Erro ao carregar áudio processado: {str(e)}"
                QMessageBox.warning(self, "Erro", error_msg)

    def cleanup_processed_file(self):
        """Remove arquivo de áudio processado"""
        if self.processed_file and os.path.exists(self.processed_file):
            try:
                os.remove(self.processed_file)
                log_msg = f"Arquivo processado removido: {self.processed_file}"
                logging.debug(log_msg)
            except Exception as e:
                logging.error(f"Erro ao remover arquivo processado: {e}")

        self.processed_file = None

    def save_processed_version(self):
        """Salva a versão processada da música atual"""
        if not self.current_song or not self.has_processed_audio:
            QMessageBox.information(
                self, "Aviso", "Nenhuma música com tom alterado para salvar."
            )
            return

        if not self.processed_file or not os.path.exists(self.processed_file):
            QMessageBox.warning(self, "Erro", "Arquivo processado não encontrado.")
            return

        try:
            # Obter nome da música original
            song_path = self.current_song
            song_name = os.path.splitext(os.path.basename(song_path))[0]

            # Criar nome para versão processada
            pitch_suffix = ""
            if self.current_pitch > 0:
                pitch_suffix = f"_+{self.current_pitch}st"
            elif self.current_pitch < 0:
                pitch_suffix = f"_{self.current_pitch}st"

            suggested_name = f"{song_name}{pitch_suffix}.mp3"

            # Diálogo para escolher local de salvamento
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Salvar música com tom alterado",
                os.path.join(self.downloads_path, suggested_name),
                "Arquivos MP3 (*.mp3);;Todos os arquivos (*)",
            )

            if save_path:
                # Copiar arquivo processado para o local escolhido
                import shutil

                shutil.copy2(self.processed_file, save_path)

                # Atualizar metadados se possível
                try:
                    from mutagen.mp3 import MP3
                    from mutagen.id3 import ID3
                    from mutagen.id3._frames import TIT2

                    audio_file = MP3(save_path, ID3=ID3)

                    # Garantir que existe tags
                    if audio_file.tags is None:
                        audio_file.add_tags()

                    # Tentar obter metadados originais
                    try:
                        original_file = MP3(self.current_song)
                        if (
                            hasattr(original_file, "tags")
                            and original_file.tags is not None
                        ):
                            # Copiar tags existentes
                            for key, value in original_file.tags.items():
                                if audio_file.tags:
                                    audio_file.tags[key] = value
                    except Exception:
                        pass

                    # Adicionar informação do pitch ao título
                    current_title = song_name
                    if audio_file.tags and "TIT2" in audio_file.tags:
                        current_title = str(audio_file.tags["TIT2"])

                    if pitch_suffix:
                        new_title = f"{current_title} ({pitch_suffix[1:]})"
                    else:
                        new_title = current_title

                    if audio_file.tags:
                        audio_file.tags["TIT2"] = TIT2(encoding=3, text=new_title)

                    audio_file.save()

                except Exception as e:
                    logging.warning(f"Erro ao atualizar metadados: {e}")

                QMessageBox.information(
                    self, "Sucesso", f"Música salva com sucesso em:\n{save_path}"
                )

                logging.info(f"Música processada salva: {save_path}")

        except Exception as e:
            error_msg = f"Erro ao salvar música: {str(e)}"
            QMessageBox.critical(self, "Erro", error_msg)
            logging.error(error_msg)

    def closeEvent(self, event):
        """Limpa recursos ao fechar"""
        if self.is_playing:
            pygame.mixer.music.stop()

        # Limpar arquivos processados
        self.cleanup_processed_file()
        self.audio_processor.cleanup()

        pygame.mixer.quit()
        event.accept()
