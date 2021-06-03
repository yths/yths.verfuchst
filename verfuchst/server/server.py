import asyncio
import json
import uuid
import datetime
import base64
import random
import functools
import collections

import verfuchst.logic.gamestate


class Client:
    def __init__(self, name):
        self.client_name = name
        self.game_id = 'lobby'
        self.last_message = datetime.datetime.now()


class Server:
    def __init__(self):
        self.clients = dict()
        self.client_expiration_threshold = 8
        self.games = dict()


    def _handle_command_register_client(self, message):
        if message['client_id'] not in self.clients:
            self.clients[message['client_id']] = Client(message['client_name'])
            response = json.dumps({'status': 'success', 'command': 'register_client'})
        else:
            response = json.dumps({'status': 'failure', 'command': 'register_client'})
        return response


    def _check_client_expiration(self):
        expired_clients = set()
        for client_id in self.clients:
            if (datetime.datetime.now() - self.clients[client_id].last_message).seconds > self.client_expiration_threshold:
                expired_clients.add(client_id)

        for client_id in expired_clients:
            del self.clients[client_id]


    def _check_game_expiration(self):
        expired_games = set()
        for game_id in self.games:
            if self.games[game_id].host_client_id not in self.clients:
                expired_games.add(game_id)
        for game_id in expired_games:
            del self.games[game_id]


    def _handle_command_get_game_state(self, message):
        if message['client_id'] in self.clients:
            self.clients[message['client_id']].last_message = datetime.datetime.now()
            self._check_client_expiration()
            self._check_game_expiration()

            game_payload = None
            for game_id in self.games:
                if message['client_id'] in self.games[game_id].players:
                    game_payload = self.games[game_id].serialize()
                    break
            response = json.dumps({'status': 'success', 'command': 'get_game_state', 'game_payload': game_payload, 'clients': [[str(client_id), self.clients[client_id].client_name, self.clients[client_id].game_id] for client_id in self.clients.keys()], 'games': [game_id for game_id in self.games if self.games[game_id].game_state == 'initialization']})
        else:
            response = json.dumps({'status': 'failure', 'command': 'get_game_state'})
        return response


    def _handle_command_create_game(self, message):
        game = verfuchst.logic.gamestate.Game(message['client_id'])
        self.games[game.game_id] = game
        self.clients[message['client_id']].game_id = game.game_id
        response = json.dumps({'status': 'success', 'command': 'create_game'})
        return response


    def _handle_command_join_game(self, message):
        self.clients[message['client_id']].game_id = message['game_id']
        try:
            self.games[message['game_id']].join(message['client_id'])
            response = json.dumps({'status': 'success', 'command': 'join_game'})
        except Exception:
            response = json.dumps({'status': 'failure', 'command': 'join_game'})
        return response


    def _handle_command_start_game(self, message):
        try:
            self.games[message['game_id']].start()
            response = json.dumps({'status': 'success', 'command': 'start_game'})
        except Exception:
            response = json.dumps({'status': 'failure', 'command': 'start_game'})
        return response


    def _handle_command_roll_die(self, message):
        try:
            self.games[message['game_id']].roll_die(message['client_id'])
            response = json.dumps({'status': 'success', 'command': 'roll_die'})
        except Exception:
            response = json.dumps({'status': 'failure', 'command': 'roll_die'})
        return response


    def _handle_command_move_piece(self, message):
        try:
            self.games[message['game_id']].move(message['client_id'], message['tile'], message['type'])
            response = json.dumps({'status': 'success', 'command': 'move_piece'})
        except Exception:
            response = json.dumps({'status': 'failure', 'command': 'move_piece'})
        return response


    async def handle_client(self, reader, writer):
        data = await reader.read(4096)
        message = json.loads(data.decode())
        if message['command'] == 'register_client':
            response = self._handle_command_register_client(message)
        elif message['command'] == 'get_game_state':
            response = self._handle_command_get_game_state(message)
        elif message['command'] == 'create_game':
            response = self._handle_command_create_game(message)
        elif message['command'] == 'join_game':
            response = self._handle_command_join_game(message)
        elif message['command'] == 'start_game':
            response = self._handle_command_start_game(message)
        elif message['command'] == 'roll_die':
            response = self._handle_command_roll_die(message)
        elif message['command'] == 'move_piece':
            response = self._handle_command_move_piece(message)

        writer.write(response.encode())
        writer.close()


    async def main(self):
        server = await asyncio.start_server(self.handle_client, '127.0.0.1', 2106)

        address = server.sockets[0].getsockname()
        print(f'serving on {address}')

        async with server:
            await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(Server().main())
