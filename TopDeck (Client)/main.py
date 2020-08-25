
import socket
import pickle
import pygame
from pygame.locals import *
from resources import *
import threading

screen_size = (640, 480)
backcolor = (34, 139, 34) #some shade of green called forest green
linecolor = (200, 10, 10) #some shade of red whose name I do not know
textcolor = (0, 0, 0) #black. There are no shades of black, I think
highlight_color = (0, 0, 255) #The bluest blue can be
resources = Resources()
card_images_path = "Card Images/"
card_size = (65, 100)
my_cards = []
player_one_cards = []
player_two_cards = []
player_three_cards = []
kadi_people = []
played_cards = []
deck = []
player_one_name = "Player 1"
player_two_name = "Player 2"
player_three_name = "Player 3"
my_name = "Mustafa"
kadi_people_location = []
played_cards_location = []
deck_location = []
#commands (buttons)
place_top_card_location = []
pick_card_location = []
go_kadi_location = []
next_player_location = []
how_to_play_location = []
reorder_location = []

current_turn = ''
current_condition = ''
wait = 'wait'
proceed = 'proceed'
current_message = wait #or proceed
card_asked_for = ''
shape_asked_for = ''
main_socket = None
next_player = ''


card_display_size = int(card_size[0]/2)

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
error_message = ''
refusing = False
won = False
winner = ''


def test():
    pygame.init()
    screen = pygame.display.set_mode((640, 480), 0, 32)
    global winner, my_name
    my_name = 'MUS'
    winner = 'MUST'
    show_win_screen(screen)

def send_state():
    data = [my_cards, current_condition, kadi_people, current_message, card_asked_for, shape_asked_for, played_cards, all_cards,
            ]
    if won:
        data.append(my_name)
    else:
        data.append('')
    data = pickle.dumps(data)
    main_socket.send(data)
    #print("Game state sent to the server")

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

def handle_reorder():
    if len(my_cards) <= 1:
        return
    #take the last card to the first position
    card = my_cards[len(my_cards)-1]
    my_cards.remove(my_cards[len(my_cards)-1])
    my_cards.insert(0, card)
    send_state()

def show_select_card_screen(screen):
    global card_asked_for
    #cards_to_show = list()
    x = 50
    y = 50
    interval = 10
    card_rects = list()
    cards_to_show = list()
    cards_on_screen = list()
    if len(my_cards) == 0:
        #select top n  cards from the deck
        for card in full_deck:
            cards_to_show.append(resources.get_card_image(card_images_path + card, card_size))
            cards_on_screen.append(card)
            card_rects.append(Rect(x, y, card_size[0], card_size[1]))
            if x + interval + card_size[0] > 640:
                x = 50
                y += interval + card_size[1]
            else:
                x += interval
    else:
        #select any card from the cards the player has
        for card in my_cards:
            cards_to_show.append(resources.get_card_image(card_images_path + card, card_size))
            card_rects.append(Rect(x, y, card_size[0], card_size[1]))
            cards_on_screen.append(card)
            if x + interval + card_size[0] > 640:
                x = 50
                y += interval + card_size[1]
            else:
                x +=  card_size[0]
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return None
            if event.type == MOUSEBUTTONDOWN:
                pos = event.pos
                for rect in card_rects:
                    if rect.collidepoint(pos[0], pos[1]):
                        index = card_rects.index(rect)
                        card = cards_on_screen[index]
                        number = get_number_from_card(card)
                        shape = get_shape_from_card(card)
                        print(number+shape)
                        card_asked_for = card
                        return card
        screen.fill(backcolor)
        pos = pygame.mouse.get_pos()
        highlight_rect = None
        for rect in card_rects:
            if rect.collidepoint(pos[0], pos[1]):
                index = card_rects.index(rect)
                highlight_rect = card_rects[index]
        x = 50
        y = 50

        surface = resources.get_font('sans.ttf').render("Select the card you want to ask for:", True, textcolor)
        rect = surface.get_rect()
        rect.top = y - resources.get_font('sans.ttf').size("Select the card you want to ask for:")[1]
        rect.left = x
        screen.blit(surface, rect)

        for card in cards_to_show:
            screen.blit(card, (x, y))
            if (x + card_size[0]) >= 640:
                x = 0
                y += card_size[1]
            else:
                x += card_size[0]
        if not highlight_rect is None:
            pygame.draw.rect(screen, highlight_color, highlight_rect, 4)
        pygame.display.update()
    #return selected_card

def show_select_shape_screen(screen):
    global shape_asked_for
    cards_to_show = list()
    card_rects = list()
    x, y = 150, 50
    interval = 5
    cards_to_show.append(resources.get_card_image(card_images_path + 'C.png', card_size))
    card_rects.append(Rect(x, y, card_size[0], card_size[1]))
    cards_to_show.append(resources.get_card_image(card_images_path + 'D.png', card_size))
    x += card_size[0] + interval
    card_rects.append(Rect(x, y, card_size[0], card_size[1]))
    cards_to_show.append(resources.get_card_image(card_images_path + 'H.png', card_size))
    x += card_size[0] + interval
    card_rects.append(Rect(x, y, card_size[0], card_size[1]))
    cards_to_show.append(resources.get_card_image(card_images_path + 'S.png', card_size))
    x += card_size[0] + interval
    card_rects.append(Rect(x, y, card_size[0], card_size[1]))
    while True:
        highlight_rect = None
        for event in pygame.event.get():
            if event.type == QUIT:
                return None
            if event.type == MOUSEBUTTONDOWN:
                pos = event.pos
                for rect in card_rects:
                    if rect.collidepoint(pos[0], pos[1]):
                        index = card_rects.index(rect)
                        c = ['C', 'D', 'H', 'S']
                        shape_asked_for = c[index]
                        return c[index]
        screen.fill(backcolor)
        x = 150
        y = 50
        pos = pygame.mouse.get_pos()
        for rect in card_rects:
            if rect.collidepoint(pos[0], pos[1]):
                highlight_rect = rect
                break
        for card in cards_to_show:
            screen.blit(card, (x, y))
            if (x + card_size[0]) >= 640:
                x = 0
                y += card_size[1]
            else:
                x += card_size[0] + interval
        y += card_size[1] + interval
        x = 150
        font = resources.get_font('sans.ttf')
        s = font.render('Your cards: ', True, textcolor)
        r = s.get_rect()
        r.topleft = (x, y)
        screen.blit(s, (x, y))
        y += font.size('Your cards: ')[1]

        for card in my_cards:
            image = resources.get_card_image(card_images_path + card, card_size)
            screen.blit(image, (x,y))
            x += card_display_size

        if not highlight_rect is None:
            pygame.draw.rect(screen, highlight_color, highlight_rect, 2)
        pygame.display.update()

def handle_pick():
    global current_message, current_condition, error_message
    picked = False
    #print("Condition: ", current_condition)
    if current_turn != my_name:
        error_message = 'It is not your turn!'
        return
    if current_condition == normal:
        my_cards.append(all_cards.pop())
        current_condition = next_
        current_message = wait
        picked = True
    elif current_condition == question:
        my_cards.append(all_cards.pop())
        current_condition = next_
        current_message = wait
        picked = True
    elif current_condition == askcard:
        my_cards.append(all_cards.pop())
        current_condition = askedcard
        current_message = wait
        picked = True
    elif current_condition == askshape:
        my_cards.append(all_cards.pop())
        current_condition = askedshape
        current_message = wait
        picked = True
    elif current_condition == picktwo:
        my_cards.append(all_cards.pop())
        my_cards.append(all_cards.pop())
        current_condition = picked2
        current_message = wait
        picked = True
    elif current_condition == pickthree:
        my_cards.append(all_cards.pop())
        my_cards.append(all_cards.pop())
        my_cards.append(all_cards.pop())
        current_condition = picked3
        current_message = wait
        picked = True
    elif current_condition == subsequent:
        error_message = "You cannot pick a card after you have placed another!"
    elif current_condition == jump:
        error_message = "You have been jumped. Click next!"
    else:
        error_message = "I don't know what it is, but you shouldn't be doing that!"
    if picked:
        #print("Condition: ", current_condition)
        if kadi_people.count(my_name) > 0:
            kadi_people.remove(my_name)
        error_message = ""
        send_state()

def handle_place_top_card():
    global current_message, current_condition, current_turn, card_asked_for, shape_asked_for
    global error_message, refusing, won
    if current_turn != my_name:
        error_message = "It is not your turn!"
        return
    if len(my_cards) == 0:
        error_message = "You do not have any cards to place!!!"
        return
    valid_cards = []
    top_card = played_cards[len(played_cards)-1]
    top_shape = get_shape_from_card(top_card)
    top_number = get_number_from_card(top_card)
    my_top_card = my_cards[len(my_cards)-1]
    placed = False

    if current_condition == normal:
        #valid cards: cards with the same number or shape as the top card, or As
        valid_cards += get_all_cards_with_shape(top_shape)
        valid_cards += get_all_cards_with_number(top_number)
        valid_cards += get_all_cards_with_number('A')
        if my_top_card in valid_cards:
            played_cards.append(my_cards.pop())
            question_cards = list()
            question_cards += get_all_cards_with_number('Q')
            question_cards += get_all_cards_with_number('8')
            current_condition = subsequent
            if played_cards[len(played_cards)-1] in question_cards:
                current_condition = question
            current_message = wait
            placed = True
        else:
            error_message = "Please select a valid card! Rules, you know."
    elif current_condition == question:
        #valid cards: other questions, or answer to the current question
        valid_cards += get_all_cards_with_shape(top_shape)
        valid_cards.append("QC.png")
        valid_cards.append("QD.png")
        valid_cards.append("QH.png")
        valid_cards.append("QS.png")
        valid_cards.append("8C.png")
        valid_cards.append("8D.png")
        valid_cards.append("8H.png")
        valid_cards.append("8S.png")
        if my_top_card in valid_cards:
            if get_number_from_card(my_top_card) in ['8', 'Q']:
                current_condition = question
            else:
                current_condition = subsequent
            played_cards.append(my_cards.pop())
            current_message = wait
            placed = True
        else:
            error_message = "Please select a valid card! Rules, you know."
    elif current_condition == askcard:
        if my_top_card == card_asked_for:
            current_condition = subsequent
            card_asked_for = ''
            current_message = wait
            played_cards.append(my_cards.pop())
            question_cards = list()
            question_cards += get_all_cards_with_number('Q')
            question_cards += get_all_cards_with_number('8')
            if played_cards[len(played_cards) - 1] in question_cards:
                current_condition = question
        else:
            error_message = "You can only place the card that has been asked for!"
    elif current_condition == askshape:
        if get_shape_from_card(my_top_card) == shape_asked_for:
            current_condition = subsequent
            shape_asked_for = None
            current_message = wait
            played_cards.append(my_cards.pop())
            question_cards = list()
            question_cards += get_all_cards_with_number('Q')
            question_cards += get_all_cards_with_number('8')
            if played_cards[len(played_cards) - 1] in question_cards:
                current_condition = question
        else:
            error_message = "You can only place the shape that has been asked for!"
    elif current_condition == picktwo:
        #valid cards: only twos or As
        valid_cards += get_all_cards_with_number(top_number)
        valid_cards.append("AC.png")
        valid_cards.append("AD.png")
        valid_cards.append("AH.png")
        valid_cards.append("AS.png")
        if my_top_card in valid_cards:
            played_cards.append(my_cards.pop())
            current_condition = subsequent
            current_message = wait
            placed = True
            refusing = True
        else:
            error_message = "You can only place a two or an A"
    elif current_condition == pickthree:
        # valid cards: only threes or As
        valid_cards += get_all_cards_with_number(top_number)
        valid_cards.append("AC.png")
        valid_cards.append("AD.png")
        valid_cards.append("AH.png")
        valid_cards.append("AS.png")
        if my_top_card in valid_cards:
            played_cards.append(my_cards.pop())
            current_condition = subsequent
            current_message = wait
            placed = True
            refusing = True
        else:
            error_message = "You can only place a three or an A"
    elif current_condition == subsequent:
        #valid cards: only cards with the same number as the top card
        valid_cards += get_all_cards_with_number(top_number)
        if my_top_card in valid_cards:
            played_cards.append(my_cards.pop())
            current_condition = subsequent
            current_message = wait
            placed = True
        else:
            error_message = "You can only place a card with the same number as the top card: " + get_number_from_card(top_card)
    elif current_condition == jump:
        #valid cards: only Js
        valid_cards += get_all_cards_with_number(top_number)
        if my_top_card in valid_cards:
            played_cards.append(my_cards.pop())
            current_condition = subsequent
            current_message = wait
            placed = True
        else:
            error_message = "You can only place a J!"
    if kadi_people.count(my_name) > 0:
        no_win_cards = []
        no_win_cards += get_all_cards_with_number('A')
        no_win_cards += get_all_cards_with_number('K')
        no_win_cards += get_all_cards_with_number('Q')
        no_win_cards += get_all_cards_with_number('J')
        no_win_cards += get_all_cards_with_number('2')
        no_win_cards += get_all_cards_with_number('3')
        no_win_cards += get_all_cards_with_number('8')
        if len(my_cards) == 0:
            top_card = played_cards[len(played_cards)-1]
            if top_card in no_win_cards:
                kadi_people.remove(my_name)
            else:
                won = True
        else:
            top_card = played_cards[len(played_cards)-1]
            my_top_card = my_cards[len(my_cards)-1]
            #if top_card in no_win_cards:
                #kadi_people.remove(my_name)
            if get_number_from_card(top_card) != get_number_from_card(my_top_card):
                kadi_people.remove(my_name)
    if placed:
        error_message = ''
        send_state()

def handle_next_player(screen):
   global current_message, current_condition, current_turn, error_message
   global refusing
   if current_turn != my_name:
       error_message = "It is not your turn!"
       return
   valid = False
   #print("current state: ", current_condition)
   if current_condition == subsequent:
       top_card = played_cards[len(played_cards)-1]
       top_number = get_number_from_card(top_card)
       if top_number == 'K':
           current_condition = kickback
           current_message = proceed
           valid = True
       elif top_number == 'Q':
           current_condition = question
           current_message = wait
           valid = True
       elif top_number == 'J':
           current_condition = jump
           current_message = proceed
           valid = True
       elif top_number == 'A':
           top_shape = get_shape_from_card(top_card)
           current_message = proceed
           valid = True
           if not refusing:
               refusing = False
               if top_shape == 'S':#A special
                   #print("You have asked for ", show_select_card_screen(screen))
                   current_condition = askcard
                   show_select_card_screen(screen)
               else:#Not A special
                   #print("You have asked for shape ", show_select_shape_screen(screen))
                   show_select_shape_screen(screen)
                   current_condition = askshape
           else:
               refusing = False
               current_condition = normal
       elif top_number == '2':
           current_condition = picktwo
           current_message = proceed
           valid = True
       elif top_number == '3':
           current_condition = pickthree
           current_message = proceed
           valid = True
       elif top_number == '8':
           current_condition = question
           current_message = wait
           valid = True
       else:
           current_condition = normal
           current_message = proceed
           valid = True
   elif current_condition == jump:
       current_condition = normal
       current_message = proceed
       valid = True
   elif current_condition == picked2:
       current_condition = normal
       current_message = proceed
       valid = True
   elif current_condition == picked3:
       current_condition = normal
       current_message = proceed
       valid = True
   elif current_condition == next_:
       current_condition = normal
       current_message = proceed
       valid = True
   elif current_condition == askedcard:
       current_condition = askcard
       current_message = proceed
       valid = True
   elif current_condition == askedshape:
       current_condition = askshape
       current_message = proceed
       valid = True
   else:
       error_message = "I don't know what you are doing, but you shouldn't be doing it!"
   if valid:
       error_message = ''
       send_state()

def handle_go_kadi():
    global error_message
    if current_turn == my_name:
        if current_condition in [subsequent, askshape, askcard, kickback, next_]:
            if kadi_people.count(my_name) == 0:
                kadi_people.append(my_name)
                send_state()
    else:
        error_message = 'You can only go kadi when it is your turn!'

def connect_to_server():
    server_address = input("Enter server computer name or IP address: ")
    port = 12345
    global main_socket
    try:
        main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        main_socket.connect((server_address, port))
        name = input("Please enter the name you want to be identified with: ")
        main_socket.send(name.encode('utf-8'))
        is_last = input("Are you the last client to connect?: y/n")
        is_last = is_last.lower()
        while not is_last in ['y', 'n']:
            is_last = input("Are you the last client to connect?: y/n")
            is_last = is_last.lower()
        if is_last == 'y':
            main_socket.send('True'.encode('utf-8'))
        else:
            main_socket.send('False'.encode('utf-8'))
        print("Please wait while other players connect to the game")
        state = main_socket.recv(100000000)
        print("Received state")
        state = pickle.loads(state)
        global all_cards, played_cards, current_turn
        global current_condition, my_cards, player_one_cards, player_two_cards, player_three_cards
        global player_one_name, player_two_name, player_three_name, kadi_people, my_name
        global card_asked_for, shape_asked_for, current_message, winner, next_player
        all_cards = state[5]
        played_cards = state[6]
        current_turn = state[9]
        current_condition = state[8]
        my_cards = state[1]
        player_one_cards = state[2]
        player_two_cards = state[3]
        player_three_cards = state[4]
        my_name = state[0][0]
        player_one_name = state[0][1]
        player_two_name = state[0][2]
        player_three_name = state[0][3]
        kadi_people = state[7]
        card_asked_for = state[10]
        shape_asked_for = state[11]
        current_message = state[12]
        winner = state[13]
        next_player = state[14]
        return True
    except Exception as ex:
        print("Something went wrong: ", ex)
        return False

def show_win_screen(screen):
    global winner
    if winner == my_name:
        text1 = "Congragulations."
        text2 = "You have won the game!!!"
        sound = pygame.mixer.Sound('sounds\hero.wav')
    else:
        text1 = "Sorry. Better luck next time"
        text2 = winner + ' has won the game.'
        sound = pygame.mixer.Sound('sounds\sad.wav')
    font = pygame.font.Font('sans.ttf', 30)
    font2 = pygame.font.Font('sans.ttf', 20)

    sound.play(-1)#loop forever!
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                print("Thank you for playing!")
                pygame.quit()
                exit(0)
            if event.type == MOUSEBUTTONDOWN:
                pass

        screen.fill(backcolor)
        x = 100
        y = 100
        s = font.render(text1, True, textcolor)
        r = s.get_rect()
        r.topleft = x, y
        screen.blit(s, r)

        y += 50
        s = font2.render(text2, True, textcolor)
        r = s.get_rect()
        r.topleft = x, y
        screen.blit(s, r)

        pygame.display.update()

def main():
    print("Greetings, human!")
    if connect_to_server():
        pass
    else:
        return
    screen = pygame.display.set_mode(screen_size, 0, 32)
    pygame.display.set_caption("TOP DECK")
    #A little magic numbers go a long way

    #player_one_location, player_two_location, player_three_location, my_location
    global deck_location, played_cards_location, kadi_people_location, next_player_location, \
    pick_card_location, how_to_play_location, winner
    my_location = [120, 320]
    player_one_location = [20, 40]
    player_two_location = [120, 40]
    player_three_location = [540, 40]
    kadi_people_location = [120, 180]
    played_cards_location = [220, 180]
    deck_location = [320, 180]
    place_top_card_location = [420, 180]
    pick_card_location = [420, 200]
    go_kadi_location = [420, 220]
    next_player_location = [420, 240]
    reorder_location = [420, 260]
    how_to_play_location = [420, 280]

    
    place_top_card_rect_dim = resources.get_font("sans.ttf").size("Place top card")

    pick_card_rect_dim = resources.get_font("sans.ttf").size("Pick card(s)")
    go_kadi_rect_dim = resources.get_font("sans.ttf").size("Go kadi")
    next_player_rect_dim = resources.get_font("sans.ttf").size("Next player")
    how_to_play_rect_dim = resources.get_font("sans.ttf").size("How to play")
    reorder_rect_dim = resources.get_font("sans.ttf").size("Reorder cards")
    


    class ReceiveState(threading.Thread):
        def __init__(self):
            super().__init__()

        def run(self):
            #print("ReceiveStateThread started...")
            while True:
                state = main_socket.recv(100000000)
                #print("Received state")
                state = pickle.loads(state)
                #print("connected", state[0])
                '''
                format of data:
                data = (c, my_cards, player_one_cards, player_two_cards, player_three_cards,
                    all_cards, played_cards, kadi_people,
                    current_condition, current_turn, card_asked_for, shape_asked_for, current_message)
                '''
                global all_cards, played_cards, current_turn
                global current_condition, my_cards, player_one_cards, player_two_cards, player_three_cards
                global player_one_name, player_two_name, player_three_name, kadi_people, my_name
                global card_asked_for, shape_asked_for, current_message, winner, next_player
                current_turn = state[9]
                current_condition = state[8]
                my_cards = state[1]
                player_one_cards = state[2]
                player_two_cards = state[3]
                player_three_cards = state[4]
                my_name = state[0][0]
                player_one_name =state[0][1]
                player_two_name = state[0][2]
                player_three_name = state[0][3]
                played_cards = state[6]
                all_cards = state[5]
                kadi_people = state[7]
                card_asked_for = state[10]
                shape_asked_for = state[11]
                current_message = state[12]
                winner = state[13]
                next_player = state[14]

    receive_state_thread = ReceiveState()
    receive_state_thread.start()

    very_small_font = pygame.font.Font('sans.ttf', 11)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                #print("Mouse buton down")
                reoder_rect = Rect(reorder_location, resources.get_font("sans.ttf").size("Reoder cards"))
                pick_card_rect = Rect(pick_card_location, resources.get_font("sans.ttf").size("Pick card(s)"))
                next_player_rect = Rect(next_player_location, resources.get_font("sans.ttf").size("Next player"))
                go_kadi_rect = Rect(go_kadi_location, resources.get_font("sans.ttf").size("Go kadi"))
                place_top_card_rect = Rect(place_top_card_location, resources.get_font("sans.ttf").size("Place top card"))

                if reoder_rect.collidepoint(event.pos[0], event.pos[1]):
                    handle_reorder()
                elif pick_card_rect.collidepoint(event.pos[0], event.pos[1]):
                    handle_pick()
                elif next_player_rect.collidepoint(event.pos[0], event.pos[1]):
                    handle_next_player(screen)
                elif go_kadi_rect.collidepoint(event.pos[0], event.pos[1]):
                    handle_go_kadi()
                elif place_top_card_rect.collidepoint(event.pos[0], event.pos[1]):
                    handle_place_top_card()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    pass

        if winner != '':
            show_win_screen(screen)
        pressed_keys = pygame.key.get_pressed()
        #check if ALT + F4 is pressed
        if pressed_keys[pygame.K_F4] and (pressed_keys[pygame.K_LALT] or pressed_keys[K_RALT]):
            return

        screen.fill(backcolor)
        if current_turn == my_name:
            screen.fill((107, 142, 35)) #olive

        m = my_name + '-You'
        if len(error_message) > 0:
            m += ' (' + error_message + ')'
        surface = resources.get_font("sans.ttf").render(m, True, textcolor)
        rect = surface.get_rect()
        rect.topleft = my_location
        rect.top = my_location[1] - resources.get_font("sans.ttf").size(m)[1]
        screen.blit(surface, rect)
        
        surface = resources.get_font("sans.ttf").render(player_one_name, True, textcolor)
        rect = surface.get_rect()
        rect.topleft = player_one_location
        rect.top = player_one_location[1] - resources.get_font("sans.ttf").size(player_one_name)[1]
        screen.blit(surface, rect)

        c = "Current turn: " + current_turn
        if current_turn == my_name:
            c += "(You)"
        surface = resources.get_font("sans.ttf").render(c, True, textcolor)
        rect = surface.get_rect()
        rect.topleft = (player_two_location[0], player_two_location[1] - resources.get_font('sans.ttf').size(c)[1] * 2)
        screen.blit(surface, rect)

        surface = resources.get_font("sans.ttf").render(player_two_name, True, textcolor)
        rect = surface.get_rect()
        rect.topleft = player_two_location
        rect.top = player_two_location[1] - resources.get_font("sans.ttf").size(player_two_name)[1]
        screen.blit(surface, rect)
        
        surface = resources.get_font("sans.ttf").render(player_three_name, True, textcolor)
        rect = surface.get_rect()
        rect.topleft = player_three_location
        rect.top = player_three_location[1] - resources.get_font("sans.ttf").size(player_three_name)[1]
        screen.blit(surface, rect)

        #draw my cards
        location = my_location.copy()
        location[0] += card_display_size
        for card in my_cards:
            image = resources.get_card_image(card_images_path + card, card_size)
            screen.blit(image, location)
            location[0] += card_display_size
        #draw player one cards
        location = player_one_location.copy()
        location[1] += card_display_size
        for _ in player_one_cards:
            image = resources.get_card_image(card_images_path + "gray_back.png", card_size)
            screen.blit(image, location)
            location[1] += card_display_size / 2
        #draw player two cards
        location = player_two_location.copy()
        location[0] += card_display_size
        for _ in player_two_cards:
            image = resources.get_card_image(card_images_path + "gray_back.png", card_size)
            screen.blit(image, location)
            location[0] += card_display_size
        #draw player three cards
        location = player_three_location.copy()
        location[1] += card_display_size
        for _ in player_three_cards:
            image = resources.get_card_image(card_images_path + "gray_back.png", card_size)
            screen.blit(image, location)
            location[1] += card_display_size / 2
        #draw the top card on the deck (the top card should be facing down)
        image = resources.get_card_image(card_images_path + "gray_back.png", card_size)
        screen.blit(image, deck_location)
        #draw the top card that has been played
        image = resources.get_card_image(card_images_path + played_cards[len(played_cards)-1], card_size)
        screen.blit(image, played_cards_location)
        #print the people who are kadi
        temp_loc = kadi_people_location.copy()
        for person in kadi_people:
            surface = resources.get_font("sans.ttf").render(person, True, textcolor)
            screen.blit(surface, temp_loc)
            temp_loc[1] += resources.get_font("sans.ttf").size(person)[1]

        pygame.draw.rect(screen, linecolor, (my_location, (400, 120)), 2)

        pygame.draw.rect(screen, linecolor, (player_one_location, (80, 400)), 2)

        pygame.draw.rect(screen, linecolor, (player_two_location, (400, 120)), 2)

        pygame.draw.rect(screen, linecolor, (player_three_location, (80, 400)), 2)

        pygame.draw.rect(screen, linecolor, (played_cards_location, (80, 120)), 1)

        pygame.draw.rect(screen, linecolor, (kadi_people_location, (80, 120)), 1)

        pygame.draw.rect(screen, linecolor, (deck_location, (80, 120)), 1)
        
        surface = resources.get_font("sans.ttf").render("Kadi people", True, textcolor)
        rect = surface.get_rect()
        rect.topleft = kadi_people_location
        rect.top = kadi_people_location[1] - resources.get_font("sans.ttf").size("A")[1]
        screen.blit(surface, rect)
        
        surface = resources.get_font("sans.ttf").render("Played cards", True, textcolor)
        rect = surface.get_rect()
        rect.topleft = played_cards_location
        rect.top = played_cards_location[1] - resources.get_font("sans.ttf").size("A")[1]
        screen.blit(surface, rect)

        surface = resources.get_font("sans.ttf").render("Deck", True, textcolor)
        rect = surface.get_rect()
        rect.topleft = deck_location
        rect.top = deck_location[1] - resources.get_font("sans.ttf").size("A")[1]
        screen.blit(surface, rect)

        mouse_position = pygame.mouse.get_pos()

        current_color = textcolor
        rect = Rect(place_top_card_location, place_top_card_rect_dim)
        if rect.collidepoint(mouse_position[0], mouse_position[1]):
            current_color = highlight_color

        surface = resources.get_font("sans.ttf").render("Place top card", True, current_color)
        rect = surface.get_rect()
        rect.topleft = place_top_card_location
        screen.blit(surface, rect)

        current_color = textcolor
        rect = Rect(pick_card_location, pick_card_rect_dim)
        if rect.collidepoint(mouse_position[0], mouse_position[1]):
            current_color = highlight_color

        surface = resources.get_font("sans.ttf").render("Pick card(s)", True, current_color)
        rect = surface.get_rect()
        rect.topleft = pick_card_location
        screen.blit(surface, rect)

        current_color = textcolor
        rect = Rect(go_kadi_location, go_kadi_rect_dim)
        if rect.collidepoint(mouse_position[0], mouse_position[1]):
            current_color = highlight_color

        surface = resources.get_font("sans.ttf").render("Go kadi", True, current_color)
        rect = surface.get_rect()
        rect.topleft = go_kadi_location
        screen.blit(surface, rect)

        current_color = textcolor
        rect = Rect(next_player_location, next_player_rect_dim)
        if rect.collidepoint(mouse_position[0], mouse_position[1]):
            current_color = highlight_color

        surface = resources.get_font("sans.ttf").render("Next player", True, current_color)
        rect = surface.get_rect()
        rect.topleft = next_player_location
        screen.blit(surface, rect)

        current_color = textcolor
        rect = Rect(reorder_location, reorder_rect_dim)
        if rect.collidepoint(mouse_position[0], mouse_position[1]):
            current_color = highlight_color

        surface = resources.get_font("sans.ttf").render("Reorder cards", True, current_color)
        rect = surface.get_rect()
        rect.topleft = reorder_location
        screen.blit(surface, rect)

        current_color = textcolor
        rect = Rect(how_to_play_location, how_to_play_rect_dim)
        if rect.collidepoint(mouse_position[0], mouse_position[1]):
            current_color = highlight_color

        surface = resources.get_font("sans.ttf").render("How to play", True, current_color)
        rect = surface.get_rect()
        rect.topleft = how_to_play_location
        screen.blit(surface, rect)

        loc = my_location.copy()
        loc[0] = 50
        if not card_asked_for == '' and not card_asked_for is None:
            print("Card:", card_asked_for)
            text = 'You must place the following card or pick a card: '
            ca = card_asked_for
            shape = ''
            if not ca is None and len(ca) > 0:
                text += get_number_from_card(ca)
                shape = get_shape_from_card(ca)
            if shape == 'C':
                text += ' clubs(flowers)'
            elif shape == 'D':
                text += ' diamonds'
            elif shape == 'H':
                text += ' hearts'
            elif shape == 'S':
                text += ' spades'
            loc[1] = 480 - resources.get_font('sans.ttf').size(text)[1] * 2
            surface = resources.get_font('sans.ttf').render(text, True, textcolor)
            screen.blit(surface, loc)
        if not shape_asked_for == '' and not shape_asked_for is None:
            text = 'You must place a card with the following shape, or pick a card: '
            shape = shape_asked_for
            if shape == 'C':
                text += ' clubs(flowers)'
            elif shape == 'D':
                text += ' diamonds'
            elif shape == 'H':
                text += ' hearts'
            elif shape == 'S':
                text += ' spades'
            #loc[1] += resources.get_font('sans.ttf').size(text) + card_size[1] + card_size[1] / 2
            loc[1] = 480 - resources.get_font('sans.ttf').size(text)[1] * 2
            surface = resources.get_font('sans.ttf').render(text, True, textcolor)
            screen.blit(surface, loc)
        loc = my_location.copy()
        loc[0] = 50
        t = 'Next player: ' + next_player
        loc[1] = 480 - resources.get_font('sans.ttf').size(t)[1]
        s = resources.get_font('sans.ttf').render(t, True, textcolor)
        r = s.get_rect()
        r.topleft = loc
        screen.blit(s, r)

        t = 'From Mus, to her, with the eyes...'
        loc = my_location.copy()
        loc[0] = 640 - very_small_font.size(t)[0] - 10
        loc[1] = 480 - very_small_font.size(t)[1]
        s = very_small_font.render(t, True, textcolor)
        r = s.get_rect()
        r.topleft = loc
        screen.blit(s, r)
        
        pygame.display.update()

if __name__ == "__main__":
    main()
    #test()

    