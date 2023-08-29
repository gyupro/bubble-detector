import cv2
import numpy as np
from PIL import Image
from IPython.display import display

from glob import glob

def detect_cut(image_path):
    # Read image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # Read in grayscale
    
    # Initializations
    height, width = image.shape
    start_row = 0
    panel_number = 0
    panels = []
    # Function to check if a slice is empty (all 255s or all 0s)
    def is_empty_slice(slice):
        return np.all(slice == 255) or np.all(slice == 0)
    
    # Iterate through rows
    for i in range(1, height):  # Start at 1 to avoid slicing from 0 to 0
        row = image[i, :]
    
        # Check if all values are 255 or 0
        if np.all(row == 255) or np.all(row == 0):
            
            # Slice the panel from start_row to i
            panel = image[start_row:i, :]
            
            # If the slice is not empty, save/display it
            if not is_empty_slice(panel):
                # display(Image.fromarray(panel))  # This is for Jupyter Notebook; replace with save function if needed
                panels.append(panel)
                panel_number += 1
    
            # Update start_row to the next row
            start_row = i + 1
    
    # Don't forget the last panel
    panel = image[start_row:, :]
    if not is_empty_slice(panel):
        # display(Image.fromarray(panel))  # This is for Jupyter Notebook; replace with save function if needed
        panels.append(panel)
        


