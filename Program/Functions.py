import json
from PyQt6.QtCore import QUrl, QPropertyAnimation, QPoint, QTimer
from PyQt6.QtMultimedia import QSoundEffect
from copy import deepcopy
import subprocess, threading

# -- Services --
from Services import CollectionService

# -- Data --
with open("Data/Dictionary.json", "r", encoding="utf-8") as dFile:
    Dictionary = json.load(dFile)

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

def SetClassVariable(classSelf, valueName:str, value):
    classSelf[valueName] = value

# ---------- Animations ------------- #

def HideCommonWindows(exceptedWindow=None):
    for i, widget in enumerate(CollectionService.getTagged("commonOpacityWindow")):
        if widget == exceptedWindow: continue
        try: 
            HideAnim = QPropertyAnimation(widget, b"windowOpacity")
            HideAnim.setEndValue(0)
            HideAnim.setDuration(GetQTime(0.2))

            currentPos = widget.pos()
            HideAnimMove = QPropertyAnimation(widget, b"pos")
            HideAnimMove.setStartValue(currentPos)
            HideAnimMove.setEndValue(QPoint(currentPos.x(), currentPos.y() + 30))

            HideAnim.start()
            HideAnimMove.start()
        except: pass

def CloneAnimation(animation: QPropertyAnimation, parent=None):
    newAnimation = QPropertyAnimation(parent or animation.parent(), animation.propertyName())

    newAnimation.setStartValue(animation.startValue())
    newAnimation.setEndValue(animation.endValue())
    newAnimation.setDuration(animation.duration())
    newAnimation.setEasingCurve(animation.easingCurve())
    newAnimation.setDirection(animation.direction())
    newAnimation.setLoopCount(animation.loopCount())

    return newAnimation

# ---------- User Settings ---------- #

def GetUserSettings():
    with open("Data/userSettings.json", "r", encoding="utf-8") as usFile:
        return json.load(usFile)

def SetUserSettings(obj):
    #print("Saving setting changes...")
    OldSettings = GetUserSettings()
    NewSettings = CloneObject(OldSettings)
    for key, value in obj.items():
        if key not in OldSettings or not CompareObjects(OldSettings[key], value):
            NewSettings[key] = value
    if CompareObjects(OldSettings, NewSettings): 
        #print("[SAVE ERROR] No changes found!")
        return
    with open("Data/userSettings.json", "w", encoding="utf-8") as usFile:
        json.dump(NewSettings, usFile, ensure_ascii=False, indent=4)
    if "language" in obj and obj["language"] != OldSettings.get("language"):
        ChangeLanguage(obj["language"], updateSettings=False)

def AppendUserSettings(obj):
    userSettings = GetUserSettings()
    for key, value in obj.items():
        userSettings[key] = value
    SetUserSettings(userSettings)

# ------------------------------------- #

def GetAdaptedTextFromDictionary(key: str):
    keyParts = key.split("/")
    
    userSettings = GetUserSettings()
    language = userSettings.get("language", "eng")

    path = Dictionary[language]
    
    for key in keyParts:
        if key in path:
            path = path[key]
        else:
            print(f"[Warn] Key '{key}' not found in path '{'/'.join(keyParts)}'")
            path = None
            break

    if path is not None:
        return str(path)
    else:
        return "[Missing]"
    
def RegisterAdaptableText(obj, key):
    CollectionService.addTag(obj, "adaptableTextWidget")
    obj.setProperty("textKey", key)
    obj.setText(GetAdaptedTextFromDictionary(key))
    
def CloneObject(obj):
    if obj is None:
        return None
    try:
        return deepcopy(obj)
    except Exception:
        print("[WARNING!] The object is uncopyable!")
        return obj
    
def CompareObjects(objA, objB):
    if objA is objB:
        return True

    if type(objA) != type(objB):
        return False

    if isinstance(objA, (int, float, str, bool, type(None))):
        return objA == objB

    if isinstance(objA, (list, tuple, set)):
        return len(objA) == len(objB) and all(CompareObjects(a, b) for a, b in zip(objA, objB))

    if isinstance(objA, dict):
        if objA.keys() != objB.keys():
            return False
        return all(CompareObjects(objA[k], objB[k]) for k in objA)

    try:
        return objA == objB
    except Exception:
        pass

    if hasattr(objA, "__dict__") and hasattr(objB, "__dict__"):
        return CompareObjects(objA.__dict__, objB.__dict__)

    return False
    
def ChangeLanguage(newLanguage, updateSettings=True):
    if updateSettings:
        UserSettings = GetUserSettings()
        UserSettings["language"] = newLanguage

        with open("Data/userSettings.json", "w", encoding="utf-8") as usFile:
            json.dump(UserSettings, usFile, ensure_ascii=False, indent=4)

    for i, widget in enumerate(CollectionService.getTagged("adaptableTextWidget")):
        try:
            textKey = widget.property("textKey")
            widget.setText(GetAdaptedTextFromDictionary(textKey))
        except: pass


def PrintText(container=None, text=None, type="origin", interval=30):
    if container == None or text == None: return
    if type == "dict":
        text = GetAdaptedTextFromDictionary(text)

    # clickSound = initSound("Resources/SFX/PrintClick.wav", container)

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
            except: return

            timer.stop()
            return

        char = container._fullText[container._printIndex]
        container.setText(container.text() + char)
        container._printIndex += 1

        # playSound(clickSound, 0.25)

        extraDelay = pauseSymbols.get(char, 0)
        timer.setInterval(interval + extraDelay)

    timer.timeout.connect(step)
    timer.start(interval)

    try: container.setProperty("Printed", False)
    except: return


def initSound(url, parent):
    effect = QSoundEffect(parent)
    effect.setSource(QUrl.fromLocalFile(url))
    effect.setLoopCount(1)

    return effect

def playSound(sound=None, volume=None):
    if sound == None: return
    
    if volume:
        sound.setVolume(volume)
    else:
        userSettings = GetUserSettings()
        try:
            sound.setVolume(userSettings["volume"])
        except: pass
    sound.play()

def RunWidgetProcess(path, key, root, uiApp):
    proc = subprocess.Popen(["py", path], cwd=root)
    uiApp.addProcess(key, proc)

    def watcher(k, p):
        p.wait()
        if uiApp.processes.get(k) == p:
            uiApp.removeProcess(k)

    thread = threading.Thread(target=watcher, args=(key, proc), daemon=True)
    thread.start()