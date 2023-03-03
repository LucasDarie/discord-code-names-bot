from ColorCard import ColorCard
from Language import Language
from Card import Card
import random
import unidecode
from CodeGameExceptions import WrongCardIdNumberGiven, WordNotInGrid

GRID_SIZE = 5

class CardGrid(object):
    def __init__(self, language:Language, starting_team_color:ColorCard) -> None:
        """constructor of the CardGrid object

        Args:
            language (Language): the langage of the grid
            starting_team_color (ColorCard): the color of the team that starts
        """
        super(CardGrid, self).__init__()
        
        word_list:list[str]

        with open(f"words/{language.value}_word_list.txt", "r") as f:
            words = [unidecode.unidecode(word.strip()).upper() for word in f.readlines()]
            word_list = random.sample(words, 25)

        self.card_list:list[list[Card]] = [[Card(word_list[i*GRID_SIZE+j], ColorCard.WHITE) for j in range(GRID_SIZE)] for i in range(GRID_SIZE)]
        self.language: Language = language
        self.starting_team_color:ColorCard = starting_team_color
        self.remaining_words_count:dict[ColorCard,int] = {ColorCard.BLUE:0, ColorCard.RED:0, ColorCard.BLACK:0, ColorCard.WHITE:(GRID_SIZE**2)-9-8-1}
        
        opponent_team = ColorCard.BLUE if starting_team_color == ColorCard.RED else ColorCard.RED

        # color randomly the grid with 9 and 8 BLUE or RED card, and 1 BLACK
        self.color_grid(self.card_list, self.starting_team_color, 9)
        self.color_grid(self.card_list, opponent_team, 8)
        self.color_grid(self.card_list, ColorCard.BLACK, 1)
    
    def color_grid(self, grid:list[list[Card]], color:ColorCard, number:int):
        """Color a number of cards of the grid with the same color. 

        The number and the color are passed in parameter

        Args:
            grid (list[list[Card]]): The grid of Card
            color (ColorCard): The color chosen to color the cards
            number (int): The number of cards that will be colored
        """
        # set number of word remaining for each card color
        self.remaining_words_count[color] = number
        for _ in range(number):
            x = random.randint(0, 4)
            y = random.randint(0, 4)

            while grid[x][y].color != ColorCard.WHITE:
                x = random.randint(0, 4)
                y = random.randint(0, 4)
            # exit : grid[x][y].color == ColorCard.WHITE
            grid[x][y].color = color

    def get_card_by_word(self, word:str) -> Card | None:
        """return the card associate with the word

        Args:
            word (str): a single word

        Returns:
            Card | None: the Card or None if the word is not present in the grid
        """
        i = 0
        j = 0
        k = 0
        while(k < GRID_SIZE**2 and (self.card_list[i][j].guessed or self.card_list[i][j].word != word)):
            k += 1
            j = k%GRID_SIZE
            i = k//GRID_SIZE
        # exit : k >= GRID_SIZE**2 or (not self.card_list[i][j].guessed and self.card_list[i][j].word == word)

        if k < GRID_SIZE**2:
            return self.card_list[i][j]
        return None
    
    def is_in_grid(self, word:str) -> bool:
        """return if the word is in the grid

        Args:
            word (str): a single word

        Returns:
            bool: True if the word is in the grid, else False
        """
        return not self.get_card_by_word(word) == None

    def guess(self, word:str) -> tuple[ColorCard, str]:
        """set a card associate to a word to guessed if the word is in the grid

        Args:
            word (str): a single word

        Raises:
            WordNotInGrid: if the word is not present in the grid

        Returns:
            ColorCard: the color of the guessed card
        """
        card = self.get_card_by_word(word)
        if card == None :
            raise WordNotInGrid()
        
        card.guessed = True
        self.remaining_words_count[card.color] -= 1
        return (card.color, card.word)


    
    def get_word_by_number(self, card_id:int) -> str:
        """get the associated word with a number given

        Args:
            card_id (int): the card id

        Raises:
            WrongCardIdNumberGiven: if the number is not between 1 and 25

        Returns:
            str: the corresponding word
        """
        if(card_id < 1 or card_id > 25):
            raise WrongCardIdNumberGiven(self.language, GRID_SIZE)
        
        i = (card_id-1)//GRID_SIZE
        j = (card_id-1)%GRID_SIZE

        return self.card_list[i][j].word
