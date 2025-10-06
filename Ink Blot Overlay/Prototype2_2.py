import dearpygui.dearpygui as dpg
import tkinter as tk
from math import floor

dpg.create_context()

root = tk.Tk()
root.withdraw()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

screen_multiplier = 0.6

sw = floor(screen_width * screen_multiplier)
sh = floor(screen_height * screen_multiplier)

spX = (screen_width // 2) - (sw // 2)
spY = (screen_height // 2) - (sh // 2) - 30

vp_title = "LeilLayerOverlay"

with dpg.window(label=vp_title+" Main Window", no_close = True) as mainWindow:
    dpg.add_text("Hello, world")
    dpg.add_button(label="Save")
    dpg.add_input_text(label="string", default_value="Quick brown fox")
    dpg.add_slider_float(label="float", default_value=0.273, max_value=1)

dpg.create_viewport(title=vp_title+" Root", width=sw, height=sh, x_pos=spX, y_pos=spY, decorated=False, always_on_top=True, disable_close = True)
dpg.set_primary_window(mainWindow, True)

dpg.setup_dearpygui()
dpg.show_viewport()

def on_mouse_drag(sender, app_data):
    try:
        dx = app_data[1]
        dy = app_data[2]
    except Exception:
        return

    if not (dpg.is_key_down(dpg.mvKey_LAlt) or dpg.is_key_down(dpg.mvKey_RAlt)):
        return

    vp = dpg.get_viewport_pos()
    dpg.set_viewport_pos([int(vp[0] + dx), int(vp[1] + dy)])

with dpg.handler_registry():
    dpg.add_mouse_drag_handler(button=dpg.mvMouseButton_Left, callback=on_mouse_drag)

def on_Close():
    pass

dpg.set_exit_callback(on_Close)

dpg.start_dearpygui()
dpg.destroy_context()