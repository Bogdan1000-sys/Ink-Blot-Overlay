from appJar import gui
import tkinter as tk
from keyboard import add_hotkey
from math import floor

root = tk.Tk()
root.withdraw()
SCREEN_WIDTH = root.winfo_screenwidth()
SCREEN_HEIGHT = root.winfo_screenheight()
root.destroy()

ww = floor(SCREEN_WIDTH * 0.6)
wh = floor(SCREEN_HEIGHT * 0.6)
x = (SCREEN_WIDTH // 2) - (ww // 2)
y = (SCREEN_HEIGHT // 2) - (wh // 2) - 100

MainApp = gui("VeilLayer Overlay", f"{ww}x{wh}+{x}+{y}", False, None, None, False, False, False)
MainApp.transparency = 0.85
MainApp.setResizable(False)
MainApp.setOnTop(True)
MainApp.topLevel.iconbitmap("Resources/Images/LeilLayer Overlay Icon V2.ico")
MainApp.config(bg="#adadad")

#MainApp.addMenuList("‎", ["‎"], None)
MainApp.appJarAbout = lambda: None
MainApp.appJarHelp = lambda: None

def on_close():
    MainApp.hide()
MainApp.topLevel.protocol("WM_DELETE_WINDOW", on_close)

MainApp.hide()

def toggle_window():
    if MainApp.topLevel.state() == "withdrawn":
        MainApp.show()
    else:
        MainApp.hide()

add_hotkey("ctrl+alt+\\", toggle_window)

MainApp.go()
