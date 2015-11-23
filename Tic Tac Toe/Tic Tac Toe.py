'''
@authors: Akash Gopal
@date: 09/04/2015
'''

import random
import sys
import copy
#map to display the board to the user
map = [[" "," "," "],
       [" "," "," "],
       [" "," "," "]]

#board contains numeric elements tat correspond to elements in the map variable
board = ['-'] * 9
PlayerTurn = ''
compTurn = ''

#all the 8 winning cominbation possible in this game
win_combinations = (
[6, 7, 8], [3, 4, 5], [0, 1, 2], [0, 3, 6], [1, 4, 7], [2, 5, 8],
[0, 4, 8], [2, 4, 6],
)

#positions of corners, sides and middle of the board
corners = [0,2,6,8]
sides = [1,3,5,7]
middle = 4

#print the board on to the output
def print_board():

    for i in range(0,3):
        for j in range(0,3):
            print map[2-i][j],
            if j != 2:
                print "|",
        print ""

#convert the board into the map so that it can be displayed properly
def copyToMap():
    for i in range(0,3):
        for j in range(0,3):
           temp = (i * 3) + j
           map[i][j] = board[temp]

#final function after game ends to show the final board of the game
def quit_game():
	print "Final Board:"
	copyToMap()
	print_board()
	sys.exit()

#to check if any winning combination has occured; be it vertical, horizontal or diagonal
def is_win(board, marker):
    for combo in win_combinations:
        if (board[combo[0]] == board[combo[1]] == board[combo[2]] == marker):
            return True
    return False

#the computer's move which includes the  strategies required for this assignment
def compMove():
    # Requirement1: to check if computer can win in the next move
    for i in range(0,len(board)):
        board_copy = copy.deepcopy(board)
        if isEmpty(board_copy, i):
            make_move(board_copy,i,compTurn)
            if is_win(board_copy, compTurn):
                return i
            
    #Requirement2: to check if player could win on his/her next move
    for i in range(0,len(board)):
        board_copy = copy.deepcopy(board)
        if isEmpty(board_copy, i):
            make_move(board_copy,i,PlayerTurn)
            if is_win(board_copy, PlayerTurn):
                return i


    #Additional Strategy 1: if middle elemt is empty, always occupy it first.
    if isEmpty(board,middle):
        return middle

    #Additional Strategy 2: if two opposite diagonal are occupied by the opponent,
    #                       make sure that we select the inner sides rather than corners
    if (board[8] == board[0] != '-') or (board[2] == board[6] != '-'):
    	return randomMove(sides)    


    #Additional Strategy 3: check if corners are free, if yes occupy them
    move = randomMove(corners)
    if move != None:
        return move            

    #Additional Strategy 4: if everything else is occupied, then come to the inner sides
    return randomMove(sides)

#check to see if the map/board in a particular position is empty
def isEmpty(board, index):
    return board[index] == '-'

#check to see if the map/board is full
def isFull():
    for i in range(1,9):
        if isEmpty(board, i):
            return False
    return True

#assign the player's move to the corresponding position in the board
def make_move(board,index,move):
    board[index] =  move

#choose the positions in the corners or inner sides randomly
def randomMove(mlist):
    winMoves = []
    for index in mlist:
        if isEmpty(board, index):
            winMoves.append(index)
            if len(winMoves) != 0:
                return random.choice(winMoves)
            else:
                return None

#entry point of the program   
def start():
   print_board()

   print "Your marker is " + PlayerTurn

   if PlayerTurn == "O":
   	print "Computer goes first"
   	game_entrance('c')
   else:
    print "You go first"          
    game_entrance('p')

#allows the player to choose his position on the board
def PlayerMove():
  try:
    move = int(raw_input("Your Choice(1-9)): "))
    while move not in [1,2,3,4,5,6,7,8,9] or not isEmpty(board, move - 1):
      move = int(raw_input("Invalid move. Please try again: (1-9) "))
  except ValueError:
    move = int(raw_input("Invalid Move. Please try again: (1-9) "))
    while move not in [1,2,3,4,5,6,7,8,9] or not isEmpty(board, move - 1):
      move = int(raw_input("Invalid Move. Please try again: (1-9) "))
  print move
  return move - 1

#alternatively keep playing the game until a result is achieved
def game_entrance(turn):
   "starts the main game loop"
   is_running = True
   player = turn 
   while is_running:
       if player == 'p':
           user_input = PlayerMove()
           make_move(board,user_input, PlayerTurn)
           if(is_win(board, PlayerTurn)):
           	copyToMap()
           	print_board()
           	print " Congrats"
           	is_running = False
           else:
               if isFull():
               	copyToMap()
               	print_board()
               	print "Match Drawn"
               	print
               	is_running = False
                   #break
               else:
               	copyToMap()
               	print_board()
               	print ""
               	print "Computer Finished Playing."
               	print 
               	player = 'c'
       
       else:
          comp_move =  compMove()
          make_move(board, comp_move, compTurn)
          if (is_win(board, compTurn)):
          	copyToMap()
          	print_board()
          	print "Computer has won!"
          	is_running = False
          	break
          else:
              if isFull():
              	copyToMap()
                print_board()
                print "\n\t -- Match Draw -- \n\t"
                is_running = False
                #break
              else:
              	copyToMap()
                print_board()
                print ""
                player = 'p'

   quit_game()


#start of the program 
print "Welcome!"
print "Choose X to play first, O to play second."

print "Here is the layout of the board before we start!"
print "7|8|9"
print "4|5|6"
print "1|2|3"
print

print "Good luck!"


PlayerTurn = raw_input("Would you like your marker to be X or O?: ").upper()
while PlayerTurn not in ["X","O"]:
	PlayerTurn = raw_input("Would you like your marker to be X or O? :").upper()
if PlayerTurn == "X":
	compTurn = "O"
else:
	compTurn = "X"
start()

