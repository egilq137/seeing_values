from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np
import matplotlib.pyplot as plt
import requests
from io import BytesIO
from enum import IntEnum
from dataclasses import dataclass

class Zone(IntEnum):
    O = 0
    I = 1
    II = 2
    III = 3
    IV = 4
    V = 5
    VI = 6
    VII = 7
    VIII = 8
    IX = 9
    X = 10

    @classmethod
    def limits(cls) -> dict['Zone', tuple[int, int]]:
        """ Returns the limits of each zone as a dictionary where the keys are
        the zones and the values are tuples of (lower_limit, upper_limit)"""
        n = len(cls)
        step = ReferenceValue.White / (n - 1)
        half = step / 2
        result = {z: (round(i * step - half), round(i * step + half)) 
                  for i, z in enumerate(cls)}
        
        # adjust limits for zone 0 (black) and zone X (white), because they 
        # don't have a full step on one side
        result[cls.O] = (ReferenceValue.Black, result[cls.O][1])
        result[cls.X] = (result[cls.X][0], ReferenceValue.White)
        
        return result

class ReferenceValue(IntEnum):
    Black = 0
    MiddleGray = 128
    White = 255


class PixelValue(int):
    """ Subclass of int such that they can be treated the same with 
    ReferenceValue"""
    def __new__(cls, value):
        if not ReferenceValue.Black <= value <= ReferenceValue.White:
            raise ValueError(
                f"Pixel value should be between {ReferenceValue.Black} \
                    and {ReferenceValue.White}")
        return super().__new__(cls, value)


def loads_image(filepath: Path) -> Image:
    return Image.open(filepath)


def open_image_from_url(url: str) -> Image:
    response = requests.get(url)
    return Image.open(BytesIO(response.content))


def is_grayscale(image: Image) -> bool:
    return image.mode == 'L'


def convert_to_grayscale(image: Image) -> Image:
    if is_grayscale(image):
        return image
    return image.convert('L')


def get_pixels(image: Image) -> list[PixelValue]:
    return list(image.get_flattened_data())

def apply_median_filter(image: Image, size: int = 7) -> Image:
    return image.filter(ImageFilter.MedianFilter(size=size))


def calculate_brightness(value: float) -> float:
    MAX_VALUE = ReferenceValue.White.value
    brightness = value / MAX_VALUE * 100
    return int(round(brightness))


def calculate_average_pixel_value(image: Image) -> float:
    """ Turns an image into grayscale and calculates the average pixel value """
    im = convert_to_grayscale(image)
    pixels = get_pixels(im)
    return sum(pixels) / len(pixels)


def get_zone_from_pixel_value(value: PixelValue) -> Zone:
    """ Returns the Zone to which a pixel belongs based on its value"""
    return next(z for z in Zone if Zone.limits()[z][0] <= value <= Zone.limits()[z][1])


def is_pixel_in_zone(value: PixelValue, zones: Zone | list[Zone]) -> bool:
    """ Determines whether a pixel is in the given zone"""
    if not isinstance(zones, list):
        zones = [zones]
    pixel_zone = get_zone_from_pixel_value(value)
    return pixel_zone in zones


def filter_image_by_zone(image: Image, zones: Zone | list[Zone]) -> Image:
    """ Keeps only the pixels from an image that belong to the given zone.
    If a pixel doesn't belong, it replaces its value with white"""
    pixels = get_pixels(image)
    
    filtered_pixels = [pixel if is_pixel_in_zone(pixel, zones) 
                       else ReferenceValue.White for pixel in pixels]
    
    filtered_image = Image.new('L', size=image.size)
    filtered_image.putdata(filtered_pixels)
    return filtered_image


def show_side_by_side_cl(image1: Image, image2: Image):
    zones = len(Zone)
    gradient = np.linspace(
        ReferenceValue.Black.value, ReferenceValue.White.value, zones)\
        .reshape(1, -1)

    fig, axes = plt.subplots(2, 2, height_ratios=[10, 1], figsize=(10, 6))

    axes[0, 0].imshow(image1)
    axes[0, 0].axis('off')
    # do RGB conversion to copy the grayscale in other channels
    axes[0, 1].imshow(image2.convert('RGB'))
    axes[0, 1].axis('off')

    for ax in axes[1]:
        ax.imshow(gradient, cmap='gray', aspect='auto')
        for i, label in enumerate(Zone):
            ax.text(i, 0, 
                    label.name,
                      ha='center', va='center',
                     color='white' if ZONE_LIMITS[label.value] <= ReferenceValue.MiddleGray else 'black', 
                     fontsize=18)
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_edgecolor('#aaaaaa')
            # spine.set_linewidth(1.5)
        ax.set_xticks([])
        ax.set_yticks([])

    # gray background
    fig.set_facecolor('gray')

    # display in second monitor
    MONITOR_X = 1920
    MONITOR_Y = -645
    MONITOR_W = 2560  # your second monitor's resolution
    MONITOR_H = 1440

    fig.canvas.manager.window.wm_geometry(f"{MONITOR_W}x{MONITOR_H}+{MONITOR_X}+{MONITOR_Y}")
    figManager = plt.get_current_fig_manager()
    # figManager.window.state('zoomed')

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    
    filepath = 'test_images/zone_system.jpg'
    original_image = loads_image(filepath)
    if not is_grayscale(original_image):
        im = convert_to_grayscale(original_image)
    im = apply_median_filter(im)

    show_side_by_side_cl(original_image, im)
    
    filtered_image = filter_image_by_zone(convert_to_grayscale(original_image), Zone.V)
    show_side_by_side_cl(original_image, filtered_image)