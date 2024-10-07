import time
import ctypes
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import winsound  


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def get_pen_coordinates():
    movements = []
    start_time = time.time()
    duration = 50

    print("Calibrating... Move the pen for 30 seconds.")
    
    while time.time() - start_time < duration:
        pt = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        x, y = pt.x, pt.y
        movements.append((x, y))
        time.sleep(0.01)  

    winsound.Beep(440, 1000)  
    return movements


def calculate_optimal_area(movements):
    min_x = min(point[0] for point in movements)
    max_x = max(point[0] for point in movements)
    min_y = min(point[1] for point in movements)
    max_y = max(point[1] for point in movements)
    
    return (min_x, min_y, max_x, max_y)


def pixels_to_mm(pixels_x, pixels_y, screen_width_px, screen_height_px, tablet_width_mm, tablet_height_mm):
    mm_per_px_x = tablet_width_mm / screen_width_px
    mm_per_px_y = tablet_height_mm / screen_height_px

    mm_x = pixels_x * mm_per_px_x
    mm_y = pixels_y * mm_per_px_y
    
    return mm_x, mm_y


def set_area_in_mm(x1, y1, x2, y2, screen_width_px, screen_height_px, tablet_width_mm, tablet_height_mm):
    x1_mm, y1_mm = pixels_to_mm(x1, y1, screen_width_px, screen_height_px, tablet_width_mm, tablet_height_mm)
    x2_mm, y2_mm = pixels_to_mm(x2, y2, screen_width_px, screen_height_px, tablet_width_mm, tablet_height_mm)

    area_tablet = (tablet_width_mm * tablet_height_mm)  
    area_playfield = (x2_mm - x1_mm) * (y2_mm - y1_mm)  
    unused_area = area_tablet - area_playfield

    result = (
        f"Detected tablet area in millimeters (min-max coordinates):\n"
        f"Width: {x1_mm:.2f} mm, Height: {y1_mm:.2f} mm, "
    )
    messagebox.showinfo("Results", result)


def start_calibration():
    try:
        screen_width_px = int(screen_width_entry.get())
        screen_height_px = int(screen_height_entry.get())

        if tablet_size_combobox.get() == "Custom":
            tablet_width_mm = float(tablet_width_entry.get())
            tablet_height_mm = float(tablet_height_entry.get())
        else:

            tablet_size = tablet_size_combobox.get()
            tablet_width_mm, tablet_height_mm = tablet_sizes[tablet_size]

        movements = get_pen_coordinates()
        x1, y1, x2, y2 = calculate_optimal_area(movements)

        set_area_in_mm(x1, y1, x2, y2, screen_width_px, screen_height_px, tablet_width_mm, tablet_height_mm)

    except ValueError:
        messagebox.showerror("Error", "Please enter valid values.")


def on_tablet_size_change(event):
    selected_size = tablet_size_combobox.get()
    if selected_size == "Custom":
 
        tablet_width_entry.config(state=tk.NORMAL)
        tablet_height_entry.config(state=tk.NORMAL)
        tablet_width_entry.delete(0, tk.END)
        tablet_height_entry.delete(0, tk.END)
    else:

        tablet_width_mm, tablet_height_mm = tablet_sizes[selected_size]
        tablet_width_entry.config(state=tk.DISABLED)
        tablet_height_entry.config(state=tk.DISABLED)
        tablet_width_entry.delete(0, tk.END)
        tablet_width_entry.insert(0, tablet_width_mm)
        tablet_height_entry.delete(0, tk.END)
        tablet_height_entry.insert(0, tablet_height_mm)


def start_countdown():
    countdown_label.config(text="10")
    countdown(10)


def countdown(count):
    if count > 0:
        countdown_label.config(text=str(count))
        root.after(1000, countdown, count - 1)
    else:
        countdown_label.config(text="Calibrating :D")
        winsound.Beep(440, 1000)  
        start_calibration()  #


def show_how_to_use():
    messagebox.showinfo("How to Use", "1. Set the screen size (pixels).\n"
                                        "2. Select your tablet or enter custom dimensions in mm.\n"
                                        "3. Click 'Start Calibration' to begin.\n"
                                        "4. You can now change the window to the game you will hear a sound after the countdown\n"
                                        "5. Play a map with Auto mod on\n"
                                        "6. Move the pen as instructed for 30 seconds.\n")






root = tk.Tk()
root.title("Graphics Tablet Calibration")


tablet_sizes = {
    "Wacom Intuos Pro": (320, 200),
    "Huion H610 Pro": (280, 175),
    "XP-Pen Deco 01": (260, 160),
    "Huion H420/420": (102, 57),
    "Wacom CTH-680": (216, 135),
    "Wacom CTL-472": (152, 95),
    "Custom": (0, 0),  
}





#################Menu bar###################
menubar = tk.Menu(root)
language_menu = tk.Menu(menubar, tearoff=0)

language_menu.add_command(label="How to Use", command=show_how_to_use)
menubar.add_cascade(label="Options", menu=language_menu)
root.config(menu=menubar)

tk.Label(root, text="Screen Size (px):").grid(row=0, column=0)
tk.Label(root, text="Width:").grid(row=1, column=0)
screen_width_entry = tk.Entry(root)
screen_width_entry.insert(0, "1920")  # Default width
screen_width_entry.grid(row=1, column=1)
tk.Label(root, text="Height:").grid(row=2, column=0)
screen_height_entry = tk.Entry(root)
screen_height_entry.insert(0, "1080")  # Default height
screen_height_entry.grid(row=2, column=1)

tk.Label(root, text="Tablet Size:").grid(row=3, column=0)
tablet_size_combobox = ttk.Combobox(root, values=list(tablet_sizes.keys()))
tablet_size_combobox.set("Select an option")
tablet_size_combobox.grid(row=3, column=1)
tablet_size_combobox.bind("<<ComboboxSelected>>", on_tablet_size_change)


tk.Label(root, text="Width (mm):").grid(row=4, column=0)
tablet_width_entry = tk.Entry(root, state=tk.DISABLED)  
tablet_width_entry.grid(row=4, column=1)
tk.Label(root, text="Height (mm):").grid(row=5, column=0)
tablet_height_entry = tk.Entry(root, state=tk.DISABLED)  
tablet_height_entry.grid(row=5, column=1)

start_button = tk.Button(root, text="Start Calibration", command=start_countdown)
start_button.grid(row=6, columnspan=2)


countdown_label = tk.Label(root, text="", font=("Helvetica", 24))
countdown_label.grid(row=7, columnspan=2)

root.mainloop()
