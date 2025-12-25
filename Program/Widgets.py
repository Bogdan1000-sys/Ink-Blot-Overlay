from WidgetsStorage.Clock.main import main as Clock

def Empty(connection):
    print("Empty Widget")

Widgets = {
    "Blots": Empty,
    "ClipboardHistory": Empty,
    "Clock": Clock,
    "ConcentrationMode": Empty,
    "Notepad": Empty,
    "ScreenFire": Empty,
    "SoundManager": Empty
}