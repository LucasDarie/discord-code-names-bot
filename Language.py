import enum
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