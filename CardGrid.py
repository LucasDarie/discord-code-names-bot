from ColorCard import ColorCard
from Language import Language
from Card import Card
import random
from CodeGameExceptions import WrongCardIdNumberGiven, WordNotInGrid, WordListFileNotFound, NotEnoughWordsInFile
from word_list import read_list_file
GRID_SIZE = 5

class CardGrid(object):
    
    def __init__(self, language:Language, starting_team_color:ColorCard, team_list:list[ColorCard], default_word_list:bool=True, guild_id_for_list:str | None = None) -> None:
        """constructor of the CardGrid object

        Args:
            language (Language): the langage of the grid
            starting_team_color (ColorCard): the color of the team that starts
            team_list (list[ColorCard]): the list of color team present in the grid
            default_word_list (bool): True : the default word list of the language will be used. False : not
            guild_id_for_list (str): the guild_id of the guild. If mentionned the guild_word_list will be added, if it's None it will not. Default to: None

        Raises:
            WordListFileNotFound: if the word file of the guild_id is not found
            NotEnoughWordsInFile: Raised when there is not enough word in the available word list to start a game
        """
        super(CardGrid, self).__init__()
        
        self.grid_size = 3 + len(team_list)

        words:list[str] = []

        if default_word_list:
            words.extend(read_list_file(path=f"words/{language.value}_word_list.txt"))

        if guild_id_for_list != None:
            try:
                    words_to_add = read_list_file(path=f"words/servers/{guild_id_for_list}_word_list.txt")
                    words.extend(words_to_add)
            except Exception as e:
                print(e)
                raise WordListFileNotFound(language=language)

        words = list(dict.fromkeys(words)) # remove duplicates
        if len(words) < self.grid_size**2:
            raise NotEnoughWordsInFile(language=language)

        word_list:list[str] = random.sample(words, self.grid_size**2)
        
        self.card_list:list[list[Card]] = [[Card(word_list[i*self.grid_size+j], ColorCard.WHITE) for j in range(self.grid_size)] for i in range(self.grid_size)]
        self.language: Language = language
        self.starting_team_color:ColorCard = starting_team_color


        self.remaining_words_count:dict[ColorCard,int] = {}
        # color randomly the grid
        self.color_all_grid(team_list=team_list)
        
    
    def color_all_grid(self, team_list:list[ColorCard]):
        """color all the grid depending on the teams given in parameters

        Args:
            team_list (list[ColorCard]): the list of teams color
        """
        nb_teams = len(team_list)
        nb_words = 6 + nb_teams
        for color_team in team_list:
            self.color_grid(color=color_team, number=nb_words if color_team != self.starting_team_color else nb_words+1)
            
        self.color_grid(color=ColorCard.BLACK, number=1)
        
        # grid_size**2 = number total of card, nb_words*nb_teams = nb colored card in the grid (+1 for starting team, +1 for black card)
        self.remaining_words_count[ColorCard.WHITE] = self.grid_size**2 - ((nb_words*nb_teams)+2)

    def color_grid(self, color:ColorCard, number:int):
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
            x = random.randint(0, self.grid_size-1)
            y = random.randint(0, self.grid_size-1)

            while self.card_list[x][y].color != ColorCard.WHITE:
                x = random.randint(0, self.grid_size-1)
                y = random.randint(0, self.grid_size-1)
            # exit : grid[x][y].color == ColorCard.WHITE
            self.card_list[x][y].color = color

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
        while(k < self.grid_size**2 and (self.card_list[i][j].guessed or self.card_list[i][j].word != word)):
            k += 1
            j = k%self.grid_size
            i = k//self.grid_size
        # exit : k >= GRID_SIZE**2 or (not self.card_list[i][j].guessed and self.card_list[i][j].word == word)

        if k < self.grid_size**2:
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
            raise WordNotInGrid(self.language)
        
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
            raise WrongCardIdNumberGiven(self.language, self.grid_size)
        
        i = (card_id-1)//self.grid_size
        j = (card_id-1)%self.grid_size

        return self.card_list[i][j].word
