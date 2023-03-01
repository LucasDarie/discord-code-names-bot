from ColorCard import ColorCard

class Card(object):
    def __init__(self, word:str, color:ColorCard) -> None:
        super(Card, self).__init__()
        
        self.word: str = word
        self.guessed:bool = False
        self.color:ColorCard = color

    def __str__(self) -> str:
        return f"{self.word}, {self.color.value}, {self.guessed}"
    
    def __repr__(self) -> str:
        return f"{{{self.word}, {self.color.value}, {self.guessed}}}"
        
        