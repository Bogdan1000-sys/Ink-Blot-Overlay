from PyQt6.QtCore import Qt
import sys, json, random, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, ROOT)

# -- Services --
from Services import ConnectionListener

# -- Functions --
from Functions import GetUserSettings, AppendUserSettings

# -- Objects --
clockSettingWindow = None

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
from Classes import ModifiedWindow, UIApplication

def main(connection):
    global clockSettingWindow, UserSettings

    uiApp = UIApplication(sys.argv, appName="ClockApplication")

    class ClockMenu(ModifiedWindow):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            
            UpdateUserSettings()

            self.setWindowTitle('Clock Menu')
            self.resize(500, 600)
            screen = uiApp.primaryScreen().availableGeometry()

            if UserSettings["Windows"][self.objectName()].get("position", False) == False:
                self.move(
                    screen.left() + random.randint(0, screen.width() - self.width()),
                    screen.top() + (screen.height() - self.height()) // 2
                )
                
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self.show()

        def onClose(self):
            UpdateUserSettings()
            activeWidgets = UserSettings.get("General", {}).get("activeWidgets", [])
            activeWidgets.remove(self.objectName())
            AppendUserSettings("General", {
                "activeWidgets": activeWidgets
            })

            connection.send("code:UpdatePreview")

    clockSettingWindow = ClockMenu(name="Clock", Modifiers=["settings", "minimize", "close"])

    # CODE -----------------------------------------------------------------------------------------------

    def Close():
        clockSettingWindow.Hide(onFinished=clockSettingWindow.deleteLater, Hard=True)

    codeFunctions = {
        "Close": Close
    }

    def onMessage(msg: str):

        if isinstance(msg, str):
            if ":" not in msg: return
            code, action = msg.split(":", 1)
            if code == "code" and action in codeFunctions:
                codeFunctions[action]()

    # -----------------------------------------------------------------------------------------------------

    listener = ConnectionListener(connection)
    listener.messageReceived.connect(onMessage)
    listener.start()
    
    sys.exit(uiApp.exec())