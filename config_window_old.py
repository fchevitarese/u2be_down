import sys

from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import load_config, save_config


class ConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Configurações")
        self.setFixedSize(500, 400)

        layout = QVBoxLayout()

        # Grupo de configurações de download
        download_group = QGroupBox("Configurações de Download")
        download_layout = QVBoxLayout()

        # Path de download
        self.path_label = QLabel("Pasta padrão para downloads:")
        download_layout.addWidget(self.path_label)

        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setText(self.config.get("default_download_path", ""))
        path_layout.addWidget(self.path_input)

        self.browse_button = QPushButton("Procurar")
        self.browse_button.clicked.connect(self.browse_path)
        path_layout.addWidget(self.browse_button)

        download_layout.addLayout(path_layout)

        # Conversão automática para MP3
        self.auto_mp3_checkbox = QCheckBox("Converter automaticamente para MP3")
        self.auto_mp3_checkbox.setChecked(
            self.config.get("auto_convert_to_mp3", True)
        )
        download_layout.addWidget(self.auto_mp3_checkbox)

        # Manter vídeo original
        self.keep_video_checkbox = QCheckBox(
            "Manter arquivo de vídeo original após conversão"
        )
        self.keep_video_checkbox.setChecked(self.config.get("keep_video", False))
        download_layout.addWidget(self.keep_video_checkbox)

        download_group.setLayout(download_layout)
        layout.addWidget(download_group)

        # Grupo de configurações do sistema
        system_group = QGroupBox("Configurações do Sistema")
        system_layout = QVBoxLayout()

        # Logging
        self.logging_checkbox = QCheckBox("Ativar logging detalhado")
        self.logging_checkbox.setChecked(self.config.get("logging_enabled", True))
        system_layout.addWidget(self.logging_checkbox)

        system_group.setLayout(system_layout)
        layout.addWidget(system_group)

        # Botões
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.save_config)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def browse_path(self):
        """Abre diálogo para selecionar pasta"""
        folder = QFileDialog.getExistingDirectory(
            self, "Selecionar pasta para downloads"
        )
        if folder:
            self.path_input.setText(folder)

    def save_config(self):
        """Salva as configurações"""
        new_config = {
            "default_download_path": self.path_input.text(),
            "logging_enabled": self.logging_checkbox.isChecked(),
            "auto_convert_to_mp3": self.auto_mp3_checkbox.isChecked(),
            "keep_video": self.keep_video_checkbox.isChecked(),
        }
        save_config(new_config)
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    config_window = ConfigWindow()
    config_window.show()
    sys.exit(app.exec_())

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_output_path)
        layout.addWidget(self.browse_button)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_config)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
        self.load_config()

    def browse_output_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self.path_input.setText(path)

    def load_config(self):
        config = load_config()
        self.path_input.setText(config.get("default_download_path", ""))

    def save_config(self):
        config = {"default_download_path": self.path_input.text().strip()}
        save_config(config)
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ConfigWindow()
    ex.show()
    sys.exit(app.exec_())
