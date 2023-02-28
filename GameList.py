from CardGrid import CardGrid
from Game import Game
from Language import Language
from CodeGameExceptions import GameInChannelAlreadyCreated, GameNotFound

class GameList(object):
    def __init__(self) -> None:
        self.game_list :dict[str:Game]= {}

    async def create_game(self, language:Language, channel_id:str, creator_id:str, guild_id:str):
        if channel_id in self.game_list:
            raise GameInChannelAlreadyCreated()
        newGame = Game(language, creator_id, channel_id, guild_id)
        self.game_list[channel_id] = newGame
        return newGame

    async def delete_game(self, channel_id):
        if channel_id in self.game_list:
            raise GameNotFound()
        self.game_list.pop(channel_id)
    
    async def get_game(self, channel_id) -> Game:
        if channel_id not in self.game_list:
            raise GameNotFound()
        return self.game_list.get(channel_id)
        