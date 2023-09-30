import pyabf
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
from tkinter import *
from tkinter import Tk, filedialog, StringVar, Button, Frame, Label
from matplotlib.widgets import SpanSelector
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from tkinter.ttk import OptionMenu
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backend_bases import PickEvent
from matplotlib.lines import Line2D
import threading
import csv
import numpy as np
from scipy import signal
import pickle 

   
def open_trace(file_name):
    abf = pyabf.ABF(file_name)
    return abf.sweepX, abf.sweepY

class Trace():
    def __init__(self, file_name):
        self.file_name = file_name
        #self.time, self.current = open_trace(file_name)
        self.abf = pyabf.ABF(self.file_name)
        self.time, self.current = self.abf.sweepX, self.abf.sweepY
        self.segments = []
        self.baseline = None
        self.peaks = []
        self.search_window = 100 #search window for setting peaks

    def add_segment(self, start_time, end_time, category):
        segment = Segment(self.file_name, start_time, end_time, category)
        self.segments.append(segment)
        return segment

    def calculate_baseline(self, window_size=10):
        kernel = np.ones(window_size) / window_size
        self.baseline = np.convolve(self.current, kernel, mode='same')

    def set_peak_position(self, peak):
        self.peaks.append(peak)

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data):
        return pickle.loads(data)


class Segment:
    def __init__(self, file_name, start_time, end_time, category):
        self.file_name = file_name
        self.start_time = start_time
        self.end_time = end_time
        self.duration = end_time - start_time
        self.category = category
    
    #def serialize(self):
        #return pickle.dumps(self)

    #@staticmethod
    #def deserialize(data):
        #return pickle.loads(data)
    
class Peak(Trace):
    def __init__(self, file_name):
        self.file_name = file_name
        self.peak_x = None
        self.peak_y = None
        super().__init__(file_name)
    
    def set_peak_position (self, x, y):
        self.peak_x = x
        self.peak_y =y


    def highest_point(self, x_clicked):
        index_clicked = np.argmin(np.abs(self.time - x_clicked))
        
        # Create a 1-second window surrounding the clicked point
        points_per_second = int(1000 * self.abf.dataPointsPerMs) #20 points per Ms given a sampling freq of 20 Hz
        start_index = max(0, index_clicked - self.search_window)
        end_index = min(len(self.time) - self.search_window, index_clicked + self.search_window)
        
        range_y = self.current[start_index:end_index] #change so that it uses plottedtrace
        max_index = np.argmax(abs(range_y))
        index_highest = start_index + max_index
        self.x_highest = self.time[index_highest]
        self.y_highest = self.current[index_highest]
        self.set_peak_position(self.x_highest, self.y_highest)

        #plot
        ax.plot(self.x_highest, self.y_highest, 'ro')
        fig.canvas.draw()

    def on_line_click(self, event):
        if isinstance(event, PickEvent):
            index = event.ind[0]
            x_clicked = self.time[index]
            y_clicked = self.current[index]
            self.highest_point(x_clicked)
        else:
            print('not instance')

    


class FileManager:
    def __init__(self, file_names, segments):
        self.file_names = file_names
        self.segments = segments
        self.current_file_index = 0
        self.current_file_name = ""
        self.current_segment = None
        self.peaks =[]
        self.window_size = 10
    
    def update_graph(self):
        self.current_file_name = self.file_names[self.current_file_index]
        ax.clear()
        self.time, self.current = open_trace(self.current_file_name)
        
        self.plottedtrace, = ax.plot(self.time, self.current, linewidth=0.5)
        self.plottedtrace.set_picker(1)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Current (pA)")
        
        # Load and plot segments for the current file, if available
        current_segments = self.get_segments_for_file(self.current_file_name)
        if current_segments:
            for segment in current_segments:
                color = 'green' if segment.category == 'burst' else 'red'
                span = ax.axvspan(segment.start_time, segment.end_time, color=color, alpha=0.3)
        
        canvas.draw()
      
    
    def filter_trace(self, event=None):
        def ButterBandStop(current):
            fs = 20000  # Sampling frequency (Hz)
            fstop = [600, 5000]

            # Design Butterworth filter
            b, a = signal.butter(2, fstop, btype='bandstop', analog=False, fs=fs)
            current_filtered = signal.filtfilt(b, a, current)

            return current, current_filtered

        # open current trace
        self.time, self.current = open_trace(self.current_file_name)
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        # Apply the Butterworth bandstop filter if it's not already applied
        if not filter_button.is_filtered:
            current, current_filtered = ButterBandStop(self.current)

            # Plot the filtered trace
            ax.clear()
            self.plottedtrace, = ax.plot(self.time, current_filtered, linewidth=0.5, color='black')
            self.plottedtrace.set_picker(1)
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Current (pA)")
            filter_button.is_filtered = True
            filter_button.config(text='Raw Trace')

        else:
            ax.clear()
            self.plottedtrace, = ax.plot(self.time, self.current, linewidth=0.5)
            self.plottedtrace.set_picker(1)
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Current (pA)")
            filter_button.is_filtered = False
            filter_button.config(text='Filter')

        # Restore the previous zoom settings
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        # Load and plot segments for the current file, if available
        current_segments = self.get_segments_for_file(self.current_file_name)
        if current_segments:
            for segment in current_segments:
                color = 'green' if segment.category == 'burst' else 'red'
                span = ax.axvspan(segment.start_time, segment.end_time, color=color, alpha=0.3)

        canvas.draw()
        #self.plottedtrace.draw()

    def add_files(self, event=None):
        #root.withdraw()
        new_files = filedialog.askopenfilenames(filetypes=[('ABF Files', '*.abf')])
        self.file_names.extend(new_files)
        print(f"Added files: {', '.join(new_files)}")
        if len(self.file_names) > 0:
            #self.update_graph()
            self.update_dropdown_menu()
    
    def next_file(self, event=None):
        self.current_file_index = (self.current_file_index + 1) % len(self.file_names)
        filter_button.is_filtered = False  # Reset the filtering state
        filter_button.config(text='Filter')
        #self.update_graph()
        self.update_dropdown_menu()
    
    def previous_file(self, event=None):
        self.current_file_index = (self.current_file_index - 1) % len(self.file_names)
        filter_button.is_filtered = False # Reset the filtering state
        filter_button.config(text='Filter')
        #self.update_graph()
        self.update_dropdown_menu()
    
    def save_table(self, event=None):
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
    
    def save_segments(self, event=None):
        if len(segments) == 0:
            print("No segments to save.")
            return

        filename = filedialog.asksaveasfilename(defaultextension='.pickle', filetypes=[('Pickle Files', '*.pickle')])
        if filename:
            with open(filename, 'wb') as file:
                pickle.dump(segments, file)
            print(f"Segments saved as {filename}")
   
    def get_segments_for_file(self, file_name):
        self.file_segments = []
        for segment in self.segments:
            if segment.file_name == file_name:
                self.file_segments.append(segment)
        return self.file_segments

    def load_segments(self, event=None):
        filename = filedialog.askopenfilename(filetypes=[('Pickle Files', '*.pickle')])
        if filename:
            with open(filename, 'rb') as file:
                loaded_segments = pickle.load(file)
            self.segments = loaded_segments
            print(f"Segments loaded from {filename}")

            self.update_graph()
    
    def update_dropdown_menu(self):
        file_menu["menu"].delete(0, "end")  # Clear the current menu options

        if len(self.file_names) > 0:
            for file_name in self.file_names:
                name= file_name.split("/")[-1].split(".")[0]
                #file_menu["menu"].add_command(label=file_name, command=lambda value=file_name: set_current_file(value))
                file_menu["menu"].add_command(label=name, command=lambda value=file_name: self.set_current_file(value))
            self.current_file_name = self.file_names[self.current_file_index]
            display_name = str(self.current_file_index) + ": " + self.current_file_name.split("/")[-1].split(".")[0]
            current_file_menu_var.set(display_name)
            self.update_graph()
        else:
            display_name = "No files added"
            current_file_menu_var.set(display_name)

    def set_current_file(self, value):
        self.current_file_name = str(value)
        selected_index = self.file_names.index(value)
        if selected_index != self.current_file_index:
            self.current_file_index = selected_index
            self.current_file_name= value
            display_name = str(self.current_file_index) + ": " + self.current_file_name.split("/")[-1].split(".")[0]
            current_file_menu_var.set(display_name)
            self.update_graph()

    def enable_zoom_and_scroll(self, canvas):
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

        def on_key_press(event):
            if event.key == '+':
                ax.set_xlim(ax.get_xlim()[0] * 1.005, ax.get_xlim()[1] * 0.995)
                canvas.draw_idle()
            elif event.key == '-':
                ax.set_xlim(ax.get_xlim()[0] * 0.995, ax.get_xlim()[1] * 1.005)
                canvas.draw_idle()
            elif event.key == '{':
                ax.set_ylim(ax.get_ylim()[0] * 1.05, ax.get_ylim()[1] * 0.95)
                canvas.draw_idle()
            elif event.key == '}':
                ax.set_ylim(ax.get_ylim()[0] * 0.95, ax.get_ylim()[1] * 1.05)
                canvas.draw_idle()
            elif event.key == 'z':
                ax.set_xlim(ax.get_xlim()[0], ax.get_xlim()[0] + 2)
                canvas.draw_idle()
            elif event.key == 'a':
                ax.set_xlim(ax.get_xlim()[0], ax.get_xlim()[0]+10)
                ax.set_ylim(-500, 50)
                canvas.draw_idle()
            elif event.key == 'f':
                ax.set_xlim(self.time[0], self.time[-1] - self.time[0])
                ax.set_ylim(-800, 50)
                canvas.draw_idle()

        def on_motion(event):
            if event.button == '2' and event.xdata and event.ydata:
                x_shift = event.xdata * 0.001
                y_shift = event.ydata * 0.001
                x_limits = ax.get_xlim()
                y_limits = ax.get_ylim()
                x_center = (x_limits[0] + x_limits[1]) / 2
                y_center = (y_limits[0] + y_limits[1]) / 2
                x_scale = (x_limits[1] - x_limits[0]) / 2
                y_scale = (y_limits[1] - y_limits[0]) / 2
                new_x_limits = [x_center - x_scale * 1.05, x_center + x_scale * 1.05]
                new_y_limits = [y_center - y_scale * 1.05, y_center + y_scale * 1.05]
                ax.set_xlim(new_x_limits[0] + x_shift, new_x_limits[1] + x_shift)
                ax.set_ylim(new_y_limits[0] + y_shift, new_y_limits[1] + y_shift)
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

    def onselect(self, xmin, xmax):
        if not segmentation_enabled:
            return

        self.current_segment = Segment(self.current_file_name, xmin, xmax, "not selected")
        span = ax.axvspan(xmin, xmax, color='grey', alpha=0.3)
        plt.draw()
    
    def mark_as_burst(self, event=None):
        self.current_segment.category = "burst"
        self.current_segment.color = 'green'
        span = ax.axvspan(self.current_segment.start_time, self.current_segment.end_time, color='green', alpha=0.3)
        plt.draw()
        self.segments.append(self.current_segment)  # Add current_segment to segments list
        print(f"Segment marked as 'burst': {self.current_segment.file_name}, {self.current_segment.start_time}s to {self.current_segment.end_time}s")
    
    def mark_as_discard(self, event=None):
        self.current_segment.category = "discard"
        self.current_segment.color = 'red'
        span = ax.axvspan(self.current_segment.start_time, self.current_segment.end_time, color='red', alpha=0.3)
        plt.draw()
        self.segments.append(self.current_segment)  # Add current_segment to segments list
        print(f"Segment marked as 'discard': {self.current_segment.file_name}, {self.current_segment.start_time}s to {self.current_segment.end_time}s")

    def edit_segment(self, segment):
        # Open a dialog box to edit the start and end time of the segment
        edit_window = Tk()
        edit_window.title("Edit Segment")
        
        start_time_label = Label(edit_window, text="Start Time (s):")
        start_time_label.pack()
        start_time_entry = Entry(edit_window)
        start_time_entry.insert(END, str(segment.start_time))
        start_time_entry.pack()

        end_time_label = Label(edit_window, text="End Time (s):")
        end_time_label.pack()
        end_time_entry = Entry(edit_window)
        end_time_entry.insert(END, str(segment.end_time))
        end_time_entry.pack()

        def save_changes():
            new_start_time = float(start_time_entry.get())
            new_end_time = float(end_time_entry.get())
            segment.start_time = new_start_time
            segment.end_time = new_end_time
            segment.duration = new_end_time - new_start_time
            self.filter_trace()
            plt.draw()
            edit_window.destroy()
            edit_window.quit()
        
        save_button = Button(edit_window, text="Save", command=save_changes)
        save_button.pack()
        
        edit_window.mainloop()
    
    def delete_segment(self, segment):
        self.segments.remove(segment)
        self.filter_trace()
        plt.draw()

    def toggle_segmentation(self):
        global segmentation_enabled
        segmentation_enabled = not segmentation_enabled

        if segmentation_enabled:
            toggle_segmentation_button.config(text='Disable Segmentation')
        else:
            toggle_segmentation_button.config(text='Enable Segmentation')
    
    def on_double_click(self, event):
        if event.button == 1 and event.dblclick:  # Left button (double-click)
            for segment in self.segments:
                if segment.start_time <= event.xdata <= segment.end_time:
                    self.edit_segment(segment)
                    break
    
    def on_right_click(self, event):
        if event.button == 3:  # Right button (click)
            for segment in self.segments:
                if segment.start_time <= event.xdata <= segment.end_time:
                    self.delete_segment(segment)
                    break

    def setPeak(self, event):
        self.current_peak = Peak(self.current_file_name)
        self.current_peak.on_line_click(event)
        self.peaks.append(self.current_peak)

        for peak in self.peaks:
            ax.plot(peak.peak_x, peak.peak_y, 'ro')
            fig.canvas.draw()

        

def EphysApp():
    global canvas, ax, fig,  filter_button, segmentation_enabled, segments, toggle_segmentation_button, file_menu, current_file_menu_var, root
    root= Tk()
    root.title("Ephys Analysis Tool")
    file_names = []
    segments= []
    #current_file_index = 0
    #current_file_name = ""
    FileMan= FileManager(file_names, segments)
    
    def on_closing():
        root.quit()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Add figure canvas
    fig, ax = plt.subplots(facecolor="gainsboro")
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side='bottom', fill='both', expand=True)

    # Add toolbar
    toolbar_frame = Frame(root)
    toolbar_frame.pack(side='top', fill='x')
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    canvas.get_tk_widget().pack(side='bottom', fill='both', expand=True)

    # Add dropdown menu of file list
    current_file_menu_var = StringVar(root)
    
    file_menu = OptionMenu(root, current_file_menu_var, *file_names)
    file_menu.pack(side="top", anchor='nw')

    # Call the update_dropdown_menu function
    FileMan.update_dropdown_menu()

    # Load files
    add_files_button = Button(master=root, command= FileMan.add_files, text='Add Files')
    add_files_button.pack(side="left")

    # Add functionality to switch files
    previous_button = Button(master=root, command= FileMan.previous_file, text='Previous')
    previous_button.pack(side="left")

    next_button = Button(master=root, command= FileMan.next_file, text='Next')
    next_button.pack(side="left")

    span_selector = SpanSelector(ax, FileMan.onselect, 'horizontal', useblit=True)

    # Add the Filter button to the toolbar
    filter_button = Button(master=root, command= FileMan.filter_trace, text='Filter')
    filter_button.pack(side="left")
    filter_button.is_filtered = False

    # Enable and disable segmentation

    segmentation_enabled = False
    toggle_segmentation_button = Button(master=root, command=FileMan.toggle_segmentation, text='Enable Segmentation')
    toggle_segmentation_button.pack(side="left")

    # Mark events as bursts or discard
    burst_button = Button(master=root, command=FileMan.mark_as_burst, text='Mark Burst')
    burst_button.pack(side="left")

    discard_button = Button(master=root, command=FileMan.mark_as_discard, text='Mark Discard')
    discard_button.pack(side="left")

    # Export table
    save_button = Button(master=root, command=FileMan.save_table, text='Save Table')
    save_button.pack(side="left")

    # save and load segments
    Button(root, text="Save Segments", command=FileMan.save_segments).pack(side="left", padx=5, pady=5)
    Button(root, text="Load Segments", command=FileMan.load_segments).pack(side="left", padx=5, pady=5)

    button_frame = Frame(root)
    button_frame.pack(side='top', fill='x')
    
    FileMan.enable_zoom_and_scroll(canvas)
    
    #calculatebase = Button(master=root, command= FileMan.calculate_baseline, text='Calculate Baseline')
    #calculatebase.pack(side="left")

    canvas.mpl_connect('button_press_event', FileMan.on_double_click)
    canvas.mpl_connect('button_press_event', FileMan.on_right_click)
    canvas.mpl_connect('pick_event', lambda event: FileMan.setPeak(event))

    root.mainloop()

EphysApp()