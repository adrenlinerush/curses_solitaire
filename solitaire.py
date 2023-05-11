import random
import curses
import sys
import logging


#turn=1
turn=3
card_width=12
card_height=10
deck_status=0
cur_stack = "deck"
cur_pos = 0
sel_stack = None
sel_pos = None
card_values = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
suits = ['♠', '♦', '♥', '♣']
deck_stack = None
stacks = None
screen = None

logging.basicConfig(filename="solitaire.log", encoding='utf-8', level=logging.DEBUG)

def init_deck():
  global card_values
  global suits
  deck = []
  for suit in suits:
    for value in card_values:
      card = {}
      card['suit'] = suit
      card['value'] = value
      card['visible'] = False
      card['highlight'] = False
      card['select'] = False
      if suit in ('♠', '♣'):
        card['color'] = 3 
      else:
        card['color'] = 2
      deck.append(card)

  random.shuffle(deck)
  return deck

def deal(deck):
  stack_names=["1","2","3","4","5","6","7"]
  stacks = {}
  x = len(stack_names)
  while (x>=0):
    for stack in range(7-x,7):
      card = deck.pop()
      if stack == (7-x):
        card['visible'] = True
      if x == 7:
        stacks[stack_names[stack]]=[card]
      else:
        stacks[stack_names[stack]].append(card)
    x -= 1
  stacks['deck'] = deck
  return stacks

def init_stacks(deck):
  stacks = deal(deck)
  stacks['♠']=[]
  stacks['♦']=[]
  stacks['♥']=[]
  stacks['♣']=[]
  return(stacks)


def init_screen():
  screen = curses.initscr()
  curses.noecho()
  curses.cbreak()
  curses.curs_set(False)
  if curses.has_colors():
    curses.start_color()
  curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
  curses.init_pair(2, curses.COLOR_RED, curses.COLOR_WHITE)
  curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
  curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
  screen.box()
  screen.scrollok(True) 
  return screen


def draw_deck(screen):
  global deck_stack
  deck_stack = screen.subwin(card_height,card_width,6,3)
  deck_stack.bkgd(' ', curses.color_pair(1) | curses.A_BOLD)
  deck_stack.addstr(4,4, "Deck")
  deck_stack.box()
  deck_stack.refresh()

def draw_inplay(screen,stacks):
  for s in range(7):
    stack = stacks[str(s+1)]
    y = 20
    x = 3 + (s*14)
    for card in stack:
      card_disp = screen.subwin(card_height,card_width,y,x)
      card['sub_win'] = card_disp
      render_card(card)
      y+=2

def render_card(card):
  card_disp = card['sub_win']
  card_disp.erase()
  card_disp.box()
  if card['visible']:
    card_disp.bkgd(' ', curses.color_pair(card['color']))
    logging.debug(highlight)
    if card['select'] and card['highlight']:
      card_disp.bkgd(' ', curses.color_pair(card['color']) | curses.A_REVERSE | curses.A_BLINK | curses.A_UNDERLINE)
    elif card['select']:
      card_disp.bkgd(' ', curses.color_pair(card['color']) | curses.A_REVERSE)
    elif card['highlight']:
      logging.debug('blink')
      card_disp.bkgd(' ', curses.color_pair(card['color']) | curses.A_BLINK | curses.A_UNDERLINE)

    card_disp.addstr(1,1, card['value'] + " " + card['suit'])
    card_disp.addstr(4,6, card['suit'])
    card_disp.addstr(8,7, card['value'] + " " + card['suit'])
  else:
    if card['highlight']:
      card_disp.bkgd(' ', curses.color_pair(1) | curses.A_BLINK | curses.A_UNDERLINE)
    else:
      card_disp.bkgd(' ', curses.color_pair(1))
  card_disp.refresh()

def draw_comp_stacks(stacks, screen):
  global suits
  s = 3
  for suit in suits:
    y = 6
    x = 3 + (s*(card_width+2))
    if len(stacks[suit]) == 0:
      card_disp = screen.subwin(card_height,card_width,y,x)
      card_disp.erase()
      card_disp.box()
      card_disp.bkgd(' ', curses.color_pair(1))
      card_disp.addstr(4,6, suit)
    else:
      card_disp = screen.subwin(card_height,card_width,y,x)
      visible_card = stacks[suit][-1]
      visible_card['sub_win'] = card_disp
      render_card(visible_card)
      visible_card['sub_win'].refresh()
      screen.refresh()
    s+=1

def deck_invisible(deck):
  for card in deck:
    try:
      if 'sub_win' in card.keys():
        card['sub_win'].bkgd(' ', curses.color_pair(4))
        erase_card(card['sub_win'])
        card['sub_win'].refresh()
        card['sub_win'].erase()
        card['sub_win']=None
      card['visible'] = False
    except Exception as e:
      logging.error('Error making card invisible.')
      logging.error(e)
      logging.error(card)

def erase_card(sub_win):
  y, x = sub_win.getmaxyx()
  sub_win.bkgd(' ', curses.color_pair(4))
  s = ' ' * (x-1)
  for l in range(y):
    sub_win.addstr(l,0,s)

def render_turn(stacks):
  global deck_status
  global deck_stack
  deck=stacks['deck']
  deck_stack.addstr(5,4, str(len(deck)) + " ")
  deck_stack.refresh()
  deck_invisible(deck)
  y=6
  x=3+card_width+2
  cards=turn
  if len(deck) < deck_status+turn:
    logging.debug("Not a full turn end of deck.")
    cards = len(deck)-deck_status
    logging.debug(cards)
  for i in range(cards):
    card=deck[deck_status+i]
    logging.debug(card)
    card_disp = screen.subwin(card_height,card_width,y,x)
    card['sub_win'] = card_disp
    card['visible'] = True
    render_card(card)
    x+=4

  if len(deck) < deck_status+turn:
    deck_status = 0
  else:
    deck_status+=turn
  

def render_screen(stacks, screen):
  title1 = 'Solitaire'
  title2 = 'By: Austin Mount'
  tx1 = int((curses.COLS-len(title1))/2)
  tx2 = int((curses.COLS-len(title2))/2)
  screen.addstr(3, tx1, title1)
  screen.addstr(4, tx1, title2)
  draw_deck(screen)
  draw_inplay(screen, stacks)
  draw_comp_stacks(stacks, screen)
  show_empty_stacks(stacks) 
  screen.refresh()

def select(stacks):
  global deck_status
  global cur_stack
  global cur_pos
  global sel_stack
  global sel_pos
  if not sel_stack:
    card = None
    try:
      sel_stack = cur_stack
      sel_pos = cur_pos
      if cur_stack == "deck":
        if deck_status == 0:
          card = stacks[cur_stack][-1]
        else:
          card = stacks[cur_stack][deck_status-1]
      else:
        card = stacks[cur_stack][cur_pos]
      card['select'] = True
      render_card(card)
    except Exception as e:
      logging.error('Error selecting card.')
      logging.error(e)
      logging.error(card)
 
def highlight(stacks):
  global deck_status
  global cur_stack
  global cur_pos
  card = None
  try:
    if cur_stack == "deck":
      if deck_status == 0:
        card = stacks[cur_stack][-1]
      else:
        card = stacks[cur_stack][deck_status-1]
    else:
      card = stacks[cur_stack][cur_pos]
    card['highlight'] = True
    render_card(card)
  except Exception as e:
    logging.error('Error highlighting card.')
    logging.error(e)
    logging.error(card)

def unselect(stacks):
  global deck_status
  global cur_stack
  global cur_pos
  global sel_stack
  global sel_pos
  if (sel_stack == cur_stack) and (sel_pos == cur_pos):
    sel_stack = None
    sel_pos = None
    card = None
    if cur_stack == "deck":
      if deck_status == 0:
        card = stacks[cur_stack][-1]
      else:
        card = stacks[cur_stack][deck_status-1]  
    else:
      card = stacks[cur_stack][cur_pos]
    card['select'] = False
    if 'sub_win' in card.keys():
      render_card(card)  
   
def unhighlight(stacks):
  global deck_status
  global cur_stack
  global cur_pos
  card = None
  try:
    if cur_stack == "deck":
      if deck_status == 0:
        card = stacks[cur_stack][-1]
      else:
        card = stacks[cur_stack][deck_status-1]
    else:
      card = stacks[cur_stack][cur_pos]
    card['highlight'] = False
    if 'sub_win' in card.keys():
      render_card(card)  
  except Exception as e:
    logging.error('Error unhighlighting card.')
    logging.error(e)
    logging.error(card)

def exit_curses():
  screen.erase()
  curses.nocbreak()
  curses.echo()
  curses.curs_set(True)
  curses.endwin()

def check_move(stacks):
  global cur_stack
  global cur_pos
  global sel_stack
  global sel_pos
  global deck_status
  global card_values
  sel_card = None
  deck_pos = None
  if sel_stack == "deck":
    if deck_status == 0:
      deck_pos=len(stacks[sel_stack])-1
    else:
      deck_pos=deck_status-1
    sel_card = stacks[sel_stack][deck_pos]
  else:
    sel_card = stacks[sel_stack][sel_pos]

  if cur_stack == sel_stack and cur_pos == sel_pos:
    logging.debug('Check Complete Stack')
    logging.debug(sel_card)

    try:
      if ((len(stacks[sel_card['suit']]) == 0 and sel_card['value'] == 'A')) or \
        (sel_card['value'] == card_values[(card_values.index(stacks[sel_card['suit']][-1]['value'])+1)]):
        logging.debug('Valid Move to Complete')
        move_to_stack(stacks,sel_card['suit'],deck_pos)
        logging.debug(stacks)
        reset()
        return True
    except Exception as e:
      logging.error('Error checking if can move card to complete stack.')
      logging.error(e)
      logging.error(sel_card)
  elif len(stacks[cur_stack]) == 0:
    if sel_card['value'] == 'K':
      logging.debug('King, can move to empty space.')
      logging.debug(sel_card)
      move_to_stack(stacks,cur_stack,deck_pos)
      logging.debug(stacks)
      reset()
      return True
  elif cur_stack != "deck":
    check_card = stacks[cur_stack][cur_pos]
    logging.debug(check_card)
    logging.debug(sel_card)
    if sel_card['color'] is not check_card['color']:
      logging.debug('Colors differ.')
      logging.debug('Looking for value.')
      logging.debug(card_values[(card_values.index(check_card['value']) -1)])
      if sel_card['value'] == card_values[(card_values.index(check_card['value']) -1)]:
        logging.debug('Valid Move to stack')
        move_to_stack(stacks,cur_stack,deck_pos)
        reset()
        return True
  return False

def reset():
  global cur_stack
  global cur_pos
  global sel_stack
  global sel_pos
  global deck_status
  if sel_stack == "deck":
    deck_status-=1
  sel_stack=0
  sel_pos=0
  cur_pos=0
  cur_stack="deck"


def move_to_stack(stacks,dest_stack,deck_pos=None):
  if not is_stack():
    move_card(sel_stack, sel_pos, dest_stack, deck_pos)
  else:
    logging.debug("Moving stack...")
    logging.debug(sel_pos)
    logging.debug(len(stacks[sel_stack]))
    for card in range(sel_pos,len(stacks[sel_stack])):
      logging.debug("Moving card...")
      logging.debug(card)
      move_card(sel_stack, card, dest_stack)    

def is_stack():
  global sel_stack
  global sel_pos
  if sel_stack != "deck":
    logging.debug("Stack is not deck...")
    if sel_pos < len(stacks[sel_stack])-1:
      logging.debug("This is not bottom card ..")
      return True
  return False

def move_card(src_stack, src_pos, dest_stack, deck_pos = None):
  global cur_stack
  global cur_pos
  global sel_stack
  global sel_pos
  card = None
  try:
    if sel_stack == "deck":
      card = stacks[sel_stack].pop(deck_pos)
    else:
      card = stacks[sel_stack].pop(sel_pos)
      if len(stacks[sel_stack]) > 0:
        stacks[sel_stack][-1]['visible'] = True
    logging.debug(card)
    card['select'] = False
    card['highlight'] = False
    try:
      if cur_stack is not sel_stack:
        stacks[cur_stack][-1]['highlight'] = False
    except Exception as e:
      logging.error('Unable to unhighlight previous card.')
      logging.error(e)
    stacks[dest_stack].append(card)
    erase_card(card['sub_win'])
  except Exception as e:
    logging.error('Error moving card.')
    logging.error(e)
    logging.error(card)
 
def show_empty_stacks(stacks):
  global cur_stack
  for i in range(7):
    stack = str(i+1)
    if len(stacks[stack]) == 0:
      card = {}
      card['visible'] = False
      if stack == cur_stack:
        card['highlight'] = True
      else:
        card['highlight'] = False
      card['select'] = False
      y = 20
      x = 3 + (i*14)
      card_disp = screen.subwin(card_height,card_width,y,x)
      card['sub_win'] = card_disp
      render_card(card)
      card_disp.addstr(5,4, "Empty")

def check_win(stacks):
  if len(stacks['deck']) == 0:
    for i in range(7):
      stack = str(i+1)
      if len(stacks[stack]) > 0:
        return
    # You won the Game
    logging.debug('You won game over!')
    exit_curses()
    sys.exit(0)

def input(char,stacks,screen):
  global cur_stack
  global cur_pos
  global sel_stack
  global sel_pos
  if char == 113: # q
    exit_curses()
    sys.exit(0)
  elif char == 81: #F2
    exit_curses()
    init_sol()
  elif char == 116: # t
    render_turn(stacks)
    highlight(stacks)
  elif char == 9: # TAB
    unhighlight(stacks)
    goto_next=True
    empty=False
    while goto_next:
      if cur_stack == "deck":
        cur_stack = "1"
        cur_pos = len(stacks[cur_stack])-1
      elif cur_stack == "7":
        cur_stack = "deck"
        cur_pos = 0
      else:
        cur_stack = str(int(cur_stack) + 1)
        cur_pos = len(stacks[cur_stack])-1
      v = 0
      if cur_stack == "deck":
        for card in stacks["deck"]:
          if card['visible']:
            v+=1
      if len(stacks[cur_stack]) > 0 and cur_stack != "deck" or v > 0:
        goto_next=False
      if len(stacks[cur_stack]) == 0 and cur_stack != "deck" and sel_stack:
        goto_next=False
        empty=True
    logging.debug(cur_stack)
    show_empty_stacks(stacks)
    if not empty:
      highlight(stacks)
    render_screen(stacks, screen)
  elif char == 32: # SPACE
    if not sel_stack:
      select(stacks)
    else:
      unselect(stacks)
  elif char == 10: # ENTER
    if sel_stack:
      refresh = check_move(stacks)
      if refresh:
        render_screen(stacks, screen)
  elif char == 65: # Up
    if cur_stack != "deck":
      if cur_pos > 0 and stacks[cur_stack][cur_pos-1]['visible']:
        unhighlight(stacks)
        cur_pos-=1
        highlight(stacks)
  elif char == 66: # Down
    if cur_stack != "deck":
      if cur_pos < len(stacks[cur_stack]):
        unhighlight(stacks)
        cur_pos+=1
        highlight(stacks)
  check_win(stacks)

def init_sol():  
  global stacks
  global screen
  deck=init_deck()
  stacks = init_stacks(deck)
  screen = init_screen()
  render_screen(stacks, screen)

init_sol()

while True:
  char = screen.getch()
  screen.addstr(1,1,str(char)+"  ")
  input(char,stacks,screen)
