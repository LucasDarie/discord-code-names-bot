from CardGrid import CardGrid
from Game import Game
from Language import Language
from CodeGameExceptions import GameInChannelAlreadyCreated, GameNotFound
import os

class GameList(object):
    def __init__(self) -> None:
        self.game_list :dict[str:Game]= {}

    async def create_game(self, language:Language, channel_id:str, creator_id:str, guild_id:str) -> Game:
        """create a game in the channel

        Args:
            language (Language): the language of the game
            channel_id (str): the discord channel id where the command was run
            creator_id (str): the discord user id of the user that run the command
            guild_id (str): the discord guild id where the command was run

        Raises:
            GameInChannelAlreadyCreated: if a game is already created in the same channel

        Returns:
            Game: the game created
        """
        if channel_id in self.game_list:
            raise GameInChannelAlreadyCreated(language)
        newGame = Game(language, creator_id, channel_id, guild_id)
        self.game_list[channel_id] = newGame
        return newGame

    async def delete_game(self, channel_id, language:Language):
        """delete the game of a channel

        Args:
            channel_id (str): the id of the channel

        Raises:
            GameNotFound: if there is no game created in this channel
        """
        if channel_id not in self.game_list:
            raise GameNotFound(language)
        # remove files
        [os.remove(os.path.join('render/', filename)) for filename in os.listdir('render/') if filename.startswith(f'{channel_id}') and filename.endswith('.png')]
        self.game_list.pop(channel_id)
    
    async def get_game(self, channel_id:str, language:Language) -> Game:
        """return the game of the channel

        Args:
            channel_id (str): the id of the channel

        Raises:
            GameNotFound: if there is no game created in this channel

        Returns:
            Game: the game of the channel
        """
        if channel_id not in self.game_list:
            raise GameNotFound(language)
        return self.game_list.get(channel_id)
        