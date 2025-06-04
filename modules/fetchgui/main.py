
import sys
from PySide6.QtWidgets import QApplication
from window import Window

app = QApplication(sys.argv)

window = Window()
window.show()

app.exec()
