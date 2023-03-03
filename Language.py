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
   
   def get_discord_equivalent(locale:interactions.Locale):
      match locale:
         case interactions.Locale.FRENCH:
            return Language.FR
         case _:
            return Language.EN