import enum
class ColorCard(enum.Enum):
   WHITE = "WHITE"
   RED = "RED"
   BLUE = "BLUE"
   BLACK = "BLACK"

   def display(self) -> str:
      match self:
         case ColorCard.RED:
            return "🟥 " + self.value
         case ColorCard.BLUE:
            return "🔵 " + self.value
         case ColorCard.BLACK:
            return "🔳 " + self.value
         case _:
            return self.value