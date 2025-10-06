# Main script based on Prototype V2

import sys
from time import sleep
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
icon = "Resources/Images/VeilLayer Overlay Icon V2.ico"

sw = floor(screen_width * screen_multiplier)
sh = floor(screen_height * screen_multiplier)

spX = (screen_width // 2) - (sw // 2)
spY = (screen_height // 2) - (sh // 2) - 30

vp_title = "VeilLayerOverlay__UNIQUE_TITLE_12345"
transparent_key = (255, 0, 255, 0)

with dpg.font_registry():
    mainButtonFont = dpg.add_font("Resources/Fonts/Segoe UI.ttf", 20, tag = "mainFont")

with dpg.window(label="VeilLayer Overlay", width=sw, height=sh, pos=(spX, spY), no_resize = True, no_scrollbar=True, no_title_bar=True) as mainWindow:
    baseButtonPadding = 5

    confirmButton = dpg.add_button(label="Confirm", width=150, height=30, pos=(baseButtonPadding, sh-30-baseButtonPadding), tag="confirmButton", callback=lambda: print("Confirmed"))
    exitButton = dpg.add_button(label="Exit", width=100, height=30, pos=(baseButtonPadding*2 + 150, sh-30-baseButtonPadding), tag="exitButton", callback=lambda: print("Exiting...") or dpg.stop_dearpygui() and sys.exit(0))
    
    with dpg.theme() as Button_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (150, 150, 150), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (120, 120, 120), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (100, 100, 100), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255), category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
            #dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)
            #dpg.add_theme_color(dpg.mvThemeCol_Border, (125, 125, 125), category=dpg.mvThemeCat_Core)

    dpg.bind_item_theme(confirmButton, Button_theme)
    dpg.bind_item_theme(exitButton, Button_theme)
    dpg.bind_font(mainButtonFont)

with dpg.theme() as mainWindow_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (200, 200, 200), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 10, category=dpg.mvThemeCat_Core)
        #dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 2, category=dpg.mvThemeCat_Core)
        #dpg.add_theme_color(dpg.mvThemeCol_Border, (255, 0, 245), category=dpg.mvThemeCat_Core)

dpg.bind_item_theme(mainWindow, mainWindow_theme)

dpg.create_viewport(title=vp_title, width=screen_width, height=screen_height, x_pos=0, y_pos=0, decorated=False, resizable=False, always_on_top=True, small_icon=icon, large_icon=icon)
dpg.set_viewport_clear_color(transparent_key)

dpg.setup_dearpygui()
dpg.show_viewport()

hwnd = None
for _ in range(100):
    hwnd = win32gui.FindWindow(None, vp_title)
    if hwnd:
        break
    sleep(0.01)

if not hwnd:
    print("Could not find viewport window, check the title.")
else:
    ex = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex | win32con.WS_EX_LAYERED)
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(255, 0, 255), 0, win32con.LWA_COLORKEY)

dpg.start_dearpygui()
dpg.destroy_context()
