from wiki_main import (get_list_of_wiki_artists, 
                       pick_random_element, 
                       get_paintings_by_artist_url,
                       pick_random_painting_from_paintings_by_artist)

from image_processing import (is_grayscale,
                              convert_to_grayscale,
                              apply_median_filter,
                              show_side_by_side_cl,
                              open_image_from_url,
                              calculate_average_pixel_value,
                              calculate_brightness)

from PIL import Image
import requests


if __name__ == '__main__':

    # get all artists
    list_of_wiki_artists = get_list_of_wiki_artists()

    user_input = ''
    while user_input != 'q':
        ARTISTS_ATTEMPTS = 3
        for _ in  range(ARTISTS_ATTEMPTS):
            artist = pick_random_element(list_of_wiki_artists)
            paintings_by_artist = get_paintings_by_artist_url(artist['url'])
            painting = pick_random_painting_from_paintings_by_artist(paintings_by_artist)

            if painting.response.status_code == 200:
                print('Success!\n', f'{painting.title} by {painting.artist} ({painting.completion_year})' )
                original_image = open_image_from_url(painting.response.url)
                break
            
            print(f'looking for a new artist...')
        
        im = convert_to_grayscale(original_image)
        im = apply_median_filter(im)
        
        avg_pixel_value = calculate_average_pixel_value(im)
        print(f'Avg brightness = {calculate_brightness(avg_pixel_value)}%')
        show_side_by_side_cl(original_image, im)

        user_input = input('Press a key to get another image or "q" to exit: ')