from asccii_art import AsciiArtPreset, AsciiArtConverter


def main():
    preset = AsciiArtPreset('presets/Notepad++WhiteOnBlack.json')
    art = AsciiArtConverter.convert('image.png', preset)
    with open('result.txt', 'w', encoding='utf-8') as file:
        file.write(art)

    pass


if __name__ == '__main__':
    main()






