import collections
import uuid
import functools
import json
import random


BOARD_CONFIG = {
    '001': {
        'label': 'start',
        'x': 64,
        'y': 64,
        'color': 'gold',
        'value': 0,
    },
    '002': {
        'label': 'end',
        'x': 576,
        'y': 128,
        'color': 'gold',
        'value': 0,
    },
    '003': {
        'label': '-1.1',
        'x': 128,
        'y': 64,
        'value': -1,
        'color': 'red3'
    },
    '004': {
        'label': '-2.1',
        'x': 192,
        'y': 64,
        'value': -2,
        'color': 'red3'
    },
    '005': {
        'label': '-3.1',
        'x': 192,
        'y': 128,
        'value': -3,
        'color': 'red3'
    },
    '006': {
        'label': '-4.1',
        'x': 192,
        'y': 192,
        'value': -4,
        'color': 'red3'
    },
    '007': {
        'label': '-5.1',
        'x': 128,
        'y': 192,
        'value': -5,
        'color': 'red3'
    },
    '008': {
        'label': '-6.1',
        'x': 128,
        'y': 256,
        'value': -6,
        'color': 'red3'
    },
    '009': {
        'label': '-7.1',
        'x': 192,
        'y': 256,
        'value': -7,
        'color': 'red3'
    },
    '010': {
        'label': '-8.1',
        'x': 256,
        'y': 256,
        'value': -8,
        'color': 'red3'
    },
    '011': {
        'label': 'g.1',
        'x': 320,
        'y': 256,
        'value': 0,
        'color': 'NavajoWhite2'
    },
    '012': {
        'label': 'g.2',
        'x': 384,
        'y': 256,
        'value': 0,
        'color': 'NavajoWhite2'
    },
    '013': {
        'label': 'g.3',
        'x': 448,
        'y': 256,
        'value': 0,
        'color': 'NavajoWhite2'
    },
    '014': {
        'label': 'g.4',
        'x': 448,
        'y': 320,
        'value': 0,
        'color': 'NavajoWhite2'
    },
    '015': {
        'label': 'g.5',
        'x': 448,
        'y': 384,
        'value': 0,
        'color': 'NavajoWhite2'
    },
    '016': {
        'label': 'g.6',
        'x': 448,
        'y': 448,
        'value': 0,
        'color': 'NavajoWhite2'
    },
    '017': {
        'label': '+8.1',
        'x': 384,
        'y': 448,
        'value': 8,
        'color': 'SpringGreen2'
    },
    '018': {
        'label': '+7.1',
        'x': 320,
        'y': 448,
        'value': 7,
        'color': 'SpringGreen2'
    },
    '019': {
        'label': '+6.1',
        'x': 320,
        'y': 384,
        'value': 6,
        'color': 'SpringGreen2'
    },
    '020': {
        'label': '+5.1',
        'x': 256,
        'y': 384,
        'value': 5,
        'color': 'SpringGreen2'
    },
    '021': {
        'label': '+4.1',
        'x': 192,
        'y': 384,
        'value': 4,
        'color': 'SpringGreen2'
    },
    '022': {
        'label': '+3.1',
        'x': 192,
        'y': 448,
        'value': 3,
        'color': 'SpringGreen2'
    },
    '023': {
        'label': '+2.1',
        'x': 192,
        'y': 512,
        'value': 2,
        'color': 'SpringGreen2'
    },
    '024': {
        'label': '+1.1',
        'x': 256,
        'y': 512,
        'value': 1,
        'color': 'SpringGreen2'
    },
    '025': {
        'label': '-1.2',
        'x': 320,
        'y': 512,
        'value': -1,
        'color': 'red3'
    },
    '026': {
        'label': '-2.2',
        'x': 384,
        'y': 512,
        'value': -2,
        'color': 'red3'
    },
    '027': {
        'label': '-3.2',
        'x': 448,
        'y': 512,
        'value': -3,
        'color': 'red3'
    },
    '028': {
        'label': '-4.2',
        'x': 512,
        'y': 512,
        'value': -4,
        'color': 'red3'
    },
    '029': {
        'label': '-5.2',
        'x': 576,
        'y': 512,
        'value': -5,
        'color': 'red3'
    },
    '030': {
        'label': '-6.2',
        'x': 576,
        'y': 448,
        'value': -6,
        'color': 'red3'
    },
    '031': {
        'label': '-7.2',
        'x': 576,
        'y': 384,
        'value': -7,
        'color': 'red3'
    },
    '032': {
        'label': '-8.2',
        'x': 576,
        'y': 320,
        'value': -8,
        'color': 'red3'
    },
    '033': {
        'label': '-9.1',
        'x': 576,
        'y': 256,
        'value': -9,
        'color': 'red3'
    },
    '034': {
        'label': '-10.1',
        'x': 576,
        'y': 192,
        'value': -10,
        'color': 'red3'
    },
}


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


    def serialize(self):
        scores = collections.defaultdict(list)
        for k in self.scores:
            scores[k] = list(self.scores[k])

        serialized_gamestate = {
            'game_id': self.game_id,
            'host_client_id': self.host_client_id,
            'players': self.players,
            'game_state': self.game_state,
            'active_player': self.active_player,
            'active_player_state': self.active_player_state,
            'board': self.board,
            'pieces': self.pieces,
            'guards': self.guards,
            'die_roll': self.die_roll,
            'scores': scores,
        }
        return json.dumps(serialized_gamestate)


    def deserialize(self, serialized_gamestate):
        data = json.loads(serialized_gamestate)

        self.game_id = data['game_id']
        self.host_client_id = data['host_client_id']
        self.players = data['players']
        self.game_state = data['game_state']
        self.active_player = data['active_player']
        self.active_player_state = data['active_player_state']
        self.board = data['board']
        tmp = collections.defaultdict(functools.partial(collections.defaultdict, str))
        for k1 in data['pieces']:
            for k2 in data['pieces'][k1]:
                tmp[k1][k2] = data['pieces'][k1][k2]
        self.pieces = tmp
        tmp = collections.defaultdict(int)
        tmp |= data['guards']
        self.guards = tmp
        self.die_roll = data['die_roll']
        tmp = collections.defaultdict(set)
        for k in data['scores']:
            tmp[k] = set(data['scores'][k])
        self.scores = tmp


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


    def _move_piece(self, client_id, tile):
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


    def _check_game_state(self):
        active_tiles = set()
        for cid in self.pieces:
            for k in self.pieces[cid]:
                active_tiles.add(self.pieces[cid][k])

        if active_tiles == set(['002']):
            self.game_state = 'completed'


    def _move_guardian(self, tile):
        self.guards[tile] -= 1
        self.guards[self.board[min(self.board.index(tile) + self.die_roll, len(self.board) - 1)]] += 1


    def move(self, client_id, tile, piece_type):
        if self.active_player_state == 'move' and self.active_player == client_id:
            if piece_type == 'piece':
                self._move_piece(client_id, tile)

                # check if game is completed
                self._check_game_state()
            elif piece_type == 'guard':
                self._move_guardian(tile)

            self.active_player = self.players[(self.players.index(client_id) +  1) % len(self.players)]
            self.active_player_state = 'roll_die'
        else:
            raise InvalidGameCommand('move')


    def calculate_score(self, tiles):
        negative = list()
        score = 0
        invert = 0
        for tid in tiles:
            if BOARD_CONFIG[tid]['value'] == 0:
                invert += 1
            elif BOARD_CONFIG[tid]['value'] > 0:
                score += BOARD_CONFIG[tid]['value']
            else:
                negative.append(BOARD_CONFIG[tid]['value'])
        negative = sorted(negative)
        for i in range(invert):
            if len(negative) > i:
                score += -1 * negative[i]
        for i in range(invert, len(negative)):
            score += negative[i]

        return score


if __name__ == '__main__':
    ...
