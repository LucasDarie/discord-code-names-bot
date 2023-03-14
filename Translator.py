import enum

class Translator(enum.Enum):
    PLAYER_LIST=0
    PLAYER_TURN=1
    WORDS_REMAINING=2
    WINNING=3
    STARTING=4
    SPY_TURN=5
    CREATE=6
    DELETE=7
    JOIN=8
    LEAVE=9
    LEAVE_GLOBAL=10