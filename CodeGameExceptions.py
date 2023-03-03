from Language import Language

class CodeNamesException(Exception):
    "Parent class of CodeNamesExceptions"
    def __init__(self, language:Language, message:str):
        self.salary = language
        self.message = message
        super().__init__(self.message)

class GameInChannelAlreadyCreated(CodeNamesException):
    "Raised when a User try to create a game in a channel where a game is already launched"
    def __init__(self, language:Language):
        match language:
            case Language.FR:
                message = "Une partie est déjà créée dans ce salon"
            case _:
                message = "A game is already created in this channel"
        super().__init__(language, message)

class GameNotFound(CodeNamesException):
    "Raised when a User try to access a game in a channel that does not have a game started"
    def __init__(self, language:Language):
        match language:
            case Language.FR:
                message = "Aucune partie créée. utilisez `/create` pour en créer une !"
            case _:
                message = "No game created. Use `/create` to create a game!"
        super().__init__(language, message)

class NotInGame(CodeNamesException):
    "Raised when a User try to leave a game but they're not in one"
    def __init__(self, language:Language):
        match language:
            case Language.FR:
                message = "Vous n'êtes pas dans la partie. `/join` pour la rejoindre"
            case _:
                message = "You are not in the game. `/join` to join the game"
        super().__init__(language, message)

class GameAlreadyStarted(CodeNamesException):
    "Raised when a User try to leave a game that is already started"
    def __init__(self, language:Language):
        match language:
            case Language.FR:
                message = "La partie n'a pas encoe commencée"
            case _:
                message = "The game did not start"
        super().__init__(language, message)

class NotEnoughPlayerInTeam(CodeNamesException):
    "Raised when there is less than 2 player in a team when the game start"
    def __init__(self, language:Language):
        match language:
            case Language.FR:
                message = "Les deux équipes doivent avoir au moins 2 joueurs chacune"
            case _:
                message = "Both teams need to have at least 2 players each"
        super().__init__(language, message)

class NotYourTurn(CodeNamesException):
    "Raised when a User use a command when they are not allowed to"
    def __init__(self, language:Language):
        match language:
            case Language.FR:
                message = "Ce n'est pas ton tour"
            case _:
                message = "It's not your turn"
        super().__init__(language, message)

class WordInGrid(CodeNamesException):
    "Raised when a word suggested by a Spy is present in the grid"
    def __init__(self, language:Language):
        match language:
            case Language.FR:
                message = "L'indice (`hint`) saisi est présent dans la grille"
            case _:
                message = "The `hint` provided is present in the grid"
        super().__init__(language, message)

class WrongHintNumberGiven(CodeNamesException):
    "Raised when the number of hint given is not superior or equal to 0"
    def __init__(self, language:Language):
        match language:
            case Language.FR:
                message = "Le nombre d'essai (`number of try`) saisi est inférieur ou égale à 0, il doit être `> 0`"
            case _:
                message = "The `number of try` given is smaller than 0, it must be `> 0`"
        super().__init__(language, message)

class WordNotInGrid(CodeNamesException):
    "Raised when a word proposed by a Player is NOT present in the grid"
    def __init__(self, language:Language):
        match language:
            case Language.FR:
                message = "Le mot saisi n'est pas dans la grille"
            case _:
                message = "The word provided is not in the grid"
        super().__init__(language, message)

class WrongCardIdNumberGiven(CodeNamesException):
    "Raised when the CardId given is greater than 25 or smaller than 1"
    def __init__(self, language:Language, grid_size:int):
        match language:
            case Language.FR:
                message = f"L'id de la carte (`card_id`) saisi n'est pas dans la grille [1-{grid_size}]"
            case _:
                message = f"The `card_id` provided is not in the grid [1-{grid_size}]"
        super().__init__(language, message)

class NoWordGuessed(CodeNamesException):
    "Raised when a User try to skip without having guessed any word"
    def __init__(self, language:Language):
        match language:
            case Language.FR:
                message = "Vous devez deviner (`/guess`) au moins 1 mot dans la grille pour passer votre tour"
            case _:
                message = "You must guess at least 1 word in the grid to skip your turn"
        super().__init__(language, message)

class NotGameCreator(CodeNamesException):
    "Raised when a User try to start a game that they did not create"
    def __init__(self, language:Language):
        match language:
            case Language.FR:
                message = "Vous n'êtes pas le créateur de la partie, vous ne pouvez pas lancer la partie"
            case _:
                message = "You are not the game creator, you can not start the game"
        super().__init__(language, message)
class NotYourRole(CodeNamesException):
    "Raised when a User try to use a command not intended for its role"
    def __init__(self, language:Language):
        match language:
            case Language.FR:
                message = "Vous n'êtes pas un espion, vous ne pouvez pas utiliser cette commande !"
            case _:
                message = "You are not a spy you can not use this command!"
        super().__init__(language, message)

class GameNotStarted(CodeNamesException):
    "Raised when a command is used but the game is not yet started"
    def __init__(self, language:Language):
        match language:
            case Language.FR:
                message = "La partie n'a pas commencé"
            case _:
                message = "The game did not start"
        super().__init__(language, message)