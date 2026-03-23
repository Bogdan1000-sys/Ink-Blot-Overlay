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
        """Add tag to a QWidget"""
        widget_tags = widget.property("Tags") or set()
        widget_tags.add(tag)
        widget.setProperty("Tags", widget_tags)

        cls._registry.setdefault(tag, []).append(widget)

    @classmethod
    def removeTag(cls, widget, tag: str):
        """Remove tag from a QWidget"""
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
        """Get all tags of a QWidget"""
        return list(widget.property("Tags") or [])

    @classmethod
    def getTagged(cls, tag: str):
        """Get all QWidgets with a specific tag"""
        cls._registry[tag] = [
            w for w in cls._registry.get(tag, []) if w is not None
        ]
        return cls._registry.get(tag, [])

    @classmethod
    def getFirstTagged(cls, tag: str):
        """Get first found QWidget with a specific tag"""
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
        """Start signal listening"""
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
        """Stop signal listening"""
        self._running = False

class LocalizationService:
    __dictPath = "Data/Dictionary.json"
    __dictionary = None

    @classmethod
    def __init__(cls):
        with open(cls.__dictPath, "r", encoding="utf-8") as dFile:
            cls.__dictionary = json.load(dFile)
    
    @classmethod
    def registerAdaptableText(cls, obj: QLabel, key: str):
        """
        Register QLabel with localization adaptable content
        obj: QLabel
        key: path to content in dictionary
        """
        CollectionService.addTag(obj, "adaptableTextWidget")
        obj.setProperty("textKey", key)
        obj.setText(cls.getAdaptedTextFromDictionary(key))

    @classmethod
    def getAdaptedTextFromDictionary(cls, key: str):
        """
        Get adapted text from dictionary using key
        key: path to content in dictionary
        """
        keyParts = key.split("/")
        SettingsService.updateUserSettings()

        language = SettingsService.settings.get("General", {}).get("language", "eng")

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
        """
        Change content in all localization adaptable QLabels

        newLanguage: (eng | rus | kg) [1st layer chapter of dictionary]
        updateSettings: Change Language settings in userSettings.json to newLanguage?
        """
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
        if os.path.isfile(cls.__path):
            cls.settings = cls.getUserSettings()
        else:
            cls.settings = cls.initializeUserSettings()

    @classmethod
    def initializeUserSettings(cls):
        with open("Data/Settings/GeneralSettingsTemplate.json", "r", encoding="utf-8") as gtFile:
            generalTemplate = json.load(gtFile)
        with open("Data/Settings/WindowSettingsTemplate.json", "r", encoding="utf-8") as wtFile:
            windowsTemplate = json.load(wtFile)

        initializedUserSettings = {
            "General": generalTemplate,
            "Windows": windowsTemplate
        }

        with open(cls.__path, "w", encoding="utf-8") as userFile:
            json.dump(initializedUserSettings, userFile, indent=4, ensure_ascii=False)

        return initializedUserSettings

    @classmethod
    def updateUserSettings(cls):
        """Update SettingsService.settings to current version of userSettings.json"""
        cls.settings = cls.getUserSettings()

    @classmethod
    def getUserSettings(cls) -> dict:
        """Get dict of settings from userSettings.json"""
        with open(cls.__path, "r", encoding="utf-8") as usFile:
            return json.load(usFile)
        
    @classmethod
    def __setJSON(cls, settings: dict):
        with open(cls.__path, "w", encoding="utf-8") as usFile:
            json.dump(settings, usFile, ensure_ascii=False, indent=4)

    @classmethod
    def setUserSettings(cls, chapter: str, settings: dict):
        """Merge chosen chapter of userSettings.json with new settings"""
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
        """Append new settings to chosen chapter of userSettings.json"""
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

    @classmethod
    def __init__(cls):
        if cls._initialized:
            return

        pygame.mixer.init()
        cls._initialized = True

    @classmethod
    def loadSound(cls, name: str, path: str):
        """Load sound to cls.sounds as name from path"""
        sound = pygame.mixer.Sound(path)
        cls.sounds[name] = sound
        return sound

    @classmethod
    def loadFolder(cls, path: str):
        """Load sounds to cls.sounds from folder on path"""
        for root, _, files in os.walk(path):
            for file in files:
                if file.lower().endswith(cls._supported):

                    full_path = os.path.join(root, file)
                    relative = os.path.relpath(full_path, path)

                    name = os.path.splitext(relative)[0].replace("\\", "/")

                    cls.loadSound(name, full_path)

        return cls.sounds

    @classmethod
    def playSound(cls, name: str, parent=None):
        """Play sound from cls.sounds with name
        Parent changes volume using SettingsService"""
        if not name in cls.sounds: return

        sound = cls.sounds[name]

        settings = SettingsService.getUserSettings()
        volume = settings["General"]["volume"]

        if parent: volume = settings["General"]["volume"] * settings["Windows"].get(parent, {"volume": 1.0})["volume"]
        sound.set_volume(volume)
        sound.play()

    @classmethod
    def stopSound(cls, name: str):
        """Stop sounds with name from cls.sounds"""
        if name in cls.sounds:
            cls.sounds[name].stop()

    @classmethod
    def isPlaying(cls, name: str) -> bool:
        if name not in cls.sounds:
            return False

        return cls.sounds[name].get_num_channels() > 0

    @classmethod
    def playMusic(cls, path: str, loop=True):
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
    def setSoundVolume(cls, sound: str, volume: float):
        if cls.sounds.get(sound) == None: return
        cls.sounds[sound].set_volume(volume)

    @classmethod
    def setSoundsVolume(cls, volume: float):
        for sound in cls.sounds.values():
            sound.set_volume(volume)


class InitializationService:
    OrderedServices = [
        SettingsService,
        LocalizationService,
        SoundService,
        CollectionService,
        ObjectService
    ]

    @classmethod
    def __init__(cls):
        for Service in cls.OrderedServices:
            Service()