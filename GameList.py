from CardGrid import CardGrid
from Game import Game
from Language import Language
from CodeGameExceptions import GameInChannelAlreadyCreated, GameNotFound, WordListFileNotFound, NotEnoughWordsInFile
import os
from Creator import Creator

class GameList(object):
    def __init__(self) -> None:
        self.game_list :dict[str, Game]= {}

    async def create_game(self, creator:Creator, nb_teams, default_word_list, server_word_list) -> Game:
        """create a game in the channel

        Args:
            creator (Creator): an object that encapsulate {
                language (Language): the language of the game
                channel_id (str): the discord channel id where the command was run
                creator_id (str): the discord user id of the user that run the command
                guild_id (str): the discord guild id where the command was run
            }
        Raises:
            GameInChannelAlreadyCreated: if a game is already created in the same channel
            WordListFileNotFound: if the word file of the guild_id is not found
            NotEnoughWordsInFile: Raised when there is not enough word in the available word list to start a game

        Returns:
            Game: the game created
        """
        if creator.channel_id in self.game_list:
            raise GameInChannelAlreadyCreated(creator.language)
        try:
            newGame = Game(creator, nb_teams, default_word_list, server_word_list)
        except (WordListFileNotFound, NotEnoughWordsInFile):
            raise
        self.game_list[creator.channel_id] = newGame
        return newGame

    async def delete_game(self, channel_id:str, language:Language):
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
        game = self.game_list.get(channel_id)
        if game is None:
            raise GameNotFound(language)
        return game
        