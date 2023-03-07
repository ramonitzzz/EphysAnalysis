import os
import sys
import pyabf
import numpy as np
import matplotlib.pyplot as plt
from PySide2 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
#from mplwidget import MplWidget
from matplotlib.figure import Figure

plt.style.use('dark_background')
class MplWidget(FigureCanvas):
    def __init__(self, parent=None):
        #super(MplWidget, self).__init__(self.figure)
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        super(MplWidget, self).__init__(self.figure)
        #self.toolbar = NavigationToolbar(self.canvas, self)
        #layout = QtWidgets.QVBoxLayout(self)
        #layout.addWidget(self.toolbar)
        #layout.addWidget(self.canvas)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Ephys GUI")
        self.setGeometry(100, 100, 1200, 600)

        # Set background color
        self.setStyleSheet("background-color: #636363;")
    

         # Create widgets
        self.file_combo = QtWidgets.QComboBox()
        self.plot_button = QtWidgets.QPushButton("Plot")
        self.add_button = QtWidgets.QPushButton("Add Files")
        self.calculate_button = QtWidgets.QPushButton("Calculate Cm and Rm")

        # Set button styles
        self.plot_button.setStyleSheet("""
            background-color: #434758;
            color: white;
            border: none;
            padding: 6px;
            border-radius: 2px;
        """)

        self.add_button.setStyleSheet("""
            background-color: #434758;
            color: white;
            border: none;
            padding: 6px;
            border-radius: 2px;
        """)

        # Set dropdown style
        self.file_combo.setStyleSheet("""
            background-color: white;
            color: #434758;
            padding: 6px;
            border: none;
            border-radius: 2px;
        """)
        
        # Create layout and add widgets
        central_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(self.file_combo, stretch=8)
        top_layout.addWidget(self.add_button, stretch=1)
        top_layout.addWidget(self.plot_button, stretch=1)
        layout.addLayout(top_layout)
        # Create matplotlib canvas
        #self.figure = plt.figure(facecolor="none")
        self.canvas = MplWidget() #****
        layout.addWidget(self.canvas)

        #add button to calculate Cm and Rm
        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(self.calculate_button)
        bottom_layout.addStretch(1)
        layout.addLayout(bottom_layout)


        # Set layout
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


        # Add navigation toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)


        # Connect signals
        self.plot_button.clicked.connect(self.plot_file)
        self.file_combo.currentIndexChanged.connect(self.update_file)
        self.add_button.clicked.connect(self.add_files)
        self.calculate_button.clicked.connect(self.calculate_capacitance_resistance)

        # Load .abf files
        self.file_list = []
        for file_name in os.listdir():
            if file_name.endswith(".abf"):
                self.file_list.append(file_name)
        self.file_combo.addItems(self.file_list)

        # Set default file
        if self.file_list:
            self.current_file = self.file_list[0]
        else:
            self.current_file = None

    def update_file(self, index):
        selected_file = self.file_combo.currentText()
        self.current_file = selected_file
        self.update_plot()

    def plot_file(self):
        self.update_plot()

    def add_files(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setNameFilter("ABF files (*.abf)")
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        if file_dialog.exec_():
            files = file_dialog.selectedFiles()
            for file_name in files:
                if file_name not in self.file_list:
                    self.file_list.append(file_name)
                    self.file_combo.addItem(file_name)
    
    def update_plot(self):
        if self.current_file is None:
            return
        abf = pyabf.ABF(self.current_file)
        data = abf.data
        time = abf.sweepX
        self.canvas.figure.clf()
        ax = self.canvas.figure.subplots()
        ax.plot(time, data[0,:], linewidth= 0.3, color="red")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Current (pA)")
        ax.format_coord = lambda x, y: f"x={x:.2f}, y={y:.2f}"
        self.canvas.figure.tight_layout()
        self.canvas.draw()
    

    def calculate_capacitance_resistance(self):
        if self.current_file is None:
            return
        abf = pyabf.ABF(self.current_file)


        # parameters
        start_time=0.5
        end_time=5
        holding_potential= abf.holdingCommand[1]
        pulse_amplitude= 10
        
        # calculate capacitance and resistance for each sweep

        voltage = abf.sweepC
        current = abf.sweepY
        sampling_rate = abf.dataRate
        start_index = int(start_time * sampling_rate)
        end_index = int(end_time * sampling_rate)
        voltage = voltage[start_index:end_index]
        current = current[start_index:end_index]
        voltage = voltage - np.mean(voltage[:100])  # subtract initial offset
        current = current - np.mean(current[:100])  # subtract initial offset

        if pulse_amplitude == 0:
            pulse_amplitude = np.max(voltage) - np.min(voltage)

        # Calculate the resistance of the cell
        steady_state_start = 0  # start time of steady-state period in s
        steady_state_end = 10  # end time of steady-state period in s

        steady_state_start_index = int(steady_state_start * abf.dataRate)
        steady_state_end_index = int(steady_state_end * abf.dataRate)
        current_mean = np.mean(current[steady_state_start_index:steady_state_end_index])

        resistance = (holding_potential - np.mean(voltage)) / current_mean
        #resistance= holding_potential/current_mean
        capacitance = -1 / (sampling_rate * pulse_amplitude) * np.trapz(voltage, dx=1/sampling_rate)
        
        # Display the results in a message box
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle("Capacitance and Resistance")
        msg_box.setText(f"Capacitance: {capacitance:.2f} pF\nResistance: {resistance:.2f} MOhm")
        msg_box.exec_()



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
