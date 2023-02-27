import unidecode
from PIL import Image, ImageDraw, ImageFont
from ColorCard import ColorCard
from CardGrid import CardGrid
from Language import Language

# Font used

FONT = 'font/KeepCalm.ttf'

# Height and width of cards
CARD_HEIGHT = 430
CARD_WIDTH = 660

# padding around cards
PADDING = 10

# height ands width of the final grid
HEIGHT = (CARD_HEIGHT + PADDING) * 5
WIDTH = (CARD_WIDTH + PADDING) * 5

# Créer une image noire
CANVAS = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))

IMAGE = Image.open('images/BASE.png')

def addTextTo(img, text:str):
    # remove or replace special characters
    text_u = unidecode.unidecode(text).upper()

    # create a drawing interface to add text
    draw = ImageDraw.Draw(img)

    # select the font
    font = ImageFont.truetype(FONT, 75)

    # get the text height and width
    _, top, _, bottom = draw.textbbox((0, 0), text_u, font)
    text_height = bottom - top
    text_width = draw.textlength(text_u, font)

    # place the text and draw it on the card
    x = (CARD_WIDTH - text_width) / 2
    y = (CARD_HEIGHT) / 2 + text_height - 4
    draw.text((x, y), text_u, font=font, fill=(0, 0, 0, 255))

    return img



def getImageColored(img, color: ColorCard, finded:bool, isSpy:bool=False):
    # get the value of the color, used in files like "RED_FIND.png"
    color_name = color.value

    # create a transparent canvas with img size and paste img
    canvas = Image.new('RGBA', img.size, (0, 0, 0, 0))
    canvas.paste(img, (0, 0))

    if isSpy and not finded:
        if color != ColorCard.WHITE:
            img2 = Image.open(f'images/{color_name}.png')
            canvas.paste(img2, (0, 0), img2)

    elif finded:
        # white base is equal to BASE.png so nothing to add
        if color != ColorCard.WHITE:
            img2 = Image.open(f'images/{color_name}.png')
            canvas.paste(img2, (0, 0), img2)
        # black does not exist because when it is finded the party is finished
        if color != ColorCard.BLACK:
            img3 = Image.open(f'images/{color_name}_FIND.png')
            canvas.paste(img3, (0, 0), img3)

    return canvas



def generateGrid(card_grid:CardGrid, isSpy:bool):

    # Loop on the 25 cards
    for i in range(5):
        for j in range(5):
            image = IMAGE.copy()
            card = card_grid.card_list[i][j]

            # get the coordinates of the image in the grid
            x = j * (CARD_WIDTH + PADDING)
            y = i * (CARD_HEIGHT + PADDING)

            # add text to the image
            
            img_with_text = addTextTo(image, card.word)

            # add the layer depending on the color, finded state and isSpy booleans

            img_with_color = getImageColored(img_with_text, color=card.color, finded=card.finded, isSpy=isSpy)
            
            # paste the card to the canvas grid
            CANVAS.paste(img_with_color, (x, y), img_with_color)



    CANVAS.save("canvas.png")


cardGrid = CardGrid(language=Language.FR)
generateGrid(cardGrid, isSpy=True)
