#!/usr/bin/env python

import asyncio
import json

import websockets
import statistics

from Client import Client
from Helper import ice_print_group_name, Action

client_dict = dict()  # dictionary containing all the clients


class _MessageType:
    action       = "action"
    action_match = "action_match"
    error        = "error"
    info         = "info"
    info_y       = "info_y"
    info_wobr    = "info_wobr"
    num_move     = "num_move"
    position     = "position"


def get_json_ws(m_type, message="", pos_1=-1, pos_2=-1, action_match=-2, player_id=-1):
    """
    The json corresponding to the web client
    """
    data = {
        "type":         m_type,
        "message":      message,
        "pos_1":        pos_1,
        "pos_2":        pos_2,
        "action_match": action_match,
        "player_id":    player_id
    }
    return json.dumps(data)


async def ws_send_error(websocket, message):
    """
    Send the error message to the web client
    """
    await websocket.send (get_json_ws(m_type=_MessageType.error, message=message))


async def ws_send_info(websocket, message):
    """
    Send the info message to the web client
    """
    await websocket.send (get_json_ws(m_type=_MessageType.info, message=message))


async def ws_send_info_y(websocket, message):
    """
    Send the info message to the web client in yellow font colour
    """
    await websocket.send (get_json_ws(m_type=_MessageType.info_y, message=message))


async def ws_send_info_wobr(websocket, message):
    """
    Send the info message to the web client without a newline
    """
    await websocket.send (get_json_ws(m_type=_MessageType.info_wobr, message=message))


async def ws_send_num_move(websocket, message):
    """
    Send the number of steps to the web client
    """
    await websocket.send (get_json_ws(m_type=_MessageType.num_move, message=message))


async def ws_send_positions(websocket, pos_1, pos_2):
    """
    Send the player positions to the web client
    """
    await websocket.send (get_json_ws (m_type=_MessageType.position, pos_1=pos_1, pos_2=pos_2))


async def ws_send_actions(websocket, action_1, action_2):
    """
    Send the player actions to the web client
    """
    await websocket.send (get_json_ws (m_type=_MessageType.action, pos_1=action_1, pos_2=action_2))


async def ws_send_action_update(websocket, action_match, player_id, message):
    """
    Send the update of player actions to the web client
    """
    await websocket.send (get_json_ws (m_type=_MessageType.action_match, action_match=action_match, player_id=player_id,
                                       message=message))


async def perform_handshake(message, websocket):
    """
    perform a handshake with the web client to fetch credentials,
    Which are used to host a TCP server accepting one connection
    """
    success     = False
    group_name  = None
    num_player  = None
    client      = None

    try:
        data = json.loads(message)
        print(data)
        group_name = data["group_name"]
        password   = data["password"]
        num_player = int(data["num_player"])
        if data["no_visualizer"] == 'true':
            does_not_have_visualizer = True
        else:
            does_not_have_visualizer = False

        # check if the group is already connected to the server
        if group_name in client_dict.keys():
            # we do not allow more than one connection
            await ws_send_error (websocket, "Connection denied: Duplicate connection to eval_server")
        else:
            # create a Client object
            client = Client(group_name, password, num_player, does_not_have_visualizer)
            await ws_send_info(websocket, "Welcome: "+group_name)
            await ws_send_info(websocket, "------------")
            await ws_send_info(websocket, "TCP server waiting for connection from eval_client on port number "
                               + str(client.port_number) + " ")
            await ws_send_num_move(websocket, client.group_name + " Port:" + str(client.port_number))
            await client.accept()

            try:
                # check if the web socket is still open
                # this happens when the user refreshes the webpage before establishing a TCP connection
                await websocket.ping()

                # check if some other connection established by the same group
                if group_name in client_dict:
                    await ws_send_error(websocket, "Connection denied: Duplicate connection to eval_server")
                else:
                    await ws_send_info_y(websocket, "eval_client connected")
                    await ws_send_info  (websocket, "Verifying Password")
                    verified, timeout = await client.verify_password()
                    if verified:
                        await ws_send_info_y(websocket, "Successful")
                        await ws_send_info  (websocket, "------------")
                        client_dict[group_name] = client
                        success = True
                    elif timeout <= 0:
                        await ws_send_error (websocket, "Failed: Timeout")
                        await ws_send_info  (websocket, "------------")
                    else:
                        await ws_send_error (websocket, "Failed")
                        await ws_send_info  (websocket, "------------")
            except (websockets.ConnectionClosed, websockets.ConnectionClosedOK):
                # this is a duplicate connection and can be discarded
                ice_print_group_name (group_name, "Terminated Dangling TCP server : port_num=", client.port_number)

            if not success:
                client.stop()

    except json.JSONDecodeError:
        print ("Handshake data loading failed: JSONDecodeError - ", message)

    return success, group_name, num_player, client


async def ws_recv_next_click(websocket, group_name):
    """
    Wait for the next button to be clicked in the browser
    """
    success = False
    try:
        message = await websocket.recv()
        if message == "next":
            success = True
    except websockets.ConnectionClosedOK:
        ice_print_group_name(group_name, "ws_recv_next_click: Connection closed")
    except websockets.ConnectionClosedError:
        ice_print_group_name(group_name, "ws_recv_next_click: Connection closed Error")
    except Exception as e:
        ice_print_group_name(group_name, "ws_recv_next_click: ", e)

    return success


async def handler(websocket):
    """ All incoming websockets are handled by this function """
    print ("Waiting for Handshake")
    message = await websocket.recv()
    success, group_name, num_players, client = await perform_handshake(message, websocket)

    if not success:
        return

    try:
        response_time_gun   = []    # response times of correct match for gun
        response_time_ai    = []    # response times of correct match for AI actions
        num_actions_matched_gun = 0
        num_actions_matched_ai  = 0

        while client.is_running:
            # display the player location if 2-player game
            pos_1, pos_2 = client.current_positions()
            await ws_send_positions(websocket, pos_1, pos_2)

            # wait for the user the click next
            success = await ws_recv_next_click(websocket, group_name)

            # display the number of moves
            await ws_send_num_move (websocket, client.current_move())

            # send action
            action_1, action_2 = client.current_actions()
            await ws_send_actions(websocket, action_1, action_2)

            if not success:
                # The websocket is disconnected
                break
            # wait to receive 2 jsons with timeout from eval_client
            await ws_send_info(websocket, "------------")
            player_processed = -1   # variable to ensure we do not process a player twice

            timeout_remaining = client.timeout
            for _ in range (num_players):
                action_match, player_id, message, action_recv, response_time, timeout_remaining = \
                    await client.handle_a_player(player_processed, timeout_remaining)

                player_processed = player_id

                # update display based on received action
                if action_match == 1:
                    # action mismatch
                    await ws_send_info_y(websocket, message="Action received: " + action_recv)

                if action_match == -1:
                    # error during processing
                    await ws_send_error(websocket, message)
                else:
                    if action_match == 0:
                        # action matched
                        # process response time
                        if action_recv == Action.shoot:
                            num_actions_matched_gun += 1
                            response_time_gun.append(response_time)
                        else:
                            num_actions_matched_ai += 1
                            response_time_ai.append(response_time)

                    # display the difference in game states for both match amd mismatch
                    await ws_send_action_update (websocket, action_match, player_id, message)

                    # send the correct json back only if there is no error
                    await client.send_game_state()
            # move one step forward
            client.move_forward ()

        await ws_send_num_move(websocket, "Eval Terminated")
        await ws_send_info_y(websocket, "------------------- Stat -------------------")

        accuracy = str(num_actions_matched_gun)+"/"+str(client.num_actions_gun())
        await send_stat(accuracy, "GUN", response_time_gun, websocket, client.timeout)

        accuracy = str(num_actions_matched_ai)+"/"+str(client.num_actions_ai())
        await send_stat(accuracy, "AI ", response_time_ai, websocket, client.timeout)

    except Exception as e:
        ice_print_group_name(group_name, "handler:", e)

    # the client is disconnected
    client = client_dict.pop(group_name)
    client.stop()


async def send_stat(accuracy, component, response_times, websocket, timeout):
    if len(response_times) == 0:
        mean    = timeout
        median  = timeout
    else:
        mean    = statistics.mean(response_times)
        median  = statistics.median(response_times)

    message = "{comp}-- accuracy={acc}; Response time (mean):{mean:.2f} (median):{median:.2f}" \
        .format(comp=component, acc=accuracy, mean=mean, median=median)
    await ws_send_info(websocket, message)


async def main():
    print ("Waiting for new websocket client")
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    print ("running main")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
