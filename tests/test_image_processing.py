import PIL
from PIL import Image
from image_processing import (loads_image,
                              is_grayscale,
                              convert_to_grayscale)
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

