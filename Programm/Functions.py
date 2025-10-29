from PyQt6.QtCore import QObject

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