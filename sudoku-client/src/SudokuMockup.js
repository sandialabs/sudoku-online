// SudokuMockup.js -- mocked-up functions that will be replaced
// with server requests

import { clearRandomCells, filledBoard, randomizeBoard, computeMoveLists } from './SudokuUtilities';
import { dimensions, flatten } from './ArrayUtilities';
import { dispatch as dispatchHeuristic } from './Heuristics';

function requestInitialBoard(degree) {
	const solution = filledBoard(degree);
	// const randomized = randomizeBoard(solution, 100);
	const opened = clearRandomCells(solution, 
	 								 Math.floor(degree*degree*degree*degree/2));
	return boardAsJson(degree, opened);
}  


function boardAsJson(degree, board) {
	return JSON.stringify({
		degree: degree,
		assignments: jsonBoardAssignments(board),
		availableMoves: jsonMoveLists(board)
	});
}


// Lay out a board's assignments in row-major order.
function jsonBoardAssignments(board) {
	// return flatten(board);
	return board;
}

function jsonMoveLists(board) {
	// return flatten(computeMoveLists(board)); 
	return computeMoveLists(board);
}

function executeHeuristic(requestString) {
	return JSON.stringify(dispatchHeuristic(JSON.parse(requestString)));
}

export {
	requestInitialBoard,
	executeHeuristic
};