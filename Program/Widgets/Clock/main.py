from PyQt6.QtCore import Qt
import sys, json, random, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, ROOT)

# -- Services --
from Services import CollectionService

# -- Functions --
from Functions import GetUserSettings

# -- Resources --

# -- Constants --
with open("Data/Pathes.json", "r", encoding="utf-8") as pFile:
    Pathes = json.load(pFile)

# -- Data --
with open(Pathes["Constants"], "r", encoding="utf-8") as cFile:
    Constants = json.load(cFile)
with open(Pathes["Data"], "r", encoding="utf-8") as dataFile:
    Data = json.load(dataFile)

UserSettings = None

def UpdateUserSettings():
    global UserSettings
    UserSettings = GetUserSettings()

UpdateUserSettings()

# -- Scripts --
from Classes import InteractableWindow, UIApplication

if __name__ == "__main__":
    uiApp = UIApplication(sys.argv)
    uiApp.setStyleSheet("""
        QPushButton:focus { outline: none; border: none; }
    """)

class ClockMenu(InteractableWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs) 

        self.setWindowTitle('Clock Menu')
        self.resize(300, 600)
        screen = uiApp.primaryScreen().availableGeometry()
        self.move(
            screen.left() + random.randint(0, screen.width() - self.width()),
            screen.top() + (screen.height() - self.height()) // 2
        )
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.show()

if __name__ == "__main__":
    menuWindow = ClockMenu(name="Clock")

    sys.exit(uiApp.exec())