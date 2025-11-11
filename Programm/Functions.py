import json
from PyQt6.QtCore import QObject

# -- Services --
from Services import CollectionService

# -- Data --
with open("Programm/Data/Dictionary.json", "r", encoding="utf-8") as dFile:
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
    
def addDynamicStyle(obj, style: str):
    obj.setStyleSheet(style)

    class _StyleWatcher(QObject):
        def eventFilter(self, watched, event):
            if watched == obj and event.type() == 105:
                if event.propertyName().data().decode() == "class":
                    obj.style().unpolish(obj)
                    obj.style().polish(obj)
                    obj.update()
            return False

    watcher = _StyleWatcher()
    obj.installEventFilter(watcher)
    obj._styleWatcher = watcher

def SetClassVariable(classSelf, valueName:str, value):
    classSelf[valueName] = value

def GetUserSettings():
    with open("Programm/Data/userSettings.json", "r", encoding="utf-8") as usFile:
        usersettings = json.load(usFile)
    return usersettings

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
    
def ChangeLanguage(newLanguage):
    UserSettings = GetUserSettings()
    UserSettings["language"] = newLanguage

    with open("Programm/Data/userSettings.json", "w", encoding="utf-8") as usFile:
        json.dump(UserSettings, usFile, ensure_ascii=False, indent=4)

    for i, widget in enumerate(CollectionService.getTagged("adaptableTextWidget")):
        textKey = widget.property("textKey")
        widget.setText(GetAdaptedTextFromDictionary(textKey))