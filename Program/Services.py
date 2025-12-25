from PyQt6.QtCore import QObject, pyqtSignal
import threading

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
                msg = self.connection.recv()
                if not msg:
                    break
                self.messageReceived.emit(msg)
            except Exception as e:
                print("Listener error:", e)
                break

    def stop(self):
        self._running = False