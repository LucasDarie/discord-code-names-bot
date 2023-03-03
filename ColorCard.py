import enum
from Language import Language

class ColorCard(enum.Enum):
   WHITE = "WHITE"
   RED = "RED"
   BLUE = "BLUE"
   BLACK = "BLACK"

   def display(self, language:Language=Language.EN, female=False) -> str:
      match self:
         case ColorCard.RED:
            return "🟥 " + self.translate(language, female)
         case ColorCard.BLUE:
            return "🔵 " + self.translate(language, female)
         case ColorCard.BLACK:
            return "🔳 " + self.translate(language, female)
         case _:
            return self.translate(language, female)

   def translate(self, language:Language, female=False) -> str:
      """translate Colors name in selected Language, default to English

      Args:
          language (Language): the language in wich the color name will be translate
          female (bool, optional): if the word is female (in french for example). Defaults to False.

      Returns:
          str: The color's name translated
      """
      match language:
         case Language.FR:
            match self:
               case ColorCard.RED:
                  return "ROUGE"
               case ColorCard.BLUE:
                  return "BLEUE" if female else "BLEU"
               case ColorCard.BLACK:
                  return "NOIRE" if female else "NOIRE"
               case ColorCard.WHITE:
                  return "BLANCHE" if female else "BLANC"
         case _:
            return self.value