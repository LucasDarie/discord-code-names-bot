from __future__ import annotations
from ColorCard import ColorCard
from Language import Language
import enum
import interactions
from Game import Game, State

class CodeNamesModal(enum.Enum):
   GUESS_TEXT_INPUT = "blue_join_button_id"
   SUGGEST_TEXT_INPUT = "red_join_button_id"
   NB_TRY_TEXT_INPUT = "green_join_button_id"

   def label(self, language:Language):
      match language:
         case Language.FR:
            match self:
               case CodeNamesModal.GUESS_TEXT_INPUT:
                  return f"Mot à deviner :"
               case CodeNamesModal.SUGGEST_TEXT_INPUT:
                  return f"Indice :"
               case CodeNamesModal.NB_TRY_TEXT_INPUT:
                  return f"Nombre d'essai :"
         case _:
            match self:
               case CodeNamesModal.GUESS_TEXT_INPUT:
                  return f"Guess a word in the grid:"
               case CodeNamesModal.SUGGEST_TEXT_INPUT:
                  return f"Hint:"
               case CodeNamesModal.NB_TRY_TEXT_INPUT:
                  return f"Number of try:"

def state_modal(game:Game) -> interactions.Modal | None:
    title = ""
    match game.state:
        case State.SPY:
            match game.language:
                case Language.FR:
                    title = f"ESPION {game.color_state.display(game.language)}"
                case _:
                    title = f"{game.color_state.display()} SPY"
            return interactions.Modal(
                title=title,
                custom_id="spy_modal",
                components=get_spy_text_input(game.language) # type: ignore
            )
        case State.PLAYER:
            match game.language:
                case Language.FR:
                    title = f"JOUEUR {game.color_state.display(game.language)}"
                case _:
                    title = f"{game.color_state.display()} PLAYER"
    return interactions.Modal(
        title=title,
        custom_id="player_modal",
        components=get_player_text_input(game.language), # type: ignore
    )

def get_player_text_input(language:Language) -> list[interactions.TextInput]:
   return [_get_guess_text_input(language=language)]

def get_spy_text_input(language:Language) -> list[interactions.TextInput]:
   return [_get_suggest_text_input(language=language), _get_nb_try_text_input(language)]
         

def _get_guess_text_input(language:Language) -> interactions.TextInput:
    return interactions.TextInput(
       type=interactions.ComponentType.INPUT_TEXT,
        style=interactions.TextStyleType.SHORT, 
        label=CodeNamesModal.GUESS_TEXT_INPUT.label(language),
        custom_id=CodeNamesModal.GUESS_TEXT_INPUT.value,
        required=True,
    )

def _get_suggest_text_input(language:Language) -> interactions.TextInput:
    return interactions.TextInput(
       type=interactions.ComponentType.INPUT_TEXT,
        style=interactions.TextStyleType.SHORT, 
        label=CodeNamesModal.SUGGEST_TEXT_INPUT.label(language),
        custom_id=CodeNamesModal.SUGGEST_TEXT_INPUT.value,
        required=True,
    )

def _get_nb_try_text_input(language:Language) -> interactions.TextInput:
    return interactions.TextInput(
       type=interactions.ComponentType.INPUT_TEXT,
        style=interactions.TextStyleType.SHORT, 
        label=CodeNamesModal.NB_TRY_TEXT_INPUT.label(language),
        custom_id=CodeNamesModal.NB_TRY_TEXT_INPUT.value,

        required=True,
    )

