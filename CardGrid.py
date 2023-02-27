from ColorCard import ColorCard
from Language import Language
from Card import Card
import random
import unidecode



class CardGrid(object):
    def __init__(self, language:Language) -> None:
        super(CardGrid, self).__init__()
        nb_random = random.randint(0, 1)
        team_colors = [ColorCard.BLUE, ColorCard.RED]
        
        word_list:list[str]

        with open(f"words/{language.value}_word_list.txt", "r") as f:
            words = [unidecode.unidecode(word.strip()).upper() for word in f.readlines()]
            word_list = random.sample(words, 25)

        self.card_list:list[list[Card]] = [[Card(word_list[i*5+j], ColorCard.WHITE) for j in range(5)] for i in range(5)]
        self.language: Language = language
        self.starting_team_color:ColorCard = team_colors[nb_random]
        
        opponent_team = team_colors[(nb_random+1)%2]

        # color randomly the grid with 9 and 8 BLUE or RED card, and 1 BLACK
        self.color_grid(self.card_list, self.starting_team_color, 9)
        self.color_grid(self.card_list, opponent_team, 8)
        self.color_grid(self.card_list, ColorCard.BLACK, 1)
    
    """
    param : 
        grid : list[list[Card]] The grid of Card
        color : ColorCard The color chosen to color the cards
        number : The number of cards that will be colored
    summary : 
        Color a number of cards of the grid with the same color. 
        The number and the color are passed in parameter
    """
    def color_grid(self, grid:list[list[Card]], color:ColorCard, number:int):
        for _ in range(number):
            x = random.randint(0, 4)
            y = random.randint(0, 4)
            while grid[x][y].color != ColorCard.WHITE:
                
                x = random.randint(0, 4)
                y = random.randint(0, 4)
            # exit : grid[x][y].color == ColorCard.WHITE
            grid[x][y].color = color