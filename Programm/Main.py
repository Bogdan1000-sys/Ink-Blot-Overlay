from PyQt6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QWidget, QScrollArea
from PyQt6.QtCore import Qt, QTimer, QThread
from PyQt6.QtGui import QWheelEvent
import sys, math, os, keyboard, json, time

# -- Services --
from Services import CollectionService

# -- Functions --
from Functions import GetAdaptedText

# -- Variables --

# -- Constants --
with open("Programm/Data/Constants.json", "r", encoding="utf-8") as cFile:
    Constants = json.load(cFile)

# -- Data --
from Data import InitializeData
Data = InitializeData()

with open("Programm/Data/Dictionary.json", "r", encoding="utf-8") as dFile:
    Dictionary = json.load(dFile)

userSettingsPath = "Programm/Data/userSettings.json"
with open(userSettingsPath, "r", encoding="utf-8") as usFile:
    UserSettings = json.load(usFile)

# -- Common Styles --
mainContainerStyle = """
QFrame[class="mainContainer"] {
    background-color: rgba(0, 0, 0, 255);
    border: 1px solid rgba(255, 106, 0, 100);
    border-radius: 10px;
}
"""

# -- Scripts --
from Classes import InteractableWindow, WidgetButton

class WidgetSelectingWindow(InteractableWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        language = UserSettings.get("language", "eng")

        self.setWindowTitle(Constants["Title"])
        self.resize(Constants["Size"]["width"], Constants["Size"]["height"])
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.widgetContainers = {}
        self.layouts = {}

        primaryContainerWidth = math.floor(Constants["Size"]["width"]*0.66)
        secondaryContainerWidth = math.floor(Constants["Size"]["width"] - primaryContainerWidth - 5)

        TopMargin = 35

        self.PrimaryContainer = QFrame(self)
        self.PrimaryContainer.setProperty("class", "mainContainer")
        self.PrimaryContainer.setStyleSheet(mainContainerStyle)
        self.PrimaryContainer.resize(primaryContainerWidth, Constants["Size"]["height"]-TopMargin)
        self.PrimaryContainer.move(0, TopMargin)

        self.PrimaryContainerLayout = QVBoxLayout(self.PrimaryContainer)
        self.PrimaryContainerLayout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        #self.mainLayout.addWidget(self.PrimaryContainer)

        self.SecondaryContainer = QFrame(self)
        self.SecondaryContainer.setProperty("class", "mainContainer")
        self.SecondaryContainer.setStyleSheet(mainContainerStyle)
        self.SecondaryContainer.resize(secondaryContainerWidth, Constants["Size"]["height"]-TopMargin)
        self.SecondaryContainer.move(Constants["Size"]["width"] - secondaryContainerWidth, TopMargin)

        self.SecondaryContainerLayout = QVBoxLayout(self.SecondaryContainer)
        self.SecondaryContainerLayout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.ThirdaryContainer = QFrame(self)
        self.ThirdaryContainer.setProperty("class", "minorContainer")
        self.ThirdaryContainer.setStyleSheet("""
            QFrame[class="minorContainer"] {
                background-color: rgba(0, 0, 0, 255);
                border: 1px solid rgba(255, 106, 0, 255);
                border-radius: 10px;
            }
        """)
        thirdContainerDifference = 20
        self.ThirdaryContainer.resize(secondaryContainerWidth-thirdContainerDifference, Constants["Size"]["height"]-TopMargin-thirdContainerDifference)
        self.ThirdaryContainer.move(Constants["Size"]["width"] - secondaryContainerWidth+(thirdContainerDifference//2), TopMargin+(thirdContainerDifference//2))

        ContainerWidth = primaryContainerWidth - 10
        ContainerHeight = 150
        ContentPaddings = 5

        def createContainer(langKey):
            title = QLabel(Dictionary[language]["labels"][langKey])
            
            CollectionService.addTag(title, "adaptableTextWidget")
            title.setProperty("textPath", {"dataBase":"Dictionary", "key":"labels/" + langKey})

            title.setProperty("class", "containerTitle")
            title.setStyleSheet("""
                QLabel[class="containerTitle"] {
                    width: 200px;
                    height: 25px;
                    padding: 5 0;
                    font-size: 14px;
                    font-family: 'Courier New', Courier, monospace;
                    
                    color: rgba(255, 106, 0, 255);
                    background-color: rgba(0, 0, 0, 0); 
                    font-size: 16px;
                    padding: 4px 8px; 
                    background-color: qlineargradient(
                        x1: 0, y1: 0,
                        x2: 0, y2: 1,
                        stop: 0 rgba(50, 25, 0, 255),
                        stop: 1 rgba(30, 15, 0, 255)
                    );
                    border: 1px solid rgba(255, 106, 0, 255);
                    border-radius: 10px;
                }
            """)
            title.setFixedWidth(ContainerWidth - 10)
            self.PrimaryContainerLayout.addWidget(title)

            class HorizontalScrollArea(QScrollArea):
                def wheelEvent(self, event: QWheelEvent):
                    delta = event.angleDelta().y()
                    self.horizontalScrollBar().setValue(
                        self.horizontalScrollBar().value() - delta
                    )

            class Container(QWidget):
                def __init__(self):
                    super().__init__()
                    self.setStyleSheet("border: none")

            scroll = HorizontalScrollArea(self.PrimaryContainer)
            scroll.setWidgetResizable(True)
            scroll.resize(ContainerWidth-10, ContainerHeight-10)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            scroll.setStyleSheet("""
                QScrollArea {
                    background-color: rgba(0, 0, 0, 255);
                    border: 1px solid rgba(255, 106, 0, 100);
                    border-radius: 10px;
                                 
                    padding-top: 5px;
                    padding-bottom: 5px;
                    padding-right: 5px;
                    padding-left: 5px;
                }

                QScrollBar:horizontal {
                    height: 0px;
                    width: 0px
                }

                QScrollBar::handle:horizontal {
                    background: rgba(255, 106, 0, 220);
                    min-width: 25px;
                }

                QScrollBar::handle:horizontal:hover {
                    background: rgba(255, 150, 50, 255);
                }

                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    background: none;
                    width: 0px;
                }

                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                    background: none;
                }
            """)
            self.PrimaryContainerLayout.addWidget(scroll)
                    
            contentContainer = Container()
            scroll.setWidget(contentContainer)

            layout = QHBoxLayout(contentContainer)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(ContentPaddings)
            layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            return title, scroll, layout

        # -- UTIL --
        self.widgetContainers["util_Title"], self.widgetContainers["util_Container"], self.layouts["util_Container_Layout"] = createContainer("Util")

        # -- VISUAL --
        self.widgetContainers["visual_Title"], self.widgetContainers["visual_Container"], self.layouts["visual_Container_Layout"] = createContainer("Visual")

        # -- INTERACTABLE --
        self.widgetContainers["interactable_Title"], self.widgetContainers["interactable_Container"], self.layouts["interactable_Container_Layout"] = createContainer("Interactable")

        WidgetsData = Data["WidgetsData"]

        self.WidgetButtons = {}

        for wName in WidgetsData:
            wData = WidgetsData[wName]
            
            folderName = wData["Type"]

            layout = self.layouts[folderName.lower() + "_Container_Layout"]
            
            widgetButton = WidgetButton(self.widgetContainers[folderName.lower() + "_Container"], data=wData, size=[(ContainerWidth//3)-(ContainerWidth//15), ContainerHeight-22])
            layout.addWidget(widgetButton)

            self.WidgetButtons[wName] = {
                "buttonBody": widgetButton,
                "button": widgetButton.button,
                "data": wData
            }

        def makeButtonClickHandler(name):
            return lambda: print("[Main]", name + ": Click!")

        for key, info in self.WidgetButtons.items():
            name = info["data"]["Name"]
            info["button"].clicked.connect( makeButtonClickHandler(name) )

        QApplication.instance().installEventFilter(self)
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    settingWindow = WidgetSelectingWindow(titleKey={"dataBase":"Dictionary", "key":"titles/widgetSelection"})
    
    def ChangeLanguage(newLanguage):
        global Data, Dictionary

        UserSettings["language"] = newLanguage

        with open(userSettingsPath, "w", encoding="utf-8") as usFile:
            json.dump(UserSettings, usFile, ensure_ascii=False, indent=4)

        Data = InitializeData(newLanguage)

        for i, widget in enumerate(CollectionService.getTagged("adaptableTextWidget")):
            textPath = widget.property("textPath")
            widget.setText( GetAdaptedText(database=(textPath["dataBase"] == "Data" and Data or Dictionary[newLanguage]), key=textPath["key"]) )
    
    sys.exit(app.exec())
