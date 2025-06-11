
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QMessageBox, QVBoxLayout, QHBoxLayout, QLayout, QPushButton, QCheckBox, QLabel, QPlainTextEdit, QWidget
from fetch import Prepare, SystemInfo, DiskInfo

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.application_name = "SystemInfo Report"
        self.version = "0.2.0"
        self.setWindowTitle(self.application_name)

        self.setup_ui()
        self.setup_menu()

    def setup_ui(self):

        # Create Widgets
        options_label = QLabel("Optionen:")

        self.start_button = QPushButton("Start")
        self.start_button.pressed.connect(self.start_fetching)

        self.log_textbox = QPlainTextEdit()
        self.log_textbox.setReadOnly(True)

        # Setup Layout
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        options_vbox = QVBoxLayout()

            # Options
        options_vbox.addWidget(options_label)

        general_info_hbox, self.general_info_checkbox = self.make_option(True, "Allgemeine Systeminformationen")
        options_vbox.addLayout(general_info_hbox)

        disk_info_hbox, self.disk_info_checkbox = self.make_option(True, "Speichergeräteinformationen")
        options_vbox.addLayout(disk_info_hbox)

        options_vbox.addStretch()

        vbox.addLayout(hbox)
        hbox.addLayout(options_vbox)
        hbox.addWidget(self.log_textbox)

        vbox.addWidget(self.start_button)

        # Set Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setLayout(vbox)

    def make_option(self, checked: bool, option_text: str) -> tuple[QHBoxLayout, QCheckBox]:
        checkbox = QCheckBox()
        checkbox.setChecked(checked)
        label = QLabel(option_text)

        layout = QHBoxLayout()
        layout.addWidget(checkbox)
        layout.addWidget(label)
        layout.addStretch()
        return layout, checkbox

    def setup_menu(self):
        menu_bar = self.menuBar()

        help_menu = menu_bar.addMenu("Hilfe")

        about_action = QAction("Über", self)
        about_action.triggered.connect(self.show_about_dialog)

        help_menu_actions: list[QAction] = [about_action]
        help_menu.addActions(help_menu_actions)

    def show_about_dialog(self):
        QMessageBox.about(self, f"Über {self.application_name}", f"{self.application_name}\nVersion {self.version}\nErstellt von Lukas Dorji")


    def start_fetching(self):
        self.log_textbox.appendPlainText("Gestartet")
        
        work_dir = Prepare().work_dir

        if self.general_info_checkbox.isChecked():
            SystemInfo(work_dir)
        
        if self.disk_info_checkbox.isChecked():
            DiskInfo(work_dir)



