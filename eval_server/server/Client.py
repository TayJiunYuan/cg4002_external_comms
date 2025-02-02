import asyncio
import json
import socket
from _socket import SHUT_RDWR
import base64
from time import perf_counter

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from GameSimulator import GameSimulator
from Helper import ice_print_group_name
from Logger import Logger


class Client:
    """
    class for coordinating all the TCP communication and gameplay with one team.
    """

    def __init__(self, group_name, secret_key, num_players, does_not_have_visualizer):
        self.group_name     = group_name
        self.secret_key     = secret_key

        self.is_running     = True
        self.num_players    = num_players

        self.timeout = 60   # the timeout for receiving any data

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket connecting to the eval client
        self.socket.bind(("", 0))
        self.port_number = self.socket.getsockname()[1]

        self.addr   = None  # address of the client
        self.conn   = None  # address of the client socket

        self.simulator = GameSimulator(num_players, does_not_have_visualizer)  # the game simulator
        self.logger    = Logger(group_name, num_players)

    async def accept (self):
        """
        Asynchronously wait for a single client to connect
        """
        if not self.is_running:
            return
        self.socket.listen(1)
        self.socket.setblocking(False)

        loop = asyncio.get_event_loop()
        self.conn, self.addr = await loop.sock_accept(self.socket)

    def stop (self):
        """
        The cleanup function
        """
        if not self.is_running:
            return
        self.is_running = False
        try:
            if self.conn is not None:
                self.conn.shutdown(SHUT_RDWR)
                self.conn.close()
                self.conn = None
            self.socket.close()
        except Exception as e:
            # this is an inconsequential error
            ice_print_group_name(self.group_name, 'client.stop: (NO PROBLEM)', e)

    async def verify_password(self):
        """
        We verify to see if the student supplied password matches
        """
        success = False
        _, timeout, text = await self.recv_text(self.timeout)

        if text == "hello":
            # our passwords match
            success = True

        return success, timeout

    async def recv_text(self, timeout):
        """
        receive and decrypt the message from client
        """
        text_received   = ""
        success         = False

        if self.is_running:
            loop = asyncio.get_event_loop()
            try:
                while True:
                    # recv length followed by '_' followed by cypher
                    data = b''
                    while not data.endswith(b'_'):
                        start_time = perf_counter()
                        task = loop.sock_recv(self.conn, 1)
                        _d = await asyncio.wait_for(task, timeout=timeout)
                        timeout -= (perf_counter() - start_time)
                        if not _d:
                            data = b''
                            break
                        data += _d
                    if len(data) == 0:
                        ice_print_group_name(self.group_name, 'recv_text: client disconnected')
                        self.stop()
                        break
                    data = data.decode("utf-8")
                    length = int(data[:-1])

                    data = b''
                    while len(data) < length:
                        start_time = perf_counter()
                        task = loop.sock_recv(self.conn, length - len(data))
                        _d = await asyncio.wait_for(task, timeout=timeout)
                        timeout -= (perf_counter() - start_time)
                        if not _d:
                            data = b''
                            break
                        data += _d
                    if len(data) == 0:
                        ice_print_group_name(self.group_name, 'recv_text: client disconnected')
                        self.stop()
                        break
                    msg = data.decode("utf8")  # Decode raw bytes to UTF-8
                    text_received = self.decrypt_message(msg)
                    success = True
                    break
            except ConnectionResetError:
                ice_print_group_name(self.group_name, 'recv_text: Connection Reset')
                self.stop()
            except asyncio.TimeoutError:
                ice_print_group_name(self.group_name, 'recv_text: Timeout while receiving data')
                timeout = -1
        else:
            timeout = -1

        return success, timeout, text_received

    def decrypt_message(self, cipher_text):
        """
        This function decrypts the response message received from the Ultra96 using
        the secret encryption key/ password
        """
        try:
            decoded_message = base64.b64decode(cipher_text)  # Decode message from base64 to bytes
            iv = decoded_message[:AES.block_size]  # Get IV value
            secret_key = bytes(str(self.secret_key), encoding="utf8")  # Convert secret key to bytes

            cipher = AES.new(secret_key, AES.MODE_CBC, iv)  # Create new AES cipher object

            decrypted_message = cipher.decrypt(decoded_message[AES.block_size:])  # Perform decryption
            decrypted_message = unpad(decrypted_message, AES.block_size)
            decrypted_message = decrypted_message.decode('utf8')  # Decode bytes into utf-8
        except Exception as e:
            decrypted_message = ""
            ice_print_group_name(self.group_name, "exception in decrypt_message: ", e)
        return decrypted_message

    def current_move (self):
        """ The text message of number of moves to be displayed on the UI """
        return self.simulator.current_move()

    def current_positions (self):
        """ The positions the player is supposed to be in """
        return self.simulator.current_positions()

    def current_actions (self):
        """ The positions the player is supposed to be in """
        return self.simulator.current_actions()

    async def handle_a_player (self, player_processed, timeout_para):
        """
        Function which will handle both the players one after another
        """
        start_time = perf_counter()

        # wait for a json from eval_client with timeout
        success, timeout, text_received = await self.recv_text(timeout_para)

        player_id       = -1
        action          = ""
        action_match    = -1  # -1 means error
        response_time   = 0

        if success:
            try:
                data = json.loads (text_received)

                # process the received game state
                player_id           = int (data["player_id"])
                action              = data["action"]
                received_game_state = data["game_state"]

                if player_id == player_processed:
                    # we have received a duplicate json, hence discarding
                    message = "player_id "+str(player_id)+" received twice, discarding the packet"
                elif player_id > self.num_players or player_id < 1:
                    message = "player_id " + str(player_id) + " INVALID, discarding the packet"
                else:
                    # does the action match
                    current_action = self.simulator.current_action(player_id)
                    if action == current_action:
                        # action matches
                        action_match = 0
                    else:
                        action_match = 1

                    # use the user sent action to alter the game state
                    self.simulator.perform_action (action, player_id)

                    # find the difference between the game states
                    message = self.simulator.get_game_state_difference (received_game_state)

                    # log the result
                    response_time = perf_counter() - start_time
                    await self.logger.write_state(response_time=response_time, player_id=player_id,
                                                  correct_action=current_action,
                                                  predicted_action=action, action_matched=action_match,
                                                  game_state_received=received_game_state,
                                                  game_state_expected=self.simulator.get_game_state_dict())

            except (ValueError, TypeError):  # includes simplejson.decoder.JSONDecodeError
                message = 'Decoding JSON has failed'
                ice_print_group_name(self.group_name, "handle_a_player: " + message)

            # check if the action and game state match
        else:
            message = "Timeout"

        return action_match, player_id, message, action, response_time, timeout

    def move_forward (self):
        """
        step the simulator ahead by one step
        """
        if not self.is_running:
            return
        if not self.simulator.move_forward():
            # all actions have been displayed
            self.is_running = False

    async def send_game_state(self):
        if not self.is_running:
            return
        loop = asyncio.get_event_loop()

        game_state  = json.dumps(self.simulator.game_state.get_dict())
        data        = str(len(game_state))+"_"+game_state

        # send the data to eval client
        try:
            task = loop.sock_sendall(self.conn, data.encode("utf-8"))
            await asyncio.wait_for(task, timeout=self.timeout)
        except ConnectionResetError:
            ice_print_group_name(self.group_name, 'send_game_state: Connection Reset')
            self.stop()
        except asyncio.TimeoutError:
            ice_print_group_name(self.group_name, 'send_game_state: Timeout while sending data')
        except OSError:
            ice_print_group_name(self.group_name, 'send_game_state: Connection terminated')
            self.stop()

        return

    def num_actions_gun (self):
        """
        return the number of actions corresponding to gun
        """
        return self.simulator.num_actions_gun()

    def num_actions_ai(self):
        """
        return the number of actions corresponding to AI
        """
        return self.simulator.num_actions_ai()
