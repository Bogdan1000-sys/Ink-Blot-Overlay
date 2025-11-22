from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QWidget, QScrollArea, QSizePolicy, QPushButton, QBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QWheelEvent, QPixmap
import sys, math, json, random, subprocess, threading

# -- Services --
from Services import CollectionService

# -- Functions --
from Functions import GetUserSettings, applyStyleClass, initSound, playSound, RegisterAdaptableText, AppendUserSettings

# -- Resources --
SelectWidgetSound = "Program/Resources/SFX/WidgetSelect.wav"

# -- Constants --
with open("Program/Data/Pathes.json", "r", encoding="utf-8") as pFile:
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
from Classes import InteractableWindow, WidgetButton, UIApplication

if __name__ == "__main__":
    uiApp = UIApplication(sys.argv)
    uiApp.setStyleSheet("""
        QPushButton:focus { outline: none; border: none; }
    """)


class WidgetSelectingWindow(InteractableWindow):

    selectedWidget = random.choice(list(Data["WidgetsData"].items()))[0]

    def UpdatePreviewInfo(self, useSound=True):
        UpdateUserSettings()

        widgetData = Data["WidgetsData"][self.selectedWidget]

        widgetButtons = CollectionService.getTagged("widgetButton")

        selectedWidgets = UserSettings.get("selecteWidgets", [])
        activeWidgets = UserSettings.get("activeWidgets", [])

        RegisterAdaptableText(self.InfoItems["NameLabel"], widgetData["Name"])
        RegisterAdaptableText(self.InfoItems["DescriptionLabel"], widgetData["Description"])

        if self.selectedWidget in selectedWidgets:
            RegisterAdaptableText(self.wcButtons["select"].label, "buttons/unselect")
            applyStyleClass(self.wcButtons["select"], "wcButton:unselect")
        else:
            RegisterAdaptableText(self.wcButtons["select"].label, "buttons/select")
            applyStyleClass(self.wcButtons["select"], "wcButton")

        if self.selectedWidget in activeWidgets:
            RegisterAdaptableText(self.wcButtons["activate"].label, "buttons/deactivate")
            applyStyleClass(self.wcButtons["activate"], "wcButton:deactivate")

            RegisterAdaptableText(self.wcButtons["activateSel"].label, "buttons/deactivateAll")
            applyStyleClass(self.wcButtons["activateSel"], "wcButton:deactivate")

            self.wcButtons["select"].hide()
            if len(activeWidgets) <= 1: 
                self.wcButtons["activateSel"].hide()
            else:
                self.wcButtons["activateSel"].show()
        else:
            RegisterAdaptableText(self.wcButtons["activate"].label, "buttons/activate")
            applyStyleClass(self.wcButtons["activate"], "wcButton")

            RegisterAdaptableText(self.wcButtons["activateSel"].label, "buttons/activateSel")
            applyStyleClass(self.wcButtons["activateSel"], "wcButton")

            self.wcButtons["select"].show()
            if len(selectedWidgets) > 0:
                self.wcButtons["activateSel"].show()
            else:
                self.wcButtons["activateSel"].hide()

        previewPixmap = QPixmap(widgetData["Icon"]).scaled(
            math.floor(self.PreviewContainer.height()*0.75),
            math.floor(self.PreviewContainer.height()*0.75)
        )
        self.PreviewLabel.setPixmap(previewPixmap)

        try:
            self.wcButtons["select"].clicked.disconnect()
            self.wcButtons["activate"].clicked.disconnect()
            self.wcButtons["activateSel"].clicked.disconnect()
        except: pass

        def RunWProcess(path, key):
            proc = subprocess.Popen(["py", path])
            uiApp.addProcess(key, proc)

            def watcher(k, p):
                p.wait()
                if uiApp.processes.get(k) == p:
                    uiApp.removeProcess(k)

            thread = threading.Thread(target=watcher, args=(key, proc), daemon=True)
            thread.start()

        def RunSelection():
            for widget in selectedWidgets:
                RunWProcess(f"Program/Widgets/{widget}/main.py", widget)

        def RunCurrent():
            RunWProcess(f"Program/Widgets/{self.selectedWidget}/main.py", self.selectedWidget)

        def TerminateActive():
            uiApp.terminateProcesses()

        def TerimnateCurrent():
            uiApp.removeProcess(self.selectedWidget)

        def OnClick(button: str):
            GetUserSettings()
            if button == "select":
                if self.selectedWidget in selectedWidgets:
                    selectedWidgets.remove(self.selectedWidget)
                else:
                    selectedWidgets.append(self.selectedWidget)
            elif button == "activate":
                if self.selectedWidget in activeWidgets:
                    TerimnateCurrent()
                    activeWidgets.remove(self.selectedWidget)
                else:
                    RunCurrent()
                    activeWidgets.append(self.selectedWidget)
            elif button == "activateSel":
                if self.selectedWidget not in activeWidgets:
                    RunSelection()
                    for i in selectedWidgets:
                        activeWidgets.append(i)
                    selectedWidgets.clear()
                else:
                    TerminateActive()
                    activeWidgets.clear()

            AppendUserSettings({"selecteWidgets": selectedWidgets, "activeWidgets": activeWidgets})
            self.UpdatePreviewInfo()

        self.wcButtons["select"].clicked.connect(lambda: OnClick("select"))
        self.wcButtons["activate"].clicked.connect(lambda: OnClick("activate"))
        self.wcButtons["activateSel"].clicked.connect(lambda: OnClick("activateSel"))

        WidgetButtonStyle = '''
            QFrame[class='widgetButton:disabled_passive'] {
                border: none;
                border-radius: 10px;
                background: qlineargradient(
                    x1: 0, y1: 1,
                    x2: 0, y2: 0,
                    stop: 0 #411c00,
                    stop: 1 #240f00);
            }
            QFrame[class='widgetButton:disabled_selected'] {
                border: 1px solid rgba(255, 106, 0, 180);
                border-radius: 10px;
                background: qlineargradient(
                    x1: 0, y1: 1,
                    x2: 0, y2: 0,
                    stop: 0 #411c00,
                    stop: 1 #240f00);
            }
            QFrame[class='widgetButton:disabled_current'] {
                border: 2px solid rgba(255, 106, 0, 255);
                border-radius: 10px;
                background: qlineargradient(
                    x1: 0, y1: 1,
                    x2: 0, y2: 0,
                    stop: 0 #411c00,
                    stop: 1 #240f00);
            }

            
            QFrame[class='widgetButton:active_passive'] {
                border: none;
                border-radius: 10px;
                background: qlineargradient(
                    x1: 0, y1: 1,
                    x2: 0, y2: 0,
                    stop: 0 #7f3600,
                    stop: 1 #4a1c00
                );
            }
            QFrame[class='widgetButton:active_selected'] {
                border: 1px solid rgba(255, 106, 0, 180);
                border-radius: 10px;
                background: qlineargradient(
                    x1: 0, y1: 1,
                    x2: 0, y2: 0,
                    stop: 0 #7f3600,
                    stop: 1 #4a1c00
                );
            }
            QFrame[class='widgetButton:active_current'] {
                border: 2px solid rgba(255, 106, 0, 255);
                border-radius: 10px;
                background: qlineargradient(
                    x1: 0, y1: 1,
                    x2: 0, y2: 0,
                    stop: 0 #7f3600,
                    stop: 1 #4a1c00
                );
            }
        '''

        if useSound:
            playSound(self.SelectWidgetSound)

        for button in widgetButtons:
            button.setStyleSheet(WidgetButtonStyle)
            
            if button.Reference in activeWidgets:
                if self.selectedWidget == button.Reference:
                    applyStyleClass(button, "widgetButton:active_current")
                elif button.Reference in selectedWidgets:
                    applyStyleClass(button, "widgetButton:active_selected")
                else:
                    applyStyleClass(button, "widgetButton:active_passive")
            else:
                if self.selectedWidget == button.Reference:
                    applyStyleClass(button, "widgetButton:disabled_current")
                elif button.Reference in selectedWidgets:
                    applyStyleClass(button, "widgetButton:disabled_selected")
                else:
                    applyStyleClass(button, "widgetButton:disabled_passive")


    def __init__(self, **kwargs):
        super().__init__(**kwargs) 

        self.SelectWidgetSound = initSound(SelectWidgetSound, self)

        self.setWindowTitle(Constants["Title"])
        self.resize(Constants["Size"]["width"], Constants["Size"]["height"])
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setStyleSheet("""
            QFrame[class='mainContainer'] {
                background-color: rgba(0, 0, 0, 255);
                border: 1px solid rgba(255, 106, 0, 100);
                border-radius: 10px;
            }
                           
            QFrame[class='minorContainer'] {
                background-color: rgba(0, 0, 0, 255);
                border: 1px solid rgba(255, 106, 0, 255);
                border-radius: 10px;
            }
                           
            QFrame[class='previewContainer'] {
                background: qlineargradient(
                    x1: 0, y1: 1,
                    x2: 0, y2: 0,
                    stop: 0 #301400,
                    stop: 1 #000000
                );
                border: 1px solid rgba(255, 106, 0, 255);
                border-radius: 10px;
            }
                           
            QLabel[class='nameLabel'] {
                background: qlineargradient(
                    x1: 0, y1: 1,
                    x2: 0, y2: 0,
                    stop: 0 #301400,
                    stop: 1 #000000
                );
                border: 1px solid rgba(255, 106, 0, 255);
                border-radius: 10px;
                font-size: 20px;
                font-family: 'Courier New', Courier, monospace;
                color: rgba(255, 106, 0, 255);
                           
                padding-top: 2px;
                padding-bottom: 2px;
                padding-right: 5px;
                padding-left: 5px;
            }
                           
            QLabel[class='descriptionLabel'] {
                background: rgba(255, 255, 255, 0);
                border: none;
                font-size: 14px;
                font-family: 'Courier New', Courier, monospace;
                color: rgba(255, 106, 0, 255);
                           
                width: 310px;
                           
                padding-top: 0px;
                padding-bottom: 0px;
                padding-right: 0px;
                padding-left: 0px;
            }
                     
            QPushButton[class='wcButton'] {
                background-color: qlineargradient(
                    x1: 0, y1: 0,
                    x2: 0, y2: 1,
                    stop: 0 rgba(70, 35, 0, 255),
                    stop: 1 rgba(40, 20, 0, 255)
                );
                border: 1px solid rgba(255, 106, 0, 255);
                border-radius: 10px;
            }
            QPushButton[class='wcButton:unselect'], QPushButton[class='wcButton:deactivate'] {
                background-color: qlineargradient(
                    x1: 0, y1: 0,
                    x2: 0, y2: 1,
                    stop: 0 rgba(50, 15, 0, 255),
                    stop: 1 rgba(20, 0, 0, 255)
                );
                border: 1px solid rgba(255, 106, 0, 255);
                border-radius: 10px;
            }
            QPushButton[class='wcButton']:hover, QPushButton[class='wcButton:unselect']:hover, QPushButton[class='wcButton:deactivate']:hover {
                background: qlineargradient(
                    x1: 0, y1: 1,
                    x2: 0, y2: 0,
                    stop: 0 #000000,
                    stop: 1 #301400
                );
            }
            QLabel[class='wcButtonLabel'] {
                background: transparent;
                font-size: 15px;
                font-family: 'Courier New', Courier, monospace;
                color: rgba(255, 106, 0, 255);
            }
       
            QLabel[class='previewLabel'] {
                background: transparent;
                border: none;
            }
        """)

        self.widgetContainers = {}
        self.layouts = {}

        primaryContainerWidth = math.floor(Constants["Size"]["width"]*0.66)
        secondaryContainerWidth = math.floor(Constants["Size"]["width"] - primaryContainerWidth - 5)

        TopMargin = 35

        self.PrimaryContainer = QFrame(self)
        self.PrimaryContainer.setProperty("class", "mainContainer")
        self.PrimaryContainer.resize(primaryContainerWidth, Constants["Size"]["height"]-TopMargin)
        self.PrimaryContainer.move(0, TopMargin)

        self.PrimaryContainerLayout = QVBoxLayout(self.PrimaryContainer)
        self.PrimaryContainerLayout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.SecondaryContainer = QFrame(self)
        self.SecondaryContainer.setProperty("class", "mainContainer")
        self.SecondaryContainer.resize(secondaryContainerWidth, Constants["Size"]["height"]-TopMargin)
        self.SecondaryContainer.move(Constants["Size"]["width"] - secondaryContainerWidth, TopMargin)

        self.SecondaryContainerLayout = QVBoxLayout(self.SecondaryContainer)
        self.SecondaryContainerLayout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        ContainerDifference = 20

        #-----------------------------------------------------------------------------------------------------------------

        self.PreviewContainer = QFrame(self)
        self.PreviewContainer.setProperty("class", "previewContainer")
        self.PreviewContainer.resize(secondaryContainerWidth-ContainerDifference, Constants["Size"]["height"]-math.floor(Constants["Size"]["height"]/2.25)-TopMargin-ContainerDifference)
        self.PreviewContainer.move(Constants["Size"]["width"] - secondaryContainerWidth+(ContainerDifference//2), TopMargin+(ContainerDifference//2)) # y: TopMargin+(ContainerDifference//2)

        self.previewContainerLayout = QVBoxLayout()
        self.previewContainerLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.previewContainerLayout.setContentsMargins(0, 0, 0, 0)
        self.PreviewContainer.setLayout(self.previewContainerLayout)

        self.PreviewLabel = QLabel(parent=self.PreviewContainer, text="")
        self.PreviewLabel.setProperty("class", "previewLabel")
        self.PreviewLabel.resize(self.PreviewContainer.width(), self.PreviewContainer.height())
        self.previewContainerLayout.addWidget(self.PreviewLabel)


        #-----------------------------------------------------------------------------------------------------------------

        self.InfoContainer = QFrame(self)
        self.InfoContainer.setProperty("class", "minorContainer")
        self.InfoContainer.resize(secondaryContainerWidth-ContainerDifference, math.floor(Constants["Size"]["height"]/2.5)-TopMargin-ContainerDifference)

        self.InfoContainer.move(Constants["Size"]["width"] - secondaryContainerWidth+(ContainerDifference//2), TopMargin+self.PreviewContainer.height()+math.floor(ContainerDifference/1.25))

        self.infoContainerLayout = QVBoxLayout()
        self.infoContainerLayout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.InfoContainer.setLayout(self.infoContainerLayout)

        self.InfoItems = {}
        self.InfoItems["NameLabel"] = QLabel(parent=self.InfoContainer, text="[ Missing ]")
        CollectionService.addTag(self.InfoItems["NameLabel"], "adaptableTextWidget")
        self.InfoItems["NameLabel"].setProperty("class", "nameLabel")

        self.InfoItems["DescriptionLabel"] = QLabel(parent=self.InfoContainer, text="[ Missing Description ]")
        CollectionService.addTag(self.InfoItems["DescriptionLabel"], "adaptableTextWidget")
        self.InfoItems["DescriptionLabel"].setProperty("class", "descriptionLabel")
        self.InfoItems["DescriptionLabel"].setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.InfoItems["DescriptionLabel"].setWordWrap(True)
        self.InfoItems["DescriptionLabel"].setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.infoContainerLayout.addWidget(self.InfoItems["NameLabel"])
        self.infoContainerLayout.addWidget(self.InfoItems["DescriptionLabel"])

        #-----------------------------------------------------------------------------------------------------------------

        self.ButtonsContainer = QFrame(self)
        self.ButtonsContainer.setProperty("class", "minorContainer")
        self.ButtonsContainer.resize(secondaryContainerWidth-ContainerDifference, math.floor(Constants["Size"]["height"]/5)-TopMargin-ContainerDifference+1)
        self.ButtonsContainer.move(Constants["Size"]["width"] - secondaryContainerWidth+(ContainerDifference//2), TopMargin+self.PreviewContainer.height()+self.InfoContainer.height()+math.floor(ContainerDifference*1.15))

        self.buttonsContainerLayout = QVBoxLayout()
        self.buttonsContainerLayout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.buttonsContainerLayout.setSpacing(3)
        self.buttonsContainerLayout.setContentsMargins(3,3,3,3)
        self.buttonsContainerLayout.setDirection(QBoxLayout.Direction.LeftToRight)
        self.ButtonsContainer.setLayout(self.buttonsContainerLayout)

        self.wcButtons = {}

        def CreateInterButton(key: str):
            button = QPushButton(parent=self.ButtonsContainer)
            button.label = QLabel("[ Missing ]", parent=button)
            RegisterAdaptableText(button.label, f"buttons/{key}")    
            button.label.setProperty("class", "wcButtonLabel")
            button.label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
            button.label.setWordWrap(True)
            button.label.setMinimumWidth(1)
            button.label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            button.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button.lay = QVBoxLayout(button)
            button.lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button.lay.addWidget(button.label)
            button.lay.setContentsMargins(0, 0, 0, 0)
            button.setProperty("class", "wcButton")
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            return button

        self.wcButtons["activate"] = CreateInterButton("activate")
        self.buttonsContainerLayout.addWidget(self.wcButtons["activate"])
        
        self.wcButtons["select"] = CreateInterButton("select")
        self.buttonsContainerLayout.addWidget(self.wcButtons["select"])

        self.wcButtons["activateSel"] = CreateInterButton("activateSel")
        self.buttonsContainerLayout.addWidget(self.wcButtons["activateSel"])

        ContainerWidth = primaryContainerWidth - 10
        ContainerHeight = 150
        ContentPaddings = 5

        def createContainer(containerName):
            title = QLabel(containerName)
            RegisterAdaptableText(title, "labels/"+containerName)
            
            title.setProperty("class", "containerTitle")
            title.setStyleSheet("""
                QLabel[class="containerTitle"] {
                    width: 200px;
                    height: 25px;
                    padding: 5 0;
                    font-size: 16px;
                    font-family: 'Courier New', Courier, monospace;
                    
                    color: rgba(255, 106, 0, 255);
                    background-color: rgba(0, 0, 0, 0); 
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

            scroll = HorizontalScrollArea(parent=self.PrimaryContainer)
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
            
            widgetButton = WidgetButton(parent=self.widgetContainers[folderName.lower() + "_Container"], data=wData, size=[math.floor(ContainerWidth/2.75)-(ContainerWidth//15), ContainerHeight-22])
            layout.addWidget(widgetButton)

            self.WidgetButtons[wName] = {
                "buttonBody": widgetButton,
                "button": widgetButton.button,
                "data": wData
            }

        def makeButtonClickHandler(name):
            def OnClick():
                self.selectedWidget = name
                self.UpdatePreviewInfo()
            return OnClick

        for key, info in self.WidgetButtons.items():
            name = info["data"]["Key"]
            info["button"].clicked.connect( makeButtonClickHandler(name) )

        self.UpdatePreviewInfo(useSound=False)
        
        #UIApplication.instance().installEventFilter(self)

        self.show()

if __name__ == "__main__":
    settingWindow = WidgetSelectingWindow(titleKey="titles/widgetSelection")
    
    sys.exit(uiApp.exec())