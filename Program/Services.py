from PyQt6.QtCore import QObject, pyqtSignal
import threading, pygame, os

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

class SoundService:
    _instance = None
    _supported = (".wav", ".mp3")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return

        pygame.mixer.init()

        self.sounds = {}
        self.music_volume = 1.0
        self.sfx_volume = 1.0

        self._initialized = True

    def loadSound(self, name: str, path: str):
        sound = pygame.mixer.Sound(path)
        sound.set_volume(self.sfx_volume)
        self.sounds[name] = sound

    def loadFolder(self, path: str):
        for root, _, files in os.walk(path):
            for file in files:
                if file.lower().endswith(self._supported):
                    full_path = os.path.join(root, file)
                    name = os.path.splitext(file)[0]
                    relative = os.path.relpath(full_path, path)
                    name = os.path.splitext(relative)[0].replace("\\", "/")
                    self.loadSound(name, full_path)

    def playSound(self, name: str):
        if name in self.sounds:
            self.sounds[name].play()

    def stopSound(self, name: str):
        if name in self.sounds:
            self.sounds[name].stop()

    def playMusic(self, path: str, loop=True):
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(self.music_volume)
        pygame.mixer.music.play(-1 if loop else 0)

    def stopMusic(self):
        pygame.mixer.music.stop()

    def setMusicVolume(self, volume: float):
        self.music_volume = volume
        pygame.mixer.music.set_volume(volume)

    def setSoundsVolume(self, volume: float):
        self.sfx_volume = volume
        for sound in self.sounds.values():
            sound.set_volume(volume)