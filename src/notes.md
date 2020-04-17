Notes:

SudokuSquare is a single square within a puzzle.  It has:
	- permissible moves for this square
	- the ability to display those moves as a D x D array
	- the ability to display its assigned move
	- row and column IDs

SudokuBlock() is a D x D array of squares.  This class will probably disappear.

SudokuBoard is a (D*D) x (D*D) array of squares.  It has:
	- permissible moves for all squares
	- a serial number
	- a 2D array of SudokuSquares

SudokuBoard needs to render squares in groups to get thicker borders between groups.

