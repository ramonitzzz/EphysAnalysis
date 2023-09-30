import pyabf
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
from tkinter import Tk, filedialog, StringVar, Button, Frame
from matplotlib.widgets import SpanSelector
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from tkinter.ttk import OptionMenu
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import csv
import numpy as np
from scipy import signal
import pickle 

class Peak:
    def __init__(self, file_name):
        self.file_name = file_name
    
    def setPeak(self, event):
        self.event = event
        x, y = self.event.xdata, self.event.ydata
        if x is not None and y is not None:
            ax.plot(x, y, 'ro')  # Draw a red dot at the clicked point
            canvas.draw()
root= Tk()

def on_closing():
        root.quit()
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

fig, ax = plt.subplots(facecolor="gainsboro")

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side='bottom', fill='both', expand=True)

# Create an instance of the Peak class
peak_instance = Peak("xd")

canvas.mpl_connect('button_press_event', peak_instance.setPeak)

root.mainloop()


############
import pyabf
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
from tkinter import Tk, filedialog, StringVar, Button, Frame
from matplotlib.widgets import SpanSelector
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from tkinter.ttk import OptionMenu
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import csv
import numpy as np
from scipy import signal
import pickle 

def update_graph():
     global file_name, abf
     abf = pyabf.ABF(file_name)
     ax.plot(abf.sweepX, abf.sweepY, linewidth=0.5)
     ax.set_xlabel("Time (s)")
     ax.set_ylabel("Current (pA)")


class Peak:
    def __init__(self, file_name):
        self.file_name = file_name
        # List to store the added dots
        self.dots = []

    
    def setPeak(self, event):
        self.event = event
        x, y = self.event.xdata, self.event.ydata
        if event.inaxes is None:
             return
        
        distance = np.sqrt((abf.sweepX - x)**2 + (abf.sweepY - y)**2)
        min_distance = np.min(distance)

        # Define a threshold for clicking on the line
        threshold = 1

        if min_distance < threshold:
            dot = [x, y]
            self.dots.append(dot)
            #plt.legend()
            ax.plot(x,y, "ro")  # Draw a red dot at the clicked point
            canvas.draw()


        
root= Tk()

def on_closing():
        root.quit()
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

file_name= "/Users/romina/Downloads/230321_rai235_W5_S002_cs03_c02_0000.abf"


fig, ax = plt.subplots(facecolor="gainsboro")

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side='bottom', fill='both', expand=True)
update_graph()

# Create an instance of the Peak class
peak_instance = Peak(file_name)

canvas.mpl_connect('button_press_event', peak_instance.setPeak)

root.mainloop()

####
        #distance = np.sqrt((self.time - x)**2 + (self.current - y)**2)
        #min_distance = np.min(distance)
        #min_distance_idx = np.argmin(distance)
        #min_distance = distance[min_distance_idx]

if min_distance < threshold:
            # Set the peak at the highest point of the peak
            peak_x = self.time[min_distance_idx]
            peak_y = self.current[min_distance_idx]
            
            self.current_peak.set_peak_position(peak_x, peak_y)  # Update the peak position
            self.peaks.append(self.current_peak)
            
            # Redraw the peak at the highest point
            ax.plot(peak_x, peak_y, "ro")
            canvas.draw()