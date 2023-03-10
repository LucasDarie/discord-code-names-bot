import unidecode
from PIL import Image, ImageDraw, ImageFont
from ColorCard import ColorCard
from CardGrid import CardGrid, GRID_SIZE
from Language import Language
import asyncio

# Font used

FONT = 'font/KeepCalm.ttf'


# Height and width of cards
CARD_HEIGHT = 430
CARD_WIDTH = 660

# padding around cards
PADDING = 10


IMAGE = Image.open('images/BASE.png')

def addTextTo(img, text:str, card_id:int):
    # remove or replace special characters
    text_u = unidecode.unidecode(text).upper()
    card_id_str = f"#{card_id}"

    # create a drawing interface to add text
    draw = ImageDraw.Draw(img)

    # select the font
    font = ImageFont.truetype(FONT, 75)

    # get the text height and width
    _, top, _, bottom = draw.textbbox((0, 0), text_u, font)
    text_height = bottom - top
    text_width = draw.textlength(text_u, font)

    # place the word text and draw it on the card
    x_text = (CARD_WIDTH - text_width) / 2
    y_text = (CARD_HEIGHT) / 2 + text_height - 4
    draw.text((x_text, y_text), text_u, font=font, fill=(0, 0, 0, 255), )


    # place the card_id text and draw it on the card
    
    x_card_id = 70
    y_card_id = 120
    draw.text((x_card_id, y_card_id), card_id_str, font=font, fill=(90, 90, 90, 255))

    return img



def getImageColored(img, color: ColorCard, guessed:bool, isSpy:bool=False):
    # get the value of the color, used in files like "RED_GUESS.png"
    color_name = color.value

    # create a transparent canvas with img size and paste img
    canvas = Image.new('RGBA', img.size, (0, 0, 0, 0))
    canvas.paste(img, (0, 0))

    if isSpy and not guessed:
        if color != ColorCard.WHITE:
            img2 = Image.open(f'images/{color_name}.png')
            canvas.paste(img2, (0, 0), img2)

    elif guessed:
        # white base is equal to BASE.png so nothing to add
        if color != ColorCard.WHITE:
            img2 = Image.open(f'images/{color_name}.png')
            canvas.paste(img2, (0, 0), img2)
        # black does not exist because when it is guessed the party is finished
        if color != ColorCard.BLACK:
            img3 = Image.open(f'images/{color_name}_GUESS.png')
            canvas.paste(img3, (0, 0), img3)

    return canvas



async def generateGrid(card_grid:CardGrid, isSpy:bool, channel_id:str):
    # height and width of the final grid
    height = (CARD_HEIGHT + PADDING) * card_grid.grid_size
    width = (CARD_WIDTH + PADDING) * card_grid.grid_size

    # Créer une image noire
    canvas = Image.new('RGBA', (width, height), (0, 0, 0, 0))

    # Loop on the 25 cards
    for i in range(card_grid.grid_size):
        for j in range(card_grid.grid_size):
            image = IMAGE.copy()
            card = card_grid.card_list[i][j]

            # get the coordinates of the image in the grid
            x = j * (CARD_WIDTH + PADDING)
            y = i * (CARD_HEIGHT + PADDING)

            # add text to the image
            
            img_with_text = addTextTo(image, card.word, card_id=(i*card_grid.grid_size+j+1))

            # add the layer depending on the color, guessed state and isSpy booleans

            img_with_color = getImageColored(img_with_text, color=card.color, guessed=card.guessed, isSpy=isSpy)
            
            # paste the card to the canvas grid
            canvas.paste(img_with_color, (x, y), img_with_color)


    c = canvas.reduce(2)
    c.save(f"render/{channel_id}{'_SPY' if isSpy else '_PLAYER'}.png")



if __name__ == "__main__":
    cardGrid = CardGrid(language=Language.FR, starting_team_color=ColorCard.BLUE, team_list=[ColorCard.BLUE, ColorCard.RED, ColorCard.GREEN, ColorCard.YELLOW])
    cardGrid.card_list[0][0].guessed = True
    cardGrid.card_list[3][2].guessed = True
    cardGrid.card_list[0][4].guessed = True
    cardGrid.card_list[3][0].guessed = True
    cardGrid.card_list[2][0].guessed = True
    cardGrid.card_list[0][0].guessed = True
    cardGrid.card_list[0][0].guessed = True
    asyncio.run(generateGrid(cardGrid, isSpy=False, channel_id="123456789"))
