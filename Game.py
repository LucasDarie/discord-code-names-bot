from Language import Language
from CardGrid import CardGrid
from ColorCard import ColorCard
import interactions as di
import enum
from CodeGameExceptions import *

class State(enum.Enum):
    WAITING = 0
    STARTING = 1
    BLUE_SPY = 2
    BLUE_PLAYER = 3
    BLUE_WIN = 4
    RED_SPY = 5
    RED_PLAYER = 6
    RED_WIN = 7
    FINISHED = 8

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
        super(CardGrid, self).__init__()

        self.creator :str = creator_id
        self.channel_id:str = channel_id
        self.guild_id:str = guild_id
        self.card_grid = CardGrid(language=language)
        self.state : State = State.WAITING
        self.player_list: dict[str:Player] = {}


    def join(self, user: di.User, team_color: ColorCard):
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
            player.team_color = team_color
            return
        # else
        self.player_list[user.id] = Player(user=user, team_color=team_color)

    def leave(self, user:di.User):
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
        
        self.player_list.pop(user.id)







    
