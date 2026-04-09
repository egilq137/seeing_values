import PIL
from PIL import Image
from image_processing import (Zone,
                              ReferenceValue,
                              PixelValue,
                              loads_image,
                              is_grayscale,
                              convert_to_grayscale,
                              calculate_brightness,
                              calculate_average_pixel_value, 
                              get_zone_from_pixel_value,
                              is_pixel_in_zone)
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
    assert calculate_brightness(ReferenceValue.Black) == 0


def test_calculate_brightness_percentage_pure_white():
    assert calculate_brightness(ReferenceValue.White) == 100


def test_calculate_brightness_percentage_middle_gray():
    assert calculate_brightness(ReferenceValue.MiddleGray) == 50


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
    assert get_zone_from_pixel_value(ReferenceValue.Black) == Zone.I


def test_pure_white_is_in_zone_nine():
    assert get_zone_from_pixel_value(ReferenceValue.White) == Zone.IX


def test_middle_gray_is_in_zone_five():
    assert get_zone_from_pixel_value(ReferenceValue.MiddleGray) == Zone.V


def test_pixel_value_one_is_in_zone_one():
    assert get_zone_from_pixel_value(PixelValue(1)) == Zone.I


def test_pixel_value_two_fifty_four_is_in_zone_nine():
    assert get_zone_from_pixel_value(PixelValue(254)) == Zone.IX


def test_pixel_value_thirty_is_in_zone_two():
    assert get_zone_from_pixel_value(PixelValue(30)) == Zone.II


def test_keep_black_if_zone_is_one():
    assert is_pixel_in_zone(ReferenceValue.Black, Zone.I) == True


def test_keep_white_if_zone_is_nine():
    assert is_pixel_in_zone(ReferenceValue.White, Zone.IX) == True


def test_dont_keep_white_if_zone_is_not_nine():
    zones_without_nine = list(set(Zone) - {Zone.IX})
    random_zone = random.choice(zones_without_nine)
    assert is_pixel_in_zone(ReferenceValue.White, random_zone) == False