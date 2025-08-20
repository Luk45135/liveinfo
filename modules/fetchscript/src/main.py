#!/usr/bin/env python3
# This file is the entry point for the app


import os
import sys
from pathlib import Path
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from fetchscript.window import Window

version_number = "0.3.3"

def main():
    # This creates the application for the Qt GUI
    app = QApplication(sys.argv)

    # This gets the path of the application icon and sets it
    icon_path = Path(os.environ.get("FETCHSCRIPT_SHARE", "../share/fetchscript/")) / "search-list.png"
    app.setWindowIcon(QIcon(str(icon_path.resolve())))
    
    # This instantiates the Window object from window.py and then shows it
    window = Window()
    window.show()
    
    # Boilerplate to handle graceful exit
    sys.exit(app.exec())

# Run the main function when this file gets executed directly
if __name__ == "__main__":
    main()
