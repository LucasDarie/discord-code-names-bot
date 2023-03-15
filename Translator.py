from Game import Game, State
import random
from ColorCard import ColorCard
from Language import Language

def get_team_message(game:Game, color:ColorCard, withSpy:bool=True) -> str:
    """return the list of player in a specific team 

    Args:
        game (Game): the game
        color (ColorCard): the team's color
        withSpy (bool, optional): chose to display or not the spy of the team. Defaults to True.

    Returns:
        str: the list of player @ for discord uses, seperatded by commas
    """
    return (str(
        [f"{random.choice([':detective:', ':man_detective:', ':woman_detective:']) if p.can_be_spy or p.isSpy else ''}<@{p.user.id}>" for p in game.teams[color] if withSpy or not p.isSpy])
        .translate({ord('['):None, ord('\''):None, ord(']'):None}))


def players_turn_message(game:Game) -> str:
    language:Language = game.language
    team_players = get_team_message(game, game.color_state, withSpy=False)
    hint = game.last_word_suggested
    tries_remaining = game.last_number_hint
    match language:
        case Language.FR:
            color_turn = game.color_state.display(language=language, female=True)
            # TODO set color emoji at the start of the sentence in every language.
            return f"Tour des JOUEURS de l'équipe {color_turn} : {team_players}\
                \nIndice: `{hint}`\nNombre d'essais restant: `{tries_remaining}{' (+1 bonus)`' if game.bonus_proposition else '`'}\
                \n`/guess` pour deviner un mot de votre équipe"
        case _:
            return f"{game.color_state.display()} PLAYERS' turn: {team_players}\
                \nHint: `{hint}`\nNumber of tries remaining: `{tries_remaining}{' (+1 bonus)`' if game.bonus_proposition else '`'}\
                \n`/guess` to guess a word of your team's color"

def final_grid_message(language:Language) -> str:
    match language:
        case Language.FR:
            return f"GRILLE FINALE :"
        case _:
            return f"FINAL GRID:"

def winning_message(game:Game) -> str:
    language:Language = game.language
    msg = ""
    for team_color in game.winners:
        match language:
            case Language.FR:
                # TODO set color emoji at the start of the sentence in every language.
                msg += f"\nL'ÉQUIPE {team_color.display(language=language, female=True)} A GAGNÉ ! GG {get_team_message(game, color=team_color)}"
            case _:
                msg += f"\n{team_color.display()} TEAM WON! GG {get_team_message(game, color=team_color)}"
            
    msg += f"\n\n{final_grid_message(language=language)}"
    return msg

def game_starting_msg(language:Language) -> str:
    match language:
        case Language.FR:
            return "La partie de `Code Names` commence ! LET'S GOOOO !"
        case _:
            return "The `Code Names` game is starting LET'S GOOO!"

def starting_message(game:Game) -> str:
    language:Language = game.language
    msg = game_starting_msg(language)+"\n"
    for team_color in game.team_colors:
        match language:
            # TODO set color emoji at the start of the sentence in every language.

            case Language.FR:
                msg += f"\nESPION {team_color.display(language=language)} : <@{game.spies[team_color].user.id}>{'🔲 `COMMENCE`' if team_color == game.color_state else ''}"
            case _:
                msg += f"\n{team_color.display()} SPY: <@{game.spies[team_color].user.id}>{'🔲 `STARTS`' if team_color == game.color_state else ''}"
                
    return msg

def remaining_words_messages(game:Game) -> str:
    language:Language = game.language
    msg=""
    for tc in game.team_colors:
        match language:
            case Language.FR:
                # TODO set color emoji at the start of the sentence in every language.
                msg += f"\nMots {tc.display(language=language)} restants : `{game.card_grid.remaining_words_count[tc]}`"
            case _:
                msg += f"\n{tc.display()} words remaining : `{game.card_grid.remaining_words_count[tc]}`"
                
    return msg

def spy_turn_message(game:Game) -> str:
    language:Language = game.language
    match language:
        case Language.FR:
            # TODO set color emoji at the start of the sentence in every language.
            return f"Tour de l'ESPION {game.color_state.display(language=language)} : <@{game.spies[game.color_state].user.id}>\n`/display` pour afficher votre propre grille\n`/suggest` pour proposer un indice à votre équipe"
        case _:
            return f"{game.color_state.display()} SPY's turn: <@{game.spies[game.color_state].user.id}>\n`/display` to see your own grid\n`/suggest` to suggest a hint to your teammates"

def state_message(game:Game) -> str:

    match game.state:
        case State.WAITING:
            return "Waiting for game creator to start the game"
        case State.SPY:
            return spy_turn_message(game)
        case State.PLAYER:
            return players_turn_message(game)
        case State.WIN:
            return winning_message(game)

def get_create_by_message(language:Language) -> str:
    match language:
        case Language.FR:
            return f"Partie créée par"
        case _:
            return f"Game created by"
 
def get_create_message(game:Game) -> str:
    language:Language = game.language
    msg_team = ""
    for team_color in game.team_colors:
        match language:
            case Language.FR:
                # TODO set color emoji at the start of the sentence in every language. 
                msg_team += f"\nÉquipe {team_color.display(language=Language, female=True)} : {get_team_message(game, color=team_color)}"
            case _:
                msg_team += f"\n{team_color.display()} team: {get_team_message(game, color=team_color)}"
                
    return f"[{str(game.language.value).upper()}] {game.language.display()} {get_create_by_message(game.language)} <@{game.creator_id}>\
            \n{msg_team}"

def get_deleted_message(player_name:str, language:Language):
    match language:
        case Language.FR:
            return f"{player_name} a supprimé la partie"
        case _:
            return f"{player_name} deleted the game"


def get_joined_message(player_name:str, color:ColorCard, language:Language):
    match language:
        case Language.FR:
            return f"{player_name} rejoint l'équipe {color.display(language=language, female=True)} !"
        case _:
            return f"{player_name} join the {color.display()} team!"

def get_left_message(player_name:str, language:Language):
    match language:
        case Language.FR:
            return f"{player_name} a quitté la partie !"
        case _:
            return f"{player_name} left the game!"

def get_global_left_message(language:Language):
    match language:
        case Language.FR:
            return f"Vous avez quitté la partie !"
        case _:
            return f"You left the game!"
        
def get_skipped_message(player_name:str, language:Language):
    match language:
        case Language.FR:
            return f"{player_name} a passé son tour..."
        case _:
            return f"{player_name} skipped their turn..."
        
def get_revealed_word_message(word_found:str, card_color:ColorCard, language:Language):
    match language:
        # TODO set color emoji at the END (or start?) of the sentence in every language.
        case Language.FR:
            return f"Le mot `{word_found}` était {card_color.display(language)}"
        case _:
            return f"The word `{word_found}` was {card_color.display()}"

def get_error_message(language:Language):
    match language:
        case Language.FR:
            return f"Une erreur est survenue. Réessayez."
        case _:
            return f"An error occured. Try again"
