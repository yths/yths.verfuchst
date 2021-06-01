import collections
import uuid

class InvalidGameCommand(Exception):
    def __init__(self, command, message='invalid game command'):
        self.command = command
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}: {self.command}'


class Game:
    def __init__(self, host_client_id):
        self.game_id = uuid.uuid4().hex
        self.host_client_id = host_client_id
        self.players = [host_client_id]
        self.game_state = 'initialization'
        self.active_player = host_client_id
        self.active_player_state = 'roll_die'
        self.board = ['001', '003', '004', '005', '006', '007', '008', '009', '010', '011', '012', '013', '014', '015', '016', '017', '018', '019', '020', '021', '022', '023', '024', '025', '026', '027', '028', '029', '030', '031', '032', '033', '034', '002']
        self.pieces = collections.defaultdict(functools.partial(collections.defaultdict, str))
        self.guards = collections.defaultdict(int)
        self.die_roll = 0
        self.scores = collections.defaultdict(set)

    def join(self, client_id):
        if self.game_state == 'initialization' and len(self.players) < 4:
            self.players.append(client_id)
        else:
            raise InvalidGameCommand('join')

    def start(self):
        if len(self.players) > 1:
            self.game_state = 'running'
            for player in self.players:
                self.pieces[player]['001'] = '001'
                self.pieces[player]['002'] = '001'
                self.pieces[player]['003'] = '001'
            for i, tid in enumerate(['011', '012', '013', '014', '015', '016', '017', '018']):
                self.guards[tid] = 1

            self.active_player = random.choice(self.players)
        else:
            self.game_state = 'initialization'
            raise InvalidGameCommand('start')

    def roll_die(self, client_id):
        if self.active_player_state == 'roll_die' and self.active_player == client_id:
            self.active_player_state = 'move'
            self.die_roll = random.randint(1, 6)
        else:
            raise InvalidGameCommand('roll_die')

    def move(self, client_id, tile, piece_type):
        if self.active_player_state == 'move' and self.active_player == client_id:
            if piece_type == 'piece':
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

            elif piece_type == 'guard':
                self.guards[tile] -= 1
                self.guards[self.board[min(self.board.index(tile) + self.die_roll, len(self.board) - 1)]] += 1


            self.active_player = self.players[(self.players.index(client_id) +  1) % len(self.players)]
            self.active_player_state = 'roll_die'
        else:
            raise InvalidGameCommand('move')


if __name__ == '__main__':
    ...
