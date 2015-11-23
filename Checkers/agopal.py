'''
@author: Akash Gopal
@date: 10/20/2015
'''

import random
import gamePlay
from copy import deepcopy
from getAllPossibleMoves import getAllPossibleMoves

# Note: I have made changes in the nextMove function and the main evaluation function.

# Used in the evaluation function
count = 0

def evaluation1(board, color):
  # Evaluation Function 1: Counting the number of pawns each player has in the current state
  opponentColor = gamePlay.getOpponentColor(color)
  value = 0
  for piece in range(1, 33):
    xy = gamePlay.serialToGrid(piece)
    x = xy[0]
    y = xy[1]
            
    if board[x][y] == color:
      value = value + 1
    elif board[x][y] == opponentColor:
      value = value - 1
  return value

def evaluation2(board,color):
  #Evaluation Function 2: Counting the number of kings of each player in the current state
  opponentColor = gamePlay.getOpponentColor(color)
  value = 0
  for piece in range(1, 33):
    xy = gamePlay.serialToGrid(piece)
    x = xy[0]
    y = xy[1]
    if board[x][y] == "R" or board[x][y] == "W":
      if board[x][y] == color:
        value = value + 1.5
      elif board[x][y] == opponentColor:
        value = value - 1.5
  return value

def evaluation3(board, color):
  # Evaluation Function 3(matrix): Corners on all sides are given utmost importance 
  # and hence my pawns will always tend to go towards the corner so that the pawns cannot be captured.
  evalMatrix = [
               [ 0, 4, 0, 4, 0, 4, 0, 4],
               [ 4, 0, 3, 0, 3, 0, 3, 0],
               [ 0, 3, 0, 2, 0, 2, 0, 4], 
               [ 4, 0, 2, 0, 1, 0, 3, 0],
               [ 0, 3, 0, 1, 0, 2, 0, 4],
               [ 4, 0, 2, 0, 2, 0, 3, 0],
               [ 0, 3, 0, 3, 0, 3, 0, 4],
               [ 4, 0, 4, 0, 4, 0, 4, 0]                        
               ]
  opponentColor = gamePlay.getOpponentColor(color)
  value = 0
  for piece in range(1, 33):
    xy = gamePlay.serialToGrid(piece)
    x = xy[0]
    y = xy[1]
            
    if board[x][y].upper() == color.upper():
      value = value + evalMatrix[x][y]
    elif board[x][y].upper() == opponentColor.upper():
      value = value - evalMatrix[x][y]
  return value

def evaluation4(board, color):
  # Evaluation Function 4: Defense: counting number of my neighbors for each pawn so that it is 
  # defensively covered so that the pawn cannot captured. Same thing for the oppnonent pawns too.
  opponentColor = gamePlay.getOpponentColor(color)
  value = 0
  for piece in range(1, 33):
    xy = gamePlay.serialToGrid(piece)
    x = xy[0]
    y = xy[1]

    if x < 7 and x > 0 and y < 7 and y > 0:
      if board[x][y].upper() == "R":
        if board[x][y].upper() == color.upper():
          if board[x-1][y-1].upper() == color.upper():
            value = value + 2
          if board[x-1][y+1].upper() == color.upper(): 
            value = value + 2

        elif board[x][y].upper() == opponentColor.upper():
          if board[x+1][y-1].upper() == opponentColor.upper():
            value = value - 2
          if board[x+1][y+1].upper() == opponentColor.upper(): 
            value = value - 2

      elif board[x][y].upper() == "W":
        if board[x][y].upper() == color.upper():
            if board[x+1][y-1].upper() == color.upper():
              value = value + 2
            if board[x+1][y+1].upper() == color.upper(): 
              value = value + 2

        elif board[x][y].upper() == opponentColor.upper():
            if board[x-1][y-1].upper() == opponentColor.upper():
              value = value - 2
            if board[x-1][y+1].upper() == opponentColor.upper(): 
              value = value - 2

  return value

def evaluation5(board, color):
  # Evaluation Function 5: Always trying to go toward the opponent's end so that the pawn turns into a king.
  # Thus calculating the x co-ordinates of the board.
  opponentColor = gamePlay.getOpponentColor(color)
  value = 0
  for piece in range(1, 33):
    xy = gamePlay.serialToGrid(piece)
    x = xy[0]
    y = xy[1]
    if color == "r":
      if board[x][y].upper() == color.upper():
        value = value + x
      elif board[x][y].upper() == opponentColor.upper():
        value = value - (8-x)
    else:
      if board[x][y].upper() == color.upper():
        value = value + (8-x)
      elif board[x][y].upper() == opponentColor.upper():
        value = value - x
  return value

def evaluation(board, color, depth, time):
  # This function adds the value obtained from each of the evaluation functions(which has their respective weights) and return a final value
  # When depth is even, max value gets evaluated, hence we send our color to each of the evaluation function
  # When depth is odd, min value gets evaluated, hence we send opponent's color to each of the evaluation function
  
  # TIME UPDATE: when there is plenty of time, use all the evaluation functions but when time is less than 10 seconds, I am only making use of only 2 evaluation functions,
  # namely, number of pawns and number of kings.
  if time > 10:
    if depth%2 == 0:
      value = 0.35 * evaluation1(board,color) + 0.20 * evaluation2(board,color) + 0.15 * evaluation3(board,color) + 0.2 * evaluation4(board,color) + 0.1 * evaluation5(board, color)
      #value = evaluation1(board,color)
    else:
      #value = evaluation1(board,color)
      value = 0.35 * evaluation1(board,gamePlay.getOpponentColor(color)) + 0.20 * evaluation2(board,gamePlay.getOpponentColor(color)) + 0.15 * evaluation3(board,gamePlay.getOpponentColor(color)) + 0.2 * evaluation4(board,gamePlay.getOpponentColor(color)) + 0.1 * evaluation5(board, gamePlay.getOpponentColor(color))
  else:
    if depth%2 == 0:
      value = 0.6 * evaluation1(board,color) + 0.4 * evaluation2(board, color)
    else:
      value = 0.6 * evaluation1(board,gamePlay.getOpponentColor(color)) + 0.4 * evaluation2(board, gamePlay.getOpponentColor(color))
  return value


def nextMove(board, color, time, movesRemaining): 
  #generates all the possible moves from the current state of board   
  global count
  count = count + 1

  moves = getAllPossibleMoves(board, color)    
  if len(moves) == 0:
    return "pass"
  elif len(moves) == 1:
    return moves[0]
  #Now the current state recieved from gamePlay is taken as maxNode  
  maxNode = returnList(board, 0, color)  
  
  # Here, I am not wasting much time for playing the first two moves
  if count < 3:
    bestmove = alphaBetaPruning(maxNode,4, time)
  # when time remaining is less than 10 seconds, only go to depth 2 
  elif (time < 10):
    bestmove = alphaBetaPruning(maxNode,2, time)
  # when time remaining is less than 10 seconds, only go to depth 4
  elif (time < 20):
    bestmove = alphaBetaPruning(maxNode,4, time)
  #start the alpha beta pruning to obtain the best move with depth currently set to 6
  else:
    bestmove = alphaBetaPruning(maxNode,6, time) 
  # print "Best Move: ", bestmove
  return bestmove

def returnList(state, depth, color):
    #returns a list containing all the parameters as its elements
    return [state, depth, color]

def alphaBetaPruning(node, depth, time):
  moves = getAllPossibleMoves(node[0], node[2])
  bestMove = moves[0]
  #to set the lower bound at max node    
  bestScore = -float("inf")
  for move in moves:
    newBoard = deepcopy(node[0])
    gamePlay.doMove(newBoard,move)
    #creating a new node from the initial board generation
    newNode = returnList(newBoard, node[1]+1, gamePlay.getOpponentColor(node[2]))    
    #calls the min function next
    score = minimum(newNode, depth, -float("inf"), float("inf"), time)
    if score > bestScore:
      bestMove = move
      bestScore = score
  return bestMove

#alpha: lower bound on minimax score
#beta: upper bound on minimax score
def minimum(minNode, depth, alpha, beta, time):
  #print "Depth min = ", minNode[1]
  if minNode[1] == depth:
    # Since the depth is reached, the leaf node is now evluatated and a value is returned to the parent node
    return evaluation(minNode[0],minNode[2],minNode[1], time)
  moves = getAllPossibleMoves(minNode[0], minNode[2])
  #to set upper bound at min node
  bestScore = float("inf")
  for move in moves:
    newBoard = deepcopy(minNode[0])
    gamePlay.doMove(newBoard, move)
    #calls next turn which is maximum node's 
    newNode = returnList(newBoard, minNode[1]+1, gamePlay.getOpponentColor(minNode[2]))
    score = maximum(newNode, depth, alpha, beta, time)
    #alpha is the lower bound which is to be found so if min node is less than next nodes, they can be pruned
    if bestScore <= alpha:
      return bestScore
    if bestScore < beta:
      beta = bestScore
    if score < bestScore:            
      bestScore = score
  return bestScore

def maximum(maxNode, depth, alpha, beta, time):
  #print "depth max =  ", maxNode[1]
  if maxNode[1] == depth:
    # Since the depth is reached, the leaf node is now evluatated and a value is returned to the parent node
    return evaluation(maxNode[0],maxNode[2], maxNode[1], time)
  moves = getAllPossibleMoves(maxNode[0], maxNode[2])
  #lower bound for max
  bestScore = -float("inf")
  for move in moves:
    newBoard = deepcopy(maxNode[0])
    gamePlay.doMove(newBoard, move)
    newNode = returnList(newBoard, maxNode[1]+1, gamePlay.getOpponentColor(maxNode[2]))
    #calls minimum as next turn is of MIN node or the opponent
    score = minimum(newNode, depth, alpha, beta,time)
    #beta is the upper bound which is to be found so if max node is greater than next nodes, they can be pruned
    if bestScore >= beta:
      return bestScore
    if bestScore > alpha:
      alpha = bestScore
    if score > bestScore:            
      bestScore = score
  return bestScore
