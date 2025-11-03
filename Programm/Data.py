import json

with open("Programm/Data/Dictionary.json", "r", encoding="utf-8") as dFile:
    Dictionary = json.load(dFile)
with open("Programm/Data/userSettings.json", "r", encoding="utf-8") as usFile:
    userSettings = json.load(usFile)

language = userSettings.get("language", "eng")

Data = {
    "WidgetsData": {
        "Blots": {
            "Key": "Blots",
            "Name": Dictionary[language]["widgetNames"]["Blots"],
            "Type": "Visual",
            "Icon": "Programm/Resources/Images/Icons/InkBlotsIcon.png",
            "Description": Dictionary[language]["widgetDescriptions"]["Blots"],
            "ScriptPath": "Programm/Widgets/Blots.py",
        },
        "ClipboardHistory": {
            "Key": "ClipboardHistory",
            "Name": Dictionary[language]["widgetNames"]["ClipboardHistory"],
            "Type": "Util",
            "Icon": "Programm/Resources/Images/Icons/ClipboardHistoryIcon.png",
            "Description": Dictionary[language]["widgetDescriptions"]["ClipboardHistory"],
            "ScriptPath": "Programm/Widgets/ClipboardHistory.py",
        },
        "Clock": {
            "Key": "Clock",
            "Name": Dictionary[language]["widgetNames"]["Clock"],
            "Type": "Visual",
            "Icon": "Programm/Resources/Images/Icons/ClockIcon.png",
            "Description": Dictionary[language]["widgetDescriptions"]["Clock"],
            "ScriptPath": "Programm/Widgets/Clock.py",
        },
        "ConcentrationMode": {
            "Key": "ConcentrationMode",
            "Name": Dictionary[language]["widgetNames"]["ConcentrationMode"],
            "Type": "Interactable",
            "Icon": "Programm/Resources/Images/Icons/ConcentrationModeIcon.png",
            "Description": Dictionary[language]["widgetDescriptions"]["ConcentrationMode"],
            "ScriptPath": "Programm/Widgets/ConcentrationMode.py",
        },
        "Notepad": {
            "Key": "Notepad",
            "Name": Dictionary[language]["widgetNames"]["Notepad"],
            "Type": "Util",
            "Icon": "Programm/Resources/Images/Icons/NotepadIcon.png",
            "Description": Dictionary[language]["widgetDescriptions"]["Notepad"],
            "ScriptPath": "Programm/Widgets/Notepad.py",
        },
        "ScreenFire": {
            "Key": "ScreenFire",
            "Name": Dictionary[language]["widgetNames"]["ScreenFire"],
            "Type": "Visual",
            "Icon": "Programm/Resources/Images/Icons/ScreenFire.png",
            "Description": Dictionary[language]["widgetDescriptions"]["ScreenFire"],
            "ScriptPath": "Programm/Widgets/ScreenFire.py",
        },
        "SoundManager": {
            "Key": "SoundManager",
            "Name": Dictionary[language]["widgetNames"]["SoundManager"],
            "Type": "Util",
            "Icon": "Programm/Resources/Images/Icons/SoundManagerIcon.png",
            "Description": Dictionary[language]["widgetDescriptions"]["SoundManager"],
            "ScriptPath": "Programm/Widgets/SoundManager.py",
        }
    }
}

def InitializeData(language = userSettings.get("language", "eng")):
    global Data
    
    for widgetKey, widgetData in Data["WidgetsData"].items():
        widgetData["Name"] = Dictionary[language]["widgetNames"][widgetKey]
        widgetData["Description"] = Dictionary[language]["widgetDescriptions"][widgetKey]

    return Data