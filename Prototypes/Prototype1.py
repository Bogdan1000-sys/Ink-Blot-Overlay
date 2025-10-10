import tkinter as tk
from tkinter import ttk
from math import floor
from keyboard import add_hotkey
from threading import Thread
from time import sleep

MainRoot = None
TkThread = None
    
def create_root():
    root = tk.Tk()
    root.title("VeilLayer Overlay")
    root.attributes("-topmost", True)
    root.resizable(False, False)
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    window_width = floor(screen_width * 0.6)
    window_height = floor(screen_height * 0.6)

    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2) - 50
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    root.mainloop()


def change_window_state():
    global MainRoot, TkThread
    if MainRoot is None:
        def start_tk():
            global MainRoot
            MainRoot = tk.Tk()
            MainRoot.title("VeilLayer Overlay")
            MainRoot.attributes("-topmost", True)
            MainRoot.resizable(False, False)

            MainRoot.update_idletasks()
            sw = MainRoot.winfo_screenwidth()
            sh = MainRoot.winfo_screenheight()
            ww = floor(sw * 0.6)
            wh = floor(sh * 0.6)
            x = (sw // 2) - (ww // 2)
            y = (sh // 2) - (wh // 2) - 50
            MainRoot.geometry(f"{ww}x{wh}+{x}+{y}")

            MainRoot.mainloop()
            MainRoot = None

        TkThread = Thread(target=start_tk, daemon=True)
        TkThread.start()
    else:
        MainRoot.after(0, MainRoot.destroy)


add_hotkey("ctrl+alt+\\", change_window_state)

while True:
    sleep(1)