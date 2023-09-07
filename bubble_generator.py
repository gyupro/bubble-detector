from typing import List, Tuple
import random
import numpy as np
from glob import glob
from PIL import Image
import cv2
from labelme.label_file import LabelFile
from labelme import utils
import random
import os
import string
from PIL import Image, ImageDraw, ImageFont

def load_label_file(item: str):
    return LabelFile(item)

def load_image_from_label(label_file) -> np.ndarray:
    return utils.img_data_to_arr(label_file.imageData)

def create_label_map(label_file) -> dict:
    label_name_to_value = {"_background_": 0}
    for shape in sorted(label_file.shapes, key=lambda x: x["label"]):
        label_name = shape["label"]
        label_name_to_value.setdefault(label_name, len(label_name_to_value))
    return label_name_to_value

def get_image_with_mask(img, shapes, label_map) -> np.ndarray:
    img_shape = img.shape
    lbl, _ = utils.shapes_to_label(img_shape, shapes, label_map)
    mask = (lbl * 255).astype(np.uint8)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
    img[:,:,3] = mask
    return img

def random_rescale(img: np.ndarray) -> Tuple[np.ndarray, float]:
    random_scale = random.uniform(0.3, 1.0)
    new_dims = (int(img.shape[1] * random_scale), int(img.shape[0] * random_scale))
    return cv2.resize(img, new_dims), random_scale

def overlay(im1: np.ndarray, im2: np.ndarray, x: int, y: int) -> np.ndarray:
    overlay_region = im2[y:y+im1.shape[0], x:x+im1.shape[1]]
    alpha = im1[:, :, 3] / 255.0
    alpha = alpha[:, :, np.newaxis]
    overlay_region[:,:,:] = (1 - alpha) * overlay_region[:,:,:] + alpha * im1[:,:,:]
    overlay_region[:, :, 3] = 255
    return im2

def get_coordinates_in_yolo_format(shape, effective_scale, x_offset, y_offset, im2_shape) -> List[Tuple[float, float]]:
    if shape['label'] == 'bubble':
        original_points = shape['points']
        adjusted_points = [(int(pt[0] * effective_scale) + x_offset, int(pt[1] * effective_scale) + y_offset) for pt in original_points]
        im2_h, im2_w, _ = im2_shape
        return [(pt[0]/im2_w, pt[1]/im2_h) for pt in adjusted_points]
    return []

def yolo_to_pixel_coordinates(yolo_coordinates: List[Tuple[float, float]], image_shape: Tuple[int, int]) -> List[Tuple[int, int]]:
    im_h, im_w = image_shape
    pixel_coordinates = [(int(pt[0] * im_w), int(pt[1] * im_h)) for pt in yolo_coordinates]
    return pixel_coordinates
def draw_polygon_on_image(image: np.ndarray, pixel_coordinates: List[Tuple[int, int]], color: Tuple[int, int, int, int] = (0, 255, 0, 255)) -> np.ndarray:
    cv2.polylines(image, [np.array(pixel_coordinates)], isClosed=True, color=color, thickness=2)
    return image
def split_text_to_fit(draw, text, max_width, font):
    lines = []
    words = text.split()
    while words:
        line = ''
        while words and draw.textsize(line + words[0], font=font)[0] <= max_width:
            line += (words.pop(0) + ' ')
        lines.append(line)
    return lines


def get_bounding_rect(shape):
    points = np.array(shape['points'])
    min_x, min_y = np.min(points, axis=0)
    max_x, max_y = np.max(points, axis=0)
    return int(min_x), int(min_y), int(max_x), int(max_y)


def draw_text(draw, rect, im1_pil):
    font_size = random.randint(20, 32)
    font = ImageFont.truetype("SpoqaHanSansNeo-Light.ttf", font_size)

    # Generate random Korean text. Replace this with your random text generator
    random_text = random.choice(ko_to_en_dict['source'])

    # Get text size
    text_width, text_height = draw.textlength(random_text, font=font)

    # Check if the text fits within the bounding rectangle, adjust font size if necessary
    while text_width > rect[2]:
        font = ImageFont.truetype("SpoqaHanSansNeo-Light.ttf", font.size - 1)
        text_width, text_height = draw.textsize(random_text, font=font)
    text_width, text_height = draw.textsize(random_text, font=font)

    # Calculate text position within the bubble
    text_x = rect[0]
    text_y = rect[1]

    # Split the text into multiple lines
    lines = split_text_to_fit(draw, random_text, rect[2], font)
    for line in lines:
        draw.text((text_x, text_y), line, font=font, fill=(0, 0, 0, 255))
        text_y += text_height  # Move down for the next line

    # Convert the PIL image back to a NumPy array (OpenCV format)
    im1 = cv2.cvtColor(np.array(im1_pil), cv2.COLOR_RGBA2BGRA)
    return im1
def paste_im1_to_im2(im1 :str, im2 :np.ndarray) -> Tuple[np.ndarray, List, Tuple[int, int, int, int]]:
    label_file = load_label_file(im1)
    img = load_image_from_label(label_file)
    label_map = create_label_map(label_file)
    im1 = get_image_with_mask(img, label_file.shapes, label_map)

    # Convert the OpenCV image (NumPy array) to a PIL Image for im1
    im1_pil = Image.fromarray(cv2.cvtColor(im1, cv2.COLOR_BGRA2RGBA))

    # Initialize ImageDraw
    draw = ImageDraw.Draw(im1_pil)

    for shape in label_file.shapes:
        if shape['label'] == 'bubble':
            rect = get_bounding_rect(shape)
            # Define font size and font
            font_size = random.randint(20, 32)
            font = ImageFont.truetype("SpoqaHanSansNeo-Light.ttf", font_size)

            # Call draw_text
            im = draw_text(draw, rect, font)    # Define the rectangle where text should be drawn. This should be your bubble.
            display(Image.fromarray(im))
    # Convert the PIL image back to a NumPy array (OpenCV format)
    im1 = cv2.cvtColor(np.array(im1_pil), cv2.COLOR_RGBA2BGRA)
    
    im1, random_scale = random_rescale(im1)


    if im1.shape[0] > im2.shape[0] or im1.shape[1] > im2.shape[1]:
        additional_scale = min(im2.shape[0] / im1.shape[0], im2.shape[1] / im1.shape[1])
        new_dims = (int(im1.shape[1] * additional_scale), int(im1.shape[0] * additional_scale))
        im1 = cv2.resize(im1, new_dims)
        effective_scale = random_scale * additional_scale
    else:
        effective_scale = random_scale

    x = random.randint(0, im2.shape[1] - im1.shape[1])
    y = random.randint(0, im2.shape[0] - im1.shape[0])
    new_box = (x, y, x + im1.shape[1], y + im1.shape[0])  # This is the new bounding box
   
    im2 = overlay(im1, im2, x, y)
    yolo_coordinates = []
    for shape in label_file.shapes:
        yolo_coordinates.extend(get_coordinates_in_yolo_format(shape, effective_scale, x, y, im2.shape))
    return im2, yolo_coordinates, new_box
    

def generate_random_string(length=25):
    letters = string.ascii_uppercase
    return ''.join(random.choice(letters) for i in range(length))

def is_overlapping(new_box, existing_boxes):
    for box in existing_boxes:
        if (new_box[0] < box[2] and new_box[2] > box[0] and
            new_box[1] < box[3] and new_box[3] > box[1]):
            return True
    return False
