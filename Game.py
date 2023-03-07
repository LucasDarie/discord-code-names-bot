import random
from Language import Language
from CardGrid import CardGrid
from ColorCard import ColorCard
import interactions as di
import enum
from CodeGameExceptions import *
import unidecode
import grid_generator
import asyncio
from PIL import Image

class State(enum.Enum):
    WAITING = 0
    SPY = 1
    PLAYER = 2
    WIN = 3

class Player(object):
    def __init__(self, user: di.User, team_color: ColorCard) -> None:
        self.user: di.User = user
        self.team_color: ColorCard = team_color
        self.isSpy: bool = False


class Game(object):
    

    def __init__(self, language:Language, creator_id : str, channel_id:str, guild_id:str, nb_teams:int) -> None:
        """constructeur of a Game object

        Args:
            language (Language): the language of the game
            creator_id (str): the discord id of the creator of the game
            channel_id (str): the channel id where the game has been created
            guild_id (str) : the guild id where the game has been created
        """
        super(Game, self).__init__()

        self.team_colors: list[ColorCard] = [ColorCard.BLUE, ColorCard.RED, ColorCard.GREEN, ColorCard.YELLOW][:nb_teams]
        
        self.state : State = State.WAITING
        self.color_state : ColorCard = random.choice(self.team_colors)
        self.winner:ColorCard | None = None

        self.language: Language = language
        
        self.creator_id :str = creator_id
        self.channel_id:str = channel_id
        self.guild_id:str = guild_id

        self.card_grid = CardGrid(language=language, starting_team_color=self.color_state)

        self.player_list: dict[str, Player] = {}
        self.spies: dict[ColorCard, Player] = {}
        self.teams:dict[ColorCard, list[Player]] = {ColorCard.BLUE:[], ColorCard.RED:[]}

        self.last_word_suggested:str = ""
        self.last_number_hint:int = 0
        self.bonus_proposition:bool = True
        self.one_word_found:bool = False
    
    async def join(self, user: di.User, team_color: ColorCard):
        """add a user to the game. 
            If the Player is already in the game, switch there team color.

        Args:
            user (di.User): the discord user that write the command
            team_color (ColorCard): the color of the desired team

        Raises:
            GameAlreadyStarted: when the game is already started
        """
        if self.state != State.WAITING:
            raise GameAlreadyStarted(self.language)
        
        # already in Game : change team color
        if user.id in self.player_list:
            player:Player = self.player_list[user.id]
            # pop the player from there team
            self.teams[player.team_color].remove(player)
            # change team colo
            player.team_color = team_color
            self.teams[team_color].append(player)
            return
        # else
        p = Player(user=user, team_color=team_color)
        self.player_list[user.id] = p
        self.teams[team_color].append(p)


    async def leave(self, user:di.User):
        """remove a user from a game

        Args:
            user (di.User): the discord user that write the command

        Raises:
            GameAlreadyStarted: when the game is already started
            NotInGame: when the user is not in the game
        """
        if self.state != State.WAITING:
            raise GameAlreadyStarted(self.language)
        
        if user.id not in self.player_list:
            raise NotInGame(self.language)
        
        player:Player = self.player_list.pop(user.id)
        self.teams[player.team_color].remove(player)


    def next_state(self):
        """change the state depending on the current state
        """
        match self.state:
            case State.WAITING :
                self.state = State.SPY

            case State.SPY :
                self.state = State.PLAYER

            case State.PLAYER :
                if self.winner:
                    self.state = State.WIN
                    return
                
                self.state = State.SPY
                self.bonus_proposition = True
                index = self.team_colors.index(self.color_state)
                self.color_state = self.team_colors[(index+1)%len(self.team_colors)]

            case State.WIN:
                pass

    def who_won(self) -> State | None:
        """return the State of the team that win if it the case, else return None

        Returns:
            State | None: the State of the team that win if it the case, else return None
        """
        # Blue team found all cards
        if self.card_grid.remaining_words_count[ColorCard.BLUE] <= 0:
            return State.BLUE_WIN
        # Red team found all cards
        elif self.card_grid.remaining_words_count[ColorCard.RED] <= 0:
            return State.RED_WIN
        # Black card found
        elif self.card_grid.remaining_words_count[ColorCard.BLACK] <= 0:
            # by blue team
            if self.state == State.BLUE_PLAYER:
                return State.RED_WIN
            # by red team
            elif self.state == State.RED_PLAYER:
                return State.BLUE_WIN
        return None

    def nb_player_in_team(self, team_color:ColorCard) -> int:
        """return the number of player in the specified "team_color" team

        Args:
            team_color (ColorCard): the color of the team

        Returns:
            int: the number of player in the team, 0 if the color is not RED or BLUE
        """
        if team_color not in [ColorCard.RED, ColorCard.BLUE]:
            return 0
        # return the number of player in the specified team
        return len(self.teams[team_color])
        # OLD : return sum(player.team_color == team_color for player in self.player_list.values())

    def chose_spies(self):
        """Define 1 spy in each team randomly
        """
        blue_spy:Player = random.choice(self.teams[ColorCard.BLUE])
        red_spy:Player = random.choice(self.teams[ColorCard.RED])
        blue_spy.isSpy = True
        red_spy.isSpy = True
        self.spies[ColorCard.BLUE] = blue_spy
        self.spies[ColorCard.RED] = red_spy

    async def start(self, creator_id:str):
        """Starts a new game if the creator_id is the same as the User that create the game

        Args:
            creator_id (str): the id of the User running the command

        Raises:
            NotGameCreator: if the command is run by another User than the one who create the game
            GameAlreadyStarted: if the game is already started
            NotEnoughPlayerInTeam: if the number of player in a team is smaller than 2
        """
        if self.creator_id != creator_id:
            raise NotGameCreator(self.language)
        
        if self.state != State.WAITING:
            raise GameAlreadyStarted(self.language)
        
        if self.nb_player_in_team(ColorCard.RED) < 2 or self.nb_player_in_team(ColorCard.BLUE) < 2:
            raise NotEnoughPlayerInTeam(self.language)
        
        self.chose_spies()

        await self.generate_grids()

        self.next_state()

    async def suggest(self, user:di.User, word:str, number:int) -> tuple[str, int]:
        """suggest a word and a number of tries for a spy

        Args:
            user (di.User): the user that run the command
            word (str): the word given by the spy user
            number (int): the number of tries given by the spy user

        Raises:
            NotInGame: if the player is not in a game
            GameNotStarted: if the game is not yet started
            NotYourRole: if the Player is not a spy
            NotYourTurn: if it's not a spy turn
            NotYourTurn: if it's not the team of the user that play
            WrongHintNumberGiven: if the number given is smaller than 0
            WordInGrid: if the word given is in the grid

        Returns:
            tuple[str, int]: the word and the number stored
        """
        if user.id not in self.player_list:
            raise NotInGame(self.language)
        
        if self.state == State.WAITING:
            raise GameNotStarted(self.language)

        player:Player = self.player_list[user.id]

        if not player.isSpy:
            raise NotYourRole(self.language)
        
        if self.state not in [State.BLUE_SPY, State.RED_SPY]:
            raise NotYourTurn(self.language)
        
        if self.state.color() != player.team_color:
            raise NotYourTurn(self.language)
        
        if number <= 0:
            raise WrongHintNumberGiven(self.language)

        # setting more than remaining word set number of try to the number of remaining words
        remaining_words = self.card_grid.remaining_words_count[player.team_color]
        if number > remaining_words:
            number = remaining_words
        
        # remove or replace special characters and keep only the first word in the possible sentence
        newWord = unidecode.unidecode(word).upper().split(" ")[0]
        if self.card_grid.is_in_grid(newWord):
            raise WordInGrid(self.language)
        
        self.last_number_hint = number
        self.last_word_suggested = newWord
        self.one_word_found = False
        self.next_state()

        return (self.last_word_suggested, self.last_number_hint)
    
    async def guess_by_card_id(self, user:di.User, card_id:int) -> tuple[ColorCard, str]:
        """porposed a card id in the grid to guess a word

        then call guess_by_word(self, user:di.User, word:str)

        Args:
            user (di.User): the user that run the command
            card_id (int): the word given by the player

        Raises:
            NotInGame: if the player is not in a game
            GameNotStarted: if the game is not yet started
            NotYourRole: if the Player is a spy
            NotYourTurn: if it's not a Player turn
            NotYourTurn: if it's not the team of the user that play
            WrongCardIdNumberGiven: _description_

        Returns:
            tuple[ColorCard, str]: the color of the guessed card and the word
        """
        # can raise WrongCardIdNumberGiven
        word = self.card_grid.get_word_by_number(card_id)
        # can raise the other Exceptions mentioned in the doc
        return await self.guess_by_word(user, word)
    
    async def guess_by_word(self, user:di.User, word:str) -> tuple[ColorCard, str]:
        """proposed a word in the grid

        Args:
            user (di.User): the user that run the command
            word (str): the word given by the player

        Raises:
            NotInGame: if the player is not in a game
            GameNotStarted: if the game is not yet started
            NotYourRole: if the Player is a spy
            NotYourTurn: if it's not a Player turn
            NotYourTurn: if it's not the team of the user that play
            WordNotInGrid: if the word is not present in the grid

        Returns:
            tuple[ColorCard, str]: the color of the guessed card and the word
        """
        if user.id not in self.player_list:
            raise NotInGame(self.language)
        
        if self.state == State.WAITING:
            raise GameNotStarted(self.language)
        
        player:Player = self.player_list[user.id]

        if player.isSpy:
            raise NotYourRole(self.language)
        
        if self.state not in [State.BLUE_PLAYER, State.RED_PLAYER]:
            raise NotYourTurn(self.language)
        
        if self.state.color() != player.team_color:
            raise NotYourTurn(self.language)

        try:
            newWord = unidecode.unidecode(word).upper().split(" ")[0]
            (color, word_found) = self.card_grid.guess(newWord) # can raise WordNotInGrid

            self.winner = self.who_won()
            # a team win or guess a wrong color
            if self.winner != None or color != player.team_color:
                self.next_state()
            # one or more proposition left
            elif self.last_number_hint > 0:
                self.last_number_hint -= 1
                self.one_word_found = True
            # no more proposition except the bonus one
            elif self.bonus_proposition:
                self.bonus_proposition = False
                self.next_state()
            
            # generate the png grids
            await self.generate_grids()
            return (color, word_found)
        except WordNotInGrid:
            raise

    async def skip(self, user:di.User):
        """skip the turn of a player

        Args:
            user (di.User): the user

        Raises:
            NotInGame: if the player is not in a game
            GameNotStarted: if the game is not yet started
            NotYourRole: if the Player is a spy
            NotYourTurn: if it's not a Player turn
            NotYourTurn: if it's not the team of the user that play
            NoWordGuessed: if the player didn't found any word
        """
        if user.id not in self.player_list:
            raise NotInGame(self.language)
        
        if self.state == State.WAITING:
            raise GameNotStarted(self.language)
        
        player:Player = self.player_list[user.id]

        if player.isSpy:
            raise NotYourRole(self.language)
        
        if self.state not in [State.BLUE_PLAYER, State.RED_PLAYER]:
            raise NotYourTurn(self.language)
        
        if self.state.color() != player.team_color:
            raise NotYourTurn(self.language)

        if not self.one_word_found:
            raise NoWordGuessed(self.language)

        self.next_state()

    async def generate_grids(self):
        taskSpy = asyncio.get_event_loop().create_task(
            grid_generator.generateGrid(
            self.card_grid, isSpy=False, channel_id=self.channel_id
        ))
        taskPlayer = asyncio.get_event_loop().create_task(
            grid_generator.generateGrid(
            self.card_grid, isSpy=True, channel_id=self.channel_id
        ))

        await asyncio.wait([taskSpy, taskPlayer])

    #def create_grid(self):
    #    loop = asyncio.get_event_loop()
    #    loop.run_until_complete(self.generate_grids())
    #    loop.close()

    def get_image_path(self, isSpy:bool=False) -> str:
        """return the image path based on the isSpy bool passed in param

        Args:
            isSpy (bool): True for the spies grid, False for the players grid

        Raises:
            GameNotStarted: if the game is not yet started
            FileNotFoundError: if the file is not accessible for any reason

        Returns:
            str: the path of the image
        """        
        if self.state == State.WAITING:
            raise GameNotStarted(self.language)
        path = f"render/{self.channel_id}{'_SPY' if isSpy else '_PLAYER'}.png"
        try:
            Image.open(path)
            return path
        except FileNotFoundError:
            raise
        
    def get_user_image_path(self,  user: di.User) -> str:
        """return the image path for the player

        Args:
            user (di.User): the user running the command

        Raises:
            NotInGame: if the player is not in the game
            GameNotStarted: if the game is not yet started
            FileNotFoundError: if the file is not accessible for any reason

        Returns:
            str: the path of the image
        """
        if user.id not in self.player_list:
            raise NotInGame(self.language)
        player:Player = self.player_list[user.id]
        return self.get_image_path(player.isSpy) # can raise GameNotStarted

        
        


        

        
        
        


        

        







    
