import sys
print(sys.path)
from Game import Game, State
from Language import Language
from CardGrid import CardGrid
from ColorCard import ColorCard
from Creator import Creator
import interactions as di
import enum
from CodeGameExceptions import *
import pytest
import copy

class TestGame:

    creator:Creator = Creator(
        Language.FR, 
        creator_id="123456789", 
        channel_id="123456789",
        guild_id="123456789"
    )
    game:Game = Game(
        creator=creator,
        nb_teams=2,
        default_word_list=True,
        server_word_list=False
    )
    user1:di.User = di.User(id=di.Snowflake("1234567891"), username="user1")
    user2:di.User = di.User(id=di.Snowflake("1234567892"), username="user2")
    user3:di.User = di.User(id=di.Snowflake("1234567893"), username="user3")
    user4:di.User = di.User(id=di.Snowflake("1234567894"), username="user4")

    @pytest.mark.asyncio
    async def test_nb_player_in_team(self):
        game:Game = copy.deepcopy(self.game)
        await game.join(self.user1, ColorCard.BLUE, False)
        await game.join(self.user2, ColorCard.BLUE, False)
        await game.join(self.user3, ColorCard.RED, False)
        await game.join(self.user4, ColorCard.RED, False)

        assert game.nb_player_in_team(team_color=ColorCard.BLUE) == 2
        assert game.nb_player_in_team(team_color=ColorCard.RED) == 2

    @pytest.mark.asyncio
    async def test_join(self):
        game:Game = copy.deepcopy(self.game)
        await game.join(self.user1, ColorCard.BLUE, False)
        
        if (p := game.player_list.get(str(self.user1.id))) is None: return
        
        assert p.user == self.user1
        assert game.teams[ColorCard.BLUE][0].user == self.user1
        
        assert len(game.player_list) == 1


        for i in game.team_colors:
            if i == ColorCard.BLUE:
                assert len(game.teams[i]) == 1
            else:
                assert len(game.teams[i]) == 0
        
    @pytest.mark.asyncio
    async def test_rejoin(self):
        game:Game = copy.deepcopy(self.game)


        # join BLUE with can_be_spy False
        await game.join(self.user1, ColorCard.BLUE, False)
        if((p := game.player_list.get(str(self.user1.id))) is None): return
        assert p.team_color == ColorCard.BLUE
        assert p.can_be_spy == False
        
        # join RED without changing can_be_spy state
        await game.join(self.user1, ColorCard.RED, None)
        assert p.team_color == ColorCard.RED
        assert p.can_be_spy == False

        # join RED with can_be_spy state changed
        await game.join(self.user1, ColorCard.RED, True)
        assert p.team_color == ColorCard.RED
        assert p.can_be_spy == True

        assert len(game.player_list) == 1
        for i in game.team_colors:
            if i == ColorCard.RED:
                assert len(game.teams[i]) == 1
            else:
                assert len(game.teams[i]) == 0

    def test_team_color(self):
        game:Game = Game(self.creator, 2, True, False)
        assert game.team_colors == [ColorCard.BLUE, ColorCard.RED]

        game:Game = Game(self.creator, 3, True, False)
        assert game.team_colors == [ColorCard.BLUE, ColorCard.RED, ColorCard.GREEN]

        game:Game = Game(self.creator, 4, True, False)
        assert game.team_colors == [ColorCard.BLUE, ColorCard.RED, ColorCard.GREEN, ColorCard.YELLOW]
    
    def test_state_WAITING(self):
        game:Game = copy.deepcopy(self.game)
        assert game.state == State.WAITING

    def test_WordListFileNotFound(self):
        with pytest.raises(WordListFileNotFound):
            Game(self.creator, nb_teams=2, default_word_list=True, server_word_list=True)

    def test_NotEnoughWordsInFile(self):
        creator2:Creator = copy.deepcopy(self.creator)
        creator3:Creator = copy.deepcopy(self.creator)
        creator4:Creator = copy.deepcopy(self.creator)
        creator2.guild_id = "tests/TEST_2_PLAYERS_FAILED"
        creator3.guild_id = "tests/TEST_3_PLAYERS_FAILED"
        creator4.guild_id = "tests/TEST_4_PLAYERS_FAILED"
        with pytest.raises(NotEnoughWordsInFile):
            Game(creator2, nb_teams=2, default_word_list=False, server_word_list=True)
            Game(creator3, nb_teams=3, default_word_list=False, server_word_list=True)
            Game(creator4, nb_teams=4, default_word_list=False, server_word_list=True)

        creator2.guild_id = "tests/TEST_2_PLAYERS_PASSED"
        creator3.guild_id = "tests/TEST_3_PLAYERS_PASSED"
        creator4.guild_id = "tests/TEST_4_PLAYERS_PASSED"
        try:
            Game(creator2, nb_teams=2, default_word_list=False, server_word_list=True)
            Game(creator3, nb_teams=3, default_word_list=False, server_word_list=True)
            Game(creator4, nb_teams=4, default_word_list=False, server_word_list=True)
        except NotEnoughWordsInFile as exc:
            assert False, f"Game creation with good word list raised an exception"