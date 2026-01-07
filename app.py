import sys
import shutil
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog,
    QTextEdit, QCheckBox, QHBoxLayout, QFrame
)
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt, QTimer
from PyPDF2 import PdfReader
import docx

# ---------------- Version -----------------
VERSION_FILE = "version.txt"

def get_version():
    try:
        with open(VERSION_FILE, "r") as f:
            return f.read().strip()
    except:
        return "1.0.0"

# ---------------- Categories -----------------
CATEGORIES = {
    "Research Papers": [".pdf"],
    "Instructions": [".docx", ".txt"],
    "Spreadsheets": [".xlsx", ".csv"],
    "Images": [".png", ".jpg", ".jpeg", ".gif"],
    "Archives": [".zip", ".rar", ".tar", ".gz"]
}

# ---------------- Main App -----------------
class FileOrganizerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Smart File Organizer v{get_version()}")
        self.setGeometry(400, 200, 550, 450)
        self.folder_path = Path.home() / "Downloads"
        self.initUI()
        self.set_dark_theme()

        # Optional: auto-run every 60 sec
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self.organize_files)
        # self.auto_timer.start(60000)  # Uncomment to auto-run every 60 sec

    def initUI(self):
        layout = QVBoxLayout()

        # Folder Selection
        self.folder_label = QLabel(f"Folder: {self.folder_path}")
        self.folder_label.setFont(QFont("Arial", 10))
        layout.addWidget(self.folder_label)

        select_btn = QPushButton("Select Folder")
        select_btn.clicked.connect(self.select_folder)
        layout.addWidget(select_btn)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Category checkboxes
        self.checkboxes = {}
        layout.addWidget(QLabel("Select categories to organize:"))
        for cat in CATEGORIES:
            cb = QCheckBox(cat)
            cb.setChecked(True)
            layout.addWidget(cb)
            self.checkboxes[cat] = cb

        # Organize Button
        organize_btn = QPushButton("Organize Files")
        organize_btn.clicked.connect(self.organize_files)
        layout.addWidget(organize_btn)

        # Log Area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("Courier", 9))
        layout.addWidget(self.log_area)

        self.setLayout(layout)

    # ---------------- Folder Selection ----------------
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", str(self.folder_path))
        if folder:
            self.folder_path = Path(folder)
            self.folder_label.setText(f"Folder: {self.folder_path}")

    # ---------------- Categorize Files ----------------
    def categorize_file(self, file_path):
        ext = file_path.suffix.lower()
        
        # PDFs → Smart research detection
        if ext == ".pdf" and self.checkboxes["Research Papers"].isChecked():
            try:
                reader = PdfReader(str(file_path))
                text = ""
                for page in reader.pages[:3]:
                    text += page.extract_text() or ""
                keywords = ["abstract", "introduction", "methodology", "references"]
                if any(k.lower() in text.lower() for k in keywords):
                    return "Research Papers"
            except:
                pass
            return "Others"

        # Word / Txt → Smart instruction detection
        if ext in [".docx", ".txt"] and self.checkboxes["Instructions"].isChecked():
            try:
                if ext == ".docx":
                    doc = docx.Document(str(file_path))
                    text = "\n".join([p.text for p in doc.paragraphs[:10]])
                else:
                    with open(file_path, "r", encoding="utf-8") as f:
                        text = "".join([next(f) for _ in range(10)])
                keywords = ["step", "instruction", "guide", "how to"]
                if any(k.lower() in text.lower() for k in keywords):
                    return "Instructions"
            except:
                pass
            return "Others"

        # Default category based on extension
        for category, extensions in CATEGORIES.items():
            if ext in extensions and self.checkboxes[category].isChecked():
                return category
        return "Others"

    # ---------------- Organize Files ----------------
    def organize_files(self):
        self.log_area.clear()
        for file in self.folder_path.iterdir():
            if file.is_file():
                category = self.categorize_file(file)
                target_folder = self.folder_path / category
                target_folder.mkdir(exist_ok=True)
                shutil.move(str(file), target_folder / file.name)
                self.log_area.append(f"Moved {file.name} → {category}")
        self.log_area.append("\nOrganization Complete!")

    # ---------------- Dark Theme ----------------
    def set_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
        palette.setColor(QPalette.HighlightedText, Qt.black)
        QApplication.setPalette(palette)

# ---------------- Main ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileOrganizerApp()
    window.show()
    sys.exit(app.exec_())
