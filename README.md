# curses_solitaire

### why

I just wanted to see if I could create a working solitaire game without a implementation reference.  There are many solitair/klondike games out there and even ones that use curses for the shell.  Just a logic exercise.

### requirements

* UTF-8 encoding/locale

### known bugs

* errors if stack gets to long to fit on screen
* some refesh issues with the deck and turning when using 3 card draw
* probably a few more

### usage

* q - quit
* t - turn cards from deck
* SPACE - select current card
* TAB - change current stack
* SHIFT+TAB - change current stack in reverse direction
* UP - change current card up in stack
* Down - Change current card down in stack
* ENTER - move selected card to current stack or to completed stack if current = selected
* F2 - deal/start new game

### screenshot

![solitaire.png](solitaire.png)
