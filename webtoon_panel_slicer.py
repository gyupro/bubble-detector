import cv2
import numpy as np
from PIL import Image
from glob import glob
from config import MIN_PANEL_HEIGHT

def is_blank_section(image_slice):
    """
    Checks if a given image slice is blank (either all white or all black).
    
    Parameters:
        image_slice: numpy array containing grayscale image data

    Returns:
        bool: True if slice is blank, False otherwise
    """
    return np.all(image_slice == 255) or np.all(image_slice == 0)

def slice_webtoon_into_color_panels(image_path):
    """
    Detects and slices a colored webtoon into individual panels based on blank sections.

    Parameters:
        image_path: str, path to the webtoon image

    Returns:
        list: A list of sliced colored panels (as numpy arrays)
    """
    color_image = cv2.imread(image_path)
    grayscale_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
    image_height, _ = grayscale_image.shape
    
    current_row = 0
    sliced_panels = []
    
    for i in range(1, image_height):
        row_pixels = grayscale_image[i, :]
        
        if is_blank_section(row_pixels):
            candidate_panel = color_image[current_row:i, :, :]
            candidate_panel_gray = grayscale_image[current_row:i, :]
            
            if not is_blank_section(candidate_panel_gray) and candidate_panel.shape[0] >= MIN_PANEL_HEIGHT:
                sliced_panels.append(candidate_panel)
            
            current_row = i + 1
            
    last_panel = color_image[current_row:, :, :]
    last_panel_gray = grayscale_image[current_row:, :]
    
    if not is_blank_section(last_panel_gray) and last_panel.shape[0] >= MIN_PANEL_HEIGHT:
        sliced_panels.append(last_panel)
    
    return sliced_panels

def slice_webtoon_into_panels(image_path):
    """
    Detects and slices a webtoon into individual panels based on blank sections.

    Parameters:
        image_path: str, path to the webtoon image

    Returns:
        list: A list of sliced panels (as numpy arrays)
    """
    grayscale_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    image_height, _ = grayscale_image.shape
    
    current_row = 0
    sliced_panels = []
    
    for i in range(1, image_height):
        row_pixels = grayscale_image[i, :]
        
        if is_blank_section(row_pixels):
            candidate_panel = grayscale_image[current_row:i, :]
            
            if not is_blank_section(candidate_panel) and candidate_panel.shape[0] >= MIN_PANEL_HEIGHT:
                sliced_panels.append(candidate_panel)
            
            current_row = i + 1
            
    last_panel = grayscale_image[current_row:, :]
    
    if not is_blank_section(last_panel) and last_panel.shape[0] >= MIN_PANEL_HEIGHT:
        sliced_panels.append(last_panel)
    
    return sliced_panels

# Example usage:
# color_panels = slice_webtoon_into_color_panels("path/to/your/color/image.jpg")
# for panel in color_panels:
#     display(Image.fromarray(cv2.cvtColor(panel, cv2.COLOR_BGR2RGB)))

# grayscale_panels = slice_webtoon_into_panels("path/to/your/grayscale/image.jpg")
# for panel in grayscale_panels:
#     display(Image.fromarray(panel, 'L'))
