from WidgetsStorage.Clock.main import main as Clock

from WidgetsStorage.GeneralSettings.main import main as GeneralSettings

def Empty(connection):
    print("Empty Widget")

Widgets = {
    "Blots": Empty,
    "ClipboardHistory": Empty,
    "Clock": Clock,
    "ConcentrationMode": Empty,
    "Notepad": Empty,
    "ScreenFire": Empty,
    "SoundManager": Empty,

    "GeneralSettings": GeneralSettings
}