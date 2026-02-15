from PyQt6.QtCore import Qt
import sys, json, random, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, ROOT)

# -- Services --
from Services import ConnectionListener

# -- Functions --
from Functions import GetUserSettings, AppendUserSettings

# -- Objects --
generalSettingsWindow = None

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
    global generalSettingsWindow, UserSettings

    uiApp = UIApplication(sys.argv, appName="GeneralSettingsApplication")

    class GeneralSettingsWindow(ModifiedWindow):
        def __init__(self, **kwargs):
            super().__init__(**kwargs) 

            UpdateUserSettings()

            self.setWindowTitle('General Settings')
            self.resize(400, 600)
            screen = uiApp.primaryScreen().availableGeometry()

            if UserSettings["Windows"][self.objectName()].get("position", False) == False:
                self.move(
                    screen.left() + random.randint(0, screen.width() - self.width()),
                    screen.top() + (screen.height() - self.height()) // 2
                )
                
            self.show()

        def closeEvent(self, event):
            event.ignore()
            self.Hide(onFinished=uiApp.exit, Hard=True)
            return

    generalSettingsWindow = GeneralSettingsWindow(titleKey="titles/generalSettings", name="GeneralSettings", Modifiers=["minimize", "close"])

    # CODE -----------------------------------------------------------------------------------------------

    def Close():
        generalSettingsWindow.Hide(onFinished=uiApp.exit, Hard=True)
        
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