from __future__ import annotations
import enum
import interactions
class Language(enum.Enum):
   FR = "fr"
   EN = "en"

   def display(self) -> str:
      match self:
         case Language.FR:
            return ":flag_fr:"
         case Language.EN:
            return ":flag_gb:"
         case _:
            return ""
   
   @classmethod
   def get_discord_equivalent(cls, locale:interactions.Locale | None) -> Language:
      match locale:
         case interactions.Locale.FRENCH:
            return Language.FR
         case _:
            return Language.EN
         
   @classmethod
   def get_by_string(cls, language_string:str) -> Language:
      """return a Language object with a string given in parameters

      Args:
          language_string (str): the Language.value string of a Language

      Returns:
          Language: the language object corresponding
      """
      match language_string:
         case Language.FR.value:
            return Language.FR
         case _:
            return Language.EN