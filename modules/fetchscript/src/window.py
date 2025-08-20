import os
import logging
from pathlib import Path
from subprocess import Popen
from PySide6.QtCore import QObject, QSize, QThread, Signal
from PySide6.QtGui import QAction, QMovie, Qt
from PySide6.QtWidgets import QMainWindow, QMessageBox, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QLabel, QPlainTextEdit, QWidget
from .fetch import Prepare, SystemInfo, DiskInfo, compile_pdf


class FetchRunner(QThread):
    def __init__(self, Window: "Window"):
        super().__init__()
        self.Window = Window

    def handle_backup(self, csv_path: Path) -> bool:
        csv_backup = csv_path.with_suffix(csv_path.suffix + ".bak")
        if csv_backup.exists():
            self.Window.logger.info(f"Restoring {csv_backup.name}")
            csv_backup.rename(csv_path)
            return True
        else:
            return False

    def run(self):
        prepare = Prepare() # Init Prepare object
        prepare.prepare_work_dir() # actually prepare working directory
        work_dir = prepare.work_dir

        if self.Window.general_info_checkbox.isChecked():
            system_info_path = Path(work_dir / "system_info.csv")
            if not self.handle_backup(system_info_path):
                SystemInfo(work_dir).write_system_info()
        
        if self.Window.disk_info_checkbox.isChecked():
            disk_info_path = Path(work_dir / "disks.csv")
            if not self.handle_backup(disk_info_path):
                DiskInfo(work_dir).write_disk_info()

        pdf_path: Path = compile_pdf(work_dir)
        Popen(["xdg-open", pdf_path])


class TextBoxLogger(logging.Handler, QObject):
    log_signal = Signal(str)

    def __init__(self, textbox: QPlainTextEdit):
        logging.Handler.__init__(self)
        QObject.__init__(self)
        self.textbox = textbox
        self.log_signal.connect(self.textbox.appendPlainText)

    def emit(self, record):
        msg = self.format(record)
        self.log_signal.emit(msg)


class Window(QMainWindow):
    def __init__(self):
        from .main import version_number
        super().__init__()
        self.application_name = "SystemReport"
        self.version = version_number
        self.setWindowTitle(self.application_name)
        self.resize(960, 540)

        self.asset_path = Path(os.environ.get("FETCHSCRIPT_SHARE", "../share/fetchscript/"))

        self.setup_ui()
        self.setup_logger()

        self.setup_menu()

    def setup_ui(self):

        # Create Widgets
        options_label = QLabel("Optionen:")

        open_folder_button = QPushButton("Öffne Ordner")
        open_folder_button.pressed.connect(self.open_folder)

        self.start_button = QPushButton("Start")
        self.start_button.pressed.connect(self.start_fetching)

        spinner_gif_path = (self.asset_path / "spinner.gif")
        self.spinner = QLabel()
        self.spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinner_movie = QMovie(str(spinner_gif_path))
        self.spinner_movie.setScaledSize(QSize(32, 32))
        self.spinner.setMovie(self.spinner_movie)
        self.spinner.hide()

        self.log_textbox = QPlainTextEdit()
        self.log_textbox.setReadOnly(True)

        # Setup Layout
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        options_vbox = QVBoxLayout()
        buttons_hbox = QHBoxLayout()

            # Options
        options_vbox.addWidget(options_label)

        general_info_hbox, self.general_info_checkbox = self.make_option(True, "Allgemeine Systeminformationen")
        options_vbox.addLayout(general_info_hbox)

        disk_info_hbox, self.disk_info_checkbox = self.make_option(True, "Speichergeräteinformationen")
        options_vbox.addLayout(disk_info_hbox)

        options_vbox.addStretch()

        vbox.addLayout(hbox)
        hbox.addLayout(options_vbox, stretch=1)
        hbox.addWidget(self.log_textbox, stretch=3)

        buttons_hbox.addWidget(open_folder_button)
        buttons_hbox.addWidget(self.start_button)
        buttons_hbox.addWidget(self.spinner)

        vbox.addLayout(buttons_hbox)

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

    def setup_logger(self):
        textbox_handler = TextBoxLogger(self.log_textbox)
        textbox_handler.setFormatter(logging.Formatter("[%(levelname)s] - %(message)s"))
        
        self.logger = logging.getLogger("fetchscript_logger")
        self.logger.addHandler(textbox_handler)
        self.logger.setLevel(logging.INFO)

    def setup_menu(self):
        menu_bar = self.menuBar()

        help_menu = menu_bar.addMenu("Hilfe")

        about_action = QAction("Über", self)
        about_action.triggered.connect(self.show_about_dialog)

        help_menu_actions: list[QAction] = [about_action]
        help_menu.addActions(help_menu_actions)

    def show_about_dialog(self):
        QMessageBox.about(self, f"Über {self.application_name}", f"{self.application_name}\nhttps://github.com/Luk45135/liveinfo\nVersion {self.version}\nErstellt von Lukas Dorji")

    def open_folder(self):
        Popen(["xdg-open", Prepare().work_dir])

    def start_fetching(self):
        # Replace button with spinner
        self.start_button.hide()
        self.spinner.show()
        self.spinner_movie.start()

        self.logger.info("Started")

        self.worker = FetchRunner(self)
        self.worker.finished.connect(self.on_fetching_done)
        self.worker.start()

    def on_fetching_done(self):
        self.spinner_movie.stop()
        self.spinner.hide()
        self.start_button.show()
        self.logger.info("Finished")


        



