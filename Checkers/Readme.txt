I have used 5 Evaluation Functions and hence got a value which is an aggregate of all 
these function multiplied by weights which i have given.

Evaluation Function 1: 	Counts the number of pawns excluding the kings of the current state.
Evaluation Function 2: 	Counts only the number of kings in the current state
Evaluation Function 3: 	I have developed an evaluation matrix which has different values 
			for different positions in the board. Thus return a aggregate of all
			the positions of the pawn.
Evaluation Function 4: 	Checks whether a particular pawn has its neighbors covered so that 
			capturing of this pawn cannot take place.
Evaluation Function 5: 	Always trying to go toward the opponents end so that the pawn turns 
			into a king. Thus calculating the x co-ordinates of the board.


To run the program:
python gameplay.py -t<timelimit> -v agopal simpleGreedy
