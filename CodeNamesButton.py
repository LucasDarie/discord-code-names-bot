from __future__ import annotations
from ColorCard import ColorCard
from Language import Language
import enum
import interactions
from Game import Game, State

class CodeNamesButton(enum.Enum):
   BLUE_JOIN_BUTTON = "blue_join_button_id"
   RED_JOIN_BUTTON = "red_join_button_id"
   GREEN_JOIN_BUTTON = "green_join_button_id"
   YELLOW_JOIN_BUTTON = "yellow_join_button_id"
   LEAVE_BUTTON = "leave_button_id"
   SPY_BUTTON = "spy_button_id"
   START_BUTTON = "start_button_id"
   SKIP_BUTTON = "skip_button_id"
   DISPLAY_GRID_BUTTON = "display_grid_button_id"
   SPY_INTERACTION_BUTTON = "spy_interaction_button_id"
   PLAYER_INTERACTION_BUTTON = "player_interaction_button_id"

   def label(self, language:Language):
      match language:
         case Language.FR:
            match self:
               case CodeNamesButton.BLUE_JOIN_BUTTON:
                  return f"EQUIPE {ColorCard.BLUE.translate(language, female=True)}"
               case CodeNamesButton.RED_JOIN_BUTTON:
                  return f"EQUIPE {ColorCard.RED.translate(language, female=True)}"
               case CodeNamesButton.GREEN_JOIN_BUTTON:
                  return f"EQUIPE {ColorCard.GREEN.translate(language, female=True)}"
               case CodeNamesButton.YELLOW_JOIN_BUTTON:
                  return f"EQUIPE {ColorCard.YELLOW.translate(language, female=False)}"
               case CodeNamesButton.SPY_BUTTON:
                  return f"DEVENIR ESPION"
               case CodeNamesButton.LEAVE_BUTTON:
                  return f"QUITTER"
               case CodeNamesButton.START_BUTTON:
                  return f"COMMENCER"
               case CodeNamesButton.SKIP_BUTTON:
                  return "PASSER SON TOUR"
               case CodeNamesButton.DISPLAY_GRID_BUTTON:
                  return "AFFICHER LA GRILLE"
               case CodeNamesButton.SPY_INTERACTION_BUTTON:
                  return "PROPOSER UN INDICE"
               case CodeNamesButton.PLAYER_INTERACTION_BUTTON:
                  return "DEVINER UN MOT"
         case _:
            match self:
               case CodeNamesButton.BLUE_JOIN_BUTTON:
                  return f"{ColorCard.BLUE.translate(language)} TEAM"
               case CodeNamesButton.RED_JOIN_BUTTON:
                  return f"{ColorCard.RED.translate(language)} TEAM"
               case CodeNamesButton.GREEN_JOIN_BUTTON:
                  return f"{ColorCard.GREEN.translate(language)} TEAM"
               case CodeNamesButton.YELLOW_JOIN_BUTTON:
                  return f"{ColorCard.YELLOW.translate(language)} TEAM"
               case CodeNamesButton.SPY_BUTTON:
                  return f"BECOME A SPY"
               case CodeNamesButton.LEAVE_BUTTON:
                  return f"LEAVE GAME"
               case CodeNamesButton.START_BUTTON:
                  return f"START GAME"
               case CodeNamesButton.SKIP_BUTTON:
                  return "SKIP"
               case CodeNamesButton.DISPLAY_GRID_BUTTON:
                  return "DISPLAY GRID"
               case CodeNamesButton.SPY_INTERACTION_BUTTON:
                  return "SUGGEST A HINT"
               case CodeNamesButton.PLAYER_INTERACTION_BUTTON:
                  return "GUESS A WORD"

   @classmethod
   def get_by_color(cls, color:ColorCard) -> CodeNamesButton:
      match color:
         case ColorCard.BLUE:
            return CodeNamesButton.BLUE_JOIN_BUTTON
         case ColorCard.RED:
            return CodeNamesButton.RED_JOIN_BUTTON
         case ColorCard.GREEN:
            return CodeNamesButton.GREEN_JOIN_BUTTON
         case ColorCard.YELLOW:
            return CodeNamesButton.YELLOW_JOIN_BUTTON
         # can't happen
         case _:
            return CodeNamesButton.SKIP_BUTTON
         

def get_display_button(language:Language) -> list[interactions.Button]:
   return [interactions.Button(
         custom_id=CodeNamesButton.DISPLAY_GRID_BUTTON.value,
         style=interactions.ButtonStyle.SUCCESS,
         label=CodeNamesButton.DISPLAY_GRID_BUTTON.label(language),
      )]

def get_spy_interaction_button(language:Language, team_color:ColorCard) -> list[interactions.Button]:
   return [interactions.Button(
            custom_id=CodeNamesButton.SPY_INTERACTION_BUTTON.value,
            style=interactions.ButtonStyle.SECONDARY,
            label=CodeNamesButton.SPY_INTERACTION_BUTTON.label(language),
            emoji=team_color.get_emoji()
      )]

def get_player_interaction_button(language:Language, team_color:ColorCard) -> list[interactions.Button]:
   return [interactions.Button(
         custom_id=CodeNamesButton.PLAYER_INTERACTION_BUTTON.value,
         style=interactions.ButtonStyle.SECONDARY,
         label=CodeNamesButton.PLAYER_INTERACTION_BUTTON.label(language),
         emoji=team_color.get_emoji()
   )]

def get_skip_button(language:Language) -> list[interactions.Button]:
   return [interactions.Button(
            custom_id=CodeNamesButton.SKIP_BUTTON.value,
            style=interactions.ButtonStyle.SUCCESS,
            label=CodeNamesButton.SKIP_BUTTON.label(language),
      )]



def state_component(game:Game) -> list[interactions.Button] | list[interactions.ActionRow] | None:
   match game.state:
      case State.WAITING:
            return get_create_buttons(game)
      case State.SPY:
            liste = get_spy_interaction_button(game.language, game.color_state)
            liste.extend(get_display_button(game.language))
            return liste
      case State.PLAYER:
            liste = get_player_interaction_button(game.language, game.color_state)
            # don't display skip button after /suggest message
            if game.one_word_found:
               liste.extend(get_skip_button(game.language))
            return liste
      case _:
            return None
       

def get_create_buttons(game:Game) -> list[interactions.ActionRow] | None:
   join_buttons = [
      interactions.Component(
         type=interactions.ComponentType.BUTTON,
         custom_id=CodeNamesButton.get_by_color(team_color).value,
         style=interactions.ButtonStyle.SECONDARY,
         label=CodeNamesButton.get_by_color(team_color).label(game.language),
         emoji=team_color.get_emoji()
      )
      for team_color in game.team_colors
   ]
   join_buttons.append(
      interactions.Component(
         type=interactions.ComponentType.BUTTON,
         custom_id=CodeNamesButton.SPY_BUTTON.value,
         style=interactions.ButtonStyle.PRIMARY,
         label=CodeNamesButton.SPY_BUTTON.label(game.language),
         emoji=interactions.Emoji(name="🕵️‍♂️")
      )
   )
   start_leave_buttons = [
      interactions.Component(
         type=interactions.ComponentType.BUTTON,
         custom_id=CodeNamesButton.LEAVE_BUTTON.value,
         style=interactions.ButtonStyle.DANGER,
         label=CodeNamesButton.LEAVE_BUTTON.label(game.language)
      ),
      interactions.Component(
         type=interactions.ComponentType.BUTTON,
         custom_id=CodeNamesButton.START_BUTTON.value,
         style=interactions.ButtonStyle.SUCCESS,
         label=CodeNamesButton.START_BUTTON.label(game.language)
      ),
   ]
   return [interactions.ActionRow(components=join_buttons), interactions.ActionRow(components=start_leave_buttons)]
