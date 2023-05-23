import pyabf
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
#plt.style.use("ggplot")
from tkinter import Tk, filedialog, StringVar, Button, Frame
from matplotlib.widgets import SpanSelector
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from tkinter.ttk import OptionMenu
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import csv
import numpy as np
from scipy import signal


class Segment:
    def __init__(self, file_name, start_time, end_time, category):
        self.file_name = file_name
        self.start_time = start_time
        self.end_time = end_time
        self.duration = end_time - start_time
        self.category = category
        self.events = []

segments = []
current_file_index = 0
file_names = []
current_file_name = ""

def onselect(xmin, xmax):
    global current_segment, segmentation_enabled
    if not segmentation_enabled:
        return

    current_segment = Segment(current_file_name, xmin, xmax, "not selected")
    span = ax.axvspan(xmin, xmax, color='red', alpha=0.5)
    plt.draw()

def toggle_segmentation():
    global segmentation_enabled, toggle_segmentation_button

    segmentation_enabled = not segmentation_enabled

    if segmentation_enabled:
        toggle_segmentation_button.config(text='Disable Segmentation')
    else:
        toggle_segmentation_button.config(text='Enable Segmentation')

def mark_as_burst(event=None):
    global current_segment
    current_segment.category = "burst"
    current_segment.color = 'green'
    span = ax.axvspan(current_segment.start_time, current_segment.end_time, color='green', alpha=0.3)
    plt.draw()
    segments.append(current_segment)  # Add current_segment to segments list
    print(f"Segment marked as 'burst': {current_segment.file_name}, {current_segment.start_time}s to {current_segment.end_time}s")

def mark_as_discard(event=None):
    global current_segment
    current_segment.category = "discard"
    current_segment.color = 'grey'
    span = ax.axvspan(current_segment.start_time, current_segment.end_time, color='grey', alpha=0.3)
    plt.draw()
    segments.append(current_segment)  # Add current_segment to segments list
    print(f"Segment marked as 'discard': {current_segment.file_name}, {current_segment.start_time}s to {current_segment.end_time}s")

def save_table(event=None):
    global segments
    if len(segments) == 0:
        print("No segments to save.")
        return

    filename = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV Files', '*.csv')])
    if filename:
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["File Name", "Start Time", "End Time", "Duration", "Category", "Events"])
            for segment in segments:
                writer.writerow([segment.file_name, segment.start_time, segment.end_time, segment.duration, segment.category, segment.events])
        print(f"Table saved as {filename}")

def add_files(event=None):
    global file_names
    #root.withdraw()
    new_files = filedialog.askopenfilenames()
    file_names.extend(new_files)
    print(f"Added files: {', '.join(new_files)}")
    if len(file_names) > 0:
        update_graph()
        update_dropdown_menu()

def ButterBandStop(current):
    fs = 20000  # Sampling frequency (Hz)
    fstop = [600, 5000]

    # Design Butterworth filter
    b, a = signal.butter(2, fstop, btype='bandstop', analog=False, fs=fs)
    current_filtered = signal.filtfilt(b, a, current)

    return current, current_filtered

def filter_trace(event=None):
    global current_file_name, abf, ax, canvas, filter_button

    abf = pyabf.ABF(current_file_name)

    # Get the current trace data
    current_trace = abf.sweepY

    # Apply the Butterworth bandstop filter if it's not already applied
    if not filter_button.is_filtered:
        current, current_filtered = ButterBandStop(current_trace)

        # Plot the filtered trace
        ax.clear()
        ax.plot(abf.sweepX, current_filtered, linewidth=0.5, color= "black")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Current (pA)")
        filter_button.is_filtered = True
        filter_button.config(text='Unfilter')

    else:
        ax.clear()
        ax.plot(abf.sweepX, abf.sweepY, linewidth=0.5)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Current (pA)")
        filter_button.is_filtered = False
        filter_button.config(text='Filter')

    canvas.draw()

def next_file(event=None):
    global current_file_index
    current_file_index = (current_file_index + 1) % len(file_names)
    filter_button.is_filtered = False  # Reset the filtering state
    update_graph()
    update_dropdown_menu()

def previous_file(event=None):
    global current_file_index
    current_file_index = (current_file_index - 1) % len(file_names)
    update_graph()
    update_dropdown_menu()

def update_graph():
    global current_file_name, abf
    current_file_name = file_names[current_file_index]
    ax.clear()
    abf = pyabf.ABF(current_file_name)
    ax.plot(abf.sweepX, abf.sweepY, linewidth=0.5)
    #ax.set_title(current_file_name)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Current (pA)")
    canvas.draw()

def update_dropdown_menu():
    global file_menu, file_names, current_file_index, current_file_name, current_file_menu_var
    
    file_menu["menu"].delete(0, "end")  # Clear the current menu options

    if len(file_names) > 0:
        for file_name in file_names:
            file_menu["menu"].add_command(label=file_name, command=lambda value=file_name: set_current_file(value))
        current_file_name = file_names[current_file_index]
        update_graph()
        display_name = current_file_name.split("/")[-1].split(".")[0]
    else:
        display_name = "No files added"
    
    current_file_menu_var.set(display_name)

def set_current_file(value):
    global current_file_name
    current_file_name.set(value)
    selected_index = file_names.index(value)
    if selected_index != current_file_index:
        current_file_index = selected_index
        update_graph()

def enable_zoom_and_scroll(canvas):
    def on_scroll(event):
        if event.button == 'down':
            direction = 1  # Scroll Up (Move Right)
        elif event.button == 'up':
            direction = -1  # Scroll Down (Move Left)
        else:
            direction = 0  # No scroll

        x_length = ax.get_xlim()[1] - ax.get_xlim()[0]
        x_shift = x_length * 0.1 * direction

        ax.set_xlim(ax.get_xlim()[0] + x_shift, ax.get_xlim()[1] + x_shift)
        canvas.draw_idle()

    def on_motion(event):
        if event.button == '2' and event.xdata and event.ydata:
            ax.set_xlim(ax.get_xlim()[0] - event.xdata * 0.001, ax.get_xlim()[1] - event.xdata * 0.001)
            ax.set_ylim(ax.get_ylim()[0] + event.ydata * 0.001, ax.get_ylim()[1] + event.ydata * 0.001)
            canvas.draw_idle()

    def on_key_press(event):
        if event.key == '+':
            ax.set_xlim(ax.get_xlim()[0] * 1.05, ax.get_xlim()[1] * 0.95)
            canvas.draw_idle()
        elif event.key == '-':
            ax.set_xlim(ax.get_xlim()[0] * 0.95, ax.get_xlim()[1] * 1.05)
            canvas.draw_idle()
        elif event.key == '{':
            ax.set_ylim(ax.get_ylim()[0] * 1.05, ax.get_ylim()[1] * 0.95)
            canvas.draw_idle()
        elif event.key == '}':
            ax.set_ylim(ax.get_ylim()[0] * 0.95, ax.get_ylim()[1] * 1.05)
            canvas.draw_idle()

    def toggle_zoom_and_scroll():
        if zoom_scroll_button.config('text')[-1] == 'Disable Zoom/Scroll':
            zoom_scroll_button.config(text='Enable Zoom/Scroll')
            canvas.mpl_disconnect(scroll_cid)
            canvas.mpl_disconnect(motion_cid)
            canvas.mpl_disconnect(key_press_cid)
        else:
            zoom_scroll_button.config(text='Disable Zoom/Scroll')
            scroll_cid = canvas.mpl_connect('scroll_event', on_scroll)
            motion_cid = canvas.mpl_connect('motion_notify_event', on_motion)
            key_press_cid = canvas.mpl_connect('key_press_event', on_key_press)

    zoom_scroll_button = Button(master=root, text='Disable Zoom/Scroll', command=toggle_zoom_and_scroll)
    zoom_scroll_button.pack()

    scroll_cid = canvas.mpl_connect('scroll_event', on_scroll)
    motion_cid = canvas.mpl_connect('motion_notify_event', on_motion)
    key_press_cid = canvas.mpl_connect('key_press_event', on_key_press)


def plot_abf_files():
    global current_file_index, current_file_name, segments, fig, ax, canvas, file_menu, root, current_file_menu_var, filter_button, segmentation_enabled, toggle_segmentation_button
    root = Tk()
    root.title("Segment Traces")
    current_file_index = 0
    segments = []

    def on_closing():
        root.quit()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    fig, ax = plt.subplots(facecolor="gainsboro")

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side='bottom', fill='both', expand=True)

    # Add toolbar
    toolbar_frame = Frame(root)
    toolbar_frame.pack(side='top', fill='x')
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    canvas.get_tk_widget().pack(side='bottom', fill='both', expand=True)

    # Load files
    add_files_button = Button(master=root, command=add_files, text='Add Files')
    add_files_button.pack(side="left")

    #Add functionality to switch files
    previous_button = Button(master=root, command=previous_file, text='Previous')
    previous_button.pack(side="left")

    next_button = Button(master=root, command=next_file, text='Next')
    next_button.pack(side="left")

    span_selector = SpanSelector(ax, onselect, 'horizontal', useblit=True)

    
    # Add the Filter button to the toolbar
    filter_button = Button(master=root, command=filter_trace, text='Filter')
    filter_button.pack(side="left")
    filter_button.is_filtered = False

    # Enable and disable segmentation
    segmentation_enabled = False
    toggle_segmentation_button = Button(master=root, command=toggle_segmentation, text='Enable Segmentation')
    toggle_segmentation_button.pack(side="left")

    # Mark events as bursts or discard
    burst_button = Button(master=root, command=mark_as_burst, text='Mark Burst')
    burst_button.pack(side="left")

    discard_button = Button(master=root, command=mark_as_discard, text='Mark Discard')
    discard_button.pack(side="left")

    # Export table
    save_button = Button(master=root, command=save_table, text='Save Table')
    save_button.pack(side="left")

    # Add dropdown menu of file list
    current_file_name = StringVar(root)

    current_file_menu_var = StringVar(root)
    current_file_menu_var.set(current_file_name)

    if len(file_names) > 0:
        current_file_name.set(file_names[current_file_index])
    else:
        current_file_name.set("No files added")
    
    file_menu_frame = Frame(root)
    file_menu_frame.pack(side='top', fill='x')
    file_menu = OptionMenu(root, current_file_menu_var, *file_names)
    file_menu.pack(side="top")

    # Call the update_dropdown_menu function
    update_dropdown_menu()

    button_frame = Frame(root)
    button_frame.pack(side='top', fill='x')
    
    enable_zoom_and_scroll(canvas)

    root.mainloop()

plot_abf_files()
