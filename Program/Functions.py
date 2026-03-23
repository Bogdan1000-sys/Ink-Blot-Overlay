from PyQt6.QtCore import QPropertyAnimation, QTimer

# -- Services --
from Services import InitializationService
from Services import (
    LocalizationService
)
InitializationService.__init__()

# -- Data --

# -- Functions --
def GetQTime(n:float):
    return int(n*1000)

def getHex(rgb):
    if isinstance(rgb, (list, tuple)) and len(rgb) >= 3:
        r, g, b = rgb[:3]
        return f"#{r:02X}{g:02X}{b:02X}"
    elif isinstance(rgb, str):
        parts = [int(x) for x in rgb.replace(' ', '').split(',')]
        return f"#{parts[0]:02X}{parts[1]:02X}{parts[2]:02X}"
    else:
        raise ValueError("Error: Unknonw format RGB")

def applyStyleClass(obj, className):
    obj.setProperty("class", className)
    obj.style().unpolish(obj)
    obj.style().polish(obj)
    obj.update()

def setClassVariable(classSelf, valueName:str, value):
    classSelf[valueName] = value

# ---------- Animations ------------- #
def CloneAnimation(animation: QPropertyAnimation, parent=None):
    newAnimation = QPropertyAnimation(parent or animation.parent(), animation.propertyName())

    newAnimation.setStartValue(animation.startValue())
    newAnimation.setEndValue(animation.endValue())
    newAnimation.setDuration(animation.duration())
    newAnimation.setEasingCurve(animation.easingCurve())
    newAnimation.setDirection(animation.direction())
    newAnimation.setLoopCount(animation.loopCount())

    return newAnimation

def PrintText(container=None, text=None, type="origin", interval=30):
    if container == None or text == None: return
    if type == "dict":
        text = LocalizationService.getAdaptedTextFromDictionary(text)

    pauseSymbols = {
        ",": 500,
        ";": 500,
        ":": 500,
        "-": 500,
        ".": 1000,
        "!": 1000,
        "?": 1000
    }

    if hasattr(container, "_printTimer"):
        container._printTimer.stop()

    container.setText("")
    container._printIndex = 0
    container._fullText = text

    timer = QTimer(container)
    container._printTimer = timer

    def step():
        if container._printIndex >= len(container._fullText):
            try: container.setProperty("Printed", True)
            except Exception: return

            timer.stop()
            return

        char = container._fullText[container._printIndex]
        container.setText(container.text() + char)
        container._printIndex += 1

        extraDelay = pauseSymbols.get(char, 0)
        timer.setInterval(interval + extraDelay)

    timer.timeout.connect(step)
    timer.start(interval)

    try: container.setProperty("Printed", False)
    except Exception: return