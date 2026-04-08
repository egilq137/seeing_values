from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np
import matplotlib.pyplot as plt
import requests
from io import BytesIO


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


def apply_median_filter(image: Image, size: int = 7) -> Image:
    return image.filter(ImageFilter.MedianFilter(size=size))


def calculate_brightness(value: int) -> float:
    MAX_VALUE = 255
    return value / MAX_VALUE * 100


def show_side_by_side_cl(image1: Image, image2: Image):
    zones = 10
    gradient = np.linspace(0, 1, zones).reshape(1, -1)

    fig, axes = plt.subplots(2, 2, height_ratios=[10, 1], figsize=(10, 6))

    axes[0, 0].imshow(image1)
    axes[0, 0].axis('off')
    # do RGB conversion to copy the grayscale in other channels
    axes[0, 1].imshow(image2.convert('RGB'))
    axes[0, 1].axis('off')

    for ax in axes[1]:
        ax.imshow(gradient, cmap='gray', aspect='auto')
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
    
    filepath = 'test_images/lakshmi.jpg'
    original_image = loads_image(filepath)
    if not is_grayscale(original_image):
        im = convert_to_grayscale(original_image)
    im = apply_median_filter(im)

    show_side_by_side_cl(original_image, im)
    