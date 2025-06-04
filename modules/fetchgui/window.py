
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QLayout, QPushButton, QCheckBox, QWidget, QLabel, QPlainTextEdit

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SystemInfoPdf")

        # Create Widgets
        options_label = QLabel("Optionen:")
        start_button = QPushButton("Start")
        log_textbox = QPlainTextEdit()
        log_textbox.setReadOnly(True)

        # Setup Layout
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()

        vbox.addLayout(hbox)
        hbox.addWidget(options_label)
        hbox.addWidget(log_textbox)

        vbox.addWidget(start_button)

        # Set Layout
        self.setLayout(vbox)


