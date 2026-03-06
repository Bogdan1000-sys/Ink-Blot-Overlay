from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QLabel
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import threading, pygame, json
from copy import deepcopy

class CollectionService:
    _registry = {}

    @classmethod
    def addTag(cls, widget, tag: str):
        """Add tag to a widget"""
        widget_tags = widget.property("Tags") or set()
        widget_tags.add(tag)
        widget.setProperty("Tags", widget_tags)

        cls._registry.setdefault(tag, []).append(widget)

    @classmethod
    def removeTag(cls, widget, tag: str):
        """Remove tag from a widget"""
        widget_tags = widget.property("Tags") or set()
        if tag in widget_tags:
            widget_tags.remove(tag)
            widget.setProperty("Tags", widget_tags)

        if tag in cls._registry:
            cls._registry[tag] = [w for w in cls._registry[tag] if w != widget]
            if not cls._registry[tag]:
                del cls._registry[tag]

    @classmethod
    def getTags(cls, widget):
        """Get all tags of a widget"""
        return list(widget.property("Tags") or [])

    @classmethod
    def getTagged(cls, tag: str):
        """Get all widgets with a specific tag"""
        cls._registry[tag] = [
            w for w in cls._registry.get(tag, []) if w is not None
        ]
        return cls._registry.get(tag, [])

    @classmethod
    def getFirstTagged(cls, tag: str):
        widgets = [w for w in cls._registry.get(tag, []) if w is not None]
        cls._registry[tag] = widgets
        return widgets[0] if widgets else None
    

class ConnectionListener(QObject):
    messageReceived = pyqtSignal(object)

    def __init__(self, connection):
        super().__init__()
        self.connection = connection
        self._running = True

    def start(self):
        threading.Thread(target=self._listen, daemon=True).start()

    def _listen(self):
        while self._running:
            try:
                if self.connection.poll(0.1):
                    msg = self.connection.recv()
                    self.messageReceived.emit(msg)
            except (EOFError, OSError):
                break

    def stop(self):
        self._running = False

class LocalizationService:
    __dictPath = "Data/Dictionary.json"
    __dictionary = None

    @classmethod
    def __init__(cls):
        with open(cls.__dictPath, "r", encoding="utf-8") as dFile: cls.__dictionary = json.load(dFile)
    
    @classmethod
    def registerAdaptableText(cls, obj: QLabel, key: str):
        CollectionService.addTag(obj, "adaptableTextWidget")
        obj.setProperty("textKey", key)
        obj.setText(cls.getAdaptedTextFromDictionary(key))

    @classmethod
    def getAdaptedTextFromDictionary(cls, key: str):
        keyParts = key.split("/")

        language = SettingsService.getUserSettings().get("General", {}).get("language", "eng")

        path = cls.__dictionary[language]
        
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
        
    @classmethod
    def changeLanguage(cls, newLanguage: str, updateSettings=True):
        if updateSettings:
            generalChapter = SettingsService.getUserSettings().get("General", {})
            generalChapter["language"] = newLanguage
            SettingsService.setUserSettings("General", generalChapter)

        for widget in CollectionService.getTagged("adaptableTextWidget"):
            try: widget.setText(cls.getAdaptedTextFromDictionary(widget.property("textKey")))
            except: pass

class SettingsService:
    settings = None
    __path = "Data/userSettings.json"
    
    @classmethod
    def __init__(cls):
        pass

    @classmethod
    def updateUserSettings(cls):
        cls.settings = cls.getUserSettings()

    @classmethod
    def getUserSettings(cls) -> dict:
        with open(cls.__path, "r", encoding="utf-8") as usFile:
            return json.load(usFile)
        
    @classmethod
    def __setJSON(cls, settings: dict):
        with open(cls.__path, "w", encoding="utf-8") as usFile:
            json.dump(settings, usFile, ensure_ascii=False, indent=4)

    @classmethod
    def setUserSettings(cls, chapter: str, settings: dict):
        _oldSettings = cls.getUserSettings()
        _newSettings = ObjectService.deepClone(_oldSettings)

        if chapter not in _newSettings or not isinstance(_newSettings[chapter], dict):
            _newSettings[chapter] = {}

        changed = ObjectService.deepUpdate(_newSettings[chapter], settings)
        if not changed:
            return

        cls.__setJSON(cls.settings)

        if chapter == "General" and "language" in settings:
            oldLang = _oldSettings.get("General", {}).get("language")
            if settings["language"] != oldLang:
                LocalizationService.changeLanguage(settings["language"], False)

    @classmethod
    def appendUserSettings(cls, chapter: str, obj: dict):
        cls.updateUserSettings()

        if chapter not in cls.settings or not isinstance(cls.settings[chapter], dict):
            cls.settings[chapter] = {}

        for key, value in obj.items():
            cls.settings[chapter][key] = value

        cls.__setJSON(cls.settings)
    
class ObjectService:
    @classmethod
    def deepUpdate(cls, old: dict, new: dict) -> bool:
        changed = False

        for key, value in new.items():
            if isinstance(value, dict) and isinstance(old.get(key), dict):
                if cls.deepUpdate(old[key], value):
                    changed = True
            else:
                if key not in old or old[key] != value:
                    old[key] = value
                    changed = True

        return changed
    
    @classmethod
    def deepClone(cls, obj: dict) -> dict:
        if obj is None:
            return None
        try:
            return deepcopy(obj)
        except Exception:
            print("[WARNING!] The object is uncopyable!")
            return obj
        
    @classmethod
    def compareObjects(cls, objA, objB):
        if objA is objB:
            return True

        if type(objA) != type(objB):
            return False

        if isinstance(objA, (int, float, str, bool, type(None))):
            return objA == objB

        if isinstance(objA, (list, tuple, set)):
            return len(objA) == len(objB) and all(cls.compareObjects(a, b) for a, b in zip(objA, objB))

        if isinstance(objA, dict):
            if objA.keys() != objB.keys():
                return False
            return all(cls.compareObjects(objA[k], objB[k]) for k in objA)

        try:
            return objA == objB
        except Exception:
            pass

        if hasattr(objA, "__dict__") and hasattr(objB, "__dict__"):
            return cls.compareObjects(objA.__dict__, objB.__dict__)

        return False

    
class SoundService:
    _initialized = False
    _supported = (".wav", ".mp3")

    sounds = {}

    music_volume = 1.0
    sfx_volume = 1.0

    @classmethod
    def init(cls):
        if cls._initialized:
            return

        pygame.mixer.init()
        cls._initialized = True

    @classmethod
    def loadSound(cls, name: str, path: str):
        cls.init()

        sound = pygame.mixer.Sound(path)
        sound.set_volume(cls.sfx_volume)
        cls.sounds[name] = sound

    @classmethod
    def loadFolder(cls, path: str):
        cls.init()

        for root, _, files in os.walk(path):
            for file in files:
                if file.lower().endswith(cls._supported):

                    full_path = os.path.join(root, file)
                    relative = os.path.relpath(full_path, path)

                    name = os.path.splitext(relative)[0].replace("\\", "/")

                    cls.loadSound(name, full_path)

    @classmethod
    def playSound(cls, name: str):
        if name in cls.sounds:
            cls.sounds[name].play()

    @classmethod
    def stopSound(cls, name: str):
        if name in cls.sounds:
            cls.sounds[name].stop()

    @classmethod
    def isPlaying(cls, name: str) -> bool:
        if name not in cls.sounds:
            return False

        return cls.sounds[name].get_num_channels() > 0

    @classmethod
    def playMusic(cls, path: str, loop=True):
        cls.init()

        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(cls.music_volume)
        pygame.mixer.music.play(-1 if loop else 0)

    @classmethod
    def stopMusic(cls):
        pygame.mixer.music.stop()

    @classmethod
    def isMusicPlaying(cls) -> bool:
        return pygame.mixer.music.get_busy()

    @classmethod
    def setMusicVolume(cls, volume: float):
        cls.music_volume = volume
        pygame.mixer.music.set_volume(volume)

    @classmethod
    def setSoundsVolume(cls, volume: float):
        cls.sfx_volume = volume

        for sound in cls.sounds.values():
            sound.set_volume(volume)