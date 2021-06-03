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

import verfuchst.logic.gamestate


class GUI:
    def __init__(self, window):
        self.client_id = uuid.uuid4().hex
        self.client_registered = False
        self.client_state = 'connect_frame'
        self.clients = collections.defaultdict(list)


        self.window = window

        self.window.state('zoomed')
        self.window.title('Verfuchst v0.1')

        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        self.connect_frame = tkinter.Frame(self.window)
        self.connect_frame.grid(row=0, column=0)
        tkinter.Label(self.connect_frame, text='Username:').grid(row=0, column=0, columnspan=1, rowspan=1, padx=5, pady=5, sticky='w')
        self.username = tkinter.StringVar()
        tkinter.Entry(self.connect_frame, width=15, textvariable=self.username).grid(row=0, column=1, columnspan=1, rowspan=1, padx=5, pady=5, sticky=tkinter.E+tkinter.W+tkinter.S+tkinter.N)
        self.server_address = tkinter.StringVar()
        tkinter.Label(self.connect_frame, text='Server Address:').grid(row=1, column=0, columnspan=1, rowspan=1, padx=5, pady=5, sticky=tkinter.E+tkinter.W+tkinter.S+tkinter.N)
        tkinter.Entry(self.connect_frame, width=15, textvariable=self.server_address).grid(row=1, column=1, columnspan=1, rowspan=1, padx=5, pady=5, sticky=tkinter.E+tkinter.W+tkinter.S+tkinter.N)
        self.server_address.set('127.0.0.1:2106')
        tkinter.Button(self.connect_frame, text='Connect', command=self.connect).grid(row=2, column=1, columnspan=1, rowspan=1, padx=5, pady=5, sticky=tkinter.E+tkinter.W+tkinter.S+tkinter.N)

        self.lobby_frame = tkinter.Frame(self.window)
        self.games = list()
        self.games_combobox = tkinter.ttk.Combobox(self.lobby_frame, values=self.games, state='readonly')
        self.games_combobox.grid(row=0, column=0, columnspan=1, rowspan=1, padx=5, pady=5, sticky='w')
        tkinter.Button(self.lobby_frame, text='Join Game', command=self.join_game).grid(row=0, column=1, columnspan=1, rowspan=1, padx=5, pady=5, sticky='we')
        tkinter.Button(self.lobby_frame, text='Create Game', command=self.create_game).grid(row=1, column=1, columnspan=1, rowspan=1, padx=5, pady=5, sticky='we')

        self.game_frame = tkinter.Frame(self.window)
        self.game_id = tkinter.StringVar()
        self.game_id.set('Game:')
        tkinter.Label(self.game_frame, textvariable=self.game_id).grid(row=0, column=0, columnspan=1, rowspan=1, padx=5, pady=5, sticky='wn')
        tkinter.Label(self.game_frame, text='Client: ' + self.client_id).grid(row=1, column=0, columnspan=1, rowspan=1, padx=5, pady=5, sticky='wn')
        self.players_list = tkinter.StringVar()
        self.players_listbox = tkinter.Listbox(self.game_frame, listvariable=self.players_list, state=tkinter.NORMAL)
        self.players_listbox.grid(row=0, column=4, columnspan=1, rowspan=4, padx=5, pady=5, sticky=tkinter.E+tkinter.W+tkinter.S+tkinter.N)
        self.start_game_button = tkinter.Button(self.game_frame, text='Start Game', command=self.start_game, state=tkinter.DISABLED)
        self.start_game_button.grid(row=2, column=0, columnspan=1, rowspan=1, padx=5, pady=5, sticky=tkinter.E+tkinter.W+tkinter.S+tkinter.N)
        self.roll_die_button = tkinter.Button(self.game_frame, text='Roll Die', command=self.roll_die, state=tkinter.DISABLED)
        self.roll_die_button.grid(row=2, column=1, columnspan=1, rowspan=1, padx=5, pady=5, sticky=tkinter.E+tkinter.W+tkinter.S+tkinter.N)

        self.game = None

        self.canvas = tkinter.Canvas(self.game_frame, width=1280, height=720)
        self.canvas.bind("<Button-1>", self.interact)
        self.canvas.bind("<Button-3>", self.confirm)
        self.canvas.grid(row=3, column=0, columnspan=4, rowspan=1, padx=5, pady=5, sticky=tkinter.E+tkinter.W+tkinter.S+tkinter.N)

        self.selected_item = [None, None]

        self.connect_frame.tkraise()

        self.window.after(1000, self.poll)


    def connect(self):
        if len(self.username.get()) <= 0:
            tkinter.messagebox.showerror(title='Connection Error', message='You did not provide a username.')
        else:
            message = json.dumps({'client_id': self.client_id, 'command': 'register_client', 'client_name': self.username.get()})
            asyncio.run(self.send(message))


    async def send(self, message):
        host, port = self.server_address.get().split(':')
        port = int(port)
        reader, writer = await asyncio.open_connection(host, port)
        writer.write(message.encode())
        await writer.drain()

        data = await reader.read(4096)
        response = json.loads(data.decode())
        if response['status'] == 'success':
            if response['command'] == 'register_client':
                self.client_registered = True
                self.connect_frame.grid_remove()
                self.lobby_frame.grid(row=0, column=0)
            elif response['command'] == 'get_game_state':
                for c, n, g in response['clients']:
                    self.clients[c] = [n, g]
                if response['game_payload'] is not None:
                    self.game = verfuchst.logic.gamestate.Game(None)
                    self.game.deserialize(response['game_payload'])
                self.games = response['games']
                self.games_combobox['values'] = self.games
            elif response['command'] == 'create_game':
                if response['status'] == 'success':
                    self.client_state = 'game_frame'
                    self.lobby_frame.grid_remove()
                    self.game_frame.grid(row=0, column=0)
                else:
                    tkinter.messagebox.showerror(title='Game Error', message='Game is no longer available.')
            elif response['command'] == 'join_game':
                if response['status'] == 'success':
                    self.client_state = 'game_frame'
                    self.lobby_frame.grid_remove()
                    self.game_frame.grid(row=0, column=0)
                else:
                    tkinter.messagebox.showerror(title='Game Error', message='Game is no longer available.')
            elif response['command'] == 'start_game':
                self.start_game_button.configure(state=tkinter.DISABLED)
            elif response['command'] == 'roll_die':
                self.roll_die_button.configure(state=tkinter.DISABLED)
            elif response['command'] == 'move_piece':
                self.selected_item = [None, None]
        else:
            print(response)
        writer.close()


    def create_game(self):
        message = json.dumps({'client_id': self.client_id, 'command': 'create_game'})
        asyncio.run(self.send(message))


    def join_game(self):
        if len(self.games_combobox.get()) <= 0:
            tkinter.messagebox.showerror(title='Game Error', message='You did not select a game.')
        else:
            message = json.dumps({'client_id': self.client_id, 'command': 'join_game', 'game_id': self.games_combobox.get()})
            asyncio.run(self.send(message))


    def start_game(self):
        message = json.dumps({'client_id': self.client_id, 'command': 'start_game', 'game_id': self.game.game_id})
        asyncio.run(self.send(message))


    def roll_die(self):
        message = json.dumps({'client_id': self.client_id, 'command': 'roll_die', 'game_id': self.game.game_id})
        asyncio.run(self.send(message))
        self.poll()


    def _draw_die(self):
        self.canvas.create_text(1280 / 2, 32, text='Last Die Roll:', anchor='nw', font='TkMenuFont', fill='black')
        self.canvas.create_rectangle(1280/2, 64, 1280/2 + 64, 64+64, fill='white', outline='black')
        if self.game.die_roll == 1:
            self.canvas.create_oval(1280/2 + 32 - 4, 64 + 32 - 4, 1280/2 + 32 + 4, 64 + 32 + 4, fill='black', outline='black') # pip 1
        elif self.game.die_roll == 2:
            self.canvas.create_oval(1280/2 + 16 - 4, 64 + 16 - 4, 1280/2 + 16 + 4, 64 + 16 + 4, fill='black', outline='black') # pip 2
            self.canvas.create_oval(1280/2 + 48 - 4, 64 + 48 - 4, 1280/2 + 48 + 4, 64 + 48 + 4, fill='black', outline='black') # pip 2
        elif self.game.die_roll == 3:
            self.canvas.create_oval(1280/2 + 32 - 4, 64 + 32 - 4, 1280/2 + 32 + 4, 64 + 32 + 4, fill='black', outline='black') # pip 1
            self.canvas.create_oval(1280/2 + 16 - 4, 64 + 16 - 4, 1280/2 + 16 + 4, 64 + 16 + 4, fill='black', outline='black') # pip 2
            self.canvas.create_oval(1280/2 + 48 - 4, 64 + 48 - 4, 1280/2 + 48 + 4, 64 + 48 + 4, fill='black', outline='black') # pip 2
        elif self.game.die_roll == 4:
            self.canvas.create_oval(1280/2 + 16 - 4, 64 + 16 - 4, 1280/2 + 16 + 4, 64 + 16 + 4, fill='black', outline='black') # pip 2
            self.canvas.create_oval(1280/2 + 48 - 4, 64 + 48 - 4, 1280/2 + 48 + 4, 64 + 48 + 4, fill='black', outline='black') # pip 2
            self.canvas.create_oval(1280/2 + 48 - 4, 64 + 16 - 4, 1280/2 + 48 + 4, 64 + 16 + 4, fill='black', outline='black') # pip 2
            self.canvas.create_oval(1280/2 + 16 - 4, 64 + 48 - 4, 1280/2 + 16 + 4, 64 + 48 + 4, fill='black', outline='black') # pip 2
        elif self.game.die_roll == 5:
            self.canvas.create_oval(1280/2 + 32 - 4, 64 + 32 - 4, 1280/2 + 32 + 4, 64 + 32 + 4, fill='black', outline='black') # pip 1
            self.canvas.create_oval(1280/2 + 16 - 4, 64 + 16 - 4, 1280/2 + 16 + 4, 64 + 16 + 4, fill='black', outline='black') # pip 2
            self.canvas.create_oval(1280/2 + 48 - 4, 64 + 48 - 4, 1280/2 + 48 + 4, 64 + 48 + 4, fill='black', outline='black') # pip 2
            self.canvas.create_oval(1280/2 + 48 - 4, 64 + 16 - 4, 1280/2 + 48 + 4, 64 + 16 + 4, fill='black', outline='black') # pip 2
            self.canvas.create_oval(1280/2 + 16 - 4, 64 + 48 - 4, 1280/2 + 16 + 4, 64 + 48 + 4, fill='black', outline='black') # pip 2
        elif self.game.die_roll == 6:
            self.canvas.create_oval(1280/2 + 16 - 4, 64 + 16 - 4, 1280/2 + 16 + 4, 64 + 16 + 4, fill='black', outline='black') # pip 2
            self.canvas.create_oval(1280/2 + 48 - 4, 64 + 48 - 4, 1280/2 + 48 + 4, 64 + 48 + 4, fill='black', outline='black') # pip 2
            self.canvas.create_oval(1280/2 + 48 - 4, 64 + 16 - 4, 1280/2 + 48 + 4, 64 + 16 + 4, fill='black', outline='black') # pip 2
            self.canvas.create_oval(1280/2 + 16 - 4, 64 + 48 - 4, 1280/2 + 16 + 4, 64 + 48 + 4, fill='black', outline='black') # pip 2
            self.canvas.create_oval(1280/2 + 48 - 4, 64 + 32 - 4, 1280/2 + 48 + 4, 64 + 32 + 4, fill='black', outline='black') # pip 2
            self.canvas.create_oval(1280/2 + 16 - 4, 64 + 32 - 4, 1280/2 + 16 + 4, 64 + 32 + 4, fill='black', outline='black') # pip 2


    def _draw_pegs(self):
        for i, player in enumerate(self.game.players):
            if i == 0:
                self.canvas.create_oval(verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['001']]['x'] - 8, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['001']]['y'] - 12, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['001']]['x'] - 8 + 4, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['001']]['y'] - 12 + 4, fill='deep sky blue', outline='deep sky blue')
                self.canvas.create_oval(verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['002']]['x'] - 2, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['002']]['y'] - 12, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['002']]['x'] - 2 + 4, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['002']]['y'] - 12 + 4, fill='deep sky blue', outline='deep sky blue')
                self.canvas.create_oval(verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['003']]['x'] + 8 - 4, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['003']]['y'] - 12, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['003']]['x'] + 8, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['003']]['y'] - 12 + 4, fill='deep sky blue', outline='deep sky blue')
            elif i == 1:
                self.canvas.create_oval(verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['001']]['x'] - 8, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['001']]['y'] + 12, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['001']]['x'] - 8 + 4, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['001']]['y'] + 12 - 4, fill='orchid1', outline='orchid1')
                self.canvas.create_oval(verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['002']]['x'] - 2, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['002']]['y'] + 12, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['002']]['x'] - 2 + 4, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['002']]['y'] + 12 - 4, fill='orchid1', outline='orchid1')
                self.canvas.create_oval(verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['003']]['x'] + 8 - 4, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['003']]['y'] + 12, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['003']]['x'] + 8, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['003']]['y'] + 12 - 4, fill='orchid1', outline='orchid1')
            elif i == 2:
                self.canvas.create_oval(verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['001']]['x'] - 12, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['001']]['y'] - 8, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['001']]['x'] - 12 + 4, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['001']]['y'] - 8 + 4, fill='SeaGreen1', outline='SeaGreen1')
                self.canvas.create_oval(verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['002']]['x'] - 12, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['002']]['y'] - 2, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['002']]['x'] - 12 + 4, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['002']]['y'] - 2 + 4, fill='SeaGreen1', outline='SeaGreen1')
                self.canvas.create_oval(verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['003']]['x'] - 12, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['003']]['y'] + 8 - 4, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['003']]['x'] - 12 + 4, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['003']]['y'] + 8, fill='SeaGreen1', outline='SeaGreen1')
            elif i == 3:
                self.canvas.create_oval(verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['001']]['x'] + 12, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['001']]['y'] - 8, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['001']]['x'] + 12 - 4, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['001']]['y'] - 8 + 4, fill='MediumPurple1', outline='MediumPurple1')
                self.canvas.create_oval(verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['002']]['x'] + 12, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['002']]['y'] - 2, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['002']]['x'] + 12 - 4, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['002']]['y'] - 2 + 4, fill='MediumPurple1', outline='MediumPurple1')
                self.canvas.create_oval(verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['003']]['x'] + 12, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['003']]['y'] + 8 - 4, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['003']]['x'] + 12 - 4, verfuchst.logic.gamestate.BOARD_CONFIG[self.game.pieces[player]['003']]['y'] + 8, fill='MediumPurple1', outline='MediumPurple1')


    def _draw_guardians(self, tid):
        if self.game.guards[tid] == 1:
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 3, outline='black', fill='black')
        elif self.game.guards[tid] == 2:
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 6 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 3, outline='black', fill='black')
        elif self.game.guards[tid] == 3:
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 5 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 3, outline='black', fill='black')
        elif self.game.guards[tid] == 4:
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 5 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
        elif self.game.guards[tid] == 5:
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 5 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
        elif self.game.guards[tid] == 6:
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 5 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 5 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
        elif self.game.guards[tid] == 7:
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 5 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 5 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 3, outline='black', fill='black')
        elif self.game.guards[tid] == 8:
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 5 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 5 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 5 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 3, outline='black', fill='black')
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 7 + 5 + 5 + 3, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 7 + 5 + 3, outline='black', fill='black')


    def _display_final_score(self, colors):
        self.start_game_button.configure(text='game is completed')
        self.canvas.delete('all')
        self.game_id.set('Game: ' + self.game.game_id)
        i = 0
        winner = list()
        for player, color in zip(self.game.players, colors[:len(self.game.players)]):
            if player in self.clients:
                i += 1
                txt = self.clients[player][0] + ': ' + str(self.game.calculate_score(self.game.scores[player])) + ' points'
                winner.append([self.clients[player][0], self.game.calculate_score(self.game.scores[player])])
                self.canvas.create_text(64, i * 43, text=txt, anchor='nw', font='TkMenuFont', fill='black')
        i += 1
        self.canvas.create_text(64, i * 43, text='Winner is: ' + sorted(winner, key=lambda x: -x[1])[0][0], anchor='nw', font=('TkMenuFont', 16, 'bold'), fill='black')


    def _draw_board(self):
        for i in range(len(self.game.board) - 1):
            tid_start = self.game.board[i]
            tid_end = self.game.board[i + 1]
            self.canvas.create_line(verfuchst.logic.gamestate.BOARD_CONFIG[tid_start]['x'], verfuchst.logic.gamestate.BOARD_CONFIG[tid_start]['y'], (verfuchst.logic.gamestate.BOARD_CONFIG[tid_end]['x'] - verfuchst.logic.gamestate.BOARD_CONFIG[tid_start]['x']) / 2 + verfuchst.logic.gamestate.BOARD_CONFIG[tid_start]['x'], (verfuchst.logic.gamestate.BOARD_CONFIG[tid_end]['y']- verfuchst.logic.gamestate.BOARD_CONFIG[tid_start]['y']) / 2 + verfuchst.logic.gamestate.BOARD_CONFIG[tid_start]['y'], width=3, fill='grey')
            self.canvas.create_line(verfuchst.logic.gamestate.BOARD_CONFIG[tid_start]['x'], verfuchst.logic.gamestate.BOARD_CONFIG[tid_start]['y'], verfuchst.logic.gamestate.BOARD_CONFIG[tid_end]['x'], verfuchst.logic.gamestate.BOARD_CONFIG[tid_end]['y'], width=1)

        self._draw_pegs()

        for tid in self.game.board:
            outline = verfuchst.logic.gamestate.BOARD_CONFIG[tid]['color']
            width = 1
            if self.selected_item[0] == tid:
                outline = 'black'
                if self.selected_item[1] == 'guard':
                    width = 3
            self.canvas.create_rectangle(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] - 8, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 8, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'] + 7, verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] + 7, fill=verfuchst.logic.gamestate.BOARD_CONFIG[tid]['color'], outline=outline, width=width, tags=('tid=' + tid,))
            self.canvas.create_text(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['x'], verfuchst.logic.gamestate.BOARD_CONFIG[tid]['y'] - 14, text=str(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['value']), anchor='center', font=('TkMenuFont', 8), fill='black')
            self._draw_guardians(tid)


    def poll(self):
        colors = ['blue', 'red', 'green', 'purple']
        if self.client_registered:
            message = json.dumps({'client_id': self.client_id, 'command': 'get_game_state'})
            asyncio.run(self.send(message))
        if self.client_state == 'game_frame':
            if self.game is not None:
                self.canvas.delete('all')
                self.game_id.set('Game: ' + self.game.game_id)
                self.players_list.set([self.clients[player][0] + ' (' + color + ')' + '[' + str(self.game.calculate_score(self.game.scores[player])) + ']' for player, color in zip(self.game.players, colors[:len(self.game.players)]) if player in self.clients])
                self.players_listbox.selection_clear(0, tkinter.END)
                self.players_listbox.selection_set(self.game.players.index(self.game.active_player))
                if self.game.host_client_id == self.client_id and self.game.game_state == 'initialization':
                    self.start_game_button.configure(state=tkinter.NORMAL)
                elif self.game.game_state == 'initialization':
                    self.start_game_button.configure(text='waiting for players')
                elif self.game.game_state == 'running':
                    self.start_game_button.configure(text='game in progress')
                    self.start_game_button.configure(state=tkinter.DISABLED)
                    if self.game.active_player == self.client_id and self.game.active_player_state == 'roll_die':
                        self.roll_die_button.configure(state=tkinter.NORMAL)
                    else:
                        self.roll_die_button.configure(state=tkinter.DISABLED)

                    self._draw_die()
                    self._draw_board()
                    if self.selected_item[0] is not None:
                        ntid = self.game.board[min(self.game.board.index(self.selected_item[0]) + self.game.die_roll, len(self.game.board) - 1)]
                        item = self.canvas.find_withtag('tid=' + ntid)
                        self.canvas.itemconfig(item, width=3, outline='white')

                    self.canvas.create_text(640, 256, text='Tiles: ' + ' '.join([str(verfuchst.logic.gamestate.BOARD_CONFIG[tid]['value']) if verfuchst.logic.gamestate.BOARD_CONFIG[tid]['value'] != 0 else 'G' for tid in self.game.scores[self.client_id]]), anchor='nw', font='TkMenuFont', fill='black')
                    score = self.game.calculate_score(self.game.scores[self.client_id])
                    self.canvas.create_text(640, 288, text='Score: ' + str(score), anchor='nw', font='TkMenuFont', fill='black')
            if self.game is not None:
                if self.game.game_state == 'completed':
                    _display_final_score(colors)
        self.window.after(1000, self.poll)


    def confirm(self, event):
        if self.game.active_player == self.client_id and self.game.active_player_state == 'move':
            item_confirmed = self.canvas.find_closest(event.x, event.y)
            if self.selected_item[0] is not None:
                ntid = self.game.board[min(self.game.board.index(self.selected_item[0]) + self.game.die_roll, len(self.game.board) - 1)]
                item_allowed = self.canvas.find_withtag('tid=' + ntid)

                if item_allowed == item_confirmed:
                    message = json.dumps({'client_id': self.client_id, 'game_id': self.game.game_id, 'command': 'move_piece', 'tile': self.selected_item[0], 'type': self.selected_item[1]})
                    asyncio.run(self.send(message))
                    self.poll()


    def _determine_move_mode(self, tid):
        mode = 0
        if tid in self.game.pieces[self.client_id].values():
            mode = 1

        occupied_tiles = list()
        for cid in self.game.pieces:
            occupied_tiles += self.game.pieces[cid].values()

        active_guards = set()
        for gid in self.game.guards:
            if self.game.guards[gid] > 0:
                if gid in occupied_tiles:
                    active_guards.add(gid)

        if tid in active_guards:
            mode = 2
            if tid in self.game.pieces[self.client_id].values():
                mode = 3
        return mode


    def _highlight_target_tile(self, tid, item):
        mode = self._determine_move_mode(tid)
        if mode == 3:
            if self.selected_item[0] == tid:
                self.canvas.itemconfig(item, width=3)
                self.selected_item = [tid, 'guard']
            else:
                self.canvas.itemconfig(item, width=1)
                self.selected_item = [tid, 'piece']
        elif mode == 2:
            self.canvas.itemconfig(item, width=3)
            self.selected_item = [tid, 'guard']
        elif mode == 1:
            self.canvas.itemconfig(item, width=1)
            self.selected_item = [tid, 'piece']


    def interact(self, event):
        if self.game.active_player == self.client_id and self.game.active_player_state == 'move':
            item = self.canvas.find_closest(event.x, event.y)
            tags = self.canvas.gettags(item)
            for t in tags:
                if t.startswith('tid='):
                    self.canvas.itemconfig(item, outline='black')
                    tid = t.split('=')[1]
                    self._highlight_target_tile(tid, item)
                    break
            else:
                self.selected_item = [None, None]
            self.poll()


if __name__ == '__main__':
    window = tkinter.Tk()
    gui = GUI(window)
    window.mainloop()
