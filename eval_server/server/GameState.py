import random
import sys

from Helper import Action


class GameState:
    def __init__(self):
        self.player_1 = Player()
        self.player_2 = Player()

    def __str__(self):
        return str(self.get_dict())

    def get_dict(self):
        data = {'p1': self.player_1.get_dict(), 'p2': self.player_2.get_dict()}
        return data

    def difference(self, received_game_state):
        """Find the difference between the current game_state and received"""
        try:
            recv_p1_dict = received_game_state["p1"]
            recv_p2_dict = received_game_state["p2"]

            p1 = self.player_1.get_difference(recv_p1_dict)
            p2 = self.player_2.get_difference(recv_p2_dict)

            diff = {'p1': p1, 'p2': p2}

            message = "Game state difference : " + str(diff)
        except KeyError:
            message = "Key error in the received Json"
        return message

    def init_players_random(self):
        """ Helper function to randomize the game state"""
        for player_id in [1, 2]:
            hp = random.randint(10, 90)
            bullets_remaining   = random.randint(0, 6)
            bombs_remaining     = random.randint(0, 2)
            shield_health       = random.randint(0, 30)
            num_unused_shield   = random.randint(0, 3)
            num_deaths          = random.randint(0, 3)

            self._init_player(player_id, bullets_remaining, bombs_remaining, hp,
                              num_deaths, num_unused_shield,
                              shield_health)

    def _init_player (self, player_id, bullets_remaining, bombs_remaining, hp,
                      num_deaths, num_unused_shield, shield_health):
        if player_id == 1:
            player = self.player_1
        else:
            player = self.player_2
        player.set_state(bullets_remaining, bombs_remaining, hp, num_deaths,
                         num_unused_shield, shield_health)

    def perform_action(self, action, player_id, position_1, position_2, does_not_have_visualizer):
        """use the user sent action to alter the game state"""

        # perform sanity check to see if our function handles all the actions
        all_actions = {"gun", "shield", "bomb", "reload", "badminton", "golf", "fencing", "boxing"}
        if not Action.actions_match(all_actions):
            print("All actions not handled by GameState.perform_action")
            sys.exit(-1)

        if player_id == 1:
            attacker            = self.player_1
            opponent            = self.player_2
            opponent_position   = position_2
        else:
            attacker            = self.player_2
            opponent            = self.player_1
            opponent_position   = position_1

        # check if the players can see each other
        can_see = self._can_see (position_1, position_2)

        # reduce the health of the opponent based on rain/snow started by the attacker, in the previous moves
        # NOTE:
        # 1) Eval_server reduce the health of an opponent due to rain/snow only if the attacker action is
        #    sent to eval server
        # 2) e.g. if P_1 walks into a rain/snow started by P_2, if P_2 action timeout, P_1 will not have HP reduction
        if does_not_have_visualizer:
            # this team has no concept of a rain/snow damage
            pass
        else:
            attacker.rain_damage(opponent, opponent_position, can_see, player_id)

        if does_not_have_visualizer:
            # for bomb and AI actions we assume the opponent is always visible
            if action in {"badminton", "golf", "fencing", "boxing", "bomb"}:
                can_see = True

        # perform the actual action
        if action == "gun":
            attacker.shoot(opponent, can_see)
        elif action == "shield":
            attacker.shield()
        elif action == "reload":
            attacker.reload()
        elif action == "bomb":
            attacker.bomb(opponent, opponent_position, can_see)
        elif action in {"badminton", "golf", "fencing", "boxing"}:
            # all these have the same behaviour
            attacker.harm_AI(opponent, can_see)
        elif action == "logout":
            # has no change in game state
            pass
        else:
            # invalid action we do nothing
            pass

    @staticmethod
    def _can_see(position_1, position_2):
        """check if the players can see each other"""
        can_see = True
        # the players cannot see each other only if one is quadrant 4 and other is in any other quadrant
        if position_1 == 4 and position_2 != 4:
            can_see = False
        elif position_1 != 4 and position_2 == 4:
            can_see = False
        return can_see


class Player:
    def __init__(self):
        self.max_bombs          = 2
        self.max_shields        = 3
        self.hp_bullet          = 5     # the hp reduction for bullet
        self.hp_AI              = 10    # the hp reduction for AI action
        self.hp_bomb            = 5
        self.hp_rain            = 5
        self.max_shield_health  = 30
        self.max_bullets        = 6
        self.max_hp             = 100

        self.num_deaths         = 0

        self.hp             = self.max_hp
        self.num_bullets    = self.max_bullets
        self.num_bombs      = self.max_bombs
        self.hp_shield      = 0
        self.num_shield     = self.max_shields

        self.rain_list = []  # list of quadrants where rain/snow has been started by the bomb of this player

    def __str__(self):
        return str(self.get_dict())

    def get_dict(self):
        data = dict()
        data['hp']              = self.hp
        data['bullets']         = self.num_bullets
        data['bombs']           = self.num_bombs
        data['shield_hp']       = self.hp_shield
        data['deaths']          = self.num_deaths
        data['shields']         = self.num_shield
        return data

    def get_difference(self, recv_dict):
        """get difference between the received player sate and our state"""
        data = self.get_dict()
        for key in list(data.keys()):
            val = data[key] - recv_dict[key]
            if val == 0:
                # there is no difference so we delete the element
                data.pop(key)
            else:
                data[key] = val
        return data

    def set_state(self, bullets_remaining, bombs_remaining, hp, num_deaths, num_unused_shield, shield_health):
        self.hp             = hp
        self.num_bullets    = bullets_remaining
        self.num_bombs      = bombs_remaining
        self.hp_shield      = shield_health
        self.num_shield     = num_unused_shield
        self.num_deaths     = num_deaths

    def shoot(self, opponent, can_see):
        while True:
            # check the ammo
            if self.num_bullets <= 0:
                break
            self.num_bullets -= 1

            # check if the opponent is visible
            if not can_see:
                break

            opponent.reduce_health(self.hp_bullet)
            break

    def reduce_health(self, hp_reduction):
        # use the shield to protect the player
        if self.hp_shield > 0:
            new_hp_shield  = max (0, self.hp_shield-hp_reduction)
            # how much should we reduce the HP by?
            hp_reduction   = max (0, hp_reduction-self.hp_shield)
            # update the shield HP
            self.hp_shield = new_hp_shield

        # reduce the player HP
        self.hp = max(0, self.hp - hp_reduction)
        if self.hp == 0:
            # if we die, we spawn immediately
            self.num_deaths += 1

            # initialize all the states
            self.hp             = self.max_hp
            self.num_bullets    = self.max_bullets
            self.num_bombs      = self.max_bombs
            self.hp_shield      = 0
            self.num_shield     = self.max_shields

    def shield(self):
        """Activate shield"""
        while True:
            if self.num_shield <= 0:
                # check the number of shields available
                break
            elif self.hp_shield > 0:
                # check if shield is already active
                break
            self.hp_shield = self.max_shield_health
            self.num_shield -= 1

    def bomb(self, opponent, opponent_position, can_see):
        """Throw a bomb at opponent"""
        while True:
            # check the ammo
            if self.num_bombs <= 0:
                break
            self.num_bombs -= 1

            # check if the opponent is visible
            if not can_see:
                # this bomb will not start a rain/snow and hence has no effect with respect to gameplay
                break

            opponent.reduce_health(self.hp_bomb)
            # start a rain/snow in the quadrant of the opponent
            self.rain_list.append(opponent_position)
            break

    def rain_damage(self, opponent, opponent_position, can_see, attacker_id):
        """
        whenever an opponent walks into a quadrant we need to reduce the health
        based on the number of rains/snow
        """
        if can_see:
            if opponent_position == 0:
                # this means the opponent is returning to the default position after a disconnect
                # so we have to update the position value
                if attacker_id == 1:
                    # the opponent is player 2, who will always return to quadrant 3
                    opponent_position = 3
                else:
                    # the opponent is player 1, who will always return to quadrant 1
                    opponent_position = 1

            for p in self.rain_list:
                if p == opponent_position:
                    opponent.reduce_health(self.hp_rain)

    def harm_AI(self, opponent, can_see):
        """ We can harm am opponent based on our AI action if we can see them"""
        if can_see:
            opponent.reduce_health(self.hp_AI)

    def reload(self):
        """ perform reload only if the magazine is empty"""
        if self.num_bullets <= 0:
            self.num_bullets = self.max_bullets
