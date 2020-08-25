import socket
import pickle
import random
import threading

connected_clients = {} # socket object and client name
player_names = []
player_sockets = []
player_one_cards = []
player_two_cards = []
player_three_cards = []
player_four_cards = []
played_cards = []
kadi_people = []
card_asked_for = None
shape_asked_for = None
#game_order = []

all_cards = [
    "KC.png", "KD.png", "KH.png", "KS.png",
"QC.png", "QD.png", "QH.png", "QS.png",
"JC.png", "JD.png", "JH.png", "JS.png",
"AC.png", "AD.png", "AH.png", "AS.png",
"2C.png", "2D.png", "2H.png", "2S.png",
"3C.png", "3D.png", "3H.png", "3S.png",
"4C.png", "4D.png", "4H.png", "4S.png",
"5C.png", "5D.png", "5H.png", "5S.png",
"6C.png", "6D.png", "6H.png", "6S.png",
"7C.png", "7D.png", "7H.png", "7S.png",
"8C.png", "8D.png", "8H.png", "8S.png",
"9C.png", "9D.png", "9H.png", "9S.png",
"10C.png", "10D.png", "10H.png", "10S.png",
]
full_deck = all_cards.copy()
all_shapes = ["C", "D", "H", "S"] #clubs, diamonds, hearts, spades
all_numbers = ["K", "Q", "J", "A", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
all_conditions = [
    "NORMAL", "QUESTION", "ASKCARD", "ASKSHAPE", "PICKTWO",
    "PICKTHREE", "SUBSEQUENT", "NEXT", "JUMP", "PICKED2",
    "PICKED3", "ASKEDSHAPE", "ASKEDCARD", "KICKBACK"
]

normal = "NORMAL"
kickback = "KICKBACK"
question = "QUESTION"
askcard="ASKCARD"
askshape = "ASKSHAPE"
picktwo = "PICKTWO"
pickthree = "PICKTHREE"
subsequent = "SUBSEQUENT"
next_ = "NEXT"
jump = "JUMP"
picked2 = "PICKED2"
picked3 = "PICKED3"
askedshape = "ASKEDSHAPE"
askedcard = "ASKEDCARD"

current_condition = normal #start game with normal condition
current_turn = ''
proceed = 'proceed'
wait = 'wait'
current_message = wait
current_turn_index = 0
order = 1 #1 for forward and -1 for backward
winner = ''

def deal_cards(number_of_cards, number_of_players): #deals number_of_cards cards to number_of_players players from all cards
    random.shuffle(all_cards)
    p = []
    if number_of_players == 1:
        p.append(player_one_cards)
    elif number_of_players == 2:
        p.append(player_one_cards)
        p.append(player_two_cards)
    elif number_of_players == 3:
        p.append(player_one_cards)
        p.append(player_two_cards)
        p.append(player_three_cards)
    elif number_of_players == 4:
        p.append(player_one_cards)
        p.append(player_two_cards)
        p.append(player_three_cards)
        p.append(player_four_cards)
    for player in p:
        for x in range(0, number_of_cards):
            card = random.choice(all_cards)
            all_cards.remove(card)
            player.append(card)
    random.shuffle(all_cards)

def send_state_1():
    c = player_names.copy()
    while len(c)!= 4:
        c.append('')
    next_index = current_turn_index + order
    if next_index >= len(player_names):
        next_index = 0
    elif next_index < 0:
        next_index = len(player_names) - 1
    next_player = player_names[next_index]
    data = (c, player_one_cards, player_two_cards, player_three_cards, player_four_cards,
            all_cards, played_cards, kadi_people,
            current_condition, current_turn, card_asked_for, shape_asked_for, current_message, winner, next_player)
    data = pickle.dumps(data)
    player_sockets[0].send(data)

def send_state_2():
    if len(player_names) < 2:
        return
    c = list()
    c.append(player_names[1])
    c.append(player_names[0])
    if len(player_names) > 2:
        c.append(player_names[2])
    if len(player_names) > 3:
        c.append(player_names[3])
    while len(c) != 4:
        c.append('')
    next_index = current_turn_index + order
    if next_index >= len(player_names):
        next_index = 0
    elif next_index < 0:
        next_index = len(player_names) - 1
    next_player = player_names[next_index]
    data = (c, player_two_cards, player_one_cards, player_three_cards, player_four_cards,
            all_cards, played_cards, kadi_people,
            current_condition, current_turn, card_asked_for, shape_asked_for, current_message, winner, next_player)
    data = pickle.dumps(data)
    player_sockets[1].send(data)
    #print("Data sent to client", player_names[1])

def send_state_3():
    if len(player_names) < 3:
        return
    c = list()
    c.append(player_names[2])
    c.append(player_names[0])
    c.append(player_names[1])
    if len(player_names) > 3:
        c.append(player_names[3])
    while len(c) != 4:
        c.append('')
    next_index = current_turn_index + order
    if next_index >= len(player_names):
        next_index = 0
    elif next_index < 0:
        next_index = len(player_names) - 1
    next_player = player_names[next_index]
    data = (c, player_three_cards, player_one_cards, player_two_cards, player_four_cards,
            all_cards, played_cards, kadi_people,
            current_condition, current_turn, card_asked_for, shape_asked_for, current_message, winner, next_player)
    data = pickle.dumps(data)
    player_sockets[2].send(data)
    #print("Data sent to client", player_names[2])

def send_state_4():
    if len(player_names) < 4:
        return
    c = list()
    c.append(player_names[3])
    c.append(player_names[0])
    c.append(player_names[1])
    c.append(player_names[2])
    next_index = current_turn_index + order
    if next_index >= len(player_names):
        next_index = 0
    elif next_index < 0:
        next_index = len(player_names) - 1
    next_player = player_names[next_index]
    data = (c, player_two_cards, player_one_cards, player_three_cards, player_four_cards,
            all_cards, played_cards, kadi_people,
            current_condition, current_turn, card_asked_for, shape_asked_for, current_message, winner, next_player)
    data = pickle.dumps(data)
    player_sockets[3].send(data)
    #print("Data sent to client", player_names[3])

def send_state():
    global all_cards, played_cards
    #ensure some cards remain on the deck
    if len(all_cards) <= 5:
        for i in range(0, len(played_cards)-3):
            c = played_cards[i]
            played_cards.remove(c)
            all_cards.append(c)
    send_state_1()
    send_state_2()
    send_state_3()
    send_state_4()

def get_number_from_card(card):
    #returns a string containing the number of the card eg K, 10, 9
    #assumes the card passed is a valid card eg KC.png
    if card.startswith("1"):
        if card[1] == '0':
            number = '10'
        else:
            number = '1'
    else:
        number = card[0]#get first character
    return number

def get_shape_from_card(card):
    #return 'C', 'D', 'H', 'S' for clubs, diamonds, hearts, and spades
    #assumes the card passed is a valid card
    if card.startswith("1"):
        if card[1] == '0':
            shape = card[2]
        else:
            shape = card[1]
    else:
        shape = card[1]
    return shape

def get_all_cards_with_shape(shape):
    #returns all cards that are of the shape passed as a list
    #assumes the shape passed is valid
    cards = []
    for card in full_deck:
        if get_shape_from_card(card) == shape:
            cards.append(card)
    return cards

def get_all_cards_with_number(number):
    #returns all cards that are of the number passed as a list
    #assumes the number passed is valid
    cards = []
    for card in full_deck:
        if get_number_from_card(card) == number:
            cards.append(card)
    return cards

def get_starting_card():
    not_valid = list()
    cards = ("A", "K", "Q", 'J', '2', '3', '8')
    for c in cards:
        not_valid += get_all_cards_with_number(c)
    selected_card = all_cards[0]
    while selected_card in not_valid:
        selected_card = random.choice(all_cards)
    played_cards.append(selected_card)

def listen_1():
    class L(threading.Thread):
        def __init__(self):
            super().__init__()

        def run(self):
            print("Ready to receive the state from player 1")
            while True:
                #client sends data in this format
                #data = (my_cards, current_condition, kadi_people, current_message, card_asked_for, shaped_asked_for)
                state = player_sockets[0].recv(100000000)
                #print("Received state from player 1")
                state = pickle.loads(state)
                global player_one_cards, current_turn, current_condition, kadi_people, card_asked_for, shape_asked_for, current_turn_index
                global played_cards, all_cards, current_message, order, winner
                player_one_cards = state[0]
                current_condition = state[1]
                kadi_people = state[2]
                message = state[3]
                card_asked_for = state[4]
                shape_asked_for = state[5]
                played_cards = state[6]
                all_cards = state[7]
                winner = state[8]
                if message == proceed:
                    if current_condition == kickback:
                        order = order * -1
                        current_condition = normal
                    else:
                        pass
                    current_message = wait
                    current_turn_index += order
                    if current_turn_index >= len(player_names):
                        current_turn_index = 0
                    elif current_turn_index < 0:
                        current_turn_index = len(player_names)- 1
                    current_turn = player_names[current_turn_index]
                    #print("current turn:", current_turn)
                send_state()
    l = L()
    l.start()

def listen_2():
    class L(threading.Thread):
        def __init__(self):
            super().__init__()

        def run(self):
            print("Ready to receive the state from player 2")
            while True:
                #client sends data in this format
                #data = (my_cards, current_condition, kadi_people, current_message, card_asked_for, shaped_asked_for)
                state = player_sockets[1].recv(100000000)
                state = pickle.loads(state)
                global player_two_cards, current_turn, current_condition, kadi_people, card_asked_for, shape_asked_for
                global current_turn_index, played_cards, all_cards, current_message, order, winner
                player_two_cards = state[0]
                current_condition = state[1]
                kadi_people = state[2]
                message = state[3]
                card_asked_for = state[4]
                shape_asked_for = state[5]
                played_cards = state[6]
                all_cards = state[7]
                winner = state[8]
                if message == proceed:
                    if current_condition == kickback:
                        order *= -1
                        current_condition = normal
                    else:
                        pass
                    current_message = wait
                    current_turn_index += order
                    if current_turn_index >= len(player_names):
                        current_turn_index = 0
                    elif current_turn_index < 0:
                        current_turn_index = len(player_names) - 1
                    current_turn = player_names[current_turn_index]
                send_state()
    l = L()
    l.start()

def listen_3():
    class L(threading.Thread):
        def __init__(self):
            super().__init__()

        def run(self):
            print("Ready to receive the state from player 3")
            while True:
                #client sends data in this format
                #data = (my_cards, current_condition, kadi_people, current_message, card_asked_for, shaped_asked_for)
                state = player_sockets[2].recv(100000000)
                state = pickle.loads(state)
                global player_three_cards, current_turn, current_condition, kadi_people, card_asked_for, shape_asked_for
                global current_turn_index, played_cards, all_cards, current_message, order, winner
                player_three_cards = state[0]
                current_condition = state[1]
                kadi_people = state[2]
                message = state[3]
                card_asked_for = state[4]
                shape_asked_for = state[5]
                played_cards = state[6]
                all_cards = state[7]
                winner = state[8]
                if message == proceed:
                    if current_condition == kickback:
                        order *= -1
                        current_condition = normal
                    else:
                        pass
                    current_message = wait
                    current_turn_index += order
                    if current_turn_index >= len(player_names):
                        current_turn_index = 0
                    elif current_turn_index < 0:
                        current_turn_index = len(player_names) - 1
                    current_turn = player_names[current_turn_index]
                send_state()
    l = L()
    l.start()

def listen_4():
    class L(threading.Thread):
        def __init__(self):
            super().__init__()

        def run(self):
            print("Ready to receive the state from player 4")
            while True:
                #client sends data in this format
                #data = (my_cards, current_condition, kadi_people, current_message, card_asked_for, shaped_asked_for, played_cards)
                state = player_sockets[3].recv(100000000)
                state = pickle.loads(state)
                global player_four_cards, current_turn, current_condition, kadi_people, card_asked_for, shape_asked_for
                global current_turn_index, played_cards, all_cards, current_message, order, winner
                player_four_cards = state[0]
                current_condition = state[1]
                kadi_people = state[2]
                message = state[3]
                card_asked_for = state[4]
                shape_asked_for = state[5]
                played_cards = state[6]
                all_cards = state[7]
                winner = state[8]
                if message == proceed:
                    if current_condition == kickback:
                        order *= -1
                        current_condition = normal
                    else:
                        pass
                    current_message = wait
                    current_turn_index += order
                    if current_turn_index >= len(player_names):
                        current_turn_index = 0
                    elif current_turn_index < 0:
                        current_turn_index = len(player_names) - 1
                    current_turn = player_names[current_turn_index]
                send_state()
    l = L()
    l.start()

def listen():
    listen_1()
    if len(player_names) > 1:
        listen_2()
    if len(player_names) > 2:
        listen_3()
    if len(player_names) > 4:
        listen_4()

def main():
    host = ''
    port = 12345
    main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    main_socket.bind((host, port))
    main_socket.listen(4)
    print("The game server is ready to accept connections.")
    print("Waiting for client connections...")
    index = 0
    while len(player_names) < 4: #accept at most 4 clients
        a, b = main_socket.accept()
        print("A connection has been received from", b)
        name = a.recv(1024).decode('utf-8')
        print("Selected name: ", name)
        if len(name) > 10:
            name = name[0: 10]
        count = 0
        while name in player_names:
            name += str(count)
            count += 1
        is_last = a.recv(1024).decode('utf-8')
        player_names.append(name)
        player_sockets.append(a)
        index += 1
        if is_last == 'True':
            break
        print("Waiting for more connections...")
    print("Received all opponents. Starting game...")
    deal_cards(4, len(player_names))
    get_starting_card()
    global current_turn, game_order, current_turn_index
    game_order = player_names.copy()
    current_turn = game_order[0]  # First player will start the game
    current_turn_index = 0
    send_state()
    listen()
    print("The server is quietly serving the clients. Game in progress...")
    while True:
        #infinite game loop
        pass

if __name__ == "__main__":
    main()