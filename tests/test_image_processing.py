import PIL
from PIL import Image
from image_processing import (Zone,
                              ReferenceValue,
                              loads_image,
                              is_grayscale,
                              convert_to_grayscale,
                              calculate_brightness,
                              calculate_average_pixel_value, 
                              get_zone_from_pixel_value)
import pytest
import random

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
    assert calculate_brightness(ReferenceValue.Black.value) == 0


def test_calculate_brightness_percentage_pure_white():
    assert calculate_brightness(ReferenceValue.White.value) == 100


def test_calculate_brightness_percentage_middle_gray():
    assert calculate_brightness(ReferenceValue.MiddleGray.value) == 50


def test_get_average_pixel_value_from_gray_image():
    """ takes the average of all pixel values in a grayscale image"""
    gray_image = loads_image('test_images/gray_card.png')
    
    # makes sure that this gray image has the same values in each pixel
    x_range, y_range = gray_image.size
    r_x, r_y = random.choice(range(x_range)), random.choice(range(y_range))
    
    # makes sure that any color channel produces the same result
    r_channel = random.choice(['R', 'G', 'B'])
    gray_image_single_channel = gray_image.getchannel(r_channel)
    r_pixel = gray_image_single_channel.getpixel((r_x, r_y))

    assert calculate_average_pixel_value(gray_image) == r_pixel


def test_pure_black_is_in_zone_one():
    assert get_zone_from_pixel_value(ReferenceValue.Black.value) == Zone.I


def test_pure_white_is_in_zone_nine():
    assert get_zone_from_pixel_value(ReferenceValue.White.value) == Zone.IX


# def test_middle_gray_is_in_zone_five():

    