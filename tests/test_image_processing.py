import PIL
from PIL import Image
from image_processing import (loads_image,
                              is_grayscale,
                              convert_to_grayscale,
                              calculate_brightness)
import pytest

@pytest.fixture
def color_image():
    return loads_image('test_images/lakshmi.jpg')

def test_loads_image_object(color_image):
    """ Test that image is proper Pillow object"""
    assert isinstance(color_image, PIL.JpegImagePlugin.JpegImageFile)


def test_color_image_is_not_grayscale(color_image):
    """ Test whether an image is already in grayscale or not"""
    assert color_image.mode != 'L'
    assert color_image.mode == 'RGB'
    assert is_grayscale(color_image) == False


def test_converts_color_image_into_grayscale(color_image):
    grayscale_image = convert_to_grayscale(color_image)
    assert grayscale_image.mode == 'L'


def test_calculate_brightness_percentage_pure_black():
    assert calculate_brightness(0) == 0


def test_calculate_brightness_percentage_pure_white():
    assert calculate_brightness(255) == 100


def test_calculate_brightness_percentage_middle_gray():
    middle_gray = 255 / 2
    assert calculate_brightness(middle_gray) == 50