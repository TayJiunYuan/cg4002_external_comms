import random


def ice_print_group_name (group_name, *arg):
    """
    print each group message in different colour
    """
    n = int (group_name[1:])
    print(group_name, end=": ")
    ice_print(arg, color=n)


def ice_print(*arg, end='\n', color=0):
    # ANSI colors
    _c = (
        "\033[0m",   # End of color
        '\033[31m',  # red
        '\033[32m',  # green
        '\033[33m',  # orange
        '\033[34m',  # blue
        '\033[35m',  # purple
        '\033[36m',  # cyan
        '\033[91m',  # light red
        '\033[92m',  # light green
        '\033[93m',  # yellow
        '\033[94m',  # lightblue
        '\033[95m',  # pink
        '\033[96m',  # light cyan
        '\033[37m',  # light grey
        '\033[90m',  # darkgrey
    )

    if color == 0:
        for a in arg:
            print(a, end=' ')
    else:
        for a in arg:
            print(_c[color] + str(a) + _c[0], end=' ')
    print(end, end='')


DEBUG = True


def ice_print_debug(*arg, color=2):
    if not DEBUG:
        return
    ice_print (*arg, color=color)


class Action:
    none        = "none"
    shoot       = "gun"
    shield      = "shield"
    bomb        = "bomb"
    reload      = "reload"
    badminton   = "badminton"
    golf        = "golf"
    fencing     = "fencing"
    boxing      = "boxing"
    logout      = "logout"
    # all actions except none and logout
    all = {shoot, shield, bomb, reload, badminton, golf, fencing, boxing}

    num_shoot_total = 7
    _num_AI         = 2

    # shoot is not AI and logout is AI
    num_AI_total = _num_AI * (len(all) - 1) + 1

    @classmethod
    def init_list(cls, _r):
        if _r > 0:
            ret = [cls.shoot]
        else:
            ret = []
        ret.extend([cls.shoot]  * cls.num_shoot_total)
        ret.extend([cls.shield] * cls._num_AI)
        ret.extend([cls.bomb]   * cls._num_AI)
        ret.extend([cls.reload] * cls._num_AI)
        ret.extend([cls.badminton] * cls._num_AI)
        ret.extend([cls.golf] * cls._num_AI)
        ret.extend([cls.fencing] * cls._num_AI)
        ret.extend([cls.boxing] * cls._num_AI)
        random.shuffle(ret)

        ret.append(cls.logout)
        return ret

    @classmethod
    def get_random_action(cls):
        return random.choice(list(cls.all))

    @classmethod
    def actions_match(cls, all_actions_para):
        """
        check if all actions match the Action class
        """
        return len(cls.all.symmetric_difference(all_actions_para)) == 0
