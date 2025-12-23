from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QWidget, QScrollArea, QSizePolicy, QPushButton, QBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QEasingCurve, QPropertyAnimation, QPoint, QTimer
from PyQt6.QtGui import QWheelEvent, QPixmap
import sys, math, json, random, os

# -- Services --
from Services import CollectionService

# -- Objects --
uiApp = None
selectionWindow = None

# -- Resources --
SelectWidgetSound = "Resources/SFX/WidgetSelect.wav"

with open("Data/Pathes.json", "r", encoding="utf-8") as pFile:
    Pathes = json.load(pFile)

# -- Functions --
from Functions import GetUserSettings, applyStyleClass, initSound, playSound, RegisterAdaptableText, AppendUserSettings, GetQTime, CloneAnimation, PrintText, CompareObjects

def addArrow(button: QPushButton):
    originalText = button.text()

    def enterEvent(event):
        if button.property("Printed") != True: return

        if not button.text().startswith(">"):
            button.setText(f"> {originalText}")
        event.accept()

    def leaveEvent(event):
        if button.property("Printed") != True: return

        button.setText(originalText)
        event.accept()

    button.enterEvent = enterEvent
    button.leaveEvent = leaveEvent

def RunProcess(path, key, args={}):
    args["selectionWindow"] = selectionWindow.objectName()

    uiApp.runProcess(path, key, args)

# -- Data --
with open(Pathes["Constants"], "r", encoding="utf-8") as cFile:
    Constants = json.load(cFile)
with open(Pathes["Data"], "r", encoding="utf-8") as dataFile:
    Data = json.load(dataFile)
with open(Pathes["WindowSettingsTemplate"], "r", encoding="utf-8") as wstFile:
    WindowSettingsTemplate = json.load(wstFile)

UserSettings = None

def UpdateUserSettings():
    global UserSettings
    UserSettings = GetUserSettings()

UpdateUserSettings()

# -- Scripts --
from Classes import InteractableWindow, WidgetButton, UIApplication, EmptyWindow

if __name__ == "__main__":
    uiApp = UIApplication(sys.argv, appName="MainApplication")

class WidgetSelectingWindow(InteractableWindow):

    selectedWidget = random.choice(list(Data["WidgetsData"].items()))[0]

    def UpdatePreviewInfo(self, useSound=True):
        UpdateUserSettings()

        widgetData = Data["WidgetsData"][self.selectedWidget]

        widgetButtons = CollectionService.getTagged("widgetButton")

        selectedWidgets = UserSettings.get("General", {}).get("selectedWidgets", [])
        activeWidgets = UserSettings.get("General", {}).get("activeWidgets", [])

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
        except Exception: pass

        def RunSelection():
            for widget in selectedWidgets:
                #uiApp.runProcess(f"Widgets/{widget}/main.py", widget)
                RunProcess(f"Widgets/{widget}/main.py", widget)

        def RunCurrent():
            #uiApp.runProcess(f"Widgets/{self.selectedWidget}/main.py", self.selectedWidget)  
            RunProcess(f"Widgets/{self.selectedWidget}/main.py", self.selectedWidget)

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

            AppendUserSettings("General", {"selectedWidgets": selectedWidgets, "activeWidgets": activeWidgets})
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
            playSound(self.objectName(), self.SelectWidgetSound)

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
        CollectionService.addTag(self, "SelectionWindow")

        self.SelectWidgetSound = initSound(SelectWidgetSound, self)

        self.setWindowTitle(Constants["Title"])
        self.resize(Constants["Size"]["width"], Constants["Size"]["height"])
        screen = uiApp.primaryScreen().availableGeometry()
        self.move(
            screen.left() + (screen.width() - self.width()) // 2,
            screen.top() + (screen.height() - self.height()) // 2
        )
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

class WelcomeWindow(EmptyWindow):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.Animations = {}
        self.SFX = {}

        self.SFX["optionsClickSound"] = initSound("Resources/SFX/PrintClick.wav", self)

        self.setWindowTitle('Welcome')
        screen = uiApp.primaryScreen().availableGeometry()
        self.move(
            screen.left() + (screen.width() - self.width()) // 2,
            screen.top() + (screen.height() - self.height()) // 2
        )
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        self.setStyleSheet("""
            background: transparent;
            border-radius: 10px;
        """)

        # Building --------------------------------------------------------------------------------------------------------------

        self.BackgroundFrame = QFrame(parent=self)
        self.BackgroundFrame.setProperty("class", "backgroundFrame")
        self.BackgroundFrame.resize(self.width(), self.height())
        self.BackgroundFrame.setStyleSheet("""
            QFrame[class='backgroundFrame'] {
                background: qlineargradient(
                    x1: 0, y1: 1,
                    x2: 0, y2: 0,
                    stop: 0 #0C0500,
                    stop: 1 #401b01
                );               
                border-radius: 10px;
            }
        """)
        self.BackgroundFrame.move(0, 0)

        self.BackgroundFrame.Shade = QWidget(parent=self.BackgroundFrame)
        self.BackgroundFrame.Shade.setProperty("class", "backgroundShade")
        self.BackgroundFrame.Shade.resize(self.BackgroundFrame.width(), self.BackgroundFrame.height())
        self.BackgroundFrame.Shade.setStyleSheet("""
            QWidget[class='backgroundShade'] {
                background: qradialgradient(
                    cx: 0.5, cy: 0.5,
                    radius: 1,
                    fx: 0.5, fy: 0.5,
                    stop: 0 rgba(0, 0, 0, 0),
                    stop: 1 rgba(0, 0, 0, 255)
                );
                border-radius: 10px;
            }
        """)
        self.BackgroundFrame.Shade.move(0, 0)
        self.BackgroundFrame.Shade.show()

        charPixmap = QPixmap("Resources/Images/Ink Blot Icon.png").scaled(
            math.floor(self.height()*0.39),
            math.floor(self.height()*0.39)
        )
        self.CharLabel = QLabel(parent=self, text="")
        self.CharLabel.setProperty("class", "charLabel")
        self.CharLabel.setStyleSheet("""
            QLabel[class='charLabel'] {
                background: transparent;
                border-radius: 100%;
                border: none;
            }
        """)
        self.CharLabel.setPixmap(charPixmap)
        self.CharLabel.resize(charPixmap.size().width(), charPixmap.size().height())
        self.CharLabel.move(
            (self.width() - self.CharLabel.width()) // 2,
            math.floor(self.CharLabel.height() * 0.2)
        )

        platformPixmap = QPixmap("Resources/Images/Platform.png").scaled(
            math.floor(self.height()*0.5),
            math.floor(self.height()*0.5)
        )
        self.PlatformLabel = QLabel(parent=self, text="")
        self.PlatformLabel.setProperty("class", "platformLabel")
        self.PlatformLabel.setStyleSheet("""
            QLabel[class='platformLabel'] {
                background: transparent;
                border-radius: 10px;
                border: none;
            }
        """)
        self.PlatformLabel.setPixmap(platformPixmap)
        self.PlatformLabel.resize(platformPixmap.size().width(), platformPixmap.size().height())
        self.PlatformLabel.move(
            (self.width() - self.PlatformLabel.width()) // 2,
            math.floor(self.CharLabel.height() * 0.4)
        )

        charGlowPixmap = QPixmap("Resources/Images/Glow.png").scaled(
            math.floor(self.height()*0.6),
            math.floor(self.height()*0.6)
        )
        self.CharGlowLabel = QLabel(parent=self, text="")
        self.CharGlowLabel.setProperty("class", "charGlowLabel")
        self.CharGlowLabel.setStyleSheet("""
            QLabel[class='charGlowLabel'] {
                background: transparent;
                border-radius: 100%;
                border: none;
            }
        """)
        self.CharGlowLabel.setPixmap(charGlowPixmap)
        self.CharGlowLabel.resize(charGlowPixmap.size().width(), charGlowPixmap.size().height())
        self.CharGlowLabel.move(
            (self.width() - self.CharGlowLabel.width()) // 2,
            math.floor(self.CharGlowLabel.height() * 0.05)
        )

        self.HelloTitle = QLabel(parent=self, text="HELLO")
        self.HelloTitle.setProperty("class", "helloTitle")
        self.HelloTitle.setStyleSheet("""
            QLabel[class='helloTitle'] {
                background: transparent;
                font-size: 45px;
                font-family: 'Courier New', Courier, monospace;
                color: rgba(255, 106, 0, 255);  
                border: none;
                padding-top: 2px;
                padding-bottom: 2px;
                padding-right: 5px;
                padding-left: 5px;
            }
        """)
        self.HelloTitle.resize(self.width(), 50)
        self.HelloTitle.move(
            (self.width() - self.HelloTitle.width()) // 2,
            math.floor(self.height() * 0.55)
        )
        self.HelloTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.text1 = QLabel(parent=self, text="I am INKY")
        self.text1.setProperty("class", "text1")
        self.text1.setStyleSheet("""
            QLabel[class='text1'] {
                background: transparent;
                font-size: 18px;
                font-family: 'Courier New', Courier, monospace;
                color: rgba(255, 106, 0, 200);  
                border: none;
                padding-top: 2px;
                padding-bottom: 2px;
                padding-right: 5px;
                padding-left: 5px;
            }
        """)
        self.text1.resize(self.width(), 30)
        self.text1.move(
            (self.width() - self.text1.width()) // 2,
            math.floor(self.height() * 0.63)
        )
        self.text1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.text2 = QLabel(parent=self, text="Your ink assistant for today!")
        self.text2.setProperty("class", "text2")
        self.text2.setStyleSheet("""
            QLabel[class='text2'] {
                background: transparent;
                font-size: 18px;
                font-family: 'Courier New', Courier, monospace;
                color: rgba(255, 106, 0, 200);  
                border: none;
                padding-top: 2px;
                padding-bottom: 2px;
                padding-right: 5px;
                padding-left: 5px;
            }
        """)
        self.text2.resize(self.width(), 30)
        self.text2.move(
            (self.width() - self.text2.width()) // 2,
            math.floor(self.height() * 0.675)
        )
        self.text2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.CharLabel.hide()
        self.PlatformLabel.hide()
        self.CharGlowLabel.hide()
        self.HelloTitle.hide()
        self.text1.hide()
        self.text2.hide()

        # OPTIONS CONTAINER ------------------------------------------------------------------

        self.OptionsContainer = QFrame(self)
        self.OptionsContainer.setProperty("class", "optionsContainer")
        self.OptionsContainer.setStyleSheet("""
            QFrame[class='optionsContainer'] {
                background: transparent;
                border: none;
                padding-top: 2px;
                padding-bottom: 2px;
            }
        """)
        self.OptionsContainer.resize(self.width(), 150)
        self.OptionsContainer.move(
            (self.width() - self.OptionsContainer.width()) // 2,
            math.floor(self.height() * 0.75)
        )

        # -----------

        self.OptionsContainer.layersLayout = QHBoxLayout()
        self.OptionsContainer.layersLayout.setSpacing(5)
        self.OptionsContainer.layersLayout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.OptionsContainer.setLayout(self.OptionsContainer.layersLayout)
        
        # --------

        self.OptionsContainer.firstLayerContainer = QFrame(self.OptionsContainer)
        self.OptionsContainer.firstLayerContainer.setProperty("class", "optionsContainer")
        self.OptionsContainer.firstLayerContainer.setFixedSize(self.OptionsContainer.width() // 4, self.OptionsContainer.height())
        self.OptionsContainer.layersLayout.addWidget(self.OptionsContainer.firstLayerContainer)

        self.OptionsContainer.firstLayerContainer.mainLayout = QVBoxLayout()
        self.OptionsContainer.firstLayerContainer.mainLayout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.OptionsContainer.firstLayerContainer.setLayout(self.OptionsContainer.firstLayerContainer.mainLayout)

        # -----

        self.OptionsContainer.secondLayerContainer = QFrame(self.OptionsContainer)
        self.OptionsContainer.secondLayerContainer.setProperty("class", "optionsContainer")
        self.OptionsContainer.secondLayerContainer.setFixedSize(math.floor(self.OptionsContainer.width() * 3/4) - 10, self.OptionsContainer.height())
        self.OptionsContainer.layersLayout.addWidget(self.OptionsContainer.secondLayerContainer)

        self.OptionsContainer.secondLayerContainer.mainLayout = QVBoxLayout()
        self.OptionsContainer.secondLayerContainer.mainLayout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.OptionsContainer.secondLayerContainer.setLayout(self.OptionsContainer.secondLayerContainer.mainLayout)

        # -----------

        self.OptionsContainer.firstLayerContainer.Options = {}
        Options = self.OptionsContainer.firstLayerContainer.Options

        menuOptionStyle = """
            QPushButton[class='menuOption'] {
                background: transparent;
                border: none;
                font-size: 16px;
                font-family: 'Courier New', Courier, monospace;
                color: rgba(255, 106, 0, 150);

                padding-left: 50px
            }

            QPushButton[class='menuLayerOption'] {
                background: transparent;
                border: none;
                font-size: 16px;
                font-family: 'Courier New', Courier, monospace;
                color: rgba(255, 106, 0, 150);

                padding-left: 0px
            }

            QPushButton[class='menuOption']:hover, QPushButton[class='menuLayerOption']:hover{
                color: rgba(255, 106, 0, 255);
            }
        """

        Options["newPack"] = QPushButton(self.OptionsContainer, text="New Pack")
        Options["newPack"].setProperty("class", "menuOption")
        RegisterAdaptableText(Options["newPack"], "labels/homePage/options/newPack")
        Options["newPack"].setStyleSheet(menuOptionStyle)
        Options["newPack"].resize(self.width(), 20)
        self.OptionsContainer.firstLayerContainer.mainLayout.addWidget(Options["newPack"], alignment=Qt.AlignmentFlag.AlignLeft)

        Options["loadPack"] = QPushButton(self.OptionsContainer, text="Load Pack")
        Options["loadPack"].setProperty("class", "menuOption")
        RegisterAdaptableText(Options["loadPack"], "labels/homePage/options/loadPack")
        Options["loadPack"].setStyleSheet(menuOptionStyle)
        Options["loadPack"].resize(self.width(), 20)
        self.OptionsContainer.firstLayerContainer.mainLayout.addWidget(Options["loadPack"], alignment=Qt.AlignmentFlag.AlignLeft)
        
        Options["exit"] = QPushButton(self.OptionsContainer, text="Exit")
        Options["exit"].setProperty("class", "menuOption")
        RegisterAdaptableText(Options["exit"], "labels/homePage/options/exit")
        Options["exit"].setStyleSheet(menuOptionStyle)
        Options["exit"].resize(self.width(), 20)
        self.OptionsContainer.firstLayerContainer.mainLayout.addWidget(Options["exit"], alignment=Qt.AlignmentFlag.AlignLeft)

        for button in Options.values():
            addArrow(button)
            if hasattr(button, "hide"):
                button.hide()

        self.OptionsContainer.show()

        # Animations --------------------------------------------------------------------------------------------------------------

        self.shadeOpacity = QGraphicsOpacityEffect(self.BackgroundFrame.Shade)
        self.shadeOpacity.setOpacity(1.0)
        self.BackgroundFrame.Shade.setGraphicsEffect(self.shadeOpacity)

        self.Animations["shadeAnim"] = QPropertyAnimation(
            self.shadeOpacity,
            b"opacity"
        )

        self.Animations["shadeAnim"].setStartValue(1)
        self.Animations["shadeAnim"].setEndValue(0.25)
        self.Animations["shadeAnim"].setDuration(GetQTime(3))
        self.Animations["shadeAnim"].setEasingCurve(QEasingCurve.Type.InOutSine)

        self.Animations["shadeAnim"].setLoopCount(1)

        def AnimateShade():
            if self.Animations["shadeAnim"].direction() == QPropertyAnimation.Direction.Forward:
                self.Animations["shadeAnim"].setDirection(QPropertyAnimation.Direction.Backward)
            else:
                self.Animations["shadeAnim"].setDirection(QPropertyAnimation.Direction.Forward)

            self.Animations["shadeAnim"].start()

        self.Animations["Hovers"] = {}

        # Character Hovering ----------------------------

        hoverDrag = 5

        self.Animations["Hovers"]["charHoverAnim"] = QPropertyAnimation(self.CharLabel, b"pos")
        self.Animations["Hovers"]["charHoverAnim"].setDuration(GetQTime(0.5))
        self.Animations["Hovers"]["charHoverAnim"].setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.Animations["Hovers"]["charHoverAnim"].setLoopCount(1)
        self.Animations["Hovers"]["charHoverAnim"].setProperty("starterX", self.CharLabel.x())
        self.Animations["Hovers"]["charHoverAnim"].setStartValue(self.CharLabel.pos())
        self.Animations["Hovers"]["charHoverAnim"].setEndValue(self.CharLabel.pos() + QPoint(0, hoverDrag))

        self.Animations["Hovers"]["platformHoverAnim"] = CloneAnimation(
            animation = self.Animations["Hovers"]["charHoverAnim"],
            parent = self.PlatformLabel
        )
        self.Animations["Hovers"]["platformHoverAnim"].setProperty("starterX", self.PlatformLabel.x())
        self.Animations["Hovers"]["platformHoverAnim"].setStartValue(self.PlatformLabel.pos())
        self.Animations["Hovers"]["platformHoverAnim"].setEndValue(self.PlatformLabel.pos() + QPoint(0, hoverDrag))

        self.Animations["Hovers"]["glowHoverAnim"] = CloneAnimation(
            animation = self.Animations["Hovers"]["charHoverAnim"],
            parent = self.CharGlowLabel
        )
        self.Animations["Hovers"]["glowHoverAnim"].setProperty("starterX", self.CharGlowLabel.x())
        self.Animations["Hovers"]["glowHoverAnim"].setStartValue(self.CharGlowLabel.pos())
        self.Animations["Hovers"]["glowHoverAnim"].setEndValue(self.CharGlowLabel.pos() + QPoint(0, hoverDrag))

        def AnimateHover(animation: QPropertyAnimation):
            animation.setStartValue(QPoint(
                animation.targetObject().x(),
                animation.startValue().y()
            ))
            animation.setEndValue(QPoint(
                animation.targetObject().x(),
                animation.endValue().y()
            ))

            if animation.direction() == QPropertyAnimation.Direction.Forward:
                animation.setDirection(QPropertyAnimation.Direction.Backward)
            else:
                animation.setDirection(QPropertyAnimation.Direction.Forward)

            animation.start()

        # Setuping --------------------------------------------------------------------------------------------------------------

        RegisterAdaptableText(self.HelloTitle, "labels/homePage/hello")
        RegisterAdaptableText(self.text1, "labels/homePage/text1")
        RegisterAdaptableText(self.text2, "labels/homePage/text2")

        self.BackgroundFrame.show()

        self.showElementIndex = 0

        def showElement(element=None, delay=None, printInterval=None):
            if element == None: return
            if delay == None: delay = 0

            element.opacityGraphics = QGraphicsOpacityEffect(element)
            element.opacityGraphics.setOpacity(0)
            element.setGraphicsEffect(element.opacityGraphics)

            element.osAnim = QPropertyAnimation(element.opacityGraphics, b"opacity")
            element.osAnim.setStartValue(0)
            element.osAnim.setEndValue(1)
            element.osAnim.setDuration(GetQTime(0.5))
            element.osAnim.setLoopCount(1)
    
            element.msAnim = QPropertyAnimation(element, b"pos")
            element.msAnim.setStartValue(element.pos() + QPoint(0, 15))
            element.msAnim.setEndValue(element.pos())
            element.msAnim.setDuration(GetQTime(0.5))
            element.msAnim.setEasingCurve(QEasingCurve.Type.OutSine)
            element.msAnim.setLoopCount(1)

            self.showElementIndex += 1

            def start():
                element.osAnim.start()
                element.msAnim.start()

                if printInterval != None and hasattr(element, "property") and element.property("textKey"):
                    PrintText(element, element.property("textKey"), "dict", printInterval)
                element.show()

            QTimer.singleShot(GetQTime(0.1) * self.showElementIndex + GetQTime(delay), start)

        def PrintElement(element=None, delay=0, printInterval=30):
            if element == None: return

            def start():
                try:
                    if printInterval != None and hasattr(element, "property"):
                        if element.property("textKey"):
                            PrintText(element, element.property("textKey"), "dict", printInterval)
                    element.show()
                except Exception: pass

            QTimer.singleShot(GetQTime(delay), start)
            
        def startShowing():
            showElement(self.CharLabel)
            showElement(self.PlatformLabel)
            showElement(self.CharGlowLabel)
            showElement(self.HelloTitle, 0.5)
            showElement(self.text1, 1.5)
            showElement(self.text2, 2.5)

            self.Animations["shadeAnim"].finished.connect(AnimateShade)
            self.Animations["shadeAnim"].start()

            def startHover():
                for anim in self.Animations["Hovers"].values():
                    anim.start()
                    anim.finished.connect(lambda a=anim:AnimateHover(a))

            def printOptions():
                UpdateUserSettings()
                global UserSettings
                
                Options = self.OptionsContainer.firstLayerContainer.Options

                # Funtions --------

                def createSelectionWindow():
                    global selectionWindow
                    self.deleteLater()
                    selectionWindow = WidgetSelectingWindow(titleKey="titles/widgetSelection", name="Selection")

                def optionBasic():
                    playSound(self.objectName(), self.SFX["optionsClickSound"])

                self.debounses["createNewOptionsDebounse"] = False
                def createNewLayerOptions(
                        OptionsData=[
                            {
                                "key": "name",
                                "textKey": "[ Missing ]"
                            }
                        ],
                        Container=None
                    ):
                    if OptionsData == None or Container==None: return
                    
                    if self.debounses["createNewOptionsDebounse"]: return
                    self.debounses["createNewOptionsDebounse"] = True
                    def changeDeb():
                        self.debounses["createNewOptionsDebounse"] = False
                    QTimer.singleShot(GetQTime(0.25), changeDeb)

                    if hasattr(Container, "Options"):
                        for button in Container.Options.values():
                            try:
                                if hasattr(button, "function"):
                                    button.clicked.disconnect(button.function)
                                button.deleteLater()
                            except Exception: continue

                    NewLayerOptions = {}

                    oi = -1
                    for option in OptionsData: 
                        oi+=1

                        key = option["key"]
                        textKey = option["textKey"]

                        NewLayerOptions[key] = QPushButton(Container, text=key)
                        NewLayerOptions[key].setProperty("class", "menuLayerOption")
                        RegisterAdaptableText(NewLayerOptions[key], textKey)
                        NewLayerOptions[key].setStyleSheet(menuOptionStyle)
                        NewLayerOptions[key].resize(self.width(), 20)
                        
                        addArrow(NewLayerOptions[key])
                        NewLayerOptions[key].hide()

                        PrintElement(NewLayerOptions[key], oi*0.5, 10)

                        try: Container.mainLayout.addWidget(NewLayerOptions[key],  alignment=Qt.AlignmentFlag.AlignLeft)
                        except Exception: pass

                    Container.Options = NewLayerOptions

                    return NewLayerOptions

                class OptionsModule():
                    selected = False

                    def onStart():
                        if OptionsModule.selected: return
                        OptionsModule.selected = True

                        optionBasic()
                        createNewLayerOptions([], Container=self.OptionsContainer.secondLayerContainer)

                        AppendUserSettings("General", {"selectedWidgets": [], "activeWidgets": []})

                        self.Hide(onFinished=createSelectionWindow, Hard=True)

                    def OnReset():
                        AppendUserSettings("Windows", WindowSettingsTemplate)
                        OptionsModule.onStart()

                    def OnKeep():
                        OptionsModule.onStart()

                    def onRun():
                        if OptionsModule.selected: return
                        OptionsModule.selected = True

                        optionBasic()
                        createNewLayerOptions([], Container=self.OptionsContainer.secondLayerContainer)

                        UpdateUserSettings()
                        global UserSettings

                        def load():
                            createSelectionWindow()
                            for i, widget in enumerate(UserSettings["General"]["activeWidgets"]):
                                #QTimer.singleShot(GetQTime(0.25) * i, lambda w=widget: uiApp.runProcess(f"Widgets/{w}/main.py", w))
                                QTimer.singleShot(GetQTime(0.25) * i, lambda w=widget: RunProcess(f"Widgets/{w}/main.py", w))

                        self.Hide(onFinished=load, Hard=True)  

                    def onOpen():
                        if OptionsModule.selected: return
                        OptionsModule.selected = True

                        optionBasic()
                        createNewLayerOptions([], Container=self.OptionsContainer.secondLayerContainer)
                        
                        UpdateUserSettings()
                        global UserSettings

                        if len(UserSettings["General"]["activeWidgets"]) > 0:
                            AppendUserSettings("General", {"selectedWidgets": UserSettings["General"]["activeWidgets"], "activeWidgets": []})

                        self.Hide(onFinished=createSelectionWindow, Hard=True)  

                    def onCancel():
                        optionBasic()
                        createNewLayerOptions([], Container=self.OptionsContainer.secondLayerContainer)

                def newPack():
                    optionBasic()

                    UpdateUserSettings()
                    global UserSettings, selectionWindow

                    if len(UserSettings["General"]["activeWidgets"]) > 0 or len(UserSettings["General"]["selectedWidgets"]) > 0:
                        opButtons = createNewLayerOptions(
                            [
                                {"key": "Start", "textKey": "labels/homePage/options/newPack_Options/start"},
                                {"key": "Cancel", "textKey": "labels/homePage/options/newPack_Options/cancel"}
                            ],
                            Container=self.OptionsContainer.secondLayerContainer
                        )
                        
                        try:
                            opButtons["Start"].function = OptionsModule.onStart
                            opButtons["Cancel"].function = OptionsModule.onCancel

                            opButtons["Start"].clicked.connect(opButtons["Start"].function)
                            opButtons["Cancel"].clicked.connect(opButtons["Cancel"].function)
                        except Exception: pass
                        
                    else:
                        if CompareObjects(UserSettings["Windows"]["Selection"], WindowSettingsTemplate["Selection"]) == True:
                            OptionsModule.onStart()
                        else:
                            opButtons = createNewLayerOptions(
                                [
                                    {"key": "Reset", "textKey": "labels/homePage/options/newPack_Options/reset"},
                                    {"key": "Keep", "textKey": "labels/homePage/options/newPack_Options/keep"},
                                    {"key": "Cancel", "textKey": "labels/homePage/options/newPack_Options/cancel"}
                                ],
                                Container=self.OptionsContainer.secondLayerContainer
                            )

                            try:
                                opButtons["Reset"].function = OptionsModule.OnReset
                                opButtons["Keep"].function = OptionsModule.OnKeep
                                opButtons["Cancel"].function = OptionsModule.onCancel

                                opButtons["Reset"].clicked.connect(opButtons["Reset"].function)
                                opButtons["Keep"].clicked.connect(opButtons["Keep"].function)
                                opButtons["Cancel"].clicked.connect(opButtons["Cancel"].function)
                            except Exception: pass
                    
                def loadPack():
                    optionBasic()

                    UpdateUserSettings()
                    global UserSettings

                    if len(UserSettings["General"]["activeWidgets"]) > 0:
                        opButtons = createNewLayerOptions(
                            [
                                {"key": "Run", "textKey": "labels/homePage/options/loadPack_Options/run"},
                                {"key": "Open", "textKey": "labels/homePage/options/loadPack_Options/open"},
                                {"key": "Cancel", "textKey": "labels/homePage/options/newPack_Options/cancel"}
                            ],
                            Container=self.OptionsContainer.secondLayerContainer
                        )

                        try:
                            opButtons["Run"].function = OptionsModule.onRun
                            opButtons["Open"].function = OptionsModule.onOpen
                            opButtons["Cancel"].function = OptionsModule.onCancel

                            opButtons["Run"].clicked.connect(opButtons["Run"].function)
                            opButtons["Open"].clicked.connect(opButtons["Open"].function)
                            opButtons["Cancel"].clicked.connect(opButtons["Cancel"].function)
                        except Exception: pass

                    else:
                        OptionsModule.onOpen()

                def exitMenu():
                    optionBasic()
                    self.close()

                # Prints -----------

                indexOfPrinting = 0

                PrintElement(Options["newPack"], indexOfPrinting * 0.5)
                indexOfPrinting += 1
                Options["newPack"].clicked.connect(newPack)
                
                if len(UserSettings["General"]["selectedWidgets"]) > 0 or len(UserSettings["General"]["activeWidgets"]) > 0:
                    PrintElement(Options["loadPack"], indexOfPrinting * 0.5)
                    indexOfPrinting += 1
                    Options["loadPack"].clicked.connect(loadPack)

                PrintElement(Options["exit"], indexOfPrinting * 0.5)
                indexOfPrinting += 1
                Options["exit"].clicked.connect(exitMenu)

                # -------------------


            QTimer.singleShot(GetQTime(0.65), startHover)
            QTimer.singleShot(GetQTime(4), printOptions)

        QTimer.singleShot(GetQTime(0.3), startShowing)

        self.PlatformLabel.raise_()
        self.CharLabel.raise_()
        self.HelloTitle.raise_()

        self.show()


if __name__ == "__main__":
    welcomeWindow = WelcomeWindow(Size={"width": 1000, "height": 600}, titleKey="titles/welcome", name="Homepage")
    
    sys.exit(uiApp.exec())