from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy, QBoxLayout
import sys, json, random, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, ROOT)

# -- Services --
from Services import InitializationService
from Services import (
    ConnectionListener,
    SettingsService,
    LocalizationService,
    SoundService
)
InitializationService.__init__()

SoundService.loadFolder("Resources/SFX")

# -- Functions --


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

# -- Scripts --
from Classes import ModifiedWindow, UIApplication

# -- Style --
ButtonStyle = '''
    QPushButton[class='scButton'] {
        background-color: qlineargradient(
            x1: 0, y1: 0,
            x2: 0, y2: 1,
            stop: 0 rgba(70, 35, 0, 255),
            stop: 1 rgba(40, 20, 0, 255)
        );
        border: 1px solid rgba(255, 106, 0, 255);
        border-radius: 15px;
    }
    QPushButton[class='scButton:unselect'], QPushButton[class='scButton:deactivate'] {
        background-color: qlineargradient(
            x1: 0, y1: 0,
            x2: 0, y2: 1,
            stop: 0 rgba(50, 15, 0, 255),
            stop: 1 rgba(20, 0, 0, 255)
        );
        border: 1px solid rgba(255, 106, 0, 255);
        border-radius: 15px;
    }
    QPushButton[class='scButton']:hover, QPushButton[class='scButton:unselect']:hover, QPushButton[class='scButton:deactivate']:hover {
        background: qlineargradient(
            x1: 0, y1: 1,
            x2: 0, y2: 0,
            stop: 0 #000000,
            stop: 1 #301400
        );
    }
    QLabel[class='scButtonLabel'] {
        background: transparent;
        font-size: 15px;
        font-family: 'Courier New', Courier, monospace;
        color: rgba(255, 106, 0, 255);
    }
'''

def main(connection):
    global generalSettingsWindow

    uiApp = UIApplication(sys.argv, appName="GeneralSettingsApplication")

    class GeneralSettingsWindow(ModifiedWindow):
        def __init__(self, **kwargs):
            super().__init__(**kwargs) 

            SettingsService.updateUserSettings()

            self.setWindowTitle('General Settings')
            self.resize(400, 600)
            screen = uiApp.primaryScreen().availableGeometry()

            if SettingsService.settings["Windows"][self.objectName()].get("position", False) == False:
                self.move(
                    screen.left() + random.randint(0, screen.width() - self.width()),
                    screen.top() + (screen.height() - self.height()) // 2
                )

            LocalizationService.registerAdaptableText(self.uis["holdAlt"], "labels/ALT")

            self.show()
            self.stylizeWindow()

        def stylizeWindow(self):
            self.mainLayout.setContentsMargins(0, 2, 0, 0)

            self.mainContainer = QFrame(self)
            self.mainContainer.setFixedSize(
                self.width(),
                self.height() - 35
            )
            self.mainContainer.setProperty("class", "mainContainer")
            self.mainContainer.setStyleSheet("""
                QFrame[class='mainContainer'] {
                    background-color: rgba(0, 0, 0, 255);
                    border: 1px solid rgba(255, 106, 0, 100);
                    border-radius: 15px;
                }
                                             
                QFrame[class='OptionsContainer'] {
                    background: qlineargradient(
                        x1: 0, y1: 0,
                        x2: 0, y2: 1,
                        stop: 0 #000000,
                        stop: 1 #1a0d00
                    );
                    border: 1px solid #42240f;
                    border-radius: 15px;
                }
                                             
                QFrame[class='ButtonsContainer'] {
                    background: transparent;
                    border: none;
                }
            """ + ButtonStyle)
            self.mainLayout.addWidget(self.mainContainer)
            self.mainContainer.show()

            self.mainContainer.mainLayout = QVBoxLayout()
            self.mainContainer.mainLayout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
            self.mainContainer.mainLayout.setSpacing(5)
            self.mainContainer.mainLayout.setContentsMargins(5,5,5,5)
            self.mainContainer.setLayout(self.mainContainer.mainLayout)

            self.elements = {}

            # NAVIGATION ---------------------------------------------------------------------------------------------

            self.elements["NavigationLayout"] = QHBoxLayout()
            self.elements["NavigationLayout"].setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.elements["NavigationLayout"].setContentsMargins(0, 0, 0, 0)
            self.mainContainer.mainLayout.addLayout(self.elements["NavigationLayout"])

            # OPTIONS LIST ---------------------------------------------------------------------------------------------

            self.elements["OptionsContainer"] = QFrame(self.mainContainer)
            self.elements["OptionsContainer"].setProperty("class", "OptionsContainer")
            self.elements["OptionsContainer"].setFixedWidth(self.mainContainer.width()-14)
            self.elements["OptionsContainer"].setFixedHeight(self.mainContainer.height()-95)
            self.mainContainer.mainLayout.addWidget(self.elements["OptionsContainer"])
            self.elements["OptionsContainer"].show()

            # BUTTONS ---------------------------------------------------------------------------------------------

            self.elements["ButtonsContainer"] = QFrame(self.mainContainer)
            self.elements["ButtonsContainer"].setProperty("class", "ButtonsContainer")
            self.elements["ButtonsContainer"].setFixedWidth(self.mainContainer.width()-14)
            self.elements["ButtonsContainer"].setFixedHeight(40)
            self.mainContainer.mainLayout.addWidget(self.elements["ButtonsContainer"])
            self.elements["ButtonsContainer"].show()

            self.elements["ButtonsLayout"] = QVBoxLayout()
            self.elements["ButtonsLayout"].setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
            self.elements["ButtonsLayout"].setSpacing(5)
            self.elements["ButtonsLayout"].setContentsMargins(0,0,0,0)
            self.elements["ButtonsLayout"].setDirection(QBoxLayout.Direction.LeftToRight)
            self.elements["ButtonsContainer"].setLayout(self.elements["ButtonsLayout"])

            def CreateButton(key: str):
                button = QPushButton(parent=self.elements["ButtonsContainer"])
                button.setProperty("class", "scButton")
                button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

                button.label = QLabel("[ Missing ]", parent=button)
                button.label.setProperty("class", "scButtonLabel")
                button.label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
                button.label.setWordWrap(True)
                button.label.setMinimumWidth(1)
                button.label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
                button.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                LocalizationService.registerAdaptableText(button.label, f"buttons/{key}")    

                button.lay = QVBoxLayout(button)
                button.lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
                button.lay.addWidget(button.label)
                button.lay.setContentsMargins(0, 0, 0, 0)
                
                return button
            
            self.scButtons = {}

            self.scButtons["cancel"] = CreateButton("cancel")
            self.scButtons["cancel"].setMaximumWidth(self.mainContainer.width()//3)
            self.elements["ButtonsLayout"].addWidget(self.scButtons["cancel"])

            self.scButtons["apply"] = CreateButton("apply")
            self.elements["ButtonsLayout"].addWidget(self.scButtons["apply"])

        def closeEvent(self, event):
            event.ignore()
            self.Hide(onFinished=uiApp.exit, Hard=True)
            return

    generalSettingsWindow = GeneralSettingsWindow(titleKey="titles/generalSettings", name="GeneralSettings", Mode="blackList", Modifiers=["settings", "gsettings"])

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