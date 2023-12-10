import asyncio
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
    
    @pytest.fixture
    def creator(self):
        return Creator(
            Language.FR, 
            creator_id="123456789", 
            channel_id="123456789",
            guild_id="123456789"
        )

    @pytest.fixture
    def game(self, creator):
        return Game(
            creator=creator,
            nb_teams=2,
            default_word_list=True,
            server_word_list=False
        )

    @pytest.fixture
    def user1(self):
        yield di.User(id=di.Snowflake(1234567891), username="user1", avatar="", client="") # type: ignore
    @pytest.fixture
    def user2(self):
        return di.User(id=di.Snowflake(1234567892), username="user2", avatar="", client="") # type: ignore
        
    @pytest.fixture
    def user3(self):
        return di.User(id=di.Snowflake(1234567893), username="user3", avatar="", client="") # type: ignore
    @pytest.fixture
    def user4(self):
        return di.User(id=di.Snowflake(1234567894), username="user4", avatar="", client="") # type: ignore


    @pytest.mark.asyncio
    async def test_nb_player_in_team(self, game, user1, user2, user3, user4):
        await game.join(user1, ColorCard.BLUE, False)
        await game.join(user2, ColorCard.BLUE, False)
        await game.join(user3, ColorCard.RED, False)
        await game.join(user4, ColorCard.RED, False)

        assert game.nb_player_in_team(team_color=ColorCard.BLUE) == 2
        assert game.nb_player_in_team(team_color=ColorCard.RED) == 2

    @pytest.mark.asyncio
    async def test_join(self, game:Game, user1:di.User):
        await game.join(user1, ColorCard.BLUE, False)
        
        if (p := game.player_list.get(str(user1.id))) is None: return
        
        assert p.user == user1
        assert game.teams[ColorCard.BLUE][0].user == user1
        
        assert len(game.player_list) == 1


        for i in game.team_colors:
            if i == ColorCard.BLUE:
                assert len(game.teams[i]) == 1
            else:
                assert len(game.teams[i]) == 0
        
    @pytest.mark.asyncio
    async def test_rejoin(self, game:Game, user1:di.User):


        # join BLUE with can_be_spy False
        await game.join(user1, ColorCard.BLUE, False)
        if((p := game.player_list.get(str(user1.id))) is None): return
        assert p.team_color == ColorCard.BLUE
        assert p.can_be_spy == False
        
        # join RED without changing can_be_spy state
        await game.join(user1, ColorCard.RED, None)
        assert p.team_color == ColorCard.RED
        assert p.can_be_spy == False

        # join RED with can_be_spy state changed
        await game.join(user1, ColorCard.RED, True)
        assert p.team_color == ColorCard.RED
        assert p.can_be_spy == True

        assert len(game.player_list) == 1
        for i in game.team_colors:
            if i == ColorCard.RED:
                assert len(game.teams[i]) == 1
            else:
                assert len(game.teams[i]) == 0

    def test_team_color(self, creator:Creator):
        game:Game = Game(creator, 2, True, False)
        assert game.team_colors == [ColorCard.BLUE, ColorCard.RED]

        game:Game = Game(creator, 3, True, False)
        assert game.team_colors == [ColorCard.BLUE, ColorCard.RED, ColorCard.GREEN]

        game:Game = Game(creator, 4, True, False)
        assert game.team_colors == [ColorCard.BLUE, ColorCard.RED, ColorCard.GREEN, ColorCard.YELLOW]
    
    def test_state_WAITING(self, game:Game):
        assert game.state == State.WAITING

    def test_WordListFileNotFound(self, creator:Creator):
        with pytest.raises(WordListFileNotFound):
            Game(creator, nb_teams=2, default_word_list=True, server_word_list=True)

    def test_NotEnoughWordsInFile(self, creator:Creator):
        creator2:Creator = copy.deepcopy(creator)
        creator3:Creator = copy.deepcopy(creator)
        creator4:Creator = copy.deepcopy(creator)
        creator2.guild_id = "tests/TEST_2_PLAYERS_FAILED"
        creator3.guild_id = "tests/TEST_3_PLAYERS_FAILED"
        creator4.guild_id = "tests/TEST_4_PLAYERS_FAILED"
        with pytest.raises(NotEnoughWordsInFile):
            Game(creator2, nb_teams=2, default_word_list=False, server_word_list=True)
        with pytest.raises(NotEnoughWordsInFile):
            Game(creator3, nb_teams=3, default_word_list=False, server_word_list=True)
        with pytest.raises(NotEnoughWordsInFile):
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


    @pytest.mark.asyncio
    async def test_leave(self, game:Game, user1:di.User, user2:di.User, user3:di.User, user4:di.User):
        
        await game.join(user1, ColorCard.BLUE, False)
        await game.join(user2, ColorCard.BLUE, False)
        await game.join(user3, ColorCard.RED, False)
        await game.join(user4, ColorCard.RED, False)

        assert len(game.player_list) == 4
        assert len(game.teams[ColorCard.BLUE]) == 2
        assert len(game.teams[ColorCard.RED]) == 2

        await game.leave(user1)
        assert len(game.player_list) == 3
        assert len(game.teams[ColorCard.BLUE]) == 1
        assert len(game.teams[ColorCard.RED]) == 2

        await game.leave(user3)
        assert len(game.player_list) == 2
        assert len(game.teams[ColorCard.BLUE]) == 1
        assert len(game.teams[ColorCard.RED]) == 1

        await game.leave(user2)
        assert len(game.player_list) == 1
        assert len(game.teams[ColorCard.BLUE]) == 0
        assert len(game.teams[ColorCard.RED]) == 1

        await game.leave(user4)
        assert len(game.player_list) == 0
        assert len(game.teams[ColorCard.BLUE]) == 0
        assert len(game.teams[ColorCard.RED]) == 0

    @pytest.mark.asyncio
    async def test_NotInGame(self, game:Game, user1:di.User, user2:di.User, user3:di.User, user4:di.User):
        await game.join(user1, ColorCard.BLUE, False)
        await game.join(user2, ColorCard.BLUE, False)
        await game.join(user3, ColorCard.RED, False)
        await game.join(user4, ColorCard.RED, False)

        assert len(game.player_list) == 4
        assert len(game.teams[ColorCard.BLUE]) == 2
        assert len(game.teams[ColorCard.RED]) == 2

        await game.invert_can_be_spy(user1)
        await game.leave(user4)

        with pytest.raises(NotInGame): await game.leave(user4)

        with pytest.raises(NotInGame): await game.invert_can_be_spy(user4)

        assert len(game.player_list) == 3

    @pytest.mark.asyncio
    async def test_GameAlreadyStarted(self, game:Game, creator:Creator, user1:di.User, user2:di.User, user3:di.User, user4:di.User):
        await game.join(user1, ColorCard.BLUE, False)
        await game.join(user2, ColorCard.BLUE, False)
        await game.join(user3, ColorCard.RED, False)
        await game.join(user4, ColorCard.RED, False)

        assert len(game.player_list) == 4
        assert len(game.teams[ColorCard.BLUE]) == 2
        assert len(game.teams[ColorCard.RED]) == 2

        await game.start(creator.creator_id)
        assert game.state == State.SPY

        with pytest.raises(GameAlreadyStarted): await game.leave(user3)
        with pytest.raises(GameAlreadyStarted): await game.join(user4, ColorCard.BLUE, False)
        with pytest.raises(GameAlreadyStarted): await game.start(creator.creator_id)
        with pytest.raises(GameAlreadyStarted): await game.invert_can_be_spy(user4)

        assert len(game.player_list) == 4
        assert len(game.teams[ColorCard.BLUE]) == 2
        assert len(game.teams[ColorCard.RED]) == 2

    @pytest.mark.asyncio
    async def test_NotGameCreator(self, game:Game, user1:di.User, user2:di.User, user3:di.User, user4:di.User):
        await game.join(user1, ColorCard.BLUE, False)
        await game.join(user2, ColorCard.BLUE, False)
        await game.join(user3, ColorCard.RED, False)
        await game.join(user4, ColorCard.RED, False)

        with pytest.raises(NotGameCreator): await game.start(str(user1.id))

    @pytest.mark.asyncio
    async def test_next_state(self, game:Game, creator:Creator, user1:di.User, user2:di.User, user3:di.User, user4:di.User):
        await game.join(user1, ColorCard.BLUE, False)
        await game.join(user2, ColorCard.BLUE, False)
        await game.join(user3, ColorCard.RED, False)
        await game.join(user4, ColorCard.RED, False)

        assert game.state == State.WAITING
        await game.start(creator.creator_id)

        assert game.state == State.SPY
        game.next_state()
        assert game.state == State.PLAYER
        game.next_state()
        assert game.state == State.SPY
        game.next_state()
        assert game.state == State.PLAYER
        
        game.winners.append(ColorCard.BLUE) # add a Winner team

        game.next_state()
        assert game.state == State.WIN