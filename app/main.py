import sys
from PySide6.QtWidgets import QApplication
from app.gui.main_window import MainWindow

# Tema scuro moderno (stile Catppuccin/Discord)
DARK_THEME_QSS = """
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: 10pt;
}
QLineEdit {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 8px 12px;
    color: #cdd6f4;
}
QLineEdit:focus {
    border: 1px solid #89b4fa;
}
QPushButton {
    background-color: #45475a;
    border: none;
    border-radius: 6px;
    padding: 8px 15px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #585b70;
}
QPushButton:pressed {
    background-color: #313244;
}
QPushButton:disabled {
    background-color: #181825;
    color: #6c7086;
}
#download_btn {
    background-color: #89b4fa;
    color: #11111b;
    font-size: 12pt;
    padding: 10px;
}
#download_btn:hover {
    background-color: #b4befe;
}
#download_btn:disabled {
    background-color: #181825;
    color: #6c7086;
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #45475a;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 15px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
    color: #89b4fa;
}
QComboBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 5px;
}
QComboBox::drop-down {
    border: none;
}
QProgressBar {
    border: 1px solid #45475a;
    border-radius: 6px;
    text-align: center;
    background-color: #313244;
    font-weight: bold;
    color: #cdd6f4; 
}
QProgressBar::chunk {
    background-color: #a6e3a1;
    border-radius: 5px;
}
QProgressBar {
    color: #11111b; 
}
"""

def main():
    app = QApplication(sys.argv)
    
    # Applica il tema a tutta l'applicazione
    app.setStyleSheet(DARK_THEME_QSS)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()