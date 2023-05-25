# Trace segmentation tool

Python-based segmentation tool for analyzing electrophysiology recordings. It allows to load ABF files, visualize the data, and manually mark segments of interest. The tool provides options to mark segments as bursts or discard and save the segment information in a CSV file.

## Installation 

1. clone the repository to your local machine: 
 ```
 git clone https://github.com/ramonitzzz/EphysAnalysis.git
```
2. create virtual environment
```
conda create ephysAnalysis
conda activate ephysAnalysis
```
3. install required packages 
```
pip install -r ephys_req.txt
```
4. make sure to be in the project directory and to have the virtual environment activated before running the code
```
python3 SegmentTraces.py
```


## Usage
The tool will open a graphical user interface (GUI) window.
Use the GUI to navigate through the ABF files, visualize the data, and manually mark segments of interest.
Use the buttons in the GUI to mark segments as bursts or discard, save the segment information in a CSV file, or load previously saved segments.



### License
This project is licensed under the MIT License.

