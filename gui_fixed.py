import logging
import os
import subprocess
import sys
from datetime import datetime

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QProgressBar,
    QSplitter,
    QGroupBox,
)
from config import (
    load_config,
    save_config,
    load_downloads_history,
    add_download_to_history,
    update_download_status,
)
from config_window import ConfigWindow
from main import (
    parse_urls_and_extract_info,
    parse_urls_parallel,
    download_videos_parallel,
)


class ParseThread(QThread):
    """Thread para parsing paralelo de URLs"""

    parse_finished = pyqtSignal(list)
    parse_error = pyqtSignal(str)

    def __init__(self, urls):
        super().__init__()
        self.urls = urls

    def run(self):
        try:
            logging.info(f"Iniciando parse paralelo de {len(self.urls)} URLs")
            for url in self.urls:
                logging.info(f"Processando URL: {url}")
            videos = parse_urls_parallel(self.urls, max_workers=3)
            self.parse_finished.emit(videos)
        except Exception as e:
            self.parse_error.emit(str(e))


class ParallelDownloadThread(QThread):
    """Thread para downloads paralelos"""

    download_progress = pyqtSignal(str, str)  # url, status
    progress_update = pyqtSignal(str, dict)  # url, progress_data
    all_finished = pyqtSignal()

    def __init__(self, videos_info, download_path, to_mp3=True):
        super().__init__()
        self.videos_info = videos_info
        self.download_path = download_path
        self.to_mp3 = to_mp3

    def progress_callback(self, url, data):
        """Callback para progresso de download"""
        self.progress_update.emit(url, data)

    def run(self):
        try:
            logging.info(
                f"Iniciando download paralelo de {len(self.videos_info)} vídeos"
            )
            results = download_videos_parallel(
                self.videos_info,
                self.download_path,
                self.to_mp3,
                max_workers=2,
                progress_callback=self.progress_callback,
            )
            logging.info(f"Downloads concluídos: {len(results)}")
        except Exception as e:
            logging.error(f"Erro nos downloads paralelos: {e}")
        finally:
            self.all_finished.emit()


class YouTubeDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.download_thread = None
        self.parse_thread = None
        self.parallel_download_thread = None
        self.setup_logging()
        self.initUI()
        self.load_downloads_history()

        # Timer para atualizar a lista periodicamente
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.load_downloads_history)
        self.update_timer.start(2000)  # Atualiza a cada 2 segundos

    def setup_logging(self):
        """Configura o logging baseado nas configurações"""
        if self.config.get("logging_enabled", True):
            logging.basicConfig(
                level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
            )
        else:
            logging.disable(logging.CRITICAL)

    def initUI(self):
        self.setWindowTitle("YouTube Downloader")
        self.setWindowIcon(QIcon("assets/settings.png"))
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal com splitter
        main_layout = QVBoxLayout()
        splitter = QSplitter(Qt.Vertical)

        # Seção superior - Controles
        controls_widget = QWidget()
        controls_layout = QVBoxLayout()

        # Grupo de entrada
        input_group = QGroupBox("URLs para Download")
        input_layout = QVBoxLayout()

        self.url_text = QTextEdit()
        self.url_text.setPlaceholderText(
            "Cole as URLs do YouTube aqui (uma por linha) ou selecione um arquivo..."
        )
        self.url_text.setMaximumHeight(100)
        input_layout.addWidget(self.url_text)

        # Botões de arquivo
        file_layout = QHBoxLayout()
        self.load_file_button = QPushButton("Carregar de Arquivo")
        self.load_file_button.clicked.connect(self.load_urls_from_file)
        file_layout.addWidget(self.load_file_button)

        self.clear_urls_button = QPushButton("Limpar URLs")
        self.clear_urls_button.clicked.connect(self.clear_urls)
        file_layout.addWidget(self.clear_urls_button)

        self.parse_urls_button = QPushButton("Parse URLs")
        self.parse_urls_button.clicked.connect(self.parse_urls)
        file_layout.addWidget(self.parse_urls_button)

        file_layout.addStretch()
        input_layout.addLayout(file_layout)

        input_group.setLayout(input_layout)
        controls_layout.addWidget(input_group)

        # Opções de download
        options_group = QGroupBox("Opções de Download")
        options_layout = QVBoxLayout()

        self.mp3_checkbox = QCheckBox("Converter para MP3")
        self.mp3_checkbox.setChecked(self.config.get("auto_convert_to_mp3", True))
        options_layout.addWidget(self.mp3_checkbox)

        self.keep_video_checkbox = QCheckBox("Manter arquivo de vídeo original")
        self.keep_video_checkbox.setChecked(self.config.get("keep_video", False))
        options_layout.addWidget(self.keep_video_checkbox)

        # Path de download
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Pasta de download:"))

        self.path_label = QLabel(self.config.get("default_download_path", ""))
        path_layout.addWidget(self.path_label)

        self.browse_path_button = QPushButton("Alterar")
        self.browse_path_button.clicked.connect(self.browse_path)
        path_layout.addWidget(self.browse_path_button)

        options_layout.addLayout(path_layout)
        options_group.setLayout(options_layout)
        controls_layout.addWidget(options_group)

        # Botões de ação
        action_layout = QHBoxLayout()

        self.download_button = QPushButton("Iniciar Download")
        self.download_button.clicked.connect(self.start_download)
        action_layout.addWidget(self.download_button)

        self.download_pending_button = QPushButton("Baixar Pendentes")
        self.download_pending_button.clicked.connect(self.download_pending)
        action_layout.addWidget(self.download_pending_button)

        self.open_folder_button = QPushButton("Abrir Pasta")
        self.open_folder_button.clicked.connect(self.open_download_folder)
        action_layout.addWidget(self.open_folder_button)

        action_layout.addStretch()
        controls_layout.addLayout(action_layout)

        controls_widget.setLayout(controls_layout)
        splitter.addWidget(controls_widget)

        # Seção inferior - Lista de downloads
        downloads_widget = QWidget()
        downloads_layout = QVBoxLayout()

        # Cabeçalho da lista
        list_header_layout = QHBoxLayout()
        list_header_layout.addWidget(QLabel("Histórico de Downloads"))
        list_header_layout.addStretch()

        # Botões de limpeza
        self.clear_completed_button = QPushButton("Limpar Concluídos")
        self.clear_completed_button.clicked.connect(self.clear_completed_downloads)
        list_header_layout.addWidget(self.clear_completed_button)

        self.clear_failed_button = QPushButton("Limpar Falhados")
        self.clear_failed_button.clicked.connect(self.clear_failed_downloads)
        list_header_layout.addWidget(self.clear_failed_button)

        self.clear_all_button = QPushButton("Limpar Tudo")
        self.clear_all_button.clicked.connect(self.clear_all_downloads)
        list_header_layout.addWidget(self.clear_all_button)

        self.refresh_button = QPushButton("Atualizar")
        self.refresh_button.clicked.connect(self.load_downloads_history)
        list_header_layout.addWidget(self.refresh_button)

        downloads_layout.addLayout(list_header_layout)

        # Tabela de downloads com configuração otimizada
        self.downloads_table = QTableWidget()
        self.downloads_table.setColumnCount(6)
        self.downloads_table.setHorizontalHeaderLabels(
            ["#", "Título", "Status", "Progresso", "Data", "Ações"]
        )

        # Configurar tamanhos fixos das colunas
        header = self.downloads_table.horizontalHeader()
        if header:
            # Configurar modo de redimensionamento
            header.setSectionResizeMode(0, QHeaderView.Fixed)  # Número - fixo
            header.setSectionResizeMode(1, QHeaderView.Stretch)  # Título - flexível
            header.setSectionResizeMode(2, QHeaderView.Fixed)  # Status - fixo
            header.setSectionResizeMode(3, QHeaderView.Fixed)  # Progresso - fixo
            header.setSectionResizeMode(4, QHeaderView.Fixed)  # Data - fixo
            header.setSectionResizeMode(5, QHeaderView.Fixed)  # Ações - fixo

            # Definir larguras fixas específicas
            self.downloads_table.setColumnWidth(0, 50)  # # - 50px para 3 dígitos
            self.downloads_table.setColumnWidth(2, 120)  # Status - 120px
            self.downloads_table.setColumnWidth(3, 150)  # Progresso - 150px
            self.downloads_table.setColumnWidth(4, 130)  # Data - 130px
            self.downloads_table.setColumnWidth(5, 100)  # Ações - 100px

        downloads_layout.addWidget(self.downloads_table)

        downloads_widget.setLayout(downloads_layout)
        splitter.addWidget(downloads_widget)

        # Definir proporções do splitter (30% controles, 70% tabela)
        splitter.setSizes([300, 700])

        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)

        # Menu
        self.create_menu()

    def create_menu(self):
        """Cria a barra de menu"""
        menubar = self.menuBar()
        if menubar:
            config_menu = menubar.addMenu("Configurações")
            if config_menu:
                config_action = config_menu.addAction("Preferências")
                if config_action:
                    config_action.triggered.connect(self.open_config)

    def open_config(self):
        """Abre a janela de configurações"""
        self.config_window = ConfigWindow()
        self.config_window.show()

    def load_urls_from_file(self):
        """Carrega URLs de um arquivo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Carregar URLs", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, "r") as file:
                    urls = file.read()
                    self.url_text.setPlainText(urls)
            except Exception as e:
                QMessageBox.critical(
                    self, "Erro", f"Erro ao carregar arquivo: {str(e)}"
                )

    def clear_urls(self):
        """Limpa o campo de URLs"""
        self.url_text.clear()

    def browse_path(self):
        """Abre diálogo para selecionar pasta de download"""
        path = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Download")
        if path:
            self.path_label.setText(path)
            # Salva a nova pasta na configuração
            config = load_config()
            config["default_download_path"] = path
            save_config(config)

    def parse_urls(self):
        """Inicia o parse paralelo de URLs"""
        urls_text = self.url_text.toPlainText().strip()
        if not urls_text:
            QMessageBox.warning(self, "Aviso", "Por favor, insira pelo menos uma URL")
            return

        urls = [url.strip() for url in urls_text.split("\n") if url.strip()]

        # Desabilita o botão durante o parsing
        self.parse_urls_button.setText("Analisando (Paralelo)...")
        self.parse_urls_button.setEnabled(False)

        # Inicia o parse paralelo em thread separada
        self.parse_thread = ParseThread(urls)
        self.parse_thread.parse_finished.connect(self.on_parse_finished)
        self.parse_thread.parse_error.connect(self.on_parse_error)
        self.parse_thread.start()

    def on_parse_finished(self, videos):
        """Callback quando o parse paralelo termina"""
        try:
            # Remove apenas duplicados pendentes
            self.clear_duplicate_downloads(videos)

            # Adiciona cada vídeo à lista com status "pending"
            for video in videos:
                add_download_to_history(video["title"], video["url"], "", "pending")

            # Atualiza a lista
            self.load_downloads_history()

        except Exception as e:
            QMessageBox.critical(
                self, "Erro", f"Erro ao processar resultados do parse: {str(e)}"
            )
        finally:
            # Reabilita o botão
            self.parse_urls_button.setText("Parse URLs")
            self.parse_urls_button.setEnabled(True)

    def on_parse_error(self, error_msg):
        """Callback quando há erro no parse paralelo"""
        QMessageBox.critical(self, "Erro no Parse", error_msg)
        self.parse_urls_button.setText("Parse URLs")
        self.parse_urls_button.setEnabled(True)

    def start_download(self):
        """Inicia download paralelo automático após parse"""
        urls_text = self.url_text.toPlainText().strip()
        if not urls_text:
            QMessageBox.warning(self, "Aviso", "Por favor, insira pelo menos uma URL")
            return

        output_path = self.path_label.text()
        if not output_path:
            QMessageBox.warning(
                self, "Aviso", "Por favor, selecione uma pasta de download"
            )
            return

        urls = [url.strip() for url in urls_text.split("\n") if url.strip()]

        # Desabilita o botão durante o parsing
        self.download_button.setText("Analisando URLs...")
        self.download_button.setEnabled(False)

        # Inicia parse seguido de download automático
        self.parse_thread = ParseThread(urls)
        self.parse_thread.parse_finished.connect(self.on_parse_finished_for_download)
        self.parse_thread.parse_error.connect(self.on_parse_error_for_download)
        self.parse_thread.start()

    def on_parse_finished_for_download(self, videos):
        """Callback quando parse termina - inicia download automático"""
        try:
            # Remove apenas duplicados pendentes
            self.clear_duplicate_downloads(videos)

            # Adiciona cada vídeo à lista com status "pending"
            for video in videos:
                add_download_to_history(video["title"], video["url"], "", "pending")

            # Atualiza a lista
            self.load_downloads_history()

            # Inicia download paralelo automaticamente
            output_path = self.path_label.text()
            convert_to_mp3 = self.mp3_checkbox.isChecked()

            self.download_button.setText("Baixando...")

            # Inicia thread de download paralelo
            self.parallel_download_thread = ParallelDownloadThread(
                videos, output_path, convert_to_mp3
            )
            self.parallel_download_thread.progress_update.connect(
                self.on_download_progress
            )
            self.parallel_download_thread.all_finished.connect(
                self.parallel_download_finished
            )
            self.parallel_download_thread.start()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao processar vídeos: {str(e)}")
            self.download_button.setText("Iniciar Download")
            self.download_button.setEnabled(True)

    def clear_duplicate_downloads(self, new_videos):
        """Remove apenas duplicados pendentes, mantendo downloads concluídos/em progresso"""
        from config import load_downloads_history, save_downloads_history

        downloads = load_downloads_history()
        new_urls = {video["url"] for video in new_videos}

        # Remove apenas entradas duplicadas que estão pendentes
        filtered_downloads = [
            d
            for d in downloads
            if not (d.get("url") in new_urls and d.get("status") == "pending")
        ]

        save_downloads_history(filtered_downloads)

    def on_download_progress(self, url, progress_data):
        """Atualiza progresso visual com informações detalhadas"""
        if not progress_data:
            return

        # Determina a fase atual
        status = progress_data.get("status", "unknown")
        phase = progress_data.get("phase", "unknown")
        percent = progress_data.get("percent", 0)

        # Formata a mensagem de progresso baseada na fase
        if phase == "download":
            if "speed" in progress_data and progress_data["speed"]:
                speed_mb = progress_data["speed"] / (1024 * 1024)
                progress_text = f"Download: {percent:.1f}% ({speed_mb:.1f} MB/s)"
            else:
                progress_text = f"Download: {percent:.1f}%"
        elif phase == "conversion":
            message = progress_data.get("message", "Convertendo...")
            progress_text = f"Conversão: {message} ({percent:.1f}%)"
        elif status == "finished":
            progress_text = "100% - Concluído"
        else:
            progress_text = f"{percent:.1f}%"

        # Atualiza a tabela com o progresso atual
        self.update_download_progress_in_table(url, status, progress_text)

    def update_download_progress_in_table(self, url, status, progress_text):
        """Atualiza o progresso específico na tabela"""
        try:
            downloads = load_downloads_history()
            for row in range(self.downloads_table.rowCount()):
                if row < len(downloads):
                    if downloads[row].get("url") == url:
                        # Atualiza a coluna de progresso (índice 3)
                        progress_item = QTableWidgetItem(progress_text)

                        # Cor baseada no status
                        if status == "downloading":
                            progress_item.setBackground(QColor("lightyellow"))
                        elif status == "converting":
                            progress_item.setBackground(QColor("lightblue"))
                        elif status == "finished":
                            progress_item.setBackground(QColor("lightgreen"))

                        self.downloads_table.setItem(row, 3, progress_item)
                        break
        except Exception as e:
            logging.error(f"Erro ao atualizar progresso na tabela: {e}")

    def on_parse_error_for_download(self, error_msg):
        """Callback quando há erro no parse - reabilita botão"""
        QMessageBox.critical(
            self, "Erro na Análise", f"Erro ao analisar URLs:\n{error_msg}"
        )
        self.download_button.setText("Iniciar Download")
        self.download_button.setEnabled(True)

    def parallel_download_finished(self):
        """Callback quando todos os downloads paralelos terminam"""
        self.download_button.setText("Iniciar Download")
        self.download_button.setEnabled(True)

        # Força atualização da lista
        self.load_downloads_history()

    def download_pending(self):
        """Inicia o download paralelo de todos os itens pendentes"""
        downloads = load_downloads_history()
        pending_downloads = [d for d in downloads if d.get("status") == "pending"]

        if not pending_downloads:
            QMessageBox.information(
                self, "Info", "Não há downloads pendentes na lista."
            )
            return

        output_path = self.path_label.text()
        if not output_path:
            QMessageBox.warning(
                self, "Aviso", "Por favor, selecione uma pasta de download"
            )
            return

        # Prepara informações dos vídeos para download paralelo
        videos_info = []
        for download in pending_downloads:
            videos_info.append(
                {
                    "title": download["title"],
                    "url": download["url"],
                    "duration": 0,  # Não usado no download
                    "uploader": "Unknown",  # Não usado no download
                }
            )

        convert_to_mp3 = self.mp3_checkbox.isChecked()

        # Desabilita botão durante download
        self.download_pending_button.setText("Baixando...")
        self.download_pending_button.setEnabled(False)

        # Inicia download paralelo
        self.parallel_download_thread = ParallelDownloadThread(
            videos_info, output_path, convert_to_mp3
        )
        self.parallel_download_thread.progress_update.connect(self.on_download_progress)
        self.parallel_download_thread.all_finished.connect(
            self.pending_download_finished
        )
        self.parallel_download_thread.start()

    def pending_download_finished(self):
        """Callback quando downloads pendentes terminam"""
        self.download_pending_button.setText("Baixar Pendentes")
        self.download_pending_button.setEnabled(True)

        # Atualiza lista de downloads
        self.load_downloads_history()

    def open_download_folder(self):
        """Abre a pasta de downloads"""
        folder_path = self.path_label.text()
        self.open_download_folder_path(folder_path)

    def open_download_folder_path(self, folder_path):
        """Abre uma pasta específica"""
        if os.path.exists(folder_path):
            if sys.platform == "linux":
                subprocess.run(["xdg-open", folder_path])
            elif sys.platform == "darwin":
                subprocess.run(["open", folder_path])
            elif sys.platform == "win32":
                subprocess.run(["explorer", folder_path])

    def open_file_location(self, file_path):
        """Abre o local do arquivo específico"""
        if os.path.exists(file_path):
            folder_path = os.path.dirname(file_path)
            self.open_download_folder_path(folder_path)

    def load_downloads_history(self):
        """Carrega o histórico de downloads na tabela"""
        downloads = load_downloads_history()
        self.downloads_table.setRowCount(len(downloads))

        for i, download in enumerate(downloads):
            # Número da linha (coluna 0)
            number_item = QTableWidgetItem(str(i + 1))
            number_item.setTextAlignment(Qt.AlignCenter)
            self.downloads_table.setItem(i, 0, number_item)

            # Título (coluna 1)
            title_item = QTableWidgetItem(download.get("title", "Unknown"))
            self.downloads_table.setItem(i, 1, title_item)

            # Status (coluna 2)
            status = download.get("status", "unknown")
            status_item = QTableWidgetItem(status.capitalize())

            # Colorir baseado no status
            if status == "completed":
                status_item.setBackground(QColor("lightgreen"))
            elif status == "failed":
                status_item.setBackground(QColor("lightcoral"))
            elif status == "downloading":
                status_item.setBackground(QColor("lightyellow"))
            elif status == "pending":
                status_item.setBackground(QColor("lightblue"))

            self.downloads_table.setItem(i, 2, status_item)

            # Progresso (coluna 3)
            if status == "completed":
                progress_item = QTableWidgetItem("100% - Concluído")
                progress_item.setBackground(QColor("lightgreen"))
            elif status == "downloading":
                progress_item = QTableWidgetItem("Em andamento...")
                progress_item.setBackground(QColor("lightyellow"))
            elif status == "failed":
                progress_item = QTableWidgetItem("Falhou")
                progress_item.setBackground(QColor("lightcoral"))
            else:
                progress_item = QTableWidgetItem("0%")

            self.downloads_table.setItem(i, 3, progress_item)

            # Data (coluna 4)
            timestamp = download.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    date_str = dt.strftime("%d/%m/%Y %H:%M")
                except Exception:
                    date_str = timestamp
            else:
                date_str = "Unknown"

            date_item = QTableWidgetItem(date_str)
            self.downloads_table.setItem(i, 4, date_item)

            # Botão de ação (coluna 5) - sempre presente
            file_path = download.get("file_path", "")
            if file_path and os.path.exists(file_path):
                open_button = QPushButton("Abrir Pasta")
                open_button.clicked.connect(
                    lambda checked, path=file_path: self.open_file_location(path)
                )
            else:
                # Mesmo se o arquivo não existir, cria botão para abrir pasta padrão
                open_button = QPushButton("Pasta Downloads")
                open_button.clicked.connect(self.open_download_folder)
                open_button.setStyleSheet("QPushButton { color: gray; }")

            self.downloads_table.setCellWidget(i, 5, open_button)

    def clear_completed_downloads(self):
        """Remove downloads concluídos do histórico"""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "Deseja remover todos os downloads concluídos do histórico?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            from config import clear_completed_downloads as clear_config_downloads

            clear_config_downloads()
            self.load_downloads_history()

            QMessageBox.information(
                self, "Concluído", "Downloads concluídos removidos do histórico."
            )

    def clear_failed_downloads(self):
        """Remove downloads com falha do histórico"""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "Deseja remover todos os downloads com falha do histórico?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            from config import clear_failed_downloads as clear_config_failed

            clear_config_failed()
            self.load_downloads_history()

            QMessageBox.information(
                self, "Concluído", "Downloads com falha removidos do histórico."
            )

    def clear_all_downloads(self):
        """Remove todos os downloads do histórico"""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "Deseja remover TODOS os downloads do histórico?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            from config import clear_all_downloads as clear_config_all

            clear_config_all()
            self.load_downloads_history()

            QMessageBox.information(
                self, "Concluído", "Todos os downloads removidos do histórico."
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = YouTubeDownloader()
    ex.show()
    sys.exit(app.exec_())
