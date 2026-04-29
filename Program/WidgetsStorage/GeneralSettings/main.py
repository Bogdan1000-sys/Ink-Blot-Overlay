from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QMargins, QParallelAnimationGroup, QPoint
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy, QBoxLayout, QGraphicsOpacityEffect, QSlider
from PyQt6.QtGui import QPixmap
import sys, json, random, os, math

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
from Functions import GetQTime

# -- Objects --
generalSettingsWindow = None

# -- Constants --
with open("Data/Pathes.json", "r", encoding="utf-8") as pFile:
    Pathes = json.load(pFile)

# -- Data --
with open(Pathes["Constants"], "r", encoding="utf-8") as cFile:
    Constants = json.load(cFile)

# -- Settings Data --
with open(Pathes["GeneralSettingsTree"], "r", encoding="utf-8") as treeFile:
    Tree = json.load(treeFile)
with open(Pathes["GeneralSettingsCarousel"], "r", encoding="utf-8") as carouselFile:
    Carousel = json.load(carouselFile)

# -- Scripts --
from Classes import ModifiedWindow, UIApplication

# -- Style --
ButtonStyle = '''
    QPushButton[class='Button'] {
        background-color: qlineargradient(
            x1: 0, y1: 0,
            x2: 0, y2: 1,
            stop: 0 rgba(70, 35, 0, 255),
            stop: 1 rgba(40, 20, 0, 255)
        );
        border: 1px solid rgba(255, 106, 0, 255);
        border-radius: 15px;
    }
    QPushButton[class='Button:unselect'], QPushButton[class='Button:deactivate'] {
        background-color: qlineargradient(
            x1: 0, y1: 0,
            x2: 0, y2: 1,
            stop: 0 rgba(50, 15, 0, 255),
            stop: 1 rgba(20, 0, 0, 255)
        );
        border: 1px solid rgba(255, 106, 0, 255);
        border-radius: 15px;
    }
    QPushButton[class='Button']:hover, QPushButton[class='Button:unselect']:hover, QPushButton[class='Button:deactivate']:hover {
        background: qlineargradient(
            x1: 0, y1: 1,
            x2: 0, y2: 0,
            stop: 0 #000000,
            stop: 1 #301400
        );
    }
    QLabel[class='ButtonLabel'] {
        background: transparent;
        font-size: 15px;
        font-family: 'Courier New', Courier, monospace;
        color: rgba(255, 106, 0, 255);
    }
'''

NavigationStyle = """
    QFrame[class='NavigationFrame'] {
        background-color: qlineargradient(
            x1: 0, y1: 0,
            x2: 0, y2: 1,
            stop: 0 rgba(70, 35, 0, 255),
            stop: 1 rgba(40, 20, 0, 255)
        );
        border: 1px solid rgba(255, 106, 0, 255);
        border-radius: 15px;
    }
    
    QLabel[class='NavigationLabel'] {
        background: transparent;
        padding: 0px 0px 0px 10px;
        font-size: 15px;
        font-family: 'Courier New', Courier, monospace;
        color: rgba(255, 106, 0, 255);
    }
"""

OptionsStyle = """
    QFrame[class='optionContainer'] {
        background: #100700;
        border-radius: 20px;
    }

    QLabel[class='optionName'] {
        background: transparent;
        font-size: 14px;
        font-family: 'Courier New', Courier, monospace;
        color: rgba(255, 106, 0, 255);
        padding-left: 5px;
    }

    QFrame[class='interContainer'] {
        background: transparent;
        border: none;
    }

    QObject[class='interconElement'] {
        min-width: 30px;
        min-height: 30px;
        
        background: #371800;
        border-radius: 15px;
        border: none;
    }

    QPushButton#dropButton {
        width: 120px;
    }

    QPushButton#dropButton:hover {
        background: #000000;
    }

    QFrame#sliderContainer {
        width: 120px;
    }

    QFrame#slider {
        background: rgba(255, 106, 0, 255);
        border-radius: 10px;
    }
    QFrame#sliderBackground {
        background: rgba(13, 5, 0, 255);
        border-radius: 10px;
    }
    
    QSlider#slider {
        background: rgb(56, 22, 0);
        border-radius: 10px;
    }
    QSlider::handle:horizontal#slider {
        background: rgb(255, 106, 0);
        border-radius: 10px;
        width: 20px;
    }
    QSlider::groove:horizontal#slider {
        background: rgb(56, 22, 0);
    }

    QLabel#text {
        background: transparent;
        padding-bottom: 2px;
        font-size: 22px;
        font-family: 'Courier New', Courier, monospace;
        color: rgba(255, 106, 0, 255);
    }

    QLabel#text1 {
        background: transparent;
        font-size: 18px;
        font-family: 'Courier New', Courier, monospace;
        color: rgba(255, 106, 0, 255);
    }

    QLabel#currentValueLabel {
        min-width: 40px;

        font-size: 14px;
        font-family: 'Courier New', Courier, monospace;
        color: rgba(255, 106, 0, 255);
    }

    QPushButton#dialogButton {
        width: 120px;

        font-size: 14px;
        font-family: 'Courier New', Courier, monospace;
        color: rgba(255, 106, 0, 255);
    }
    QPushButton#dialogButton:hover {
        background: #1f0d00;
    }
    QFrame#dialogContainer {
        background: black;
    }
    QLabel#QuestionLabel {
        width: 110px;
        height: 30px;

        background: transparent;
        font-size: 14px;
        font-family: 'Courier New', Courier, monospace;
        color: rgba(255, 106, 0, 255);
    }
    QPushButton#dialogVariantButton {
        border-radius: 5px;
        background: #371800;
    }
    QPushButton#dialogVariantButton:hover {
        background: #1f0d00;
    }

    QFrame#dropContainer {
        background: #371800;
        border-radius: 15px;
        border: none;
    }

    QPushButton#optionButton {
        background: #733200;
        border-radius: 5px;
        border: none;

        font-size: 14px;
        font-family: 'Courier New', Courier, monospace;
        color: rgba(255, 106, 0, 255);
    }

    QPushButton#optionButton:hover {
        background: #522402;
        color: rgba(153, 64, 0, 255);
    }
"""

def main(connection):
    global generalSettingsWindow

    uiApp = UIApplication(sys.argv, appName="GeneralSettingsApplication")

    tree = SettingsService.getSettingsTree()
    chapter = list(tree.keys())[0]
    index = list(tree.keys()).index(chapter)
    
    class OptionContainer(QFrame):
        def __init__(self, parent=None, key=None):
            super().__init__(parent)

            settings = SettingsService.getUserSettings().get("General", {})

            self._margins = QMargins(0, 0, 0, 0)
            self.setContentsMargins(self._margins)

            self.setFixedSize(self.parent().width() - 40, 40)
            self.setProperty("class", "optionContainer")
            self.setStyleSheet(OptionsStyle)
            self.show()

            self.lay = QHBoxLayout()
            self.lay.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
            self.lay.setContentsMargins(0, 0, 0, 0)
            self.lay.setSpacing(0)
            self.lay.setDirection(QBoxLayout.Direction.LeftToRight)
            self.setLayout(self.lay)

            optionData = tree[chapter].get("branches", {})[key]

            self.nameLabel = QLabel("[ Opt. Name ]", parent=self)
            self.nameLabel.setProperty("class", "optionName")
            self.nameLabel.setFixedSize(self.width()//2, self.height())
            self.nameLabel.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.lay.addWidget(self.nameLabel)

            self.interContainer = QFrame(parent=self)
            self.interContainer.setProperty("class", "interContainer")
            self.interContainer.setFixedSize(self.width()//2, self.height())
            self.lay.addWidget(self.interContainer)

            self.interContainer.lay = QHBoxLayout()
            self.interContainer.lay.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
            self.interContainer.lay.setContentsMargins(0, 0, 5, 0)
            self.interContainer.lay.setSpacing(5)
            self.interContainer.lay.setDirection(QBoxLayout.Direction.LeftToRight)
            self.interContainer.setLayout(self.interContainer.lay)

            self.opacity = QGraphicsOpacityEffect()
            self.opacity.setOpacity(0.0)
            self.setGraphicsEffect(self.opacity)

            opacityAnim = QPropertyAnimation(self.opacity, b"opacity")
            opacityAnim.setStartValue(0.0)
            opacityAnim.setEndValue(1)
            opacityAnim.setDuration(GetQTime(0.5))
            opacityAnim.setEasingCurve(QEasingCurve.Type.InOutSine)
            opacityAnim.setLoopCount(1)

            self.showAnim = QParallelAnimationGroup()
            self.showAnim.addAnimation(opacityAnim)

            LocalizationService.registerAdaptableText(self.nameLabel, optionData["name"])
            
            if settings.get(key):
                currentValueLabel:QLabel

            if optionData["type"] == "dropdown":
                dropButton = QPushButton(self)
                dropButton.setObjectName("dropButton")
                dropButton.setProperty("class", "interconElement")
                
                dropButton.lay = QHBoxLayout()
                dropButton.lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
                dropButton.lay.setContentsMargins(0, 0, 0, 0)
                dropButton.lay.setSpacing(0)
                dropButton.lay.setDirection(QBoxLayout.Direction.LeftToRight)
                dropButton.setLayout(dropButton.lay)

                dropButton.dropArrows = QLabel(text="↓↓↓↓↓↓",parent=dropButton)
                dropButton.dropArrows.setObjectName("text")
                dropButton.lay.addWidget(dropButton.dropArrows)

                def createDropContainer():
                    dropContainer = QFrame(self)
                    dropContainer.setObjectName("dropContainer")
                    dropContainer.setProperty("class", "interconElement")

                    dropContainer.setFixedSize(
                        dropButton.width(),
                        dropButton.height() * len(optionData["options"]) + 20
                    )

                    targetPos = dropButton.mapToGlobal(QPoint(0, dropButton.height() + 2))
                    dropContainer.move(targetPos)

                    dropContainer.opacity = QGraphicsOpacityEffect()
                    dropContainer.opacity.setOpacity(0.0)

                    dropContainer.showAnims = QParallelAnimationGroup()

                    showOpacity = QPropertyAnimation(dropContainer.opacity, b"opacity")
                    showOpacity.setStartValue(0.0)
                    showOpacity.setEndValue(1.0)
                    showOpacity.setDuration(GetQTime(0.15))
                    showOpacity.setEasingCurve(QEasingCurve.Type.InOutCubic)
                    showOpacity.setLoopCount(1)

                    showPos = QPropertyAnimation(dropContainer, b"pos")
                    showPos.setStartValue(targetPos + QPoint(0, -10))
                    showPos.setEndValue(targetPos)
                    showPos.setDuration(GetQTime(0.15))
                    showPos.setEasingCurve(QEasingCurve.Type.InOutCubic)
                    showPos.setLoopCount(1)

                    dropContainer.showAnims.addAnimation(showOpacity)
                    dropContainer.showAnims.addAnimation(showPos)

                    dropContainer.lay = QVBoxLayout(dropContainer)
                    dropContainer.lay.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
                    dropContainer.lay.setContentsMargins(0, 0, 0, 0)
                    dropContainer.lay.setSpacing(2)
                    dropContainer.setLayout(dropContainer.lay)

                    def changeValue(newValue):
                        dropContainer.deleteLater()
                        currentValueLabel.setText(newValue)
                        SettingsService.appendUserSettings("General", {optionData["key"]: newValue})
                        if optionData["key"] == "language": connection.send(f"language:{newValue}")

                    dropContainer.options = {}
                    for value in optionData["options"]:
                        optButton = QPushButton(text=value, parent=dropContainer)
                        optButton.setObjectName("optionButton")
                        optButton.setFixedSize(
                            dropContainer.width() - 10,
                            dropButton.height()
                        )
                        dropContainer.lay.addWidget(optButton)

                        optButton.clicked.connect(lambda _, v=value: changeValue(v))

                        dropContainer.options[value] = optButton
                    
                    dropContainer.setWindowFlags(Qt.WindowType.Popup)
                    dropContainer.show()

                    dropContainer.showAnims.start()

                dropButton.clicked.connect(createDropContainer)

                self.interContainer.lay.addWidget(dropButton)
            elif optionData["type"] == "slider":

                sliderContainer = QFrame(self)
                sliderContainer.setObjectName("sliderContainer")
                sliderContainer.setProperty("class", "interconElement")
                sliderContainer.resize(120, 30)
                
                # -----------------
                sliderContainer.sliderBackground = QFrame(sliderContainer)
                sliderContainer.sliderBackground.setObjectName("sliderBackground")
                sliderContainer.sliderBackground.resize(
                    sliderContainer.width() - 10,
                    sliderContainer.height() - 10
                )
                sliderContainer.sliderBackground.move(
                    sliderContainer.x() + 5,
                    sliderContainer.y() + 5
                )

                sliderContainer.slider = QSlider(Qt.Orientation.Horizontal, parent=sliderContainer)
                sliderContainer.slider.setObjectName("slider")
                sliderContainer.slider.resize(
                    sliderContainer.width() - 10,
                    sliderContainer.height() - 10
                )
                sliderContainer.slider.move(
                    sliderContainer.x() + 5,
                    sliderContainer.y() + 5
                )
                sliderContainer.slider.setMinimum(int(optionData["options"]["min"]*100))
                sliderContainer.slider.setMaximum(int(optionData["options"]["max"]*100))
                sliderContainer.slider.setValue(int(settings[key]*100))

                def changeValue(newValue): 
                    newValue = float(newValue/100)
                    currentValueLabel.setText(str(newValue))
                    SettingsService.appendUserSettings("General", {optionData["key"]: newValue})

                sliderContainer.slider.valueChanged.connect(changeValue)

                # INTERACTION -------------------------------

                margins = {"min": sliderContainer.x() + 5, "max": sliderContainer.x() + sliderContainer.width() - 5}

                # -------------------------------------------

                self.interContainer.lay.addWidget(sliderContainer)
            elif optionData["type"] == "dialogButton":
                
                dialogButton = QPushButton(text="< O >", parent=self.interContainer)
                dialogButton.setObjectName("dialogButton")
                dialogButton.setProperty("class", "interconElement")
                self.interContainer.lay.addWidget(dialogButton)

                def CreateDialog():
                    dialogContainer = QFrame(self)
                    dialogContainer.setObjectName("dialogContainer")
                    dialogContainer.setProperty("class", "interconElement")

                    dialogContainer.adjustSize()
                    dialogContainer.setFixedWidth(dialogButton.width())

                    targetPos = dialogButton.mapToGlobal(QPoint(0, dialogButton.height() + 2))
                    dialogContainer.move(targetPos)

                    dialogContainer.opacity = QGraphicsOpacityEffect()
                    dialogContainer.opacity.setOpacity(0.0)

                    dialogContainer.showAnims = QParallelAnimationGroup()

                    showOpacity = QPropertyAnimation(dialogContainer.opacity, b"opacity")
                    showOpacity.setStartValue(0.0)
                    showOpacity.setEndValue(1.0)
                    showOpacity.setDuration(GetQTime(0.15))
                    showOpacity.setEasingCurve(QEasingCurve.Type.InOutCubic)
                    showOpacity.setLoopCount(1)

                    showPos = QPropertyAnimation(dialogContainer, b"pos")
                    showPos.setStartValue(targetPos + QPoint(0, -10))
                    showPos.setEndValue(targetPos)
                    showPos.setDuration(GetQTime(0.15))
                    showPos.setEasingCurve(QEasingCurve.Type.InOutCubic)
                    showPos.setLoopCount(1)

                    dialogContainer.showAnims.addAnimation(showOpacity)
                    dialogContainer.showAnims.addAnimation(showPos)

                    dialogContainer.lay = QVBoxLayout(dialogContainer)
                    dialogContainer.lay.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
                    dialogContainer.lay.setContentsMargins(5, 5, 5, 5)
                    dialogContainer.lay.setSpacing(2)
                    dialogContainer.setLayout(dialogContainer.lay)

                    dialogContainer.QuestionLabel = QLabel(text="[ Question ]", parent=dialogContainer); LocalizationService.registerAdaptableText(dialogContainer.QuestionLabel, optionData["options"]["question"])
                    dialogContainer.QuestionLabel.setWordWrap(True)
                    dialogContainer.QuestionLabel.setObjectName("QuestionLabel")
                    dialogContainer.QuestionLabel.setProperty("class", "interconElement")
                    dialogContainer.lay.addWidget(dialogContainer.QuestionLabel)

                    # ------
                    dialogContainer.PositiveButton = QPushButton(parent=dialogContainer);
                    dialogContainer.PositiveButton.setObjectName("dialogVariantButton")
                    dialogContainer.PositiveButton.setProperty("class", "interconElement")
                    # --
                    dialogContainer.PositiveButton.lay = QVBoxLayout()
                    dialogContainer.PositiveButton.lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    dialogContainer.PositiveButton.lay.setContentsMargins(0, 0, 0, 0)
                    dialogContainer.PositiveButton.lay.setSpacing(0)
                    dialogContainer.PositiveButton.setLayout(dialogContainer.PositiveButton.lay)
                    # --
                    dialogContainer.PositiveButton.textLabel = QLabel(text="YES", parent=dialogContainer.PositiveButton); LocalizationService.registerAdaptableText(dialogContainer.PositiveButton.textLabel, optionData["options"]["yes"])
                    dialogContainer.PositiveButton.textLabel.setObjectName("text1")
                    dialogContainer.PositiveButton.lay.addWidget(dialogContainer.PositiveButton.textLabel)
                    dialogContainer.lay.addWidget(dialogContainer.PositiveButton)

                    # ----------------------------

                    dialogContainer.NegativeButton = QPushButton(parent=dialogContainer); # LocalizationService.registerAdaptableText(dialogContainer.NegativeButton, optionData["options"]["no"])
                    dialogContainer.NegativeButton.setObjectName("dialogVariantButton")
                    dialogContainer.NegativeButton.setProperty("class", "interconElement")
                    dialogContainer.lay.addWidget(dialogContainer.NegativeButton)
                     # --
                    dialogContainer.NegativeButton.lay = QVBoxLayout()
                    dialogContainer.NegativeButton.lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    dialogContainer.NegativeButton.lay.setContentsMargins(0, 0, 0, 0)
                    dialogContainer.NegativeButton.lay.setSpacing(0)
                    dialogContainer.NegativeButton.setLayout(dialogContainer.NegativeButton.lay)
                    # --
                    dialogContainer.NegativeButton.textLabel = QLabel(text="NO", parent=dialogContainer.NegativeButton); LocalizationService.registerAdaptableText(dialogContainer.NegativeButton.textLabel, optionData["options"]["no"])
                    dialogContainer.NegativeButton.textLabel.setObjectName("text1")
                    dialogContainer.NegativeButton.lay.addWidget(dialogContainer.NegativeButton.textLabel)
                    dialogContainer.lay.addWidget(dialogContainer.NegativeButton)
                    # ------
                    dialogContainer.setWindowFlags(Qt.WindowType.Popup)
                    dialogContainer.show()

                    dialogContainer.showAnims.start()
                
                dialogButton.clicked.connect(CreateDialog)


            if settings.get(key) != None:
                currentValueLabel = QLabel(text=str(settings[key]), parent=self.interContainer)
                currentValueLabel.setObjectName("currentValueLabel")
                currentValueLabel.setProperty("class", "interconElement")
                currentValueLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.interContainer.lay.addWidget(currentValueLabel)
            


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

            # self.buttons["settingsButton"].setFixedWidth(100)

            self.updateOptionsLayout()

        Options = {}

        def updateOptionsLayout(self):
            LocalizationService.registerAdaptableText(self.elements["NavigationLabel"].label, "generalSettings/"+chapter)

            for key in self.Options.keys():
                self.Options[key].deleteLater()
            self.Options.clear()

            data = tree[chapter].get("branches")
            if data == None: print("[ GENERAL SETTINGS ] No 'branches' found!"); return
            for key in data.keys():
                optContainer = OptionContainer(parent=self, key=key)
                self.elements["OptionsContainer"].lay.addWidget(optContainer)
                self.Options[key] = optContainer

            for i, optContainer in enumerate(self.Options.values()):
                QTimer.singleShot(
                    GetQTime(float(i)*0.05),
                    lambda opt=optContainer: opt.showAnim.start()
                )

            for point in self.elements["navigationPoints"]:
                if self.elements["navigationPoints"].index(point) == index: point.select()
                else: point.unselect()

        switchDebounce = False
        def switchChapter(self, direction=">"):
            if self.switchDebounce: return
            self.switchDebounce = True
            def changeDeb(): self.switchDebounce = False
            QTimer.singleShot(GetQTime(0.25), changeDeb)

            nonlocal index, chapter
            global Carousel

            if direction == ">": 
                index += 1
                if index > len(Carousel)-1: index = 0
            else: # "<"
                index -= 1
                if index < 0: index = len(Carousel)-1
            
            chapter = Carousel[index]

            self.updateOptionsLayout()
            SoundService.playSound("ClickSound", self.objectName())

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

            elementWidth = self.mainContainer.width() - 14
            elementHeights = {
                "NavigationContainer": int(float(self.mainContainer.height())*0.06),
                "OptionsContainer": int(float(self.mainContainer.height())*0.90), # 0.87
                # "ButtonsContainer": int(float(self.mainContainer.height())*0.07)
            }

            # NAVIGATION ---------------------------------------------------------------------------------------------

            self.elements["NavigationContainer"] = QFrame(self.mainContainer)
            self.elements["NavigationContainer"].setProperty("class", "NavigationContainer")
            self.elements["NavigationContainer"].setStyleSheet("""QFrame[class='NavigationContainer'] {background: none; border: none;}""")
            self.elements["NavigationContainer"].setFixedWidth(elementWidth)
            self.elements["NavigationContainer"].setFixedHeight(elementHeights["NavigationContainer"])

            self.mainContainer.mainLayout.addWidget(self.elements["NavigationContainer"])
            self.elements["NavigationContainer"].show()

            self.elements["NavigationLabel"] = QFrame(self.elements["NavigationContainer"])
            self.elements["NavigationLabel"].setProperty("class", "NavigationFrame")
            self.elements["NavigationLabel"].setStyleSheet(NavigationStyle)
            self.elements["NavigationLabel"].setFixedWidth(
                int(float(self.elements["NavigationContainer"].width())*0.75)
            )
            self.elements["NavigationLabel"].setFixedHeight(self.elements["NavigationContainer"].height())
            self.elements["NavigationLabel"].show()

            self.elements["NavigationLabel"].label = QLabel(text="Navigation", parent=self.elements["NavigationLabel"])
            self.elements["NavigationLabel"].label.setFixedWidth(int(float(self.elements["NavigationLabel"].width())*0.5))
            self.elements["NavigationLabel"].label.setFixedHeight(self.elements["NavigationLabel"].height())
            self.elements["NavigationLabel"].label.setProperty("class", "NavigationLabel")
            self.elements["NavigationLabel"].label.setStyleSheet(NavigationStyle)
            self.elements["NavigationLabel"].label.move(
                self.elements["NavigationLabel"].x(),
                self.elements["NavigationLabel"].y()
            )
            self.elements["NavigationLabel"].label.show()

            self.elements["NavigationLabel"].points = QFrame(self.elements["NavigationLabel"])
            self.elements["NavigationLabel"].points.setFixedWidth(int(float(self.elements["NavigationLabel"].width())*0.5))
            self.elements["NavigationLabel"].points.setFixedHeight(self.elements["NavigationLabel"].height())
            self.elements["NavigationLabel"].points.setProperty("class", "PointsContainer")
            self.elements["NavigationLabel"].points.setStyleSheet("""QFrame[class='PointsContainer'] {background: rgba(255,255,255,0); border: none; border-radius: 15px;}""")
            self.elements["NavigationLabel"].points.move(
                self.elements["NavigationLabel"].x() + self.elements["NavigationLabel"].width() // 2,
                self.elements["NavigationLabel"].y()
            )
            self.elements["NavigationLabel"].points.show()

            self.elements["NavigationLabel"].points.lay = QHBoxLayout()
            self.elements["NavigationLabel"].points.lay.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.elements["NavigationLabel"].points.lay.setSpacing(10)
            self.elements["NavigationLabel"].points.lay.setContentsMargins(10, 0, 10, 0)
            self.elements["NavigationLabel"].points.lay.setDirection(QBoxLayout.Direction.LeftToRight)
            self.elements["NavigationLabel"].points.setLayout(self.elements["NavigationLabel"].points.lay)

            self.NavPoints = {}

            def CreatePoint(parent=self.elements["NavigationLabel"].points):
                size = math.floor(parent.height()//3.6)

                label = QLabel(parent)
                label.setFixedSize(size, size)
                label.setProperty("class", "pointLabel")
                label.setStyleSheet("""
                    QLabel[class='pointLabel'] {
                        background: transparent;
                        border: none;
                    }
                """)

                pixmap = QPixmap("Resources/Images/navPoint.ico").scaled(size, size)
                label.setPixmap(pixmap)

                opacity = QGraphicsOpacityEffect()
                opacity.setOpacity(0.0)
                label.setGraphicsEffect(opacity)

                label.show()
                parent.lay.addWidget(label)

                showOpacity = QPropertyAnimation(opacity, b"opacity")
                showOpacity.setEndValue(1.0)
                showOpacity.setDuration(GetQTime(0.25))

                hideOpacity = QPropertyAnimation(opacity, b"opacity")
                hideOpacity.setEndValue(0.25)
                hideOpacity.setDuration(GetQTime(0.25))

                label.select = showOpacity.start
                label.unselect = hideOpacity.start
                
                return label
            
            self.elements["navigationPoints"] = []
            
            for i in range(3):
                point = CreatePoint()
                self.elements["navigationPoints"].append(point)
                if i == 0: point.select()
                else: point.unselect()

            self.elements["SwitchesContainer"] = QFrame(self.elements["NavigationContainer"])
            self.elements["SwitchesContainer"].setProperty("class", "SwitchesContainer")
            # self.elements["SwitchesContainer"].setStyleSheet("""QFrame[class='SwitchesContainer'] {background: rgba(255, 255, 255, 50); border: none; border-radius: 15px;}""")
            self.elements["SwitchesContainer"].setStyleSheet(ButtonStyle)
            self.elements["SwitchesContainer"].setFixedWidth(int(float(self.elements["NavigationContainer"].width())*0.25))
            self.elements["SwitchesContainer"].setFixedHeight(self.elements["NavigationContainer"].height())
            self.elements["SwitchesContainer"].move(int(float(self.elements["NavigationContainer"].width())*0.75), 0)
            self.elements["SwitchesContainer"].show()

            self.elements["SwitchesContainer"].lay = QVBoxLayout()
            self.elements["SwitchesContainer"].lay.setAlignment(Qt.AlignmentFlag.AlignJustify)
            self.elements["SwitchesContainer"].lay.setSpacing(5)
            self.elements["SwitchesContainer"].lay.setContentsMargins(5,0,0,0)
            self.elements["SwitchesContainer"].lay.setDirection(QBoxLayout.Direction.LeftToRight)
            self.elements["SwitchesContainer"].setLayout(self.elements["SwitchesContainer"].lay)

            def CreateSwitchButton(direction=""):
                button = QPushButton(parent=self.elements["SwitchesContainer"])
                button.setProperty("class", "Button")
                button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

                button.label = QLabel(text=direction, parent=button)
                button.label.setProperty("class", "ButtonLabel")
                button.label.setStyleSheet("""font-size: 22px""")
                button.label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
                button.label.setWordWrap(True)
                button.label.setMinimumWidth(1)
                button.label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
                button.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                button.lay = QVBoxLayout(button)
                button.lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
                button.lay.addWidget(button.label)
                button.lay.setContentsMargins(0, 0, 0, 0)
                
                return button

            self.elements["LeftSwitchButton"] = CreateSwitchButton("<")
            self.elements["SwitchesContainer"].lay.addWidget(self.elements["LeftSwitchButton"])
            self.elements["LeftSwitchButton"].clicked.connect(lambda: self.switchChapter("<"))

            self.elements["RightSwitchButton"] = CreateSwitchButton(">")
            self.elements["SwitchesContainer"].lay.addWidget(self.elements["RightSwitchButton"])
            self.elements["RightSwitchButton"].clicked.connect(lambda: self.switchChapter(">"))

            # OPTIONS LIST ---------------------------------------------------------------------------------------------

            self.elements["OptionsContainer"] = QFrame(self.mainContainer)
            self.elements["OptionsContainer"].setProperty("class", "OptionsContainer")
            self.elements["OptionsContainer"].setFixedWidth(elementWidth)
            self.elements["OptionsContainer"].setFixedHeight(elementHeights["OptionsContainer"])
            self.mainContainer.mainLayout.addWidget(self.elements["OptionsContainer"])
            self.elements["OptionsContainer"].show()

            self.elements["OptionsContainer"].lay = QVBoxLayout()
            self.elements["OptionsContainer"].lay.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            self.elements["OptionsContainer"].lay.setSpacing(5)
            self.elements["OptionsContainer"].lay.setContentsMargins(10,10,10,10)
            self.elements["OptionsContainer"].lay.setDirection(QBoxLayout.Direction.TopToBottom)
            self.elements["OptionsContainer"].setLayout(self.elements["OptionsContainer"].lay)


            # RESULT BUTTONS [ DEPRECATED ] ---------------------------------------------------------------------------------------------

            # self.elements["ButtonsContainer"] = QFrame(self.mainContainer)
            # self.elements["ButtonsContainer"].setProperty("class", "ButtonsContainer")
            # self.elements["ButtonsContainer"].setFixedWidth(elementWidth)
            # self.elements["ButtonsContainer"].setFixedHeight(elementHeights["ButtonsContainer"])
            # self.mainContainer.mainLayout.addWidget(self.elements["ButtonsContainer"])
            # self.elements["ButtonsContainer"].show()

            # self.elements["ButtonsContainer"].lay = QVBoxLayout()
            # self.elements["ButtonsContainer"].lay.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
            # self.elements["ButtonsContainer"].lay.setSpacing(5)
            # self.elements["ButtonsContainer"].lay.setContentsMargins(0,0,0,0)
            # self.elements["ButtonsContainer"].lay.setDirection(QBoxLayout.Direction.LeftToRight)
            # self.elements["ButtonsContainer"].setLayout(self.elements["ButtonsContainer"].lay)

            # def CreateResultButton(key: str):
            #     button = QPushButton(parent=self.elements["ButtonsContainer"])
            #     button.setProperty("class", "Button")
            #     button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            #     button.label = QLabel("[ Missing ]", parent=button)
            #     button.label.setProperty("class", "ButtonLabel")
            #     button.label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
            #     button.label.setWordWrap(True)
            #     button.label.setMinimumWidth(1)
            #     button.label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            #     button.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            #     LocalizationService.registerAdaptableText(button.label, f"buttons/{key}")    

            #     button.lay = QVBoxLayout(button)
            #     button.lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
            #     button.lay.addWidget(button.label)
            #     button.lay.setContentsMargins(0, 0, 0, 0)
                
            #     return button
            
            # self.scButtons = {}

            # self.scButtons["cancel"] = CreateResultButton("cancel")
            # self.scButtons["cancel"].setMaximumWidth(self.mainContainer.width()//3)
            # self.elements["ButtonsContainer"].lay.addWidget(self.scButtons["cancel"])

            # self.scButtons["apply"] = CreateResultButton("apply")
            # self.elements["ButtonsContainer"].lay.addWidget(self.scButtons["apply"])


        def closeEvent(self, event):
            event.ignore()
            self.Hide(onFinished=uiApp.exit, Hard=True)
            return

    generalSettingsWindow = GeneralSettingsWindow(titleKey="titles/generalSettings", name="GeneralSettings", Mode="blackList", Modifiers=["gsettings"])

    # CODE -----------------------------------------------------------------------------------------------

    def Close():
        generalSettingsWindow.Hide(onFinished=uiApp.exit, Hard=True)
        
    codeFunctions = {
        "Close": Close
    }

    def onMessage(msg: str):
        if isinstance(msg, str):
            if ":" not in msg: return
            prefix, affix = msg.split(":", 1)
            if prefix == "code" and affix in codeFunctions:
                codeFunctions[affix]()
            elif prefix == "language":
                LocalizationService.changeLanguage(affix, False)


    # -----------------------------------------------------------------------------------------------------

    listener = ConnectionListener(connection)
    listener.messageReceived.connect(onMessage)
    listener.start()
    
    sys.exit(uiApp.exec())