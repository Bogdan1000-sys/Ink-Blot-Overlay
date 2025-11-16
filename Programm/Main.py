from PyQt6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QWidget, QScrollArea, QSizePolicy, QPushButton, QBoxLayout
from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint, QTimer
from PyQt6.QtGui import QWheelEvent, QPixmap
import sys, math, json, random

# -- Services --
from Services import CollectionService

# -- Functions --
from Functions import GetUserSettings, applyStyleClass, initSound, playSound, RegisterAdaptableText, AppendUserSettings

# -- Resources --
SelectWidgetSound = "Programm/Resources/SFX/WidgetSelect.wav"

# -- Constants --
with open("Programm/Data/Pathes.json", "r", encoding="utf-8") as pFile:
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
from Classes import InteractableWindow, WidgetButton

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

        def OnClick(button: str):
            GetUserSettings()
            if button == "select":
                if self.selectedWidget in selectedWidgets:
                    selectedWidgets.remove(self.selectedWidget)
                else:
                    selectedWidgets.append(self.selectedWidget)
            elif button == "activate":
                if self.selectedWidget in activeWidgets:
                    activeWidgets.remove(self.selectedWidget)
                else:
                    activeWidgets.append(self.selectedWidget)
            elif button == "activateSel":
                if self.selectedWidget not in activeWidgets:
                    for i in selectedWidgets:
                        activeWidgets.append(i)
                    selectedWidgets.clear()
                else:
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
        
        self.wcButtons["select"] = QPushButton(parent=self.ButtonsContainer)
        self.wcButtons["select"].label = QLabel("Select", parent=self.wcButtons["select"])
        RegisterAdaptableText(self.wcButtons["select"].label, "buttons/select")
        self.wcButtons["select"].label.setProperty("class", "wcButtonLabel")
        self.wcButtons["select"].label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.wcButtons["select"].label.setWordWrap(True)
        self.wcButtons["select"].label.setMinimumWidth(1)
        self.wcButtons["select"].label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.wcButtons["select"].label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wcButtons["select"].lay = QVBoxLayout(self.wcButtons["select"])
        self.wcButtons["select"].lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wcButtons["select"].lay.addWidget(self.wcButtons["select"].label)
        self.wcButtons["select"].lay.setContentsMargins(0, 0, 0, 0)
        self.wcButtons["select"].setProperty("class", "wcButton")
        self.wcButtons["select"].setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.wcButtons["activate"] = QPushButton(parent=self.ButtonsContainer)
        self.wcButtons["activate"].label = QLabel("Active", parent=self.wcButtons["activate"])
        RegisterAdaptableText(self.wcButtons["activate"].label, "buttons/activate")
        self.wcButtons["activate"].label.setProperty("class", "wcButtonLabel")
        self.wcButtons["activate"].label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.wcButtons["activate"].label.setWordWrap(True)
        self.wcButtons["activate"].label.setMinimumWidth(1)
        self.wcButtons["activate"].label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.wcButtons["activate"].label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wcButtons["activate"].lay = QVBoxLayout(self.wcButtons["activate"])
        self.wcButtons["activate"].lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wcButtons["activate"].lay.addWidget(self.wcButtons["activate"].label)
        self.wcButtons["activate"].lay.setContentsMargins(0, 0, 0, 0)
        self.wcButtons["activate"].setProperty("class", "wcButton")
        self.wcButtons["activate"].setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.wcButtons["activateSel"] = QPushButton(parent=self.ButtonsContainer)
        self.wcButtons["activateSel"].label = QLabel("Activate Selected", parent=self.wcButtons["activateSel"])
        RegisterAdaptableText(self.wcButtons["activateSel"].label, "buttons/activateSel")
        self.wcButtons["activateSel"].label.setProperty("class", "wcButtonLabel")
        self.wcButtons["activateSel"].label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.wcButtons["activateSel"].label.setWordWrap(True)
        self.wcButtons["activateSel"].label.setMinimumWidth(1)
        self.wcButtons["activateSel"].label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.wcButtons["activateSel"].label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wcButtons["activateSel"].lay = QVBoxLayout(self.wcButtons["activateSel"])
        self.wcButtons["activateSel"].lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wcButtons["activateSel"].lay.addWidget(self.wcButtons["activateSel"].label)
        self.wcButtons["activateSel"].lay.setContentsMargins(0, 0, 0, 0)
        self.wcButtons["activateSel"].setProperty("class", "wcButton")
        self.wcButtons["activateSel"].setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.buttonsContainerLayout.addWidget(self.wcButtons["activate"])
        self.buttonsContainerLayout.addWidget(self.wcButtons["select"])
        self.buttonsContainerLayout.addWidget(self.wcButtons["activateSel"])

        #-----------------------------------------------------------------------------------------------------------------

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

        QApplication.instance().installEventFilter(self)
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    settingWindow = WidgetSelectingWindow(titleKey="titles/widgetSelection")
    
    sys.exit(app.exec())
