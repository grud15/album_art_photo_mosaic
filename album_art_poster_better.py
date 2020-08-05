
"""
The objective of this code is to take album art from users' searches of their favorite albums and make a photo-mosaic
from those inputs.
"""

# Libraries imported to make it happen!
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from simpleimage import SimpleImage
import random
from PIL import Image
import time
import urllib.request

# import json
# from json.decoder import JSONDecodeError
# print(json.dumps(VARIABLE, sort_keys=True, indent=4))

# AUTHORIZATION FLOW FOR SPOTIFY API
auth_manager = SpotifyClientCredentials()
spotify_object = spotipy.Spotify(auth_manager=auth_manager)

NUM_RC = 20     # Number of rows and columns of small images that make up large image
SMALL_IMAGE_SIZE = 32   # Number of pixels in the x and y directions for small image
LARGE_IMAGE_SIZE = 640  # Number of pixels in the x and y directions for large image
DPI_GOOD = 300  # Dots per inch for high quality printing
DPI_BAD = 75    # Dots per inch for low quality printing (prevent screenshotting)
RESIZE_CONSTANT = 3     # Ensures resize occurs uniformly and without loss in resolution
RESIZE_GOOD = 2560      # Enlarges image so that pixels per inch(ppi) > 300 for 8x8in image
RESIZE_BAD = 480        # Makes image smaller so that ppi is lower (prevent screenshotting)
OPACITY_CONSTANT = .3  # Controls the opacity of blended images (if 0 only first image shows)


def main():
    find_main_album()
    image_list = find_other_albums()
    create_overlay(image_list)
    final_image = make_final_image()
    save_final_image(final_image)


def find_main_album():
    intro()
    get_main_album()


def intro():
    print()
    print("Let's use your favorite album to make cool art!")
    time.sleep(2)


def get_main_album():
    # This function helps finds and confirms a user's favorite album which will be the main image in mosaic
    while True:
        print()
        user_input = input("Search for an album: ")
        search_result = spotify_object.search(user_input, limit=1, type='album')['albums']['items'][0]['name']
        artist_from_search = \
        spotify_object.search(user_input, limit=1, type='album')['albums']['items'][0]['artists'][0][
            'name']
        main_album_id = spotify_object.search(user_input, limit=1, type='album')['albums']['items'][0]['id']
        try:
            user_confirm = int(
                input("Is " + search_result + " by " + artist_from_search + " the correct album? (Y=1/N=2): "))
        except ValueError:
            print("Please enter 1 or 2.")
            continue
        if user_confirm > 2:
            print("Please enter 1 or 2.")
            continue
        if user_confirm == 2:
            print("Try searching again...")
            continue
        if user_confirm == 1:
            interpret_main_album_input(main_album_id)
            break


def interpret_main_album_input(main_album_id):
    # This function saves the image to a designated spot on computer
    url = spotify_object.album(main_album_id)['images'][0]['url']
    urllib.request.urlretrieve(url, "C:/Users/grudm/Desktop/Python/main_album_art.jpg")
    print("Album saved!")


def find_other_albums():
    user_input = instructions()
    image_list = get_other_album(user_input)
    return image_list


def instructions():
    # The user can search for as many other albums as they wish to make up the mosaic (including 0)
    print()
    while True:
        try:
            user_input = int(
                input("How many other albums would you like to search for: "))
        except ValueError:
            print("Please enter a positive integer or 0.")
            continue
        return user_input


def get_other_album(user_input):
    # Searches, confirms, and saves album art for other albums
    image_list = ["C:/Users/grudm/Desktop/Python/main_album_art.jpg"]
    for i in range(user_input):
        find_other_album(i, image_list)
        print(str(i + 1) + "/" + str(user_input) + " albums added.")
    print()
    print("Album selection complete!")
    return image_list


def find_other_album(i, image_list):
    while True:
        print()
        user_input = input("Search for an album: ")
        search_result = spotify_object.search(user_input, limit=1, type='album')['albums']['items'][0]['name']
        artist_from_search = \
            spotify_object.search(user_input, limit=1, type='album')['albums']['items'][0]['artists'][0][
                'name']
        other_album_id = spotify_object.search(user_input, limit=1, type='album')['albums']['items'][0]['id']
        try:
            user_confirm = int(
                input("Is " + search_result + " by " + artist_from_search + " the correct album? (Y=1/N=2): "))
        except ValueError:
            print("Please enter 1 or 2.")
            continue
        if user_confirm > 2:
            print("Please enter 1 or 2.")
            continue
        if user_confirm == 2:
            print("Try searching again...")
            continue
        if user_confirm == 1:
            interpret_other_album_input(i, other_album_id, image_list)
            break


def interpret_other_album_input(i, other_album_id, image_list):
    url = spotify_object.album(other_album_id)['images'][0]['url']
    save_location = "C:/Users/grudm/Desktop/Python/other_album_art" + str(i + 1) + ".jpg"
    image_list.append(save_location)
    urllib.request.urlretrieve(url, save_location)


def create_overlay(image_list):
    # Create mosaic image
    small_image_list = make_small_images(image_list)
    make_overlay(small_image_list)


def make_small_images(image_list):
    # Access other album art images, resize them, and then return a list
    new_image_list = []
    for i in range(len(image_list)):
        new_image = SimpleImage(image_list[i])
        new_image_list.append(new_image)
    small_image_list = []
    for i in range(len(new_image_list)):
        new_small_image = new_image_list[i].pil_image.resize((SMALL_IMAGE_SIZE, SMALL_IMAGE_SIZE))
        save_location = "C:/Users/grudm/Desktop/Python/small_album_art" + str(i + 1) + ".jpg"
        new_small_image.save(save_location)
        small_image = SimpleImage(save_location)
        small_image_list.append(small_image)
    return small_image_list


def make_overlay(small_image_list):
    # Used returned small_image_list to make small image mosaic of other album arts *includes main album art
    overlay = SimpleImage.blank(LARGE_IMAGE_SIZE, LARGE_IMAGE_SIZE)
    for row in range(NUM_RC):
        for column in range(NUM_RC):
            image = random.choice(small_image_list)
            height = image.height
            width = image.width
            put_image(image, overlay, row, column, height, width)
    save_location = 'C:/Users/grudm/Desktop/Python/overlay.jpg'
    overlay.pil_image.save(save_location, dpi=(DPI_GOOD, DPI_GOOD))


def put_image(image, overlay, row, column, height, width):
    for y in range(height):
        for x in range(width):
            pixel = image.get_pixel(x, y)
            overlay.set_pixel(x + column * SMALL_IMAGE_SIZE, y + row * SMALL_IMAGE_SIZE, pixel)


def make_final_image():
    # Blend the main_image with the overlay mosaic to create final product
    # Can be controlled by NUM_RC and OPACITY_CONSTANT
    main_image = Image.open('C:/Users/grudm/Desktop/Python/main_album_art.jpg')
    overlay = Image.open('C:/Users/grudm/Desktop/Python/overlay.jpg')
    main_image = main_image.convert('RGBA')
    overlay = overlay.convert('RGBA')
    final_image = Image.blend(main_image, overlay, OPACITY_CONSTANT)
    final_image = final_image.convert('RGB')
    final_image = final_image.resize((RESIZE_GOOD, RESIZE_GOOD), RESIZE_CONSTANT)
    return final_image


def save_final_image(final_image):
    # Saves an high quality image and saves a lower quality image used for posting (prevents screenshotting)
    save_location = 'C:/Users/grudm/Desktop/Python/final_image.jpg'
    final_image.save(save_location, dpi=(DPI_GOOD, DPI_GOOD))
    media_final_image = final_image.resize((RESIZE_BAD, RESIZE_BAD), RESIZE_CONSTANT)
    save_location_extra = 'C:/Users/grudm/Desktop/Python/final_image_for_media.jpg'
    media_final_image.save(save_location_extra, dpi=(DPI_BAD, DPI_BAD))


if __name__ == '__main__':
    main()