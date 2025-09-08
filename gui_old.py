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
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QSplitter,
    QGroupBox,
)

from config import (
    load_config,
    save_config,
    load_downloads_history,
    clear_completed_downloads,
)
from config_window import ConfigWindow
from main import download_videos


class DownloadThread(QThread):
    progress = pyqtSignal(dict)
    finished = pyqtSignal()

    def __init__(self, url_file, output_path, convert_to_mp3, keep_video):
        super().__init__()
        self.url_file = url_file
        self.output_path = output_path
        self.convert_to_mp3 = convert_to_mp3
        self.keep_video = keep_video

    def run(self):
        logging.debug("DownloadThread started")
        try:
            download_videos(
                self.url_file,
                self.output_path,
                self.convert_to_mp3,
                self.keep_video,
                self.progress_callback,
            )
        except Exception as e:
            logging.error(f"Error in download thread: {e}")
        finally:
            self.finished.emit()

    def progress_callback(self, data):
        self.progress.emit(data)


class YouTubeDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.download_thread = None
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
                level=logging.DEBUG,
                format="%(asctime)s - %(levelname)s - %(message)s"
            )
        else:
            logging.disable(logging.CRITICAL)

    def initUI(self):
        self.setWindowTitle("YouTube Downloader")
        self.setWindowIcon(QIcon("assets/settings.png"))
        self.setGeometry(100, 100, 1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal com splitter
        main_layout = QVBoxLayout()
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Seção superior - Controles
        controls_widget = QWidget()
        controls_layout = QVBoxLayout()

        # Grupo de entrada
        input_group = QGroupBox("URLs para Download")
        input_layout = QVBoxLayout()

        self.url_text = QTextEdit()
        self.url_text.setPlaceholderText(
            "Cole as URLs do YouTube aqui (uma por linha)..."
        )
        self.url_text.setMaximumHeight(100)
        input_layout.addWidget(self.url_text)

        # Botões de arquivo
        file_layout = QHBoxLayout()
        self.file_button = QPushButton("Selecionar Arquivo")
        self.file_button.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_button)

        self.clear_urls_button = QPushButton("Limpar URLs")
        self.clear_urls_button.clicked.connect(self.clear_urls)
        file_layout.addWidget(self.clear_urls_button)
        
        file_layout.addStretch()
        input_layout.addLayout(file_layout)
        input_group.setLayout(input_layout)
        controls_layout.addWidget(input_group)

        # Grupo de opções
        options_group = QGroupBox("Opções de Download")
        options_layout = QVBoxLayout()

        self.mp3_checkbox = QCheckBox("Converter para MP3")
        self.mp3_checkbox.setChecked(
            self.config.get("auto_convert_to_mp3", True)
        )
        options_layout.addWidget(self.mp3_checkbox)

        self.keep_video_checkbox = QCheckBox("Manter vídeo original")
        self.keep_video_checkbox.setChecked(
            self.config.get("keep_video", False)
        )
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

        self.clear_completed_button = QPushButton("Limpar Concluídos")
        self.clear_completed_button.clicked.connect(self.clear_completed_downloads)
        list_header_layout.addWidget(self.clear_completed_button)

        self.refresh_button = QPushButton("Atualizar")
        self.refresh_button.clicked.connect(self.load_downloads_history)
        list_header_layout.addWidget(self.refresh_button)

        downloads_layout.addLayout(list_header_layout)

        # Tabela de downloads
        self.downloads_table = QTableWidget()
        self.downloads_table.setColumnCount(5)
        self.downloads_table.setHorizontalHeaderLabels([
            "Título", "Status", "Progresso", "Data", "Ações"
        ])
        
        # Configurar redimensionamento das colunas
        header = self.downloads_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        downloads_layout.addWidget(self.downloads_table)
        downloads_widget.setLayout(downloads_layout)
        splitter.addWidget(downloads_widget)

        # Configurar splitter
        splitter.setSizes([300, 400])
        main_layout.addWidget(splitter)

        central_widget.setLayout(main_layout)
        self._createMenuBar()

    def _createMenuBar(self):
        """Cria a barra de menu"""
        menubar = self.menuBar()
        
        # Menu Configurações
        config_menu = menubar.addMenu("Configurações")
        
        config_action = config_menu.addAction("Preferências")
        config_action.triggered.connect(self.open_config)

    def open_config(self):
        """Abre a janela de configurações"""
        config_window = ConfigWindow()
        if config_window.exec_():
            # Recarrega configurações após fechar a janela
            self.config = load_config()
            self.path_label.setText(self.config.get("default_download_path", ""))
            self.mp3_checkbox.setChecked(
                self.config.get("auto_convert_to_mp3", True)
            )
            self.keep_video_checkbox.setChecked(
                self.config.get("keep_video", False)
            )
            self.setup_logging()

    def select_file(self):
        """Seleciona arquivo com URLs"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar arquivo com URLs", "", "Text files (*.txt)"
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    self.url_text.setPlainText(content)
            except Exception as e:
                QMessageBox.warning(
                    self, "Erro", f"Erro ao ler arquivo: {e}"
                )

    def clear_urls(self):
        """Limpa o campo de URLs"""
        self.url_text.clear()

    def browse_path(self):
        """Seleciona pasta para download"""
        folder = QFileDialog.getExistingDirectory(
            self, "Selecionar pasta para downloads"
        )
        if folder:
            self.path_label.setText(folder)
            # Atualiza configuração
            self.config["default_download_path"] = folder
            save_config(self.config)

    def start_download(self):
        """Inicia o download"""
        urls = self.url_text.toPlainText().strip()
        if not urls:
            QMessageBox.warning(
                self, "Aviso", "Por favor, insira pelo menos uma URL"
            )
            return

        output_path = self.path_label.text()
        if not output_path:
            QMessageBox.warning(
                self, "Aviso", "Por favor, selecione uma pasta de download"
            )
            return

        # Salva URLs temporariamente
        temp_file = "temp_urls.txt"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(urls)

        # Inicia thread de download
        self.download_thread = DownloadThread(
            temp_file,
            output_path,
            self.mp3_checkbox.isChecked(),
            self.keep_video_checkbox.isChecked()
        )
        
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.start()
        
        self.download_button.setText("Baixando...")
        self.download_button.setEnabled(False)

    def download_finished(self):
        """Chamado quando o download termina"""
        self.download_button.setText("Iniciar Download")
        self.download_button.setEnabled(True)
        
        # Remove arquivo temporário
        try:
            os.remove("temp_urls.txt")
        except:
            pass
            
        # Atualiza lista de downloads
        self.load_downloads_history()

    def open_download_folder(self):
        """Abre a pasta de downloads"""
        folder_path = self.path_label.text()
        if os.path.exists(folder_path):
            if sys.platform == "linux":
                subprocess.run(["xdg-open", folder_path])

    def open_file_location(self, file_path):
        """Abre o local do arquivo específico"""
        if os.path.exists(file_path):
            folder_path = os.path.dirname(file_path)
            if sys.platform == "linux":
                subprocess.run(["xdg-open", folder_path])

    def load_downloads_history(self):
        """Carrega o histórico de downloads na tabela"""
        downloads = load_downloads_history()
        
        self.downloads_table.setRowCount(len(downloads))
        
        for i, download in enumerate(downloads):
            # Título
            title_item = QTableWidgetItem(download.get("title", "Unknown"))
            self.downloads_table.setItem(i, 0, title_item)
            
            # Status
            status = download.get("status", "unknown")
            status_item = QTableWidgetItem(status.capitalize())
            
            # Colorir baseado no status
            if status == "completed":
                status_item.setBackground(QColor("lightgreen"))
            elif status == "failed":
                status_item.setBackground(QColor("lightcoral"))
            elif status == "downloading":
                status_item.setBackground(QColor("lightyellow"))
                
            self.downloads_table.setItem(i, 1, status_item)
            
            # Progresso
            if status == "completed":
                progress_item = QTableWidgetItem("100%")
            elif status == "downloading":
                progress_item = QTableWidgetItem("Em andamento...")
            else:
                progress_item = QTableWidgetItem("0%")
                
            self.downloads_table.setItem(i, 2, progress_item)
            
            # Data
            timestamp = download.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    date_str = dt.strftime("%d/%m/%Y %H:%M")
                except:
                    date_str = timestamp
            else:
                date_str = "Unknown"
                
            date_item = QTableWidgetItem(date_str)
            self.downloads_table.setItem(i, 3, date_item)
            
            # Botão de ação
            file_path = download.get("file_path", "")
            if file_path and os.path.exists(file_path):
                open_button = QPushButton("Abrir Pasta")
                open_button.clicked.connect(
                    lambda checked, path=file_path: 
                    self.open_file_location(path)
                )
                self.downloads_table.setCellWidget(i, 4, open_button)

    def clear_completed_downloads(self):
        """Remove downloads concluídos do histórico"""
        reply = QMessageBox.question(
            self, 
            "Confirmar", 
            "Deseja remover todos os downloads concluídos do histórico?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            clear_completed_downloads()
            self.load_downloads_history()


def main():
    app = QApplication(sys.argv)
    downloader = YouTubeDownloader()
    downloader.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

        self.urls_label = QLabel("Enter URLs (one per line):")
        layout.addWidget(self.urls_label)

        self.urls_text = QTextEdit()
        layout.addWidget(self.urls_text)

        self.convert_to_mp3_check = QCheckBox("Convert to MP3")
        layout.addWidget(self.convert_to_mp3_check)

        self.keep_video_check = QCheckBox("Keep the video file")
        layout.addWidget(self.keep_video_check)

        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_bar)

        logging.debug("Adding progress dialog")
        self.progress_dialog = CustomProgressDialog(self)
        self.progress_dialog.setLabelText("Converting...")
        self.progress_dialog.setCancelButton(None)  # Remove the cancel button
        self.progress_dialog.setRange(0, 0)  # Indeterminate progress
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)
        self.progress_dialog.hide()
        logging.debug("Progress dialog initialized and hidden")

        # Connect signals to log events
        self.progress_dialog.canceled.connect(self.on_progress_dialog_canceled)
        self.progress_dialog.finished.connect(self.on_progress_dialog_finished)

        central_widget.setLayout(layout)
        self.load_config()

    def _createMenuBar(self):
        logging.debug("Creating menu bar")
        menuBar = self.menuBar()
        # Creating menus using a QMenu object
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        # Creating menus using a title
        editMenu = menuBar.addMenu("&Edit")
        helpMenu = menuBar.addMenu("&Help")

    def show_about_dialog(self):
        QMessageBox.about(self, "About", "YouTube Downloader v1.0")

    def on_progress_dialog_canceled(self):
        logging.debug("Progress dialog canceled")

    def on_progress_dialog_finished(self):
        logging.debug("Progress dialog finished")

    def browse_output_path(self):
        logging.debug("browse_output_path called")
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self.path_input.setText(path)

    def start_download(self):
        logging.debug("start_download called")
        urls = self.urls_text.toPlainText().strip()
        output_path = self.default_download_path
        convert_to_mp3 = self.convert_to_mp3_check.isChecked()
        keep_video = self.keep_video_check.isChecked()

        if not urls or not output_path:
            QMessageBox.critical(self, "Error", "Please provide URLs and output path.")
            return

        url_file = "urls.txt"
        with open(url_file, "w") as file:
            file.write(urls)

        self.download_thread = DownloadThread(
            url_file, output_path, convert_to_mp3, keep_video
        )
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.start()
        self.status_label.setText("Downloading...")
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.progress_dialog.hide()
        self.download_started = True
        logging.debug("Download started")

    def update_progress(self, data):
        if data.get("status") == "finished":
            self.progress_bar.setValue(100)
            if self.convert_to_mp3_check.isChecked() and self.download_started:
                self.status_label.setText("Converting...")
                self.progress_bar.hide()
                self.progress_dialog.show()
                logging.debug("Progress dialog shown for conversion")
            else:
                self.status_label.setText("Download completed.")
        else:
            self.progress_bar.setValue(
                int(data.get("downloaded_bytes", 0) / data.get("total_bytes", 1) * 100)
            )

    def download_finished(self):
        logging.debug("download_finished called")
        if self.convert_to_mp3_check.isChecked() and self.download_started:
            self.progress_dialog.hide()
            logging.debug("Progress dialog hidden after conversion")
            self.status_label.setText("Conversion completed.")
            QMessageBox.information(self, "Success", "Conversion completed.")
        else:
            self.status_label.setText("Download completed.")
            QMessageBox.information(self, "Success", "Download completed.")
        self.download_started = False
        logging.debug("Download finished")
        self.clear_inputs()

    def clear_inputs(self):
        logging.debug("Clearing inputs")
        self.urls_text.clear()
        self.convert_to_mp3_check.setChecked(False)

    def set_progress_dialog_value(self, value):
        logging.debug(f"Setting progress dialog value: {value}")
        self.progress_dialog.setValue(value)

    def open_config_window(self):
        self.config_window = ConfigWindow()
        self.config_window.show()

    def load_config(self):
        config = load_config()
        self.default_download_path = config.get("default_download_path", "")


if __name__ == "__main__":
    logging.debug("Application started")
    app = QApplication(sys.argv)
    ex = YouTubeDownloader()
    ex.show()
    sys.exit(app.exec_())
