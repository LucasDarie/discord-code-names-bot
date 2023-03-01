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
    BLUE_SPY = 1
    BLUE_PLAYER = 2
    BLUE_WIN = 3
    RED_SPY = 4
    RED_PLAYER = 5
    RED_WIN = 6

    def color(self) -> ColorCard | None:
        """return the color of the team associate to each state, if no color is associate return None

        Returns:
            ColorCard | None : the color of the team associate to each state, None if no color is associate
        """
        match self:
            case State.BLUE_SPY | State.BLUE_PLAYER | State.BLUE_WIN:
                return ColorCard.BLUE
            case State.RED_SPY | State.RED_PLAYER | State.RED_WIN:
                return ColorCard.RED
            case _:
                return None

class Player(object):
    def __init__(self, user: di.User, team_color: ColorCard) -> None:
        self.user: di.User = user
        self.team_color: ColorCard = team_color
        self.isSpy: bool = False


class Game(object):
    

    def __init__(self, language:Language, creator_id : str, channel_id:str, guild_id:str) -> None:
        """constructeur of a Game object

        Args:
            language (Language): the language of the game
            creator_id (str): the discord id of the creator of the game
            channel_id (str): the channel id where the game has been created
            guild_id (str) : the guild id where the game has been created
        """
        super(Game, self).__init__()

        nb_random = random.randint(0, 1)
        team_colors = [ColorCard.BLUE, ColorCard.RED]
        
        self.language: Language = language
        self.starting_team_color:ColorCard = team_colors[nb_random]
        self.creator_id :str = creator_id
        self.channel_id:str = channel_id
        self.guild_id:str = guild_id
        self.card_grid = CardGrid(language=language, starting_team_color=self.starting_team_color)
        self.state : State = State.WAITING
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
            raise GameAlreadyStarted()
        
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
            raise GameAlreadyStarted()
        
        if user.id not in self.player_list:
            raise NotInGame()
        
        player:Player = self.player_list.pop(user.id)
        self.teams[player.team_color].remove(player)
        print(self.player_list)


    def next_state(self):
        """change the state depending on the current state
        """
        match self.state:
            case State.WAITING :
                if self.starting_team_color == ColorCard.BLUE:
                    self.state = State.BLUE_SPY
                else: 
                    self.state = State.RED_SPY

            case State.BLUE_SPY :
                self.state = State.BLUE_PLAYER
            case State.BLUE_PLAYER :
                winner = self.who_won() # State.BLUE_WIN | State.RED_WIN | None
                if winner == None:
                    self.state = State.RED_SPY
                else:
                    self.state = winner

            case State.RED_SPY :
                self.state = State.RED_PLAYER

            case State.RED_PLAYER :
                winner = self.who_won() # State.BLUE_WIN | State.RED_WIN | None
                if winner == None:
                    self.state = State.BLUE_SPY
                else:
                    self.state = winner

            case State.RED_WIN | State.BLUE_WIN:
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
            raise NotGameCreator()
        
        if self.state != State.WAITING:
            raise GameAlreadyStarted()
        
        if self.nb_player_in_team(ColorCard.RED) < 2:
            raise NotEnoughPlayerInTeam(f"{ColorCard.RED.value}")
        
        if self.nb_player_in_team(ColorCard.BLUE) < 2:
            raise NotEnoughPlayerInTeam(f"{ColorCard.BLUE.value}")
        
        self.chose_spies()

        await self.generate_grids()

        self.next_state()

    async def suggest(self, user:di.User, word:str, number:int) -> tuple[str, int]:
        """suggest a word and a number of try for a spy

        Args:
            user (di.User): the user that run the command
            word (str): the word given by the spy user
            number (int): the number of try given by the spy user

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
            raise NotInGame()
        
        if self.state == State.WAITING:
            raise GameNotStarted()

        player:Player = self.player_list[user.id]

        if not player.isSpy:
            raise NotYourRole()
        
        if self.state not in [State.BLUE_SPY, State.RED_SPY]:
            raise NotYourTurn("it's up to the players to play") # TODO message
        
        if self.state.color() != player.team_color:
            raise NotYourTurn("it's not your team's turn")
        
        if number < 0:
            raise WrongHintNumberGiven()
        
        # remove or replace special characters and keep only the first word in the possible sentence
        newWord = unidecode.unidecode(word).upper().split(" ")[0]
        if self.card_grid.is_in_grid(newWord):
            raise WordInGrid()
        
        self.last_number_hint = number
        self.last_word_suggested = newWord
        self.one_word_found = False
        self.next_state()

        return (self.last_word_suggested, self.last_number_hint)
    
    async def find_by_card_id(self, user:di.User, card_id:int) -> tuple[ColorCard, str]:
        """porposed a card id in the grid to find a word

        then call find_by_word(self, user:di.User, word:str)

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
            tuple[ColorCard, str]: the color of the finded card and the word
        """
        # can raise WrongCardIdNumberGiven
        word = self.card_grid.get_word_by_number(card_id)
        # can raise the other Exceptions mentioned in the doc
        return await self.find_by_word(user, word)
    
    async def find_by_word(self, user:di.User, word:str) -> tuple[ColorCard, str]:
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
            tuple[ColorCard, str]: the color of the finded card and the word
        """
        if user.id not in self.player_list:
            raise NotInGame()
        
        if self.state == State.WAITING:
            raise GameNotStarted()
        
        player:Player = self.player_list[user.id]

        if player.isSpy:
            raise NotYourRole()
        
        if self.state not in [State.BLUE_PLAYER, State.RED_PLAYER]:
            raise NotYourTurn("it's up to the spies to play") # TODO message
        
        if self.state.color() != player.team_color:
            raise NotYourTurn("it's not your team's turn")

        try:
            newWord = unidecode.unidecode(word).upper().split(" ")[0]
            (color, word_found) = self.card_grid.find(newWord) # can raise WordNotInGrid
            # find a wrong color
            if color != player.team_color:
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
        except WordNotInGrid as word_in_grid:
            raise word_in_grid

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
            NoWordFound: if the player didn't found any word
        """
        if user.id not in self.player_list:
            raise NotInGame()
        
        if self.state == State.WAITING:
            raise GameNotStarted()
        
        player:Player = self.player_list[user.id]

        if player.isSpy:
            raise NotYourRole()
        
        if self.state not in [State.BLUE_PLAYER, State.RED_PLAYER]:
            raise NotYourTurn("it's up to the spies to play") # TODO message
        
        if self.state.color() != player.team_color:
            raise NotYourTurn("it's not your team's turn")

        if not self.one_word_found:
            raise NoWordFound()

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
            raise GameNotStarted()
        path = f"render/{self.channel_id}{'_SPY' if isSpy else '_PLAYER'}.png"
        try:
            Image.open(path)
            return path
        except FileNotFoundError as e:
            raise e
        
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
            raise NotInGame()
        player:Player = self.player_list[user.id]
        return self.get_image_path(player.isSpy) # can raise GameNotStarted

        
        


        

        
        
        


        

        







    
