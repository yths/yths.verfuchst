import asyncio
import json
import uuid
import datetime
import pickle
import base64
import random
import functools
import collections

import verfuchst.logic.gamestate

clients = dict()
client_expiration_threshold = 8
games = dict()


class Client:
    def __init__(self, name):
        self.client_name = name
        self.game_id = 'lobby'
        self.last_message = datetime.datetime.now()


async def handle_client(reader, writer):
    global games
    global clients
    data = await reader.read(4096)
    message = json.loads(data.decode())
    if message['command'] == 'register_client':
        if message['client_id'] not in clients:
            clients[message['client_id']] = Client(message['client_name'])
        response = json.dumps({'status': 'success', 'command': 'register_client'})
    elif message['command'] == 'get_game_state':
        if message['client_id'] in clients:
            clients[message['client_id']].last_message = datetime.datetime.now()
            expired_clients = set()
            for client_id in clients:
                if (datetime.datetime.now() - clients[client_id].last_message).seconds > client_expiration_threshold:
                    expired_clients.add(client_id)
            for client_id in expired_clients:
                del clients[client_id]
            expired_games = set()
            for game_id in games:
                if games[game_id].host_client_id not in clients:
                    expired_games.add(game_id)
            for game_id in expired_games:
                del games[game_id]
            game_payload = None
            for game_id in games:
                if message['client_id'] in games[game_id].players:
                    game_payload = games[game_id]
                    break
            response = json.dumps({'status': 'success', 'command': 'get_game_state', 'game_payload': base64.b64encode(pickle.dumps(game_payload)).decode('ascii'), 'clients': [[str(client_id), clients[client_id].client_name, clients[client_id].game_id] for client_id in clients.keys()], 'games': [game_id for game_id in games if games[game_id].game_state == 'initialization']})
    elif message['command'] == 'create_game':
        game = verfuchst.logic.gamestate.Game(message['client_id'])
        games[game.game_id] = game
        clients[message['client_id']].game_id = game.game_id
        response = json.dumps({'status': 'success', 'command': 'create_game'})
    elif message['command'] == 'join_game':
        clients[message['client_id']].game_id = message['game_id']
        try:
            games[message['game_id']].join(message['client_id'])
            response = json.dumps({'status': 'success', 'command': 'join_game'})
        except Exception:
            response = json.dumps({'status': 'failure', 'command': 'join_game'})
    elif message['command'] == 'start_game':
        try:
            games[message['game_id']].start()
            response = json.dumps({'status': 'success', 'command': 'start_game'})
        except Exception:
            response = json.dumps({'status': 'failure', 'command': 'start_game'})

    elif message['command'] == 'roll_die':
        try:
            games[message['game_id']].roll_die(message['client_id'])
            response = json.dumps({'status': 'success', 'command': 'roll_die'})
        except Exception:
            response = json.dumps({'status': 'failure', 'command': 'roll_die'})
    elif message['command'] == 'move_piece':
        try:
            games[message['game_id']].move(message['client_id'], message['tile'], message['type'])
            response = json.dumps({'status': 'success', 'command': 'move_piece'})
        except Exception:
            response = json.dumps({'status': 'failure', 'command': 'move_piece'})

    writer.write(response.encode())
    writer.close()


async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 2106)

    address = server.sockets[0].getsockname()
    print(f'serving on {address}')

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
