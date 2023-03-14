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
from Creator import Creator

class State(enum.Enum):
    WAITING = 0
    SPY = 1
    PLAYER = 2
    WIN = 3

class Player(object):
    def __init__(self, user: di.User, team_color: ColorCard, can_be_spy:bool=False) -> None:
        self.user: di.User = user
        self.team_color: ColorCard = team_color
        self.isSpy: bool = False
        self.can_be_spy: bool = can_be_spy


class Game(object):
    

    def __init__(self, creator:Creator, nb_teams:int, default_word_list:bool, server_word_list:bool) -> None:
        """constructeur of a Game object

        Args:
            language (Language): the language of the game
            creator_id (str): the discord id of the creator of the game
            channel_id (str): the channel id where the game has been created
            guild_id (str) : the guild id where the game has been created

        Raises:
            WordListFileNotFound: if the word file of the guild_id is not found
            NotEnoughWordsInFile: Raised when there is not enough word in the available word list to start a game
        """
        super(Game, self).__init__()
        self.team_colors: list[ColorCard] = [ColorCard.BLUE, ColorCard.RED, ColorCard.GREEN, ColorCard.YELLOW][:nb_teams]
        self.nb_minimum_player: int = 2 # TODO : solo mode
        
        self.state : State = State.WAITING
        self.color_state : ColorCard = random.choice(self.team_colors)
        self.winners:list[ColorCard] = []

        self.language: Language = creator.language
        
        self.creator_id :str = creator.creator_id
        self.channel_id:str = creator.channel_id
        self.guild_id:str = creator.guild_id

        try:
            self.card_grid = CardGrid(
                language=creator.language, 
                starting_team_color=self.color_state, 
                team_list=self.team_colors,
                default_word_list=default_word_list, 
                guild_id_for_list=creator.guild_id if server_word_list else None
            )
        except (WordListFileNotFound, NotEnoughWordsInFile):
            raise

        self.player_list: dict[str, Player] = {}
        self.spies: dict[ColorCard, Player] = {}
        self.teams:dict[ColorCard, list[Player]] = {color:[] for color in self.team_colors}

        self.last_word_suggested:str = ""
        self.last_number_hint:int = 0
        self.bonus_proposition:bool = True
        self.one_word_found:bool = False
    
    async def join(self, user: di.User, team_color: ColorCard, can_be_spy: bool | None):
        """add a user to the game. 
            If the Player is already in the game, switch there team color.

        Args:
            user (di.User): the discord user that write the command
            team_color (ColorCard): the color of the desired team
            can_be_spy (bool | None): indicate if the player want to be a spy for the game. if can_be_spy == None : invert the bool

        Raises:
            GameAlreadyStarted: when the game is already started
            TeamNotAvailable: when the team given is not is the teams list of the game
        """
        if self.state != State.WAITING:
            raise GameAlreadyStarted(self.language)

        if team_color not in self.team_colors:
            raise TeamNotAvailable(self.language)
        
        # already in Game : change team color
        if user.id in self.player_list:
            player:Player = self.player_list[user.id]
            # pop the player from there team
            self.teams[player.team_color].remove(player)
            # change team color
            player.team_color = team_color
            # change can_be_spy state
            if can_be_spy != None :
                player.can_be_spy = can_be_spy

            self.teams[team_color].append(player)
            return
        # else
        p = Player(user=user, team_color=team_color, can_be_spy=can_be_spy)
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
                if len(self.winners) > 0:
                    self.state = State.WIN
                    return
                # else
                self.state = State.SPY
                self.bonus_proposition = True
                index = self.team_colors.index(self.color_state)
                # change the color of the team for the next team to play
                self.color_state = self.team_colors[(index+1)%len(self.team_colors)]

            case State.WIN:
                pass

    def is_won(self) -> bool:
        """return if the game is won by some team(s). Edit the value of self.winners with the list of winners teams

        Returns:
            bool: True if a or some team(s) won the game
        """
        i = 0
        while i < len(self.team_colors):
            color_team = self.team_colors[i]
            i += 1
            if self.card_grid.remaining_words_count[color_team] <= 0:
                self.winners = [color_team]
                return True
        # exit condition : i >= len(self.team_colors) : no winner

        # Black card found
        if self.card_grid.remaining_words_count[ColorCard.BLACK] <= 0:
            # return all teams except the team that found black card
            temp_team_colors = self.team_colors.copy()
            temp_team_colors.remove(self.color_state)
            self.winners = temp_team_colors
            return True
        return False

    def nb_player_in_team(self, team_color:ColorCard) -> int:
        """return the number of player in the specified "team_color" team

        Args:
            team_color (ColorCard): the color of the team

        Returns:
            int: the number of player in the team, 0 if the color is not in team_colors
        """
        if team_color not in self.team_colors:
            return 0
        # return the number of player in the specified team
        return len(self.teams[team_color])

    def chose_spies(self):
        """Define 1 spy in each team randomly
        """
        for team_color in self.team_colors:
            # get the list of pretenders in the team
            spy_pretenders = [player for player in self.teams[team_color] if player.can_be_spy]

            # reset can_be_spy (for display)
            for player in spy_pretenders:
                player.can_be_spy = False

            # if no spy pretender : chose a spy in the whole team
            if len(spy_pretenders) == 0:
                spy_pretenders = self.teams[team_color]
            spy: Player = random.choice(spy_pretenders)
            spy.isSpy = True
            self.spies[team_color] = spy

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
        
        i = 0
        while i < len(self.team_colors):
            if self.nb_player_in_team(self.team_colors[i]) < self.nb_minimum_player:
                raise NotEnoughPlayerInTeam(self.language)
            i += 1
        
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
        
        if self.state != State.SPY:
            raise NotYourTurn(self.language)
        
        if self.color_state != player.team_color:
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
        
        if self.state != State.PLAYER:
            raise NotYourTurn(self.language)
        
        if self.color_state != player.team_color:
            raise NotYourTurn(self.language)

        try:
            newWord = unidecode.unidecode(word).upper().split(" ")[0]
            (color, word_found) = self.card_grid.guess(newWord) # can raise WordNotInGrid

            isWon = self.is_won()
            # a team won or player guessed a wrong color
            if isWon or color != player.team_color:
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
        
        if self.state != State.PLAYER:
            raise NotYourTurn(self.language)
        
        if self.color_state != player.team_color:
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

    def invert_can_be_spy(self, user:di.User):
        """invert the state of 'can_be_spy' field of the player

        Args:
            user (di.User): the user running the command

        Raises:
            NotInGame: if the player is not in the game
            GameAlreadyStarted: when the game is already started
        """
        if user.id not in self.player_list:
            raise NotInGame(self.language)
        
        if self.state != State.WAITING:
            raise GameAlreadyStarted(self.language)
        
        player:Player = self.player_list[user.id]
        player.can_be_spy = not player.can_be_spy

    def get_all_pretenders_id(self) -> list[int]:
        return [p.user.id for p in self.player_list.values() if p.can_be_spy]
        


        

        
        
        


        

        







    
