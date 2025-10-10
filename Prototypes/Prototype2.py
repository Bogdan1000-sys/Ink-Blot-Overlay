import sys
import time
import dearpygui.dearpygui as dpg
import tkinter as tk
from math import floor

if sys.platform != "win32":
    raise RuntimeError("Error: win32 required")

import win32con, win32gui, win32api

dpg.create_context()

root = tk.Tk()
root.withdraw()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

screen_multiplier = 0.6
icon = "Resources/Images/LeilLayer Overlay Icon V2.ico"

sw = floor(screen_width * screen_multiplier)
sh = floor(screen_height * screen_multiplier)

spX = (screen_width // 2) - (sw // 2)
spY = (screen_height // 2) - (sh // 2) - 30

vp_title = "LeilLayerOverlay__UNIQUE_TITLE_12345"
transparent_key = (255, 0, 255, 0)

with dpg.window(label="Example Window", width=sw, height=sh, pos=(spX, spY), no_resize = True) as mainWindow:
    dpg.add_text("Hello, world")
    dpg.add_button(label="Save")
    dpg.add_input_text(label="string", default_value="Quick brown fox")
    dpg.add_slider_float(label="float", default_value=0.273, max_value=1)

#with dpg.theme() as mainWindow_theme:
 #   with dpg.theme_component(dpg.mvAll):
  #      dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (100, 100, 100, 255), category=dpg.mvThemeCat_Core)

#dpg.bind_item_theme(mainWindow, mainWindow_theme)

dpg.create_viewport(title=vp_title, width=screen_width, height=screen_height, x_pos=0, y_pos=0, decorated=False, resizable=False, always_on_top=True, small_icon=icon, large_icon=icon)
dpg.set_viewport_clear_color(transparent_key)

dpg.setup_dearpygui()
dpg.show_viewport()

hwnd = None
for _ in range(100):
    hwnd = win32gui.FindWindow(None, vp_title)
    if hwnd:
        break
    time.sleep(0.01)

if not hwnd:
    print("Could not find viewport window, check the title.")
else:
    ex = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex | win32con.WS_EX_LAYERED)
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(255, 0, 255), 0, win32con.LWA_COLORKEY)

dpg.start_dearpygui()
dpg.destroy_context()
