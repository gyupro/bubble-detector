import cv2
import numpy as np
from PIL import Image
from IPython.display import display

from glob import glob

def is_blank_section(image_slice):
    """
    Checks if a given image slice is blank (either all white or all black).
    
    Parameters:
        image_slice: numpy array containing grayscale image data

    Returns:
        bool: True if slice is blank, False otherwise
    """
    return np.all(image_slice == 255) or np.all(image_slice == 0)


def slice_webtoon_into_panels(image_path):
    """
    Detects and slices a webtoon into individual panels based on blank sections.

    Parameters:
        image_path: str, path to the webtoon image

    Returns:
        list: A list of sliced panels (as numpy arrays)
    """
    # Read image in grayscale
    grayscale_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Get image dimensions
    image_height, image_width = grayscale_image.shape
    
    # Initialize variables
    current_row = 0
    panel_count = 0
    sliced_panels = []
    
    # Iterate through rows to find blank sections
    for i in range(1, image_height):
        row_pixels = grayscale_image[i, :]
        
        if is_blank_section(row_pixels):
            candidate_panel = grayscale_image[current_row:i, :]
            
            if not is_blank_section(candidate_panel):
                sliced_panels.append(candidate_panel)
                panel_count += 1

            # Move to the next row after the blank section
            current_row = i + 1
            
    # Handle the last panel
    last_panel = grayscale_image[current_row:, :]
    if not is_blank_section(last_panel):
        sliced_panels.append(last_panel)
    
    return sliced_panels

# Example usage:
# panels = slice_webtoon_into_panels("path/to/your/image.jpg")
# for panel in panels:
#     display(Image.fromarray(panel))
