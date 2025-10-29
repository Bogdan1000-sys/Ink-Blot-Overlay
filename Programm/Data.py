from Dictionary import LDictionary

def InitializeData(language: str):
    if language == None:
        language = "eng"

    return {
        "WidgetsData": {
            "Blots": {
                "Name": LDictionary[language]["widgetNames"]["Blots"],
                "Type": "Interactable",
                "Icon": "Programm/Resources/Images/Icons/InkBlotsIcon.png",
                "Description": LDictionary[language]["widgetDescriptions"]["Blots"],
                "ScriptPath": "Programm/Widgets/Blots.py",
            },
            "ClipboardHistory": {
                "Name": LDictionary[language]["widgetNames"]["ClipboardHistory"],
                "Type": "Util",
                "Icon": "Programm/Resources/Images/Icons/ClipboardHistoryIcon.png",
                "Description": LDictionary[language]["widgetDescriptions"]["ClipboardHistory"],
                "ScriptPath": "Programm/Widgets/ClipboardHistory.py",
            },
            "Clock": {
                "Name": LDictionary[language]["widgetNames"]["Clock"],
                "Type": "Visual",
                "Icon": "Programm/Resources/Images/Icons/ClockIcon.png",
                "Description": LDictionary[language]["widgetDescriptions"]["Clock"],
                "ScriptPath": "Programm/Widgets/Clock.py",
            },
            "ConcentrationMode": {
                "Name": LDictionary[language]["widgetNames"]["ConcentrationMode"],
                "Type": "Interactable",
                "Icon": "Programm/Resources/Images/Icons/ConcentrationModeIcon.png",
                "Description": LDictionary[language]["widgetDescriptions"]["ConcentrationMode"],
                "ScriptPath": "Programm/Widgets/ConcentrationMode.py",
            },
            "Notepad": {
                "Name": LDictionary[language]["widgetNames"]["Notepad"],
                "Type": "Util",
                "Icon": "Programm/Resources/Images/Icons/NotepadIcon.png",
                "Description": LDictionary[language]["widgetDescriptions"]["Notepad"],
                "ScriptPath": "Programm/Widgets/Notepad.py",
            },
            "ScreenFire": {
                "Name": LDictionary[language]["widgetNames"]["ScreenFire"],
                "Type": "Visual",
                "Icon": "Programm/Resources/Images/Icons/ScreenFire.png",
                "Description": LDictionary[language]["widgetDescriptions"]["ScreenFire"],
                "ScriptPath": "Programm/Widgets/ScreenFire.py",
            },
            "SoundManager": {
                "Name": LDictionary[language]["widgetNames"]["SoundManager"],
                "Type": "Util",
                "Icon": "Programm/Resources/Images/Icons/SoundManagerIcon.png",
                "Description": LDictionary[language]["widgetDescriptions"]["SoundManager"],
                "ScriptPath": "Programm/Widgets/SoundManager.py",
            }
        }
    }
