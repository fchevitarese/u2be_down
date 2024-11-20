import logging
import sys

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QProgressDialog,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from config import load_config
from config_window import ConfigWindow
from main import download_videos

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class CustomProgressDialog(QProgressDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.cancel()  # Cancel immediately after creation to prevent auto-show

    def showEvent(self, event):
        if self.parent.download_started:
            logging.debug("Progress dialog shown")
            super().showEvent(event)
        else:
            logging.debug(
                "Progress dialog show event ignored because download has not started"
            )

    def hideEvent(self, event):
        logging.debug("Progress dialog hidden")
        super().hideEvent(event)

    def show(self):
        if self.parent.download_started:
            logging.debug("Progress dialog show called")
            super().show()
        else:
            logging.debug(
                "Progress dialog show call ignored because download has not started"
            )


class DownloadThread(QThread):
    progress = pyqtSignal(dict)

    def __init__(self, url_file, output_path, convert_to_mp3, keep_video):
        super().__init__()
        self.url_file = url_file
        self.output_path = output_path
        self.convert_to_mp3 = convert_to_mp3
        self.keep_video = keep_video

    def run(self):
        logging.debug("DownloadThread started")
        download_videos(
            self.url_file,
            self.output_path,
            self.convert_to_mp3,
            self.keep_video,
            self.progress_callback,
        )

    def progress_callback(self, data):
        self.progress.emit(data)


class YouTubeDownloader(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.initUI()
        self._createMenuBar()
        self.download_started = False
        logging.debug("YouTubeDownloader initialized")

    def initUI(self):
        self.setWindowTitle("YouTube Downloader")
        self.setWindowIcon(QIcon("assets/settings.png"))  # Set the window icon

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

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
