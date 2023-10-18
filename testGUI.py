from test import *
import wx
import pyabf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.widgets import SpanSelector
from tkinter.ttk import OptionMenu
from matplotlib.backend_bases import PickEvent
from matplotlib.lines import Line2D
import threading
import csv
import numpy as np
from scipy import signal
import pickle 

def EphysApp():
    app = wx.App(False)
    frame = wx.Frame(None, wx.ID_ANY, "Ephys Analysis Tool")
    panel = wx.Panel(frame)

    def on_closing(event):
        frame.Close()
        frame.Destroy()

    frame.Bind(wx.EVT_CLOSE, on_closing)

    file_names = []
    segments = []
    peaks = []
    traces = []
    FileMan = FileManager(file_names, segments, peaks, traces)

    # Create a menu bar
    menubar = wx.MenuBar()

    # Create a "File" menu
    file_menu = wx.Menu()
    
    # Add "Open" option to the "File" menu
    open_item = file_menu.Append(wx.ID_OPEN, "&Open", "Open a file")
    frame.Bind(wx.EVT_MENU, FileMan.add_files, open_item)

    # Add "Save" option to the "File" menu
    save_item = file_menu.Append(wx.ID_SAVE, "&Save", "Save the current file")
    frame.Bind(wx.EVT_MENU, FileMan.save_table, save_item)

    # Add "Exit" option to the "File" menu
    exit_item = file_menu.Append(wx.ID_EXIT, "E&xit", "Exit the application")
    frame.Bind(wx.EVT_MENU, on_closing, exit_item)

    # Add the "File" menu to the menu bar
    menubar.Append(file_menu, "&File")

    frame.SetMenuBar(menubar)

    # Create a figure
    fig, ax = plt.subplots(facecolor="gainsboro")
    fig.tight_layout()

    canvas = FigureCanvas(panel, -1, fig)
    canvas_sizer = wx.BoxSizer(wx.VERTICAL)
    canvas_sizer.Add(canvas, 1, wx.EXPAND | wx.ALL)
    panel.SetSizerAndFit(canvas_sizer)

    # Create a navigation toolbar
    toolbar = NavigationToolbar2Wx(canvas)
    canvas_sizer.Add(toolbar, 0, wx.EXPAND)
    
    # Add the dropdown menu of file list
    current_file_menu_var = wx.ComboBox(panel, choices=file_names, style=wx.CB_READONLY)
    current_file_menu_var.Bind(wx.EVT_COMBOBOX, FileMan.update_dropdown_menu)

    # Create buttons
    add_files_button = wx.Button(panel, label='Add Files')
    previous_button = wx.Button(panel, label='Previous')
    next_button = wx.Button(panel, label='Next')
    filter_button = wx.Button(panel, label='Filter')
    toggle_segmentation_button = wx.Button(panel, label='Enable Segmentation')
    burst_button = wx.Button(panel, label='Mark Burst')
    discard_button = wx.Button(panel, label='Mark Discard')
    toggle_peaks_button = wx.Button(panel, label= 'Enable Peak Selection')
    save_button = wx.Button(panel, label='Save Table')
    save_segments_button = wx.Button(panel, label='Save Segments')
    load_segments_button = wx.Button(panel, label='Load Segments')
    save_data_button = wx.Button(panel, label='Save Trace Data')
    load_data_button = wx.Button(panel, label='Load Trace Data')

    # Bind buttons to their respective functions
    add_files_button.Bind(wx.EVT_BUTTON, FileMan.add_files)
    previous_button.Bind(wx.EVT_BUTTON, FileMan.previous_file)
    next_button.Bind(wx.EVT_BUTTON, FileMan.next_file)
    filter_button.Bind(wx.EVT_BUTTON, FileMan.filter_trace)
    toggle_segmentation_button.Bind(wx.EVT_BUTTON, FileMan.toggle_segmentation)
    burst_button.Bind(wx.EVT_BUTTON, FileMan.mark_as_burst)
    discard_button.Bind(wx.EVT_BUTTON, FileMan.mark_as_discard)
    toggle_peaks_button.Bind(wx.EVT_BUTTON, FileMan.toggle_peaks)
    save_button.Bind(wx.EVT_BUTTON, FileMan.save_table)
    save_segments_button.Bind(wx.EVT_BUTTON, FileMan.save_segments)
    load_segments_button.Bind(wx.EVT_BUTTON, FileMan.load_segments)
    save_data_button.Bind(wx.EVT_BUTTON, FileMan.save_traces)
    load_data_button.Bind(wx.EVT_BUTTON, FileMan.load_traces)

    # Create a button sizer
    button_sizer = wx.BoxSizer(wx.HORIZONTAL)
    button_sizer.Add(add_files_button, 0, wx.ALL, 5)
    button_sizer.Add(previous_button, 0, wx.ALL, 5)
    button_sizer.Add(next_button, 0, wx.ALL, 5)
    button_sizer.Add(filter_button, 0, wx.ALL, 5)
    button_sizer.Add(toggle_segmentation_button, 0, wx.ALL, 5)
    button_sizer.Add(burst_button, 0, wx.ALL, 5)
    button_sizer.Add(discard_button, 0, wx.ALL, 5)
    button_sizer.Add(save_button, 0, wx.ALL, 5)
    button_sizer.Add(save_segments_button, 0, wx.ALL, 5)
    button_sizer.Add(load_segments_button, 0, wx.ALL, 5)
    button_sizer.Add(save_data_button, 0, wx.ALL, 5)
    button_sizer.Add(load_data_button, 0, wx.ALL, 5)

    # Create a main sizer
    main_sizer = wx.BoxSizer(wx.VERTICAL)
    main_sizer.Add(current_file_menu_var, 0, wx.EXPAND | wx.ALL, 5)
    main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 5)
    main_sizer.Add(panel, 1, wx.EXPAND)
    
    frame.SetSizer(main_sizer)
    frame.Show(True)
    app.MainLoop()

EphysApp()