class GameInChannelAlreadyCreated(Exception):
    "Raised when a User try to create a game in a channel where a game is already launched"
    pass

class GameNotFound(Exception):
    "Raised when a User try to access a game in a channel that does not have a game started"
    pass

class NotInGame(Exception):
    "Raised when a User try to leave a game but they're not in one"
    pass

class GameAlreadyStarted(Exception):
    "Raised when a User try to leave a game that is already started"
    pass

class NotEnoughPlayerInTeam(Exception):
    "Raised when there is less than 2 player in a team when the game start"
    pass

class NotYourTurn(Exception):
    "Raised when a User use a command when they are not allowed to"
    pass

class WordInGrid(Exception):
    "Raised when a word suggested by a Spy is present in the grid"
    pass

class WrongHintNumberGiven(Exception):
    "Raised when the number of hint given is not superior or equal to 0"
    pass

class WordNotInGrid(Exception):
    "Raised when a word proposed by a Player is NOT present in the grid"
    pass

class WrongCardIdNumberGiven(Exception):
    "Raised when the CardId given is greater than 25 or smaller than 1"
    pass

class NoWordFound(Exception):
    "Raised when a User try to skip without having found (proposed) any word"
    pass

class NotGameCreator(Exception):
    "Raised when a User try to start a game that they did not create"
    pass
class NotYourRole(Exception):
    "Raised when a User try to use a command not intended for its role"

class GameNotStarted(Exception):
    "Raised when a command is used but the game is not yet started"