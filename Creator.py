from Language import Language

class Creator(object):
    """
    A class to represent a creator of a game.
    Args:
        language (Language): The language of the creator.
        creator_id (str): The id of the creator.
        channel_id (str): The id of the channel where the game is created.
        guild_id (str): The id of the guild where the game is created.
    """
    def __init__(self, language:Language, creator_id : str, channel_id:str, guild_id:str) -> None:
        self.language: Language = language
        self.creator_id : str = creator_id
        self.channel_id:str = channel_id
        self.guild_id:str = guild_id