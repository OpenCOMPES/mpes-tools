from PyQt5.QtWidgets import QApplication
from mpes_tools.Main import ARPES_Analyser  # Assuming the first code is saved as main_window.py

import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Initialize the Qt application
    window = ARPES_Analyser()  # Create an instance of your main window
    window.show()  # Show the window
    sys.exit(app.exec_())  # Run the Qt event loop
    
# if __name__ == "__main__":
#     window = MainWindow()  # Instantiate the MainWindow
#     window.show()  # Show the window