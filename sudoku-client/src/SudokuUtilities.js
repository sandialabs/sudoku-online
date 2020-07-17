// ECMAScript 6 has sets but is missing functions for set operations.
// This file provides equivalents.

import { 
	array2D, 
	arrayRotateLeft,
	arrayRotateRight,
	dimensions,
	swapRows2D, 
	swapColumns2D
} from './ArrayUtilities';

import { clone } from 'ramda';

function setUnion(a, b) {
	return new Set([...a, ...b]);
}

function setIntersection(a, b) {
	return new Set([...a].filter(x => b.has(x)));
}

function setDifference(a, b) {
	return new Set([...a].filter(x => !b.has(x)));
}

function setSymmetricDifference(a, b) {
	return setDifference(setUnion(a, b), setIntersection(a, b));
}

var SerialNumbers = { };

/** Request a serial number for a named category
 *
 * A serial number is a monotonically increasing integer.  We allow
 * multiple categories of serial numbers by requiring the user 
 * to specify a category name:
 *
 * let serial1 = newSerialNumber("foo"); (returns 0)
 * let serial2 = newSerialNumber("foo"); (returns 1)
 * let serial3 = newSerialNumber("foo"); (returns 2)
 * let other_serial1 = newSerialNumber("bar"); (returns 0)
 * let serial4 = newSerialNumber("foo"); (returns 3)
 *
 * Serial numbers for different categories are not guaranteed
 * to be disjoint.
 */

function newSerialNumber(key) {
	let newSerial = 0;
	if (key in SerialNumbers) {
		newSerial = SerialNumbers[key] + 1;
	}
	SerialNumbers[key] = newSerial;
	return newSerial;
}

function getDegree(board) {
	return Math.sqrt(board.length);
}

function initialMoveList(degree) {
	return range(degree*degree);
}

function range(size) {
	return [...Array(size).keys()];
}

// Return a base-case solution for a Sudoku board.  You can
// use randomizeFilledBoard() to scramble this while 
// maintaining the correctness of the solution.

function filledBoard(degree) {
	const boardSize = degree*degree;
	var board = array2D(boardSize, boardSize);
	const rows = degree*degree;
	const columns = degree*degree;
	var row, column;

	// Start by filling the first row of the board trivially.  We 
	// will transform this first row to get all the others.
	for (column = 0; column < columns; ++column) {
		board[0][column] = column;
	}

	// The board is full, but all the columns have the same value.  
	// Rotating according to the following scheme will fix that.
	for (row = 1; row < boardSize; ++row) {
		const isFirstRowInBlock = ((row % degree) === 0);

		if (isFirstRowInBlock) {
			board[row] = arrayRotateLeft(board[row-1], 1);
		} else {
			board[row] = arrayRotateLeft(board[row-1], degree);
		}
	}
	return board;
}

// Return a random integer in (low, high].
function randomInRange(low, high) {
	return Math.floor(
		low + Math.random() * (high - low)
		);
}

/// Return a Set() with the assignments in a given row.
//
// Arguments:
//     board: 2d array filled with integers and nulls.  Board must be square.
//     row: Integer between 0 and rows-1, inclusive.
//
// Returns: EC6 Set() containing all of the non-null elements from that row.

function assignmentsInRow(board, row) {
	let noNulls = [];
	const degree = getDegree(board);
	for (let c = 0; c < degree*degree; ++c) { 
		if (board[row][c] !== null) {
			noNulls.push(board[row][c]);
		}
	}
	return new Set(noNulls);
}


/// Return a Set() with the assignments in a given column.
//
// Arguments:
//     board: 2d array filled with integers and nulls.  Board must be square.
//     column: Integer between 0 and columns-1, inclusive.
//
// Returns: EC6 Set() containing all of the non-null elements from that column.

function assignmentsInColumn(board, column) {
	let noNulls = [];
	const degree = getDegree(board);
	for (let r = 0; r < degree*degree; ++r) {
		if (board[r][column] !== null) {
			noNulls.push(board[r][column]);
		}
	}
	return new Set(noNulls);
}


/// Return a Set() with the assignments in a given block.
//
// Arguments:
//     board: 2d array filled with integers and nulls.  Board must be square.
//     blockRow: Row (in [0, d)) of the block you want
//     blockColumn: Column (in [0, d)) of the column you want
//
// Returns: EC6 Set() containing all of the non-null elements from that block.

function assignmentsInBlock(board, blockRow, blockColumn) {
	let noNulls = [];
	const degree = getDegree(board);
	const blockUpperLeft = (blockRow*degree, blockColumn*degree);
	for (let r = blockUpperLeft[0]; r < blockUpperLeft[0] + degree; ++r) {
		for (let c = blockUpperLeft[1]; c < blockUpperLeft[1] + degree; ++c) {
			const value = board[r][c];
			if (value !== null) {
				noNulls.push(value);
			}
		}
	}
	return new Set(noNulls);
}

/// Compute the move lists for every cell in a board.
//
// If a board has an assignment in a given cell, that cell's move 
// list is empty.  Otherwise it is a set of integers between 0 and
// (degree * degree) - 1.
// 
// Arguments:
// 	   board: 2D array filled with integers and nulls
// 
// Returns: 
//     2D array of move lists

function computeMoveLists(board) {
	const D = getDegree(board);
	const [rows, columns] = dimensions(board);
	const rowIndices = range(rows);

	// First we need the assignments for each different region 
	// in the board -- row, column, or block.  We need each one
	// D*D different times so it's worth precomputing them.
	const rowAssignments = rowIndices.map((row) => (assignmentsInRow(board, row)));
	const columnAssignments = rowIndices.map((col) => (assignmentsInColumn(board, col)));
	let blockAssignments = array2D(D, D);
	for (let r = 0; r < D; ++r) {
		for (let c = 0; c < D; ++c) {
			blockAssignments[r][c] = assignmentsInBlock(board, r, c);
		}
	}

	// Now we can walk over the entire board and compute the
	// set of available moves for each cell as 
	// (allMoves - union(rowAssignments, colAssignments, blockAssignments)).
	
	let moveLists = array2D(rows, columns);
	const fullMoveSet = new Set(range(D*D));

	for (let r = 0; r < rows; ++r) {
		for (let c = 0; c < columns; ++c) {
			const blockRow = Math.floor(r/D);
			const blockColumn = Math.floor(c/D);
			const foo = setUnion(rowAssignments[r], columnAssignments[c]);
			const assignmentSet = setUnion(
				blockAssignments[blockRow][blockColumn],
				foo
				);

			const moveSet = setDifference(
				fullMoveSet, assignmentSet
				);
			moveLists[r][c] = [...moveSet];
		}
	}

	return moveLists;
}




// Randomize a filled, correct board by permuting rows and columns within 
// blocks.  Returns a new array -- argument is treated as immutable.
//
// Arguments:
//     board: 2D array filled with integers.  Rows and columns must be equal.
//         Rows and columns must be a perfect square.  
// 
// Optional Arguments:
//     numSwaps (integer): How many times to swap two rows/columns.  
//         More swaps == less chance of repeating an earlier board. 
//         (assuming that you've seeded the random number generator)
//         Defaults to 100.
//         
function randomizeFilledBoard(board, numSwaps=100) {
	const D = getDegree(board);

	for (let i = 0; i < numSwaps; ++i) {
		// First: are we swapping rows or columns?
		const swapRow = randomInRange(0, 2);
		let whichBlock = randomInRange(0, D);
		let fromId = (D*whichBlock) + randomInRange(0, D);
		let toId = (D*whichBlock) + randomInRange(0, D);
		if (swapRow) {
			board = swapRows2D(board, fromId, toId);
		} else {
			board = swapColumns2D(board, fromId, toId);
		}
	}
}

// Return a random int in the range [min, max)
 function randomInt(min, max) {
 	return Math.floor(Math.random() * max) + min;
 }
 
// Null out zero or more cells from an existing board.
// 
// This function will take an existing board and choose (uniformly 
// at random) a user-specified number of cells to replace with nulls.
// A new board is returned: the argument is not modified.
// 
// Note: cells that are already null will remain that way.
// 
// Arguments:
//     board: 2D square array filled with integers and nulls
//     numEmpties (int): How many cells to make empty
//     
// Returns:
//     New board with same dimensions and contents, but some cells
//     will have their values replaced with 'null'
 

 function clearRandomCells(board, numEmpties) {
 	const result = clone(board);
 	const [rows,columns] = dimensions(board);

 	for (let i = 0; i < numEmpties; ++i) {
 		let r = randomInt(0, rows);
 		let c = randomInt(0, columns);
 		while (result[r][c] == null) {
 			r = randomInt(0, rows);
 			c = randomInt(0, columns);
 		}
 		result[r][c] = null;
 	}
 	return result;
 }

function boardIsConsistent(board) {
	const D = getDegree(board);
	const [rows, columns] = dimensions(board);
	let row, column;
	const allMoves = range(D*D);

	// Check all the rows individually
	for (row = 0; row < rows; ++row) {
		let currentMoves = clone(allMoves);
		for (column = 0; column < columns; ++column) {
			const move = board[row][column];
			if (move !== null) {
				if (currentMoves[move] === -1) {
					return false;
				} else {
					currentMoves[move] = -1;
				}
			}
		}
	}

	// Check all the columns individually
	for (column = 0; column < columns; ++column) {
		let currentMoves = clone(allMoves);
		for (row = 0; row < rows; ++row) {
			const move = board[row][column];
			if (move !== null) {
				if (currentMoves[move] === -1) {
					return false;
				} else {
					currentMoves[move] = -1;
				}
			}
		}
	}

	// Check each block
	for (row = 0; row < D; ++row) {
		for (column = 0; column < D; ++column) {
			let currentMoves = clone(allMoves);
			for (let r = D*row; r < D*(row+1); ++r) {
				for (let c = D*column; c < D*(column+1); ++c) {
					const move = board[r][c];
					if (move !== null) {
						if (currentMoves[move] === -1) {
							return false;
						} else {
							currentMoves[move] = -1;
						}
					}		
				}
			}
		}
	}
	
	return true;
}

function makeBoard(degree, assignments, availableMoves) {
	return {
		'degree': degree,
		'assignments': clone(assignments),
		'availableMoves': clone(availableMoves)
	};
}

export { 
	clearRandomCells,
	computeMoveLists,
	filledBoard,
	initialMoveList,
	makeBoard,
	newSerialNumber, 
	range, 
	setDifference, 
	setIntersection, 
	setUnion,
	walkTree
	 };
