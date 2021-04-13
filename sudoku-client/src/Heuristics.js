// Heuristics.js -- dummy implementation of Sudoku heuristics

import { computeMoveLists, makeBoard } from './SudokuUtilities';
import { clone } from 'ramda';

function dispatch(request) {

    console.log('dispatch: Board is ');
    console.log(request.board);

    if (request.heuristic === 'listHeuristics') {
        return listHeuristics();
    } else if (request.heuristic === 'include/exclude') {
        return evaluateIncludeExclude(request);
    } else if (request.heuristic === 'pivot') {
        return evaluatePivot(request);
    } else {
        console.log('ERROR: Unknown heuristic ' + request.heuristic);
        return null;
    }
}

function evaluateIncludeExclude(request) {
    return [
        constrainMoves(
            assignValue(request.board, request.action.cell, request.action.value)
            )
        ];
}

/** Assign a value to a cell in a board
 *
 * Arguments:
 *     board {sudokuBoard}: Board with at least one unassigned cell
 *     cell {list of 2 integers}: Which cell to assign
 *     value {integer}: Value to put into that cell
 *
 * 
 */
function assignValue(board, cell, value) {
    const D = board.degree;

    // Assumption check: the coordinates are within the bounds of the board
    console.assert(cell[0] >= 0 && cell[0] < D*D,
    {
        value: cell[0],
        maxRow: D*D,
        error: 'Cell row for assignment must be between 0 and maxRow.'
    });
    console.assert(cell[1] >= 0 && cell[1] < D*D,
    {
        value: cell[``],
        maxColumn: D*D,
        error: 'Cell column for assignment must be between 0 and maxColumn.'
    });
    
    // Assumption check: the chosen value must be between 0 and D*D-1, inclusive.
    console.assert(value >= 0 && value < D*D,
        {value: value,
         error: 'Chosen value must be between 0 and ' + D*D-1}
         );
   
    // Assumption check: the cell is not yet assigned
    console.assert(board.assignments[cell[0]][cell[1]] === null,
        {
            board: board,
            cell: cell,
            error: 'Cell ' + cell + ' is already assigned!'
        });

    const newBoard = makeBoard(board.degree, board.assignments, board.availableMoves);
    newBoard.assignments[cell[0]][cell[1]] = value;
    return newBoard;
}

// The 'pivot' heuristic takes an input board and the ID of an unassigned
// cell.  It creates one child board for each possible assignment of
// a value to that cell.
function evaluatePivot(request) {
    const board = request.board;
    const cell = request.action.cell;

    const possibleAssignments = board.availableMoves[cell[0]][cell[1]];
    console.log('evaluatePivot: Possible assignments for ' 
        + cell + ': '
        + possibleAssignments);

    let resultBoards = [];
    possibleAssignments.forEach(value => {
        resultBoards.push(
            constrainMoves(
                assignValue(board, cell, value)
                )
            );
        });
    return resultBoards;
}


// XXX NOTE: This does not take into account external forces that might
// constrain the move list.
function constrainMoves(board) {
    return makeBoard(
        board.degree,
        board.assignments,
        computeMoveLists(board.assignments)
        );
}

function listHeuristics() {
    return [
        { 'internal_name': 'include/exclude', 'user_name': 'Assign Single Cell' },
        { 'internal_name': 'pivot', 'user_name': 'Expand All Possibilities' }

    ];
}

export { dispatch };
