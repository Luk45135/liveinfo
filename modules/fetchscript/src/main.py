#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from fetchscript.window import Window

def main():
    app = QApplication(sys.argv)

    icon_path = Path(os.environ.get("FETCHSCRIPT_SHARE", "../share/fetchscript/")) / "search-list.png"
    app.setWindowIcon(QIcon(str(icon_path.resolve())))
    
    window = Window()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
