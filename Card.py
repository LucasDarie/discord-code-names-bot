from ColorCard import ColorCard

class Card(object):
    def __init__(self, word:str, color:ColorCard) -> None:
        super(Card, self).__init__()
        
        self.word: str = word
        self.finded:bool = False
        self.color:ColorCard = color

    def __str__(self) -> str:
        return f"{self.word}, {self.color.value}, {self.finded}"
    
    def __repr__(self) -> str:
        return f"{{{self.word}, {self.color.value}, {self.finded}}}"
        
        