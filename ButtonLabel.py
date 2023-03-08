from __future__ import annotations
from ColorCard import ColorCard
from Language import Language
import enum
class ButtonLabel(enum.Enum):
   BLUE_JOIN_BUTTON = "blue_join_button_id"
   RED_JOIN_BUTTON = "red_join_button_id"
   GREEN_JOIN_BUTTON = "green_join_button_id"
   YELLOW_JOIN_BUTTON = "yellow_join_button_id"
   LEAVE_BUTTON = "leave_button_id"
   START_BUTTON = "start_button_id"
   SKIP_BUTTON = "skip_button_id"
   DISPLAY_GRID_BUTTON = "display_grid_button_id"

   def label(self, language:Language):
      match language:
         case Language.FR:
            match self:
               case ButtonLabel.BLUE_JOIN_BUTTON:
                  return f"EQUIPE {ColorCard.BLUE.translate(language, female=True)} 🔵"
               case ButtonLabel.RED_JOIN_BUTTON:
                  return f"EQUIPE {ColorCard.RED.translate(language, female=True)} 🔴"
               case ButtonLabel.GREEN_JOIN_BUTTON:
                  return f"EQUIPE {ColorCard.GREEN.translate(language, female=True)} 🟢"
               case ButtonLabel.YELLOW_JOIN_BUTTON:
                  return f"EQUIPE {ColorCard.YELLOW.translate(language, female=False)} 🟡"
               case ButtonLabel.LEAVE_BUTTON:
                  return f"QUITTER"
               case ButtonLabel.START_BUTTON:
                  return f"COMMENCER"
               case ButtonLabel.SKIP_BUTTON:
                  return "PASSER SON TOUR"
               case ButtonLabel.DISPLAY_GRID_BUTTON:
                  return "AFFICHER LA GRILLE"
         case _:
            match self:
               case ButtonLabel.BLUE_JOIN_BUTTON:
                  return f"{ColorCard.BLUE.translate(language)} TEAM 🔵"
               case ButtonLabel.RED_JOIN_BUTTON:
                  return f"{ColorCard.RED.translate(language)} TEAM 🔴"
               case ButtonLabel.GREEN_JOIN_BUTTON:
                  return f"{ColorCard.GREEN.translate(language)} TEAM 🟢"
               case ButtonLabel.YELLOW_JOIN_BUTTON:
                  return f"{ColorCard.YELLOW.translate(language)} TEAM 🟡"
               case ButtonLabel.LEAVE_BUTTON:
                  return f"LEAVE GAME"
               case ButtonLabel.START_BUTTON:
                  return f"START GAME"
               case ButtonLabel.SKIP_BUTTON:
                  return "SKIP"
               case ButtonLabel.DISPLAY_GRID_BUTTON:
                  return "DISPLAY GRID"
               
   @classmethod
   def get_by_color(cls, color:ColorCard) -> ButtonLabel:
      match color:
         case ColorCard.BLUE:
            return ButtonLabel.BLUE_JOIN_BUTTON
         case ColorCard.RED:
            return ButtonLabel.RED_JOIN_BUTTON
         case ColorCard.GREEN:
            return ButtonLabel.GREEN_JOIN_BUTTON
         case ColorCard.YELLOW:
            return ButtonLabel.YELLOW_JOIN_BUTTON