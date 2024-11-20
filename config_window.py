import sys

from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
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
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Configuration")

        layout = QVBoxLayout()

        self.path_label = QLabel("Default Download Path:")
        layout.addWidget(self.path_label)

        self.path_input = QLineEdit()
        layout.addWidget(self.path_input)

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
