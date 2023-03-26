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

def get_create_modal(language:Language) -> interactions.Modal:
    match language:
        case Language.FR:
            title = f"Créer une Partie de Code Names"
        case _:
            title = f"Create a Code Names Game"
    return interactions.Modal(
        title=title,
        custom_id="player_modal",
        components=get_player_text_input(), # type: ignore
    )

""" 
@interactions.option(
    description="Chose the language of the game",
    type=interactions.OptionType.STRING,
    name="language",
    required=True,
    choices=[
        interactions.Choice(name="French", value=Language.FR.value),
        interactions.Choice(name="English", value=Language.EN.value)
    ] 
)
@interactions.option(
    description="Chose the number of team of the game",
    type=interactions.OptionType.INTEGER,
    name="nb_teams",
    required=True,
    choices=[
        interactions.Choice(name="1", value=1),
        interactions.Choice(name="2", value=2),
        interactions.Choice(name="3", value=3),
        interactions.Choice(name="4", value=4)
    ] 
)
@interactions.option(
    description="Select True if you want to play with the default word list of the selected language, else False",
    name="default_word_list",
    type=interactions.OptionType.BOOLEAN,
    required=False
)
@interactions.option(
    description="Select True if you want to play with your server word list, else False",
    name="server_word_list",
    type=interactions.OptionType.BOOLEAN,
    required=False
)
 """

def create_language_option(language:Language) -> interactions.SelectOption:
    return interactions.SelectOption(
                label="I'm a cool option1. :)",
                value="internal_option_value1",
                description="some extra info about me! :D1",
            )

def get_language_select() -> list[interactions.SelectMenu]:
    return [interactions.SelectMenu(
        options=[
            interactions.SelectOption(
                label="I'm a cool option1. :)",
                value="internal_option_value1",
                description="some extra info about me! :D1",
            ), 
            interactions.SelectOption(
                label="I'm a cool option2. :)",
                value="internal_option_value2",
                description="some extra info about me! :D2",
            )
        ],
        placeholder="Check out my options. :)",
        custom_id="menu_component1",
    )]


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

