import random
import gamePlay
from getAllPossibleMoves import getAllPossibleMoves

def nextMove(board, color, time, movesRemaining):
    '''Just play randomly among the possible moves'''
    inp1 = input("Enter number of pawn to move: ")
    inp2 = input("ENter destn")
    bestMove = [inp1,inp2]
    #print "RandomMove = ", bestMove
    return bestMove