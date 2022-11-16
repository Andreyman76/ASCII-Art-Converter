import json
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import os.path


def grayscale(img) -> np.ndarray:
    """Converts a color image to black and white (a two-dimensional array of brightnesses)"""
    height = len(img)
    width = len(img[0])

    result = np.zeros(shape=(height, width), dtype=float)

    for y in range(height):
        for x in range(width):
            color = 0.299 * img[y][x][0] + 0.587 * img[y][x][1] + 0.114 * img[y][x][2]
            result[y][x] = color

    return result


class AsciiArtPreset:
    """Preset for converting images to ASCII art"""
    def __init__(self, filename: str = None):
        self.symbol_width = 0
        self.symbol_height = 0
        self.brightness = {}

        if filename is not None:
            self.load(filename)
        pass

    def save(self, filename: str):
        """Save this preset to json file"""
        if os.path.isfile(filename):
            raise FileExistsError(f'File {filename} already exists')

        with open(filename, 'w', encoding='utf-8') as file:
            data = {
                'width': self.symbol_width,
                'height': self.symbol_height,
                'brightness': self.brightness
            }
            json.dump(data, file, ensure_ascii=False, indent=4)
        pass

    def load(self, filename: str):
        """Load preset from json file and initialize this object with loaded data"""
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.symbol_width = data['width']
            self.symbol_height = data['height']
            self.brightness = data['brightness']
        pass

    @staticmethod
    def __get_average_brightness(image, x, y, width, height) -> float:
        """Calculate the average brightness in a given area of a black and white image"""
        brightness = 0.0

        for _y in range(height):
            for _x in range(width):
                brightness += image[y + _y][x + _x]

        return brightness / (width * height)

    def generate_preset(self, screen: str, entered: str, symbol_width: int, symbol_height: int, x: int = 0, y: int = 0):
        """Generate a preset based on the screenshot of the text, the entered text itself,
        the width and height of the characters, as well as the initial position
        (the coordinates of the upper left corner of the first character in the screenshot)."""
        self.symbol_width = symbol_width
        self.symbol_height = symbol_height

        img = plt.imread(screen)
        img = grayscale(img)
        symbol_sets = entered.split('\n')
        for symbol_set in symbol_sets:
            _x = x
            for symbol in symbol_set:
                brightness = AsciiArtPreset.__get_average_brightness(img, _x, y, symbol_width, symbol_height)
                self.brightness[symbol] = brightness
                _x += symbol_width

            y += symbol_height
        pass


class AsciiArtConverter:
    def __init__(self):
        pass

    @staticmethod
    def __choose_symbol(color: float, brightness: dict) -> float:
        """Select the symbol with the most suitable brightness"""
        min_difference = 10.0
        result = ''

        for symbol, brightness in brightness.items():
            difference = abs(color - brightness)
            if difference < min_difference:
                min_difference = difference
                result = symbol

        return result

    @staticmethod
    def convert(image: str, preset: AsciiArtPreset, output_width: int = 0, output_height: int = 0) -> str:
        """Convert the image to ASCII art using the path to the original image and preset,
        as well as the width and height of the resulting ASCII art"""
        result = ''
        img = Image.open(image)
        original_width = img.width
        original_height = img.height
        koeff = preset.symbol_height / preset.symbol_width

        if output_width == output_height == 0:
            img = img.resize((int(original_width * koeff), original_height), Image.ANTIALIAS)
        elif output_width == 0:
            k = (original_height / output_height) / koeff
            new_width = int(original_width / k)
            img = img.resize((new_width, output_height), Image.ANTIALIAS)
        elif output_height == 0:
            k = (original_width / output_width) * koeff
            new_height = int(original_height / k)
            img = img.resize((output_width, new_height), Image.ANTIALIAS)
        else:
            img = img.resize((output_width, output_height), Image.ANTIALIAS)
            pass

        img.save('temp.png')
        img = plt.imread('temp.png')
        img = grayscale(img)

        width = len(img[0])
        height = len(img)

        for y in range(height):
            for x in range(width):
                result += AsciiArtConverter.__choose_symbol(img[y][x], preset.brightness)

            result += '\n'

        return result
