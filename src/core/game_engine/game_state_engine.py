class GameStateEngine:
    def __init__(self):
        self.player_1 = Player()
        self.player_2 = Player()

    def __str__(self):
        return str(self.get_dict())

    def get_dict(self):
        data = {"p1": self.player_1.get_dict(), "p2": self.player_2.get_dict()}
        return data

    def perform_action(self, action, player_id, can_see, snow_bomb_count):
        """use the user sent action to alter the game state"""

        if player_id == 1:
            attacker = self.player_1
            opponent = self.player_2

        else:
            attacker = self.player_2
            opponent = self.player_1

        attacker.rain_damage(opponent, can_see, snow_bomb_count)

        # perform the actual action
        if action == "gun":
            attacker.shoot(opponent, can_see)
        elif action == "shield":
            attacker.shield()
        elif action == "reload":
            attacker.reload()
        elif action == "bomb":
            attacker.bomb(opponent, can_see)
        elif action in {"badminton", "golf", "fencing", "boxing"}:
            # all these have the same behaviour
            attacker.harm_AI(opponent, can_see)
        elif action == "logout":
            # has no change in game state
            pass
        else:
            # invalid action we do nothing
            pass


class Player:
    def __init__(self):
        self.max_bombs = 2
        self.max_shields = 3
        self.hp_bullet = 5  # the hp reduction for bullet
        self.hp_AI = 10  # the hp reduction for AI action
        self.hp_bomb = 5
        self.hp_rain = 5
        self.max_shield_health = 30
        self.max_bullets = 6
        self.max_hp = 100

        self.num_deaths = 0

        self.hp = self.max_hp
        self.num_bullets = self.max_bullets
        self.num_bombs = self.max_bombs
        self.hp_shield = 0
        self.num_shield = self.max_shields

        self.rain_list = (
            []
        )  # list of quadrants where rain/snow has been started by the bomb of this player

    def __str__(self):
        return str(self.get_dict())

    def get_dict(self):
        data = dict()
        data["hp"] = self.hp
        data["bullets"] = self.num_bullets
        data["bombs"] = self.num_bombs
        data["shield_hp"] = self.hp_shield
        data["deaths"] = self.num_deaths
        data["shields"] = self.num_shield
        return data

    def set_state(
        self,
        bullets_remaining,
        bombs_remaining,
        hp,
        num_deaths,
        num_unused_shield,
        shield_health,
    ):
        self.hp = hp
        self.num_bullets = bullets_remaining
        self.num_bombs = bombs_remaining
        self.hp_shield = shield_health
        self.num_shield = num_unused_shield
        self.num_deaths = num_deaths

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
            new_hp_shield = max(0, self.hp_shield - hp_reduction)
            # how much should we reduce the HP by?
            hp_reduction = max(0, hp_reduction - self.hp_shield)
            # update the shield HP
            self.hp_shield = new_hp_shield

        # reduce the player HP
        self.hp = max(0, self.hp - hp_reduction)
        if self.hp == 0:
            # if we die, we spawn immediately
            self.num_deaths += 1

            # initialize all the states
            self.hp = self.max_hp
            self.num_bullets = self.max_bullets
            self.num_bombs = self.max_bombs
            self.hp_shield = 0
            self.num_shield = self.max_shields

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

    def bomb(self, opponent, can_see):
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
            break

    def rain_damage(self, opponent, can_see, snow_bomb_count):
        """
        whenever an opponent walks into a quadrant we need to reduce the health
        based on the number of rains/snow
        """
        if can_see:
            for _ in range(snow_bomb_count):
                print("hi im here)")
                opponent.reduce_health(self.hp_rain)

    def harm_AI(self, opponent, can_see):
        """We can harm am opponent based on our AI action if we can see them"""
        if can_see:
            opponent.reduce_health(self.hp_AI)

    def reload(self):
        """perform reload only if the magazine is empty"""
        if self.num_bullets <= 0:
            self.num_bullets = self.max_bullets
