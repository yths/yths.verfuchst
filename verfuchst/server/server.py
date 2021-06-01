import asyncio
import json
import uuid
import datetime
import pickle
import base64
import random
import functools
import collections

clients = dict()
client_expiration_threshold = 8
games = dict()

class Client:
    def __init__(self, name):
        self.client_name = name
        self.game_id = 'lobby'
        self.last_message = datetime.datetime.now()


class Game:
    def __init__(self, host_client_id):
        self.game_id = uuid.uuid4().hex
        self.host_client_id = host_client_id
        self.players = [host_client_id]
        self.game_state = 'initialization'
        self.active_player = host_client_id
        self.active_player_state = 'roll_die'
        self.board = ['001', '003', '004', '005', '006', '007', '008', '009', '010', '011', '012', '013', '014', '015', '016', '017', '018', '019', '020', '021', '022', '023', '024', '025', '026', '027', '028', '029', '030', '031', '032', '033', '034', '002']
        # self.board = ['001', '003', '004', '005', '006', '033', '034', '002']
        self.pieces = collections.defaultdict(functools.partial(collections.defaultdict, str))
        self.guards = collections.defaultdict(int)
        self.die_roll = 0
        self.scores = collections.defaultdict(set)

    def join(self, client_id):
        if self.game_state == 'initialization' and len(self.players) < 4:
            self.players.append(client_id)
        else:
            raise

    def start(self):
        if len(self.players) > 1:
            self.game_state = 'running'
            # self.board = ['001', '002']
            for player in self.players:
                self.pieces[player]['001'] = '001'
                self.pieces[player]['002'] = '001'
                self.pieces[player]['003'] = '001'
            for i, tid in enumerate(['011', '012', '013', '014', '015', '016', '017', '018']):
                self.guards[tid] = 1

            self.active_player = random.choice(self.players)
            print(self.active_player)
        else:
            self.game_state = 'initialization'
            raise

    def roll_die(self, client_id):
        if self.active_player_state == 'roll_die' and self.active_player == client_id:
            self.active_player_state = 'move'
            self.die_roll = random.randint(1, 6)
        else:
            raise

    def move(self, client_id, tile, type):
        if self.active_player_state == 'move' and self.active_player == client_id:
            if type == 'piece':
                for k in self.pieces[client_id]:
                    if self.pieces[client_id][k] == tile:
                        self.pieces[client_id][k] = self.board[min(self.board.index(tile) + self.die_roll, len(self.board) - 1)]
                        break

                occupied = False
                if tile not in ['001', '002']:
                    if self.guards[tile] == 0:
                        for cid in self.pieces:
                            for k in self.pieces[cid]:
                                if tile == self.pieces[cid][k]:
                                    occupied = True
                    else:
                        occupied = True
                    if not occupied:
                        self.board.remove(tile)
                        self.scores[self.active_player].add(tile)

                active_tiles = set()
                for cid in self.pieces:
                    for k in self.pieces[cid]:
                        active_tiles.add(self.pieces[cid][k])

                if active_tiles == set(['002']):
                    self.game_state = 'completed'

            elif type == 'guard':
                self.guards[tile] -= 1
                self.guards[self.board[min(self.board.index(tile) + self.die_roll, len(self.board) - 1)]] += 1


            self.active_player = self.players[(self.players.index(client_id) +  1) % len(self.players)]
            self.active_player_state = 'roll_die'
        else:
            raise


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
        game = Game(message['client_id'])
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
