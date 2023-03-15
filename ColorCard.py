from __future__ import annotations
import enum
from Language import Language
from interactions import Emoji, Snowflake

class ColorCard(enum.Enum):
   WHITE = "WHITE"
   RED = "RED"
   BLUE = "BLUE"
   GREEN = "GREEN"
   YELLOW = "YELLOW"
   BLACK = "BLACK"

   def display(self:ColorCard, language:Language=Language.EN, female=False) -> str:
      match self:
         case ColorCard.RED:
            return "<:red_diamond:1082757439830634547> " + self.translate(language, female)
         case ColorCard.BLUE:
            return "🔵 " + self.translate(language, female)
         case ColorCard.GREEN:
            return "<:green_triangle:1082752939619274812> " + self.translate(language, female)
         case ColorCard.YELLOW:
            return "<:yellow_star:1082752942785953852> " + self.translate(language, female)
         case ColorCard.BLACK:
            return "🔳 " + self.translate(language, female)
         case _:
            return self.translate(language, female)

   def translate(self:ColorCard, language:Language, female=False) -> str:
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
               case ColorCard.GREEN:
                  return "VERTE" if female else "VERT"
               case ColorCard.YELLOW:
                  return "JAUNE"
               case ColorCard.BLACK:
                  return "NOIRE" if female else "NOIRE"
               case ColorCard.WHITE:
                  return "BLANCHE" if female else "BLANC"
         case _:
            return self.value
         
   def get_emoji(self:ColorCard) -> Emoji:
      match self:
         case ColorCard.BLUE:
            return Emoji(name="🔵")
         case ColorCard.RED:
            return Emoji(id=Snowflake("1082757439830634547"), name="red_diamond")
         case ColorCard.GREEN:
            return Emoji(id=Snowflake("1082752939619274812"), name="green_triangle")
         case ColorCard.YELLOW:
            return Emoji(id=Snowflake("1082752942785953852"), name="yellow_star")
         # can't happen
         case _:
            return Emoji()
         
      
   @classmethod
   def get_by_string(cls, color_string:str) -> ColorCard:
      """return a ColorCard object with a string given in parameters

      Args:
          color_string (str): the ColorCard.value string of a color

      Returns:
          ColorCard: the color card object corresponding
      """
      match color_string:
         case ColorCard.BLUE.value:
            return ColorCard.BLUE

         case ColorCard.RED.value:
            return ColorCard.RED

         case ColorCard.GREEN.value:
            return ColorCard.GREEN

         case ColorCard.YELLOW.value:
            return ColorCard.YELLOW

         case ColorCard.BLACK.value:
            return ColorCard.BLACK

         case _:
            return ColorCard.WHITE