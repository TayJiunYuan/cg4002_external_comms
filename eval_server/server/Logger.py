import json
import os
import time
import random as random

import aiofiles as aiofiles


class Logger:
    """
    class log team performance.
    """

    def __init__(self, group_name, num_players):
        # create the folder for the logs
        log_dir = os.path.join(os.path.dirname(__file__), 'evaluation_logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.log_filepath_json = os.path.join(log_dir, '{}_{}_logs.json'.format(group_name, num_players))

        # used to distinguish 2 different usages of eval_server for the same group
        # not foolproof, needs manual verification
        self.random_id = random.randint(1, 10 * 1000)

    async def write_state (self, response_time: float, player_id: int,
                           correct_action: str, predicted_action: str, action_matched: int,
                           game_state_received: dict, game_state_expected: dict):
        data = dict()
        data['id']                  = self.random_id
        data['timestamp']           = time.time()
        data['response_time']       = response_time
        data['player_id']           = player_id
        data['correct_action']      = correct_action
        data['predicted_action']    = predicted_action
        data['action_matched']      = action_matched
        data['game_state_received'] = game_state_received
        data['game_state_expected'] = game_state_expected

        log_filepath = self.log_filepath_json
        mode = 'a'
        if not os.path.exists(log_filepath):  # first write
            mode = 'w'

        async with aiofiles.open(log_filepath, mode=mode) as f:
            await f.write(json.dumps(data) + '\n')
