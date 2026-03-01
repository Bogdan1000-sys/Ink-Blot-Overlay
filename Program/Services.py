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

    _initialized = False
    _supported = (".wav", ".mp3")

    sounds = {}

    music_volume = 1.0
    sfx_volume = 1.0

    # -------------------
    # Init
    # -------------------
    @classmethod
    def init(cls):
        if cls._initialized:
            return

        pygame.mixer.init()
        cls._initialized = True

    # -------------------
    # Load
    # -------------------
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

    # -------------------
    # Sound
    # -------------------
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

    # -------------------
    # Music
    # -------------------
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

    # -------------------
    # Volume
    # -------------------
    @classmethod
    def setMusicVolume(cls, volume: float):
        cls.music_volume = volume
        pygame.mixer.music.set_volume(volume)

    @classmethod
    def setSoundsVolume(cls, volume: float):
        cls.sfx_volume = volume

        for sound in cls.sounds.values():
            sound.set_volume(volume)