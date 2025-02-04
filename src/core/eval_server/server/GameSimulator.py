import random

from GameState import GameState
from Helper import Action


class GameSimulator:
    """
    Class that will generate randomized list of actions.
    Actions will be displayed on the evaluation server UI for the
    players to follow.
    """
    def __init__(self, num_players, does_not_have_visualizer):
        # create the players
        self.game_state     = GameState()
        self.num_players    = num_players

        # generate the list of action and moves to perform
        self.num_moves_gun  = 0
        self.num_moves_ai   = 0

        self.moves      = self._init_moves (num_players)
        self.move_index = 0  # move to be made
        self.num_moves  = len(self.moves)

        self.does_not_have_visualizer = does_not_have_visualizer  # some teams do not have visualizer

    def _init_moves(self, num_players):
        """
        Create a random list of moves
        """
        # randomize the size of the list
        _r = random.randint(0, 1)

        actions_1 = Action.init_list(_r)
        n = len(actions_1)

        _g = actions_1.count(Action.shoot)
        self.num_moves_gun += _g
        self.num_moves_ai  += n-_g

        if num_players == 2:
            actions_2 = Action.init_list(_r)
            _g = actions_2.count(Action.shoot)
            self.num_moves_gun += _g
            self.num_moves_ai  += n-_g
        else:
            actions_2 = [Action.none]*n

        # generate random positions to move
        if num_players == 2:
            m = n//2
            positions_1 = [1]
            positions_2 = [3]
            self._get_positions (m, positions_1)
            self._get_positions (m, positions_2)
            # adding the disconnect move
            positions_1.extend([0, 2])
            positions_2.extend([3, 4])
            m = n-m
            self._get_positions (m, positions_1)
            self._get_positions (m, positions_2)

            # adding the disconnect move
            positions_1[n-3] = 0
            positions_2[n-3] = 0
        else:
            positions_1 = [1]*(n-4)
            # add the disconnect position
            positions_1.append(0)
            positions_1.extend([1]*(n-len(positions_1)))

            positions_2 = [1]*n

        # use the 4 lists to make a single list of moves
        moves = []
        for i in range(n):
            moves.append(_Move(actions_1[i], positions_1[i], actions_2[i], positions_2[i]))

        return moves

    @staticmethod
    def _get_positions(n, ret):
        """ Generates a list of moves """
        prev_pos = ret[-1]

        for _ in range(n):
            r = random.random()
            if r < 0.49:
                next_pos = prev_pos + 1
            elif r < 0.98:
                next_pos = prev_pos + 3
            else:
                next_pos = prev_pos
            next_pos = (next_pos % 4)   # modulo arithmetic with translation
            if next_pos == 0:
                next_pos = 4

            prev_pos = next_pos
            ret.append(prev_pos)

    def current_move(self):
        """ The text message of number of moves to be displayed on the UI """
        return "{} / {}".format(self.move_index+1, self.num_moves)

    def current_positions (self):
        """ The positions the player is supposed to be in """
        move = self.moves[self.move_index]
        return move.position_1, move.position_2

    def current_actions (self):
        """ The actions performed by the players """
        move = self.moves[self.move_index]
        return move.action_1, move.action_2

    def current_action(self, player_id):
        """ The actions performed by the players """
        move = self.moves[self.move_index]
        if player_id == 1:
            return move.action_1
        else:
            return move.action_2

    def move_forward(self):
        """ step ahead in the simulation """
        success = False
        self.move_index += 1
        if self.num_moves > self.move_index:
            success = True

        return success

    def perform_action(self, action, player_id):
        """use the user sent action to alter the game state"""

        move = self.moves[self.move_index]

        self.game_state.perform_action (action, player_id, move.position_1, move.position_2,
                                        self.does_not_have_visualizer)

    def get_game_state_difference(self, received_game_state):
        """Find the difference between the current game_state and received"""
        return self.game_state.difference(received_game_state)

    def num_actions_gun (self):
        """
        return the number of actions corresponding to gun
        """
        return self.num_moves_gun

    def num_actions_ai(self):
        """
        return the number of actions corresponding to AI
        """
        return self.num_moves_ai

    def get_game_state_dict(self):
        return self.game_state.get_dict()


class _Move:
    def __init__(self, action_1, position_1, action_2, position_2):
        self.action_1   = action_1
        self.position_1 = position_1
        self.action_2   = action_2
        self.position_2 = position_2

    def __str__(self):
        return "p1:{},{}; p2:{},{}".format(self.position_1, self.action_1, self.position_2, self.action_2)
