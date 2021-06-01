import asyncio
import json
import uuid
import tkinter
import tkinter.ttk
import tkinter.messagebox
import pickle
import base64
import collections
import random

client_id = uuid.uuid4().hex
client_registered = False
client_state = 'connect_frame'
clients = collections.defaultdict(list)

window = tkinter.Tk()
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

connect_frame = tkinter.Frame(window)
connect_frame.grid(row=0, column=0)
lobby_frame = tkinter.Frame(window)
game_frame = tkinter.Frame(window)


server_address = tkinter.StringVar()
username = tkinter.StringVar()
games = list()
games_combobox = tkinter.ttk.Combobox(lobby_frame, values=games, state='readonly')
games_combobox.grid(row=0, column=0, columnspan=1, rowspan=1, padx=5, pady=5, sticky='w')
game = None


players_list = tkinter.StringVar()


board_config = {
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
                        self.pieces[client_id][k] = self.board[min(self.board.index(tile) + self.die_roll, len(self.board))]
                        break

            self.active_player = self.players[(self.players.index(client_id) +  1) % len(self.players)]
            self.active_player_state = 'roll_die'
        else:
            raise


async def send(message):
    global clients
    global client_registered
    global client_state
    global game
    global selected_item
    host, port = server_address.get().split(':')
    port = int(port)
    reader, writer = await asyncio.open_connection(host, port)
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(4096)
    response = json.loads(data.decode())
    if response['status'] == 'success':
        if response['command'] == 'register_client':
            client_registered = True
            connect_frame.grid_remove()
            lobby_frame.grid(row=0, column=0)
        elif response['command'] == 'get_game_state':
            for c, n, g in response['clients']:
                clients[c] = [n, g]
            game = pickle.loads(base64.b64decode(response['game_payload']))
            games = response['games']
            games_combobox['values'] = games
        elif response['command'] == 'create_game':
            if response['status'] == 'success':
                client_state = 'game_frame'
                lobby_frame.grid_remove()
                game_frame.grid(row=0, column=0)
            else:
                tkinter.messagebox.showerror(title='Game Error', message='Game is no longer available.')
        elif response['command'] == 'join_game':
            if response['status'] == 'success':
                client_state = 'game_frame'
                lobby_frame.grid_remove()
                game_frame.grid(row=0, column=0)
            else:
                tkinter.messagebox.showerror(title='Game Error', message='Game is no longer available.')
        elif response['command'] == 'start_game':
            if response['status'] == 'success':
                start_game_button.configure(state=tkinter.DISABLED)
        elif response['command'] == 'roll_die':
            if response['status'] == 'success':
                roll_die_button.configure(state=tkinter.DISABLED)
        elif response['command'] == 'move_piece':
            if response['status'] == 'success':
                selected_item = [None, None]
                # print('message successful sent')

    writer.close()


def connect():
    if len(username.get()) <= 0:
        tkinter.messagebox.showerror(title='Connection Error', message='You did not provide a username.')
    else:
        message = json.dumps({'client_id': client_id, 'command': 'register_client', 'client_name': username.get()})
        asyncio.run(send(message))


def create_game():
    message = json.dumps({'client_id': client_id, 'command': 'create_game'})
    asyncio.run(send(message))


def join_game():
    global client_state
    if len(games_combobox.get()) <= 0:
        tkinter.messagebox.showerror(title='Game Error', message='You did not select a game.')
    else:
        message = json.dumps({'client_id': client_id, 'command': 'join_game', 'game_id': games_combobox.get()})
        asyncio.run(send(message))


def start_game():
    global game
    message = json.dumps({'client_id': client_id, 'command': 'start_game', 'game_id': game.game_id})
    asyncio.run(send(message))


def roll_die():
    global game
    message = json.dumps({'client_id': client_id, 'command': 'roll_die', 'game_id': game.game_id})
    asyncio.run(send(message))
    poll()

selected_item = [None, None]
def interact(event):
    global selected_item
    global game
    global client_id
    if game.active_player == client_id and game.active_player_state == 'move':
        occupied_tiles = list()
        for cid in game.pieces:
            occupied_tiles += game.pieces[cid].values()

        active_guards = set()
        for tid in game.guards:
            if game.guards[tid] > 0:
                if tid in occupied_tiles:
                    active_guards.add(tid)


        item = canvas.find_closest(event.x, event.y)
        tags = canvas.gettags(item)
        for t in tags:
            if t.startswith('tid='):
                tid = t.split('=')[1]
                mode = 0
                if tid in game.pieces[client_id].values():
                    mode = 1
                if tid in active_guards:
                    mode = 2
                if tid in game.pieces[client_id].values() and tid in active_guards:
                    mode = 3

                canvas.itemconfig(item, outline='black')
                if mode == 3:
                    if selected_item[0] == tid:
                        canvas.itemconfig(item, width=3)
                        selected_item = [t.split('=')[1], 'guard']
                    else:
                        canvas.itemconfig(item, width=1)
                        selected_item = [t.split('=')[1], 'piece']
                elif mode == 2:
                    canvas.itemconfig(item, width=3)
                    selected_item = [t.split('=')[1], 'guard']
                elif mode == 1:
                    canvas.itemconfig(item, width=1)
                    selected_item = [t.split('=')[1], 'piece']
                break
        else:
            selected_item = [None, None]
        poll()


def confirm(event):
    global selected_item
    global game
    if game.active_player == client_id and game.active_player_state == 'move':
        item_confirmed = canvas.find_closest(event.x, event.y)
        if selected_item[0] is not None:
            ntid = game.board[min(game.board.index(selected_item[0]) + game.die_roll, len(game.board) - 1)]
            item_allowed = canvas.find_withtag('tid=' + ntid)

            if item_allowed == item_confirmed:
                message = json.dumps({'client_id': client_id, 'game_id': game.game_id, 'command': 'move_piece', 'tile': selected_item[0], 'type': selected_item[1]})
                asyncio.run(send(message))
                poll()

window.state('zoomed')
window.title('Verfuchst v0.1')

tkinter.Label(connect_frame, text='Username:').grid(row=0, column=0, columnspan=1, rowspan=1, padx=5, pady=5, sticky='w')
tkinter.Entry(connect_frame, width=15, textvariable=username).grid(row=0, column=1, columnspan=1, rowspan=1, padx=5, pady=5, sticky=tkinter.E+tkinter.W+tkinter.S+tkinter.N)
tkinter.Label(connect_frame, text='Server Address:').grid(row=1, column=0, columnspan=1, rowspan=1, padx=5, pady=5, sticky=tkinter.E+tkinter.W+tkinter.S+tkinter.N)
tkinter.Entry(connect_frame, width=15, textvariable=server_address).grid(row=1, column=1, columnspan=1, rowspan=1, padx=5, pady=5, sticky=tkinter.E+tkinter.W+tkinter.S+tkinter.N)
server_address.set('127.0.0.1:2106')
tkinter.Button(connect_frame, text='Connect', command=connect).grid(row=2, column=1, columnspan=1, rowspan=1, padx=5, pady=5, sticky=tkinter.E+tkinter.W+tkinter.S+tkinter.N)


tkinter.Button(lobby_frame, text='Join Game', command=join_game).grid(row=0, column=1, columnspan=1, rowspan=1, padx=5, pady=5, sticky='we')
tkinter.Button(lobby_frame, text='Create Game', command=create_game).grid(row=1, column=1, columnspan=1, rowspan=1, padx=5, pady=5, sticky='we')

game_id = tkinter.StringVar()
game_id.set('Game:')
tkinter.Label(game_frame, textvariable=game_id).grid(row=0, column=0, columnspan=1, rowspan=1, padx=5, pady=5, sticky='wn')
tkinter.Label(game_frame, text='Client: ' + client_id).grid(row=1, column=0, columnspan=1, rowspan=1, padx=5, pady=5, sticky='wn')
players_listbox = tkinter.Listbox(game_frame, listvariable=players_list, state=tkinter.NORMAL)
players_listbox.grid(row=0, column=4, columnspan=1, rowspan=4, padx=5, pady=5, sticky=tkinter.E+tkinter.W+tkinter.S+tkinter.N)
start_game_button = tkinter.Button(game_frame, text='Start Game', command=start_game, state=tkinter.DISABLED)
start_game_button.grid(row=2, column=0, columnspan=1, rowspan=1, padx=5, pady=5, sticky=tkinter.E+tkinter.W+tkinter.S+tkinter.N)
roll_die_button = tkinter.Button(game_frame, text='Roll Die', command=roll_die, state=tkinter.DISABLED)
roll_die_button.grid(row=2, column=1, columnspan=1, rowspan=1, padx=5, pady=5, sticky=tkinter.E+tkinter.W+tkinter.S+tkinter.N)
canvas = tkinter.Canvas(game_frame, width=1280, height=720)
canvas.bind("<Button-1>", interact)
canvas.bind("<Button-3>", confirm)
canvas.grid(row=3, column=0, columnspan=4, rowspan=1, padx=5, pady=5, sticky=tkinter.E+tkinter.W+tkinter.S+tkinter.N)

connect_frame.tkraise()


def calculate_score(tiles):
    negative = list()
    score = 0
    invert = 0
    for tid in tiles:
        if board_config[tid]['value'] == 0:
            invert += 1
        elif board_config[tid]['value'] > 0:
            score += board_config[tid]['value']
        else:
            negative.append(board_config[tid]['value'])
    negative = sorted(negative)
    for i in range(invert):
        if len(negative) > i:
            score += -1 * negative[i]
    for i in range(invert, len(negative)):
        score += negative[i]

    return score


def poll():
    colors = ['blue', 'red', 'green', 'purple']
    global clients
    global game
    global client_state
    global canvas
    global selected_item
    if client_registered:
        message = json.dumps({'client_id': client_id, 'command': 'get_game_state'})
        asyncio.run(send(message))
    if client_state == 'game_frame':
        canvas.delete('all')
        game_id.set('Game: ' + game.game_id)
        players_list.set([clients[player][0] + ' (' + color + ')' + '[' + str(calculate_score(game.scores[player])) + ']' for player, color in zip(game.players, colors[:len(game.players)]) if player in clients])
        players_listbox.selection_clear(0, tkinter.END)
        players_listbox.selection_set(game.players.index(game.active_player))
        if game.host_client_id == client_id and game.game_state == 'initialization':
            start_game_button.configure(state=tkinter.NORMAL)
        elif game.game_state == 'initialization':
            start_game_button.configure(text='waiting for players')
        elif game.game_state == 'running':
            start_game_button.configure(text='game in progress')
            if game.active_player == client_id and game.active_player_state == 'roll_die':
                roll_die_button.configure(state=tkinter.NORMAL)
            else:
                roll_die_button.configure(state=tkinter.DISABLED)

            canvas.create_text(1280 / 2, 32, text='Last Die Roll:', anchor='nw', font='TkMenuFont', fill='black')
            canvas.create_rectangle(1280/2, 64, 1280/2 + 64, 64+64, fill='white', outline='black')
            if game.die_roll == 1:
                canvas.create_oval(1280/2 + 32 - 4, 64 + 32 - 4, 1280/2 + 32 + 4, 64 + 32 + 4, fill='black', outline='black') # pip 1
            elif game.die_roll == 2:
                canvas.create_oval(1280/2 + 16 - 4, 64 + 16 - 4, 1280/2 + 16 + 4, 64 + 16 + 4, fill='black', outline='black') # pip 2
                canvas.create_oval(1280/2 + 48 - 4, 64 + 48 - 4, 1280/2 + 48 + 4, 64 + 48 + 4, fill='black', outline='black') # pip 2
            elif game.die_roll == 3:
                canvas.create_oval(1280/2 + 32 - 4, 64 + 32 - 4, 1280/2 + 32 + 4, 64 + 32 + 4, fill='black', outline='black') # pip 1
                canvas.create_oval(1280/2 + 16 - 4, 64 + 16 - 4, 1280/2 + 16 + 4, 64 + 16 + 4, fill='black', outline='black') # pip 2
                canvas.create_oval(1280/2 + 48 - 4, 64 + 48 - 4, 1280/2 + 48 + 4, 64 + 48 + 4, fill='black', outline='black') # pip 2
            elif game.die_roll == 4:
                canvas.create_oval(1280/2 + 16 - 4, 64 + 16 - 4, 1280/2 + 16 + 4, 64 + 16 + 4, fill='black', outline='black') # pip 2
                canvas.create_oval(1280/2 + 48 - 4, 64 + 48 - 4, 1280/2 + 48 + 4, 64 + 48 + 4, fill='black', outline='black') # pip 2
                canvas.create_oval(1280/2 + 48 - 4, 64 + 16 - 4, 1280/2 + 48 + 4, 64 + 16 + 4, fill='black', outline='black') # pip 2
                canvas.create_oval(1280/2 + 16 - 4, 64 + 48 - 4, 1280/2 + 16 + 4, 64 + 48 + 4, fill='black', outline='black') # pip 2
            elif game.die_roll == 5:
                canvas.create_oval(1280/2 + 32 - 4, 64 + 32 - 4, 1280/2 + 32 + 4, 64 + 32 + 4, fill='black', outline='black') # pip 1
                canvas.create_oval(1280/2 + 16 - 4, 64 + 16 - 4, 1280/2 + 16 + 4, 64 + 16 + 4, fill='black', outline='black') # pip 2
                canvas.create_oval(1280/2 + 48 - 4, 64 + 48 - 4, 1280/2 + 48 + 4, 64 + 48 + 4, fill='black', outline='black') # pip 2
                canvas.create_oval(1280/2 + 48 - 4, 64 + 16 - 4, 1280/2 + 48 + 4, 64 + 16 + 4, fill='black', outline='black') # pip 2
                canvas.create_oval(1280/2 + 16 - 4, 64 + 48 - 4, 1280/2 + 16 + 4, 64 + 48 + 4, fill='black', outline='black') # pip 2
            elif game.die_roll == 6:
                canvas.create_oval(1280/2 + 16 - 4, 64 + 16 - 4, 1280/2 + 16 + 4, 64 + 16 + 4, fill='black', outline='black') # pip 2
                canvas.create_oval(1280/2 + 48 - 4, 64 + 48 - 4, 1280/2 + 48 + 4, 64 + 48 + 4, fill='black', outline='black') # pip 2
                canvas.create_oval(1280/2 + 48 - 4, 64 + 16 - 4, 1280/2 + 48 + 4, 64 + 16 + 4, fill='black', outline='black') # pip 2
                canvas.create_oval(1280/2 + 16 - 4, 64 + 48 - 4, 1280/2 + 16 + 4, 64 + 48 + 4, fill='black', outline='black') # pip 2
                canvas.create_oval(1280/2 + 48 - 4, 64 + 32 - 4, 1280/2 + 48 + 4, 64 + 32 + 4, fill='black', outline='black') # pip 2
                canvas.create_oval(1280/2 + 16 - 4, 64 + 32 - 4, 1280/2 + 16 + 4, 64 + 32 + 4, fill='black', outline='black') # pip 2
            for i in range(len(game.board) - 1):
                tid_start = game.board[i]
                tid_end = game.board[i + 1]
                canvas.create_line(board_config[tid_start]['x'], board_config[tid_start]['y'], (board_config[tid_end]['x'] - board_config[tid_start]['x']) / 2 + board_config[tid_start]['x'], (board_config[tid_end]['y']- board_config[tid_start]['y']) / 2 + board_config[tid_start]['y'], width=3, fill='grey')
                canvas.create_line(board_config[tid_start]['x'], board_config[tid_start]['y'], board_config[tid_end]['x'], board_config[tid_end]['y'], width=1)

            try:
                for i, player in enumerate(game.players):
                    if i == 0:
                        canvas.create_oval(board_config[game.pieces[player]['001']]['x'] - 8, board_config[game.pieces[player]['001']]['y'] - 12, board_config[game.pieces[player]['001']]['x'] - 8 + 4, board_config[game.pieces[player]['001']]['y'] - 12 + 4, fill='deep sky blue', outline='deep sky blue')
                        canvas.create_oval(board_config[game.pieces[player]['002']]['x'] - 2, board_config[game.pieces[player]['002']]['y'] - 12, board_config[game.pieces[player]['002']]['x'] - 2 + 4, board_config[game.pieces[player]['002']]['y'] - 12 + 4, fill='deep sky blue', outline='deep sky blue')
                        canvas.create_oval(board_config[game.pieces[player]['003']]['x'] + 8 - 4, board_config[game.pieces[player]['003']]['y'] - 12, board_config[game.pieces[player]['003']]['x'] + 8, board_config[game.pieces[player]['003']]['y'] - 12 + 4, fill='deep sky blue', outline='deep sky blue')
                    elif i == 1:
                        canvas.create_oval(board_config[game.pieces[player]['001']]['x'] - 8, board_config[game.pieces[player]['001']]['y'] + 12, board_config[game.pieces[player]['001']]['x'] - 8 + 4, board_config[game.pieces[player]['001']]['y'] + 12 - 4, fill='orchid1', outline='orchid1')
                        canvas.create_oval(board_config[game.pieces[player]['002']]['x'] - 2, board_config[game.pieces[player]['002']]['y'] + 12, board_config[game.pieces[player]['002']]['x'] - 2 + 4, board_config[game.pieces[player]['002']]['y'] + 12 - 4, fill='orchid1', outline='orchid1')
                        canvas.create_oval(board_config[game.pieces[player]['003']]['x'] + 8 - 4, board_config[game.pieces[player]['003']]['y'] + 12, board_config[game.pieces[player]['003']]['x'] + 8, board_config[game.pieces[player]['003']]['y'] + 12 - 4, fill='orchid1', outline='orchid1')
                    elif i == 2:
                        canvas.create_oval(board_config[game.pieces[player]['001']]['x'] - 12, board_config[game.pieces[player]['001']]['y'] - 8, board_config[game.pieces[player]['001']]['x'] - 12 + 4, board_config[game.pieces[player]['001']]['y'] - 8 + 4, fill='SeaGreen1', outline='SeaGreen1')
                        canvas.create_oval(board_config[game.pieces[player]['002']]['x'] - 12, board_config[game.pieces[player]['002']]['y'] - 2, board_config[game.pieces[player]['002']]['x'] - 12 + 4, board_config[game.pieces[player]['002']]['y'] - 2 + 4, fill='SeaGreen1', outline='SeaGreen1')
                        canvas.create_oval(board_config[game.pieces[player]['003']]['x'] - 12, board_config[game.pieces[player]['003']]['y'] + 8 - 4, board_config[game.pieces[player]['003']]['x'] - 12 + 4, board_config[game.pieces[player]['003']]['y'] + 8, fill='SeaGreen1', outline='SeaGreen1')
                    elif i == 3:
                        canvas.create_oval(board_config[game.pieces[player]['001']]['x'] + 12, board_config[game.pieces[player]['001']]['y'] - 8, board_config[game.pieces[player]['001']]['x'] + 12 - 4, board_config[game.pieces[player]['001']]['y'] - 8 + 4, fill='MediumPurple1', outline='MediumPurple1')
                        canvas.create_oval(board_config[game.pieces[player]['002']]['x'] + 12, board_config[game.pieces[player]['002']]['y'] - 2, board_config[game.pieces[player]['002']]['x'] + 12 - 4, board_config[game.pieces[player]['002']]['y'] - 2 + 4, fill='MediumPurple1', outline='MediumPurple1')
                        canvas.create_oval(board_config[game.pieces[player]['003']]['x'] + 12, board_config[game.pieces[player]['003']]['y'] + 8 - 4, board_config[game.pieces[player]['003']]['x'] + 12 - 4, board_config[game.pieces[player]['003']]['y'] + 8, fill='MediumPurple1', outline='MediumPurple1')
            except:
                pass

            for tid in game.board:
                outline = board_config[tid]['color']
                width = 1
                if selected_item[0] == tid:
                    outline = 'black'
                    if selected_item[1] == 'guard':
                        width = 3
                canvas.create_rectangle(board_config[tid]['x'] - 8, board_config[tid]['y'] - 8, board_config[tid]['x'] + 7, board_config[tid]['y'] + 7, fill=board_config[tid]['color'], outline=outline, width=width, tags=('tid=' + tid,))
                canvas.create_text(board_config[tid]['x'], board_config[tid]['y'] - 14, text=str(board_config[tid]['value']), anchor='center', font=('TkMenuFont', 8), fill='black')
                if game.guards[tid] == 1:
                    canvas.create_rectangle(board_config[tid]['x'] - 7, board_config[tid]['y'] - 7, board_config[tid]['x'] - 7 + 3, board_config[tid]['y'] - 7 + 3, outline='black', fill='black')
                elif game.guards[tid] == 2:
                    canvas.create_rectangle(board_config[tid]['x'] - 7, board_config[tid]['y'] - 7, board_config[tid]['x'] - 7 + 3, board_config[tid]['y'] - 7 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7 + 5, board_config[tid]['y'] - 7, board_config[tid]['x'] - 7 + 6 + 3, board_config[tid]['y'] - 7 + 3, outline='black', fill='black')
                elif game.guards[tid] == 3:
                    canvas.create_rectangle(board_config[tid]['x'] - 7, board_config[tid]['y'] - 7, board_config[tid]['x'] - 7 + 3, board_config[tid]['y'] - 7 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7 + 5, board_config[tid]['y'] - 7, board_config[tid]['x'] - 7 + 5 + 3, board_config[tid]['y'] - 7 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7 + 5 + 5, board_config[tid]['y'] - 7, board_config[tid]['x'] - 7 + 5 + 5 + 3, board_config[tid]['y'] - 7 + 3, outline='black', fill='black')
                elif game.guards[tid] == 4:
                    canvas.create_rectangle(board_config[tid]['x'] - 7, board_config[tid]['y'] - 7, board_config[tid]['x'] - 7 + 3, board_config[tid]['y'] - 7 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7 + 5, board_config[tid]['y'] - 7, board_config[tid]['x'] - 7 + 5 + 3, board_config[tid]['y'] - 7 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7 + 5 + 5, board_config[tid]['y'] - 7, board_config[tid]['x'] - 7 + 5 + 5 + 3, board_config[tid]['y'] - 7 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7, board_config[tid]['y'] - 7 + 5 + 5, board_config[tid]['x'] - 7 + 3, board_config[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
                elif game.guards[tid] == 5:
                    canvas.create_rectangle(board_config[tid]['x'] - 7, board_config[tid]['y'] - 7, board_config[tid]['x'] - 7 + 3, board_config[tid]['y'] - 7 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7 + 5, board_config[tid]['y'] - 7, board_config[tid]['x'] - 7 + 5 + 3, board_config[tid]['y'] - 7 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7 + 5 + 5, board_config[tid]['y'] - 7, board_config[tid]['x'] - 7 + 5 + 5 + 3, board_config[tid]['y'] - 7 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7, board_config[tid]['y'] - 7 + 5 + 5, board_config[tid]['x'] - 7 + 3, board_config[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7 + 5, board_config[tid]['y'] - 7 + 5 + 5, board_config[tid]['x'] - 7 + 5 + 3, board_config[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
                elif game.guards[tid] == 6:
                    canvas.create_rectangle(board_config[tid]['x'] - 7, board_config[tid]['y'] - 7, board_config[tid]['x'] - 7 + 3, board_config[tid]['y'] - 7 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7 + 5, board_config[tid]['y'] - 7, board_config[tid]['x'] - 7 + 5 + 3, board_config[tid]['y'] - 7 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7 + 5 + 5, board_config[tid]['y'] - 7, board_config[tid]['x'] - 7 + 5 + 5 + 3, board_config[tid]['y'] - 7 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7, board_config[tid]['y'] - 7 + 5 + 5, board_config[tid]['x'] - 7 + 3, board_config[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7 + 5, board_config[tid]['y'] - 7 + 5 + 5, board_config[tid]['x'] - 7 + 5 + 3, board_config[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7 + 5 + 5, board_config[tid]['y'] - 7 + 5 + 5, board_config[tid]['x'] - 7 + 5 + 5 + 3, board_config[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
                elif game.guards[tid] == 7:
                    canvas.create_rectangle(board_config[tid]['x'] - 7, board_config[tid]['y'] - 7, board_config[tid]['x'] - 7 + 3, board_config[tid]['y'] - 7 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7 + 5, board_config[tid]['y'] - 7, board_config[tid]['x'] - 7 + 5 + 3, board_config[tid]['y'] - 7 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7 + 5 + 5, board_config[tid]['y'] - 7, board_config[tid]['x'] - 7 + 5 + 5 + 3, board_config[tid]['y'] - 7 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7, board_config[tid]['y'] - 7 + 5 + 5, board_config[tid]['x'] - 7 + 3, board_config[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7 + 5, board_config[tid]['y'] - 7 + 5 + 5, board_config[tid]['x'] - 7 + 5 + 3, board_config[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7 + 5 + 5, board_config[tid]['y'] - 7 + 5 + 5, board_config[tid]['x'] - 7 + 5 + 5 + 3, board_config[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7, board_config[tid]['y'] - 7 + 5, board_config[tid]['x'] - 7 + 3, board_config[tid]['y'] - 7 + 5 + 3, outline='black', fill='black')
                elif game.guards[tid] == 8:
                    canvas.create_rectangle(board_config[tid]['x'] - 7, board_config[tid]['y'] - 7, board_config[tid]['x'] - 7 + 3, board_config[tid]['y'] - 7 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7 + 5, board_config[tid]['y'] - 7, board_config[tid]['x'] - 7 + 5 + 3, board_config[tid]['y'] - 7 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7 + 5 + 5, board_config[tid]['y'] - 7, board_config[tid]['x'] - 7 + 5 + 5 + 3, board_config[tid]['y'] - 7 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7, board_config[tid]['y'] - 7 + 5 + 5, board_config[tid]['x'] - 7 + 3, board_config[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7 + 5, board_config[tid]['y'] - 7 + 5 + 5, board_config[tid]['x'] - 7 + 5 + 3, board_config[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7 + 5 + 5, board_config[tid]['y'] - 7 + 5 + 5, board_config[tid]['x'] - 7 + 5 + 5 + 3, board_config[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7, board_config[tid]['y'] - 7 + 5, board_config[tid]['x'] - 7 + 3, board_config[tid]['y'] - 7 + 5 + 3, outline='black', fill='black')
                    canvas.create_rectangle(board_config[tid]['x'] - 7 + 5 + 5, board_config[tid]['y'] - 7 + 5, board_config[tid]['x'] - 7 + 5 + 5 + 3, board_config[tid]['y'] - 7 + 5 + 3, outline='black', fill='black')
            if selected_item[0] is not None:
                ntid = game.board[min(game.board.index(selected_item[0]) + game.die_roll, len(game.board) - 1)]
                item = canvas.find_withtag('tid=' + ntid)
                canvas.itemconfig(item, width=3, outline='white')

            canvas.create_text(640, 256, text='Tiles: ' + ' '.join([str(board_config[tid]['value']) if board_config[tid]['value'] != 0 else 'G' for tid in game.scores[client_id]]), anchor='nw', font='TkMenuFont', fill='black')
            score = calculate_score(game.scores[client_id])
            canvas.create_text(640, 288, text='Score: ' + str(score), anchor='nw', font='TkMenuFont', fill='black')
        elif game.game_state == 'completed':
            start_game_button.configure(text='game is completed')
            canvas.delete('all')
            game_id.set('Game: ' + game.game_id)
            i = 0
            winner = list()
            for player, color in zip(game.players, colors[:len(game.players)]):
                if player in clients:
                    i += 1
                    txt = clients[player][0] + ': ' + str(calculate_score(game.scores[player])) + ' points'
                    winner.append([clients[player][0], calculate_score(game.scores[player])])
                    canvas.create_text(64, i * 43, text=txt, anchor='nw', font='TkMenuFont', fill='black')
            i += 1
            canvas.create_text(64, i * 43, text='Winner is: ' + sorted(winner, key=lambda x: -x[1])[0][0], anchor='nw', font=('TkMenuFont', 16, 'bold'), fill='black')
    window.after(1000, poll)


if __name__ == '__main__':
    window.after(1000, poll)
    window.mainloop()
    # message = json.dumps({'client_id': uuid.uuid4().hex})
    # asyncio.run(send(message))
    # asyncio.run(send(message))
