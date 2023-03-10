from Language import Language

class Creator(object):
    def __init__(self, language:Language, creator_id : str, channel_id:str, guild_id:str) -> None:
        self.language: Language = language
        self.creator_id : str = creator_id
        self.channel_id:str = channel_id
        self.guild_id:str = guild_id