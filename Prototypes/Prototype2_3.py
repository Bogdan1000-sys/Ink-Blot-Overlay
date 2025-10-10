import dearpygui.dearpygui as dpg
import tkinter as tk
from math import floor
import threading

dpg.create_context()

# Variables
is_dragging = False

# Attributes
mainColor = (255, 106, 0)
passiveColor = (255, 106, 0, 150)

root = tk.Tk()
root.withdraw()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

screen_multiplier = 0.6

sw = 1000 #floor(screen_width * screen_multiplier)
sh = 600 #floor(screen_height * screen_multiplier)

spX = (screen_width // 2) - (sw // 2)
spY = (screen_height // 2) - (sh // 2) - 30

vp_title = "Ink Blot Overlay"

with dpg.font_registry():
    mainButtonFont = dpg.add_font("Resources/Fonts/Segoe UI.ttf", 25, tag = "mainFont")

iWidth, iHeight, iChannels, iData = dpg.load_image("Resources/Images/Ink Blot Icon.png")
with dpg.texture_registry(show=False):
    icon_texture_id = dpg.add_static_texture(iWidth, iHeight, iData, tag="icon_texture")
    
with dpg.window(label=vp_title+" Main Window", no_close = True, no_scroll_with_mouse=True, no_scrollbar=True, horizontal_scrollbar=False) as mainWindow:
    icon_size = 25
    dpg.add_image("icon_texture", width=icon_size, height=icon_size, pos=[icon_size*0.1, icon_size*0.1])
    dpg.add_button(label="X", width=icon_size, height=icon_size, pos=[sw-(icon_size*1.1)+1, icon_size*0.1], callback=lambda: dpg.stop_dearpygui())
    dpg.add_button(label="_", width=icon_size, height=icon_size, pos=[sw-icon_size*2.2, icon_size*0.1], callback=lambda: dpg.minimize_viewport())
    dpg.add_text("Ink Blot Overlay", pos=[(icon_size*1.25), icon_size*0.3], color=mainColor)
    
    dpg.add_text("Hold Alt to drag", pos=[sw - 120, sh - 27], color=passiveColor, tag="dragInfo")
    
    
with dpg.theme() as global_theme:   
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, mainColor, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (163, 68, 0), category=dpg.mvThemeCat_Core)

dpg.bind_theme(global_theme)

with dpg.theme() as mainWindow_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (0, 0, 0, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Border, mainColor, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 10, category=dpg.mvThemeCat_Core)

dpg.bind_item_theme(mainWindow, mainWindow_theme)

dpg.create_viewport(title=vp_title+" Root", width=sw, height=sh, x_pos=spX, y_pos=spY, decorated=False, always_on_top=True, disable_close = True)
dpg.set_primary_window(mainWindow, True)

dpg.setup_dearpygui()
dpg.show_viewport()

def DraggingThread():
    global is_dragging

    def on_mouse_drag(sender, app_data):
        global is_dragging
        try:
            dx = app_data[1]
            dy = app_data[2]
        except Exception:
            return

        if not (dpg.is_key_down(dpg.mvKey_LAlt) or dpg.is_key_down(dpg.mvKey_RAlt)):
            return
        
        if not is_dragging:
            is_dragging = True
            #print(">>> Drag started")

        vp = dpg.get_viewport_pos()
        dpg.set_viewport_pos([int(vp[0] + dx), int(vp[1] + dy)])

    def on_mouse_release(sender, app_data):
        global is_dragging
        if is_dragging:
            #print("<<< Drag ended")
            is_dragging = False

    with dpg.handler_registry():
        dpg.add_mouse_drag_handler(button=dpg.mvMouseButton_Left, callback=on_mouse_drag)
        dpg.add_mouse_release_handler(button=dpg.mvMouseButton_Left, callback=on_mouse_release)

        dpg.add_key_down_handler(key=dpg.mvKey_LAlt, callback=lambda s,a,u: dpg.configure_item("dragInfo", color=mainColor))
        dpg.add_key_down_handler(key=dpg.mvKey_RAlt, callback=lambda s,a,u: dpg.configure_item("dragInfo", color=mainColor))
        dpg.add_key_release_handler(key=dpg.mvKey_LAlt, callback=lambda s,a,u: dpg.configure_item("dragInfo", color=passiveColor))
        dpg.add_key_release_handler(key=dpg.mvKey_RAlt, callback=lambda s,a,u: dpg.configure_item("dragInfo", color=passiveColor))

threading.Thread(target=DraggingThread, daemon=True).start()

dpg.start_dearpygui()
dpg.destroy_context()